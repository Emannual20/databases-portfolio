"""Measure transactional workloads to show where embedded OLAP is a poor fit."""
from __future__ import annotations

import csv
import json
import platform
import sqlite3
import statistics
import time

import duckdb

from common import RESULTS

ROWS = 1_000
RUNS = 7


def _sqlite_workload() -> dict[str, float]:
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE s(id INTEGER PRIMARY KEY, k TEXT NOT NULL, v REAL NOT NULL)")
    data = [(i, f"k{i}", i * 1.5) for i in range(ROWS)]
    start = time.perf_counter()
    for row in data:
        con.execute("INSERT INTO s VALUES (?, ?, ?)", row)
    con.commit()
    single = (time.perf_counter() - start) * 1000
    con.execute("DELETE FROM s")
    start = time.perf_counter()
    con.executemany("INSERT INTO s VALUES (?, ?, ?)", data)
    con.commit()
    repeated = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    values = [con.execute("SELECT v FROM s WHERE id=?", (i,)).fetchone()[0] for i in range(ROWS)]
    point = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    selected = con.execute("SELECT id,k,v FROM s WHERE id BETWEEN ? AND ? ORDER BY id", (490, 509)).fetchall()
    selective = (time.perf_counter() - start) * 1000
    assert values == [i * 1.5 for i in range(ROWS)] and len(selected) == 20
    con.close()
    return {"single_row_inserts_ms": single, "repeated_inserts_ms": repeated,
            "point_lookups_ms": point, "small_selective_query_ms": selective}


def _duck_workload() -> dict[str, float]:
    con = duckdb.connect()
    con.execute("CREATE TABLE s(id INTEGER PRIMARY KEY, k VARCHAR, v DOUBLE)")
    data = [(i, f"k{i}", i * 1.5) for i in range(ROWS)]
    start = time.perf_counter()
    for row in data:
        con.execute("INSERT INTO s VALUES (?, ?, ?)", row)
    single = (time.perf_counter() - start) * 1000
    con.execute("DELETE FROM s")
    start = time.perf_counter()
    con.executemany("INSERT INTO s VALUES (?, ?, ?)", data)
    repeated = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    values = [con.execute("SELECT v FROM s WHERE id=?", [i]).fetchone()[0] for i in range(ROWS)]
    point = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    selected = con.execute("SELECT id,k,v FROM s WHERE id BETWEEN ? AND ? ORDER BY id", [490, 509]).fetchall()
    selective = (time.perf_counter() - start) * 1000
    assert values == [i * 1.5 for i in range(ROWS)] and len(selected) == 20
    con.close()
    return {"single_row_inserts_ms": single, "repeated_inserts_ms": repeated,
            "point_lookups_ms": point, "small_selective_query_ms": selective}


def run(runs: int = RUNS) -> list[dict[str, object]]:
    if runs < 5:
        raise ValueError("Use at least five runs")
    RESULTS.mkdir(parents=True, exist_ok=True)
    samples = {engine: {key: [] for key in ("single_row_inserts_ms", "repeated_inserts_ms", "point_lookups_ms", "small_selective_query_ms")}
               for engine in ("sqlite", "duckdb")}
    for i in range(runs):
        for engine in (("sqlite", "duckdb") if i % 2 == 0 else ("duckdb", "sqlite")):
            observed = _sqlite_workload() if engine == "sqlite" else _duck_workload()
            for key, value in observed.items():
                samples[engine][key].append(value)
    records = []
    for workload in samples["sqlite"]:
        sqlite_values = samples["sqlite"][workload]
        duck_values = samples["duckdb"][workload]
        s_med, d_med = statistics.median(sqlite_values), statistics.median(duck_values)
        records.append({"workload": workload.removesuffix("_ms"), "rows": ROWS if "insert" in workload or "point" in workload else 20,
                        "runs": runs, "sqlite_median_ms": s_med, "sqlite_min_ms": min(sqlite_values),
                        "sqlite_max_ms": max(sqlite_values), "duckdb_median_ms": d_med,
                        "duckdb_min_ms": min(duck_values), "duckdb_max_ms": max(duck_values),
                        "sqlite_over_duckdb_speedup": s_med / d_med if d_med else None,
                        "results_validated": True})
    payload = {"environment": {"platform": platform.platform(), "python": platform.python_version(),
                                "sqlite": sqlite3.sqlite_version, "duckdb": duckdb.__version__,
                                "rows": ROWS, "storage": "in-memory for both engines"},
               "results": records,
               "interpretation": "The measurements cover statement-by-statement writes, batched repeated inserts, point lookups and a 20-row selective query. Results are machine- and version-specific; SQLite is designed for transactional row access, while DuckDB's setup and vectorized execution favor bulk analytical work."}
    (RESULTS / "boundary-results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with (RESULTS / "boundary-results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    for row in records:
        print(row)
    return records


if __name__ == "__main__":
    run()
