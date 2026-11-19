"""Interleaved SQLite/DuckDB analytical benchmarks on equivalent 2M-row data."""
from __future__ import annotations

import csv
import json
import os
import platform
import sqlite3
import statistics
import time
from datetime import date, datetime

import duckdb

from common import DASHBOARD_SQL, EXPECTED_ROWS, HISTORY_DB, MONTHLY_SQL, PARQUET_PATH, RESULTS

RUNS = 7


def canonical(rows: list[tuple]) -> list[tuple]:
    """Normalize engine-specific date/numeric scalar representations."""
    normalized = []
    for row in rows:
        out = []
        for value in row:
            if isinstance(value, (date, datetime)):
                value = value.isoformat()
            elif isinstance(value, float):
                value = round(value, 2)
            out.append(value)
        normalized.append(tuple(out))
    return normalized


def run(runs: int = RUNS) -> list[dict[str, object]]:
    if runs < 5:
        raise ValueError("Use at least five timed runs")
    if not HISTORY_DB.exists() or not PARQUET_PATH.exists():
        raise FileNotFoundError("Run prepare.py and to_parquet.py first")
    RESULTS.mkdir(parents=True, exist_ok=True)
    sq = sqlite3.connect(HISTORY_DB)
    duck = duckdb.connect()
    outputs: list[dict[str, object]] = []
    try:
        sq_count = sq.execute("SELECT COUNT(*) FROM report_history").fetchone()[0]
        dq_count = duck.execute("SELECT COUNT(*) FROM read_parquet(?)", [str(PARQUET_PATH)]).fetchone()[0]
        if sq_count != dq_count or sq_count != EXPECTED_ROWS:
            raise RuntimeError(f"Engine row counts differ: SQLite={sq_count}, DuckDB={dq_count}")
        for name, template in (("dashboard", DASHBOARD_SQL), ("monthly", MONTHLY_SQL)):
            sqlite_sql = template.format(source="report_history")
            duck_sql = template.format(source="read_parquet(?)")
            expected = canonical(sq.execute(sqlite_sql).fetchall())
            actual = canonical(duck.execute(duck_sql, [str(PARQUET_PATH)]).fetchall())
            if expected != actual:
                raise AssertionError(f"{name} result sets differ (SQLite {len(expected)}, DuckDB {len(actual)})")
            # Warm both engines before measurement.
            sq.execute(sqlite_sql).fetchall()
            duck.execute(duck_sql, [str(PARQUET_PATH)]).fetchall()
            times = {"sqlite": [], "duckdb": []}
            for i in range(runs):
                order = ("sqlite", "duckdb") if i % 2 == 0 else ("duckdb", "sqlite")
                for engine in order:
                    start = time.perf_counter()
                    if engine == "sqlite":
                        rows = sq.execute(sqlite_sql).fetchall()
                    else:
                        rows = duck.execute(duck_sql, [str(PARQUET_PATH)]).fetchall()
                    times[engine].append((time.perf_counter() - start) * 1000)
                    if canonical(rows) != expected:
                        raise AssertionError(f"{engine} result changed during {name} timing")
            s_med = statistics.median(times["sqlite"])
            d_med = statistics.median(times["duckdb"])
            outputs.append({"query": name, "runs": runs, "result_rows": len(expected),
                            "sqlite_median_ms": s_med, "sqlite_min_ms": min(times["sqlite"]),
                            "sqlite_max_ms": max(times["sqlite"]), "duckdb_median_ms": d_med,
                            "duckdb_min_ms": min(times["duckdb"]), "duckdb_max_ms": max(times["duckdb"]),
                            "sqlite_over_duckdb_speedup": s_med / d_med if d_med else None,
                            "results_equivalent": True})
    finally:
        sq.close()
        duck.close()
    machine = {"platform": platform.platform(), "processor": platform.processor(),
               "python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
               "duckdb": duckdb.__version__, "cpu_count": os.cpu_count(),
               "dataset_rows": EXPECTED_ROWS, "parquet_bytes": PARQUET_PATH.stat().st_size}
    payload = {"environment": machine, "results": outputs}
    (RESULTS / "sqlite-vs-duckdb.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with (RESULTS / "sqlite-vs-duckdb.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(outputs[0]))
        writer.writeheader()
        writer.writerows(outputs)
    for row in outputs:
        print(f"{row['query']}: SQLite median {row['sqlite_median_ms']:.2f} ms "
              f"[{row['sqlite_min_ms']:.2f}–{row['sqlite_max_ms']:.2f}], DuckDB median "
              f"{row['duckdb_median_ms']:.2f} ms [{row['duckdb_min_ms']:.2f}–{row['duckdb_max_ms']:.2f}], "
              f"speedup {row['sqlite_over_duckdb_speedup']:.2f}x; equivalent results")
    return outputs


if __name__ == "__main__":
    run()
