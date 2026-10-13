from __future__ import annotations

from datetime import datetime

import duckdb
import polars as pl

from .config import Settings


def connect(settings: Settings) -> duckdb.DuckDBPyConnection:
    settings.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(settings.duckdb_path))
    connection.execute("CREATE SCHEMA IF NOT EXISTS raw")
    connection.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    connection.execute("CREATE SCHEMA IF NOT EXISTS audit")
    connection.execute("CREATE TABLE IF NOT EXISTS audit.refresh_log (refreshed_at TIMESTAMP, source_name VARCHAR, status VARCHAR, row_count BIGINT, detail VARCHAR)")
    return connection


def replace_raw(connection: duckdb.DuckDBPyConnection, settings: Settings, frame: pl.DataFrame) -> None:
    if frame.width == 0:
        raise ValueError("A consulta não retornou colunas; a RAW não foi substituída.")
    connection.register("incoming_data", frame)
    try:
        connection.execute(f"CREATE OR REPLACE TABLE {settings.raw_table} AS SELECT * FROM incoming_data")
        connection.execute(f"CREATE OR REPLACE VIEW {settings.analytics_view} AS SELECT * FROM {settings.raw_table}")
    finally:
        connection.unregister("incoming_data")


def validate(connection: duckdb.DuckDBPyConnection, settings: Settings) -> list[tuple[str, str, int, str]]:
    count = connection.execute(f"SELECT count(*) FROM {settings.raw_table}").fetchone()[0]
    results = [("row_count", "pass", count, "registros carregados")]
    if not settings.primary_key:
        return results
    keys = ", ".join(settings.primary_key)
    null_condition = " OR ".join(f"{key} IS NULL" for key in settings.primary_key)
    nulls = connection.execute(f"SELECT count(*) FROM {settings.raw_table} WHERE {null_condition}").fetchone()[0]
    duplicates = connection.execute(f"SELECT count(*) FROM (SELECT {keys}, count(*) FROM {settings.raw_table} GROUP BY {keys} HAVING count(*) > 1)").fetchone()[0]
    results.extend([("primary_key_nulls", "pass" if nulls == 0 else "fail", nulls, f"chave: {keys}"), ("primary_key_duplicates", "pass" if duplicates == 0 else "fail", duplicates, f"chave: {keys}")])
    return results


def log_refresh(connection: duckdb.DuckDBPyConnection, settings: Settings, status: str, row_count: int | None, detail: str) -> None:
    connection.execute("INSERT INTO audit.refresh_log VALUES (?, ?, ?, ?, ?)", [datetime.now(), settings.source_name, status, row_count, detail])
