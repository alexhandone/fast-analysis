from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _safe_identifier(value: str, label: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise ValueError(f"{label} deve usar apenas letras, números e _. Valor recebido: {value!r}")
    return value


@dataclass(frozen=True)
class Settings:
    source_name: str
    query_file: Path
    duckdb_path: Path
    sqlserver_url: str | None
    primary_key: tuple[str, ...]

    @property
    def raw_table(self) -> str:
        return f"raw.{self.source_name}"

    @property
    def analytics_view(self) -> str:
        return f"analytics.vw_{self.source_name}"


def load_settings(require_source: bool = False) -> Settings:
    load_dotenv(PROJECT_ROOT / ".env")
    source_name = _safe_identifier(os.getenv("FA_SOURCE_NAME", "operacao"), "FA_SOURCE_NAME")
    query_file = PROJECT_ROOT / os.getenv("FA_QUERY_FILE", "sql/sqlserver/operacao.sql")
    duckdb_path = PROJECT_ROOT / os.getenv("FA_DUCKDB_PATH", "data/fast_analysis.duckdb")
    primary_key = tuple(_safe_identifier(column.strip(), "FA_PRIMARY_KEY") for column in os.getenv("FA_PRIMARY_KEY", "").split(",") if column.strip())
    sqlserver_url = os.getenv("SQLSERVER_URL")
    if require_source and not sqlserver_url:
        raise ValueError("SQLSERVER_URL não foi definido. Crie .env a partir de .env.example.")
    return Settings(source_name, query_file, duckdb_path, sqlserver_url, primary_key)
