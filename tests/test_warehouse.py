import tempfile
import unittest
from pathlib import Path

import polars as pl

from fast_analysis.config import Settings
from fast_analysis.warehouse import connect, replace_raw, validate


class WarehouseTest(unittest.TestCase):
    def test_replaces_raw_and_reports_primary_key_issues(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = Settings(
                source_name="pedidos",
                query_file=Path(directory) / "source.sql",
                duckdb_path=Path(directory) / "analysis.duckdb",
                sqlserver_url=None,
                primary_key=("id_pedido",),
            )
            warehouse = connect(settings)
            try:
                replace_raw(
                    warehouse,
                    settings,
                    pl.DataFrame({"id_pedido": [1, 1, None], "status": ["novo", "novo", "erro"]}),
                )
                results = {name: (status, value) for name, status, value, _ in validate(warehouse, settings)}
                self.assertEqual(warehouse.execute("SELECT count(*) FROM analytics.vw_pedidos").fetchone()[0], 3)
                self.assertEqual(results["primary_key_nulls"], ("fail", 1))
                self.assertEqual(results["primary_key_duplicates"], ("fail", 1))
            finally:
                warehouse.close()


if __name__ == "__main__":
    unittest.main()
