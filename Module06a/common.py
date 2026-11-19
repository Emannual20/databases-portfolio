"""Shared paths, queries and validation helpers for Module 6a."""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SOURCE_DB = REPO / "Module05" / "normalize.db"
HISTORY_DB = HERE / "history.db"
CSV_PATH = HERE / "report_jobpart.csv"
PARQUET_PATH = HERE / "report_history.parquet"
RESULTS = HERE / "benchmark-results"
QUARTERS = 10
DAYS_PER_QUARTER = 91
EXPECTED_ROWS = 2_000_000

DASHBOARD_SQL = """SELECT machine_id, site, technician, ROUND(SUM(part_price), 2) AS cost
FROM {source}
WHERE done_on >= '2026-01-01'
GROUP BY machine_id, site, technician
ORDER BY machine_id, site, technician"""
MONTHLY_SQL = """SELECT strftime(done_on, '%Y-%m') AS month, machine_id,
COUNT(*) AS jobs, ROUND(SUM(part_price), 2) AS cost
FROM {source}
GROUP BY month, machine_id ORDER BY month, machine_id"""


def require_source() -> int:
    """Validate Module 5 source and return its report row count."""
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Module 5 database not found: {SOURCE_DB}")
    with sqlite3.connect(SOURCE_DB) as con:
        found = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", ("report_jobpart",)).fetchone()
        if not found:
            raise RuntimeError(f"{SOURCE_DB} has no report_jobpart table")
        count = con.execute("SELECT COUNT(*) FROM report_jobpart").fetchone()[0]
        if not count:
            raise RuntimeError("Module 5 report_jobpart is empty")
        return int(count)


def write_csv_from_history() -> int:
    """Export the 200k source table; DuckDB expands it to the same history."""
    rows = 0
    with sqlite3.connect(SOURCE_DB) as con, CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(("job_id", "machine_id", "site", "technician", "part_no", "part_price", "done_on"))
        cur = con.execute("SELECT job_id,machine_id,site,technician,part_no,part_price,done_on FROM report_jobpart ORDER BY job_id,part_no")
        while batch := cur.fetchmany(25_000):
            writer.writerows(batch)
            rows += len(batch)
    return rows


def aggregates_sqlite() -> dict[str, object]:
    with sqlite3.connect(HISTORY_DB) as con:
        return {
            "rows": con.execute("SELECT COUNT(*) FROM report_history").fetchone()[0],
            "sum_price": con.execute("SELECT ROUND(SUM(part_price),2) FROM report_history").fetchone()[0],
            "min_date": con.execute("SELECT MIN(done_on) FROM report_history").fetchone()[0],
            "max_date": con.execute("SELECT MAX(done_on) FROM report_history").fetchone()[0],
            "distinct_months": con.execute("SELECT COUNT(DISTINCT substr(done_on,1,7)) FROM report_history").fetchone()[0],
        }


def aggregates_duckdb(source: str) -> dict[str, object]:
    con = duckdb.connect()
    try:
        return {
            "rows": con.execute(f"SELECT COUNT(*) FROM {source}").fetchone()[0],
            "sum_price": con.execute(f"SELECT ROUND(SUM(part_price),2) FROM {source}").fetchone()[0],
            "min_date": str(con.execute(f"SELECT MIN(done_on) FROM {source}").fetchone()[0]),
            "max_date": str(con.execute(f"SELECT MAX(done_on) FROM {source}").fetchone()[0]),
            "distinct_months": con.execute(f"SELECT COUNT(DISTINCT strftime(done_on,'%Y-%m')) FROM {source}").fetchone()[0],
        }
    finally:
        con.close()
