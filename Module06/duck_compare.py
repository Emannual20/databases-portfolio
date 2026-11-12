"""Run the dashboard query in SQLite and DuckDB, on normalized and denormalized data.

Queries A and B are Round 4's dashboard queries, made portable: DuckDB needs `site` in
GROUP BY (SQLite lets it slide) and a plain '2026-03-01' string instead of date(...).
Both changes leave the result unchanged (site is determined by machine_id).

Run from the repo root:
    uv run --with duckdb python module05/duck_compare.py
"""
import csv
import sqlite3
import statistics
import tempfile
import time
from pathlib import Path

import duckdb

SQLITE_DB = Path(__file__).with_name("normalize.db")
RUNS = 5   # each timing is repeated this many times; the median is reported

SCENARIOS = [
    {
        "label": "normalized (joins)",
        "tables": ["machine", "job", "part", "job_part"],
        "query": """
            SELECT m.machine_id, m.site, j.technician, SUM(p.part_price) AS cost
            FROM job j
            JOIN machine m   ON m.machine_id = j.machine_id
            JOIN job_part jp ON jp.job_id = j.job_id
            JOIN part p      ON p.part_no = jp.part_no
            WHERE j.done_on >= '2026-03-01'
            GROUP BY m.machine_id, m.site, j.technician
        """,
    },
    {
        "label": "denormalized (report table)",
        "tables": ["report_jobpart"],
        "query": """
            SELECT machine_id, site, technician, SUM(part_price) AS cost
            FROM report_jobpart
            WHERE done_on >= '2026-03-01'
            GROUP BY machine_id, site, technician
        """,
    },
]


def time_runs(run_once):
    """Return (median seconds over RUNS, number of rows returned)."""
    times, rows = [], None
    for _ in range(RUNS):
        t0 = time.perf_counter()
        rows = run_once()
        times.append(time.perf_counter() - t0)
    return statistics.median(times), len(rows)


def copy_tables(lite, duck, names):
    """Copy SQLite tables into DuckDB through temporary CSV files."""
    with tempfile.TemporaryDirectory() as tmp:
        for name in names:
            path = Path(tmp) / f"{name}.csv"
            cur = lite.execute(f'SELECT * FROM "{name}"')
            with path.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow([d[0] for d in cur.description])
                w.writerows(cur)
            duck.execute(
                f'CREATE TABLE "{name}" AS SELECT * FROM read_csv_auto(\'{path.as_posix()}\')'
            )
            n = duck.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            print(f"copied {name}: {n} rows")


def main() -> None:
    if not SQLITE_DB.exists():
        raise SystemExit(f"{SQLITE_DB} not found")

    lite = sqlite3.connect(SQLITE_DB)
    duck = duckdb.connect()                       # in-memory

    needed = sorted({t for s in SCENARIOS for t in s["tables"]})
    copy_tables(lite, duck, needed)

    results = []
    for s in SCENARIOS:
        q = s["query"]
        s_med, s_rows = time_runs(lambda: lite.execute(q).fetchall())
        d_med, d_rows = time_runs(lambda: duck.execute(q).fetchall())
        flag = "" if s_rows == d_rows else "   <-- ROW COUNTS DIFFER, check the query!"
        results.append((s["label"], s_med * 1000, d_med * 1000, s_rows, d_rows, flag))

    print(f"\nmedian of {RUNS} runs, milliseconds (the copy into DuckDB is not timed)")
    print(f"{'scenario':32s} {'SQLite':>10s} {'DuckDB':>10s}   rows (SQLite / DuckDB)")
    for label, s_ms, d_ms, s_rows, d_rows, flag in results:
        print(f"{label:32s} {s_ms:10.1f} {d_ms:10.1f}   {s_rows} / {d_rows}{flag}")


if __name__ == "__main__":
    main()