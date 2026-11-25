"""End-to-end checks for the Module 6a generated datasets and evidence."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Module06a"))
import common  # noqa: E402
import prepare  # noqa: E402
import to_parquet  # noqa: E402
import race  # noqa: E402
import explain  # noqa: E402
import boundary  # noqa: E402


class Module06aIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prepared = prepare.build_history()
        cls.converted = to_parquet.convert()

    def test_historical_and_csv_counts(self) -> None:
        self.assertEqual(self.prepared["history_rows"], common.EXPECTED_ROWS)
        self.assertEqual(self.prepared["csv_rows"], self.prepared["source_rows"])
        self.assertEqual(self.converted["sqlite"]["rows"], common.EXPECTED_ROWS)

    def test_parquet_count_and_aggregate_equivalence(self) -> None:
        self.assertEqual(self.converted["sqlite"], self.converted["duckdb_parquet"])

    def test_analytical_benchmark_equivalence_and_artifacts(self) -> None:
        results = race.run(runs=5)
        self.assertEqual({r["query"] for r in results}, {"dashboard", "monthly"})
        self.assertTrue(all(r["results_equivalent"] for r in results))
        self.assertTrue((common.RESULTS / "sqlite-vs-duckdb.csv").exists())
        json_results = json.loads((common.RESULTS / "sqlite-vs-duckdb.json").read_text(encoding="utf-8"))
        self.assertEqual(len(json_results["results"]), 2)

    def test_explain_analyze_generated(self) -> None:
        plan = explain.capture()
        self.assertIn("EXPLAIN ANALYZE", plan)
        self.assertTrue((common.RESULTS / "explain-analyze.txt").exists())

    def test_transactional_boundary_workloads_complete(self) -> None:
        results = boundary.run(runs=5)
        self.assertEqual(len(results), 4)
        self.assertTrue(all(row["results_validated"] for row in results))
        self.assertTrue((common.RESULTS / "boundary-results.csv").exists())


if __name__ == "__main__":
    unittest.main()
