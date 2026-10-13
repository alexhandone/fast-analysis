from __future__ import annotations

import argparse
from datetime import datetime

from .config import PROJECT_ROOT, load_settings
from .refresh import refresh
from .warehouse import connect


def command_refresh(_: argparse.Namespace) -> None:
    settings = load_settings(require_source=True)
    rows, checks = refresh(settings)
    print("FAST ANALYSIS REFRESH")
    print(f"Fonte: SQL Server | dataset: {settings.source_name}")
    print(f"RAW atualizada: {settings.raw_table} ({rows:,} registros)")
    print(f"View analítica: {settings.analytics_view}")
    for name, status, value, detail in checks:
        print(f"{'✓' if status == 'pass' else '!'} {name}: {value:,} ({detail})")


def command_inspect(_: argparse.Namespace) -> None:
    settings = load_settings()
    warehouse = connect(settings)
    try:
        tables = warehouse.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema IN ('raw', 'analytics', 'audit') ORDER BY 1, 2").fetchall()
        print(f"DuckDB: {settings.duckdb_path}")
        for schema, table in tables:
            print(f"- {schema}.{table}")
        history = warehouse.execute("SELECT refreshed_at, status, row_count, detail FROM audit.refresh_log ORDER BY refreshed_at DESC LIMIT 5").fetchall()
        if history:
            print("\nÚltimos refreshes:")
            for refreshed_at, status, row_count, detail in history:
                print(f"- {refreshed_at} | {status} | {row_count or 0} | {detail}")
    finally:
        warehouse.close()


def command_export(args: argparse.Namespace) -> None:
    settings = load_settings()
    query_path = PROJECT_ROOT / args.query
    warehouse = connect(settings)
    try:
        frame = warehouse.execute(query_path.read_text(encoding="utf-8")).pl()
    finally:
        warehouse.close()
    output_dir = PROJECT_ROOT / "exports"
    output_dir.mkdir(exist_ok=True)
    output = output_dir / f"{args.name}_{datetime.now():%Y%m%d_%H%M%S}.{args.format}"
    if args.format == "csv":
        frame.write_csv(output)
    else:
        frame.write_excel(output)
    print(f"Exportado: {output} ({frame.height:,} registros)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline local do fast-analysis")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("refresh", help="Extrai SQL Server e substitui a RAW").set_defaults(func=command_refresh)
    commands.add_parser("inspect", help="Lista objetos e histórico local").set_defaults(func=command_inspect)
    export = commands.add_parser("export", help="Executa SQL no DuckDB e gera arquivo")
    export.add_argument("--query", required=True, help="Arquivo SQL relativo à raiz do projeto")
    export.add_argument("--name", required=True, help="Prefixo do arquivo exportado")
    export.add_argument("--format", choices=("csv", "xlsx"), default="csv")
    export.set_defaults(func=command_export)
    args = parser.parse_args()
    args.func(args)
