"""Capture real DuckDB EXPLAIN ANALYZE plans for both analytical workloads."""
from __future__ import annotations

import json
import re

import duckdb

from common import DASHBOARD_SQL, MONTHLY_SQL, PARQUET_PATH, RESULTS


def capture() -> str:
    if not PARQUET_PATH.exists():
        raise FileNotFoundError("Run to_parquet.py first")
    RESULTS.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    blocks = []
    summaries = []
    try:
        for name, template in (("dashboard", DASHBOARD_SQL), ("monthly", MONTHLY_SQL)):
            sql = template.format(source=f"read_parquet('{PARQUET_PATH.as_posix()}')")
            plan = str(con.execute("EXPLAIN ANALYZE " + sql).fetchone()[1])
            blocks.append(f"{'=' * 78}\n{name.upper()} QUERY\n{sql}\n\nACTUAL EXPLAIN ANALYZE\n{plan}\n")
            # Keep operator and cardinality evidence sourced from DuckDB's printed actual plan.
            operators = sorted(set(re.findall(r"(?m)^\s*([A-Z][A-Z_ ]*(?:SCAN|GROUP_BY|AGGREGATE|ORDER_BY)[A-Z_]*)\s*$", plan)))
            cardinalities = [int(v.replace(",", "")) for v in re.findall(r"(?m)^\s*([\d,]+) rows\s*$", plan)]
            summaries.append({"query": name, "operators_observed": operators,
                              "row_counts_observed": cardinalities,
                              "scan_rows": max(cardinalities, default=None),
                              "interpretation": "Projection pushdown reads only referenced columns; scan/aggregate cardinalities and operator timings are reported in the captured plan."})
    finally:
        con.close()
    text = "\n".join(blocks)
    (RESULTS / "explain-analyze.txt").write_text(text, encoding="utf-8")
    benchmark_path = RESULTS / "sqlite-vs-duckdb.json"
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8")) if benchmark_path.exists() else None
    metadata = {"summaries": summaries, "benchmark_comparison_available": benchmark is not None,
                "benchmark_results": benchmark.get("results") if benchmark else None}
    (RESULTS / "explain-summary.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(text)
    print("Plan summary saved to", RESULTS / "explain-summary.json")
    return text


if __name__ == "__main__":
    capture()
