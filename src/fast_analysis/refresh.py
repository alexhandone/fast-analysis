from __future__ import annotations

from pathlib import Path

import polars as pl
from sqlalchemy import create_engine

from .config import Settings
from .warehouse import connect, log_refresh, replace_raw, validate


def read_query(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Consulta não encontrada: {path}")
    query = path.read_text(encoding="utf-8").strip()
    if not query or query.startswith("-- Edite"):
        raise ValueError(f"Edite a consulta de origem antes do refresh: {path}")
    return query


def extract_sqlserver(settings: Settings) -> pl.DataFrame:
    engine = create_engine(settings.sqlserver_url)
    try:
        with engine.connect() as source_connection:
            return pl.read_database(query=read_query(settings.query_file), connection=source_connection)
    finally:
        engine.dispose()


def refresh(settings: Settings) -> tuple[int, list[tuple[str, str, int, str]]]:
    warehouse = connect(settings)
    try:
        frame = extract_sqlserver(settings)
        replace_raw(warehouse, settings, frame)
        checks = validate(warehouse, settings)
        row_count = frame.height
        failures = sum(status == "fail" for _, status, _, _ in checks)
        log_refresh(warehouse, settings, "success" if failures == 0 else "warning", row_count, f"{len(checks)} validações; {failures} com falha")
        return row_count, checks
    except Exception as error:
        log_refresh(warehouse, settings, "failed", None, str(error))
        raise
    finally:
        warehouse.close()
