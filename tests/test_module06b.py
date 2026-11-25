"""Checks for Module 6b JSON and key/value experiments."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Module06b"))
import json_bench  # noqa: E402
import kv_compare  # noqa: E402


class Module06bTests(unittest.TestCase):
    def test_json_constraints_functions_index_and_plans(self) -> None:
        result = json_bench.run()
        self.assertEqual(result["device_count"], 3)
        self.assertTrue(result["queries_equivalent"])
        self.assertTrue(result["indexed_expression_uses_ix_device_vendor"])
        self.assertTrue(result["invalid_json_rejected"])
        self.assertTrue((json_bench.RESULTS / "json-query-plans.txt").exists())

    def test_key_value_integrity_and_outputs(self) -> None:
        result = kv_compare.run(runs=3)
        self.assertTrue(result["values_validated_each_run"])
        self.assertEqual(result["sessions_per_run"], 50_000)
        self.assertEqual(result["sqlite_cross_session_query"]["count"], 500)
        self.assertTrue((kv_compare.RESULTS / "kv-results.csv").exists())
        self.assertTrue((kv_compare.RESULTS / "kv-results.json").exists())


if __name__ == "__main__":
    unittest.main()
