"""Expand the exported Module 5 CSV to Parquet with DuckDB and verify parity."""
from __future__ import annotations

import json
import platform
import sqlite3
import time

import duckdb

from common import (CSV_PATH, DAYS_PER_QUARTER, EXPECTED_ROWS, HISTORY_DB,
                    PARQUET_PATH, QUARTERS, RESULTS, aggregates_duckdb,
                    aggregates_sqlite)


def convert() -> dict[str, object]:
    if not CSV_PATH.exists() or not HISTORY_DB.exists():
        raise FileNotFoundError("Run prepare.py first to create report_jobpart.csv and history.db")
    RESULTS.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    con = duckdb.connect()
    try:
        base = con.read_csv(str(CSV_PATH), header=True, auto_detect=True)
        expanded = base.query("base", f"""SELECT job_id + q.k * 1000000 AS job_id,
            machine_id, site, technician, part_no, part_price,
            CAST(done_on AS DATE) + q.k * {DAYS_PER_QUARTER} AS done_on
            FROM base CROSS JOIN range(0, {QUARTERS}) AS q(k)""")
        expanded.write_parquet(str(PARQUET_PATH), compression="zstd")
        count = con.execute("SELECT COUNT(*) FROM read_parquet(?)", [str(PARQUET_PATH)]).fetchone()[0]
        if count != EXPECTED_ROWS:
            raise RuntimeError(f"Parquet row count is {count:,}; expected {EXPECTED_ROWS:,}")
    finally:
        con.close()
    sqlite_stats = aggregates_sqlite()
    parquet_stats = aggregates_duckdb(f"read_parquet('{PARQUET_PATH.as_posix()}')")
    if sqlite_stats != parquet_stats:
        raise RuntimeError(f"SQLite and Parquet analytical data differ: {sqlite_stats} != {parquet_stats}")
    result = {"sqlite": sqlite_stats, "duckdb_parquet": parquet_stats,
              "parquet_bytes": PARQUET_PATH.stat().st_size,
              "csv_bytes": CSV_PATH.stat().st_size,
              "history_db_bytes": HISTORY_DB.stat().st_size,
              "parquet_to_csv_ratio": round(PARQUET_PATH.stat().st_size / CSV_PATH.stat().st_size, 4),
              "parquet_to_history_db_ratio": round(PARQUET_PATH.stat().st_size / HISTORY_DB.stat().st_size, 4),
              "conversion_seconds": round(time.perf_counter() - t0, 3),
              "python": platform.python_version(), "duckdb": duckdb.__version__}
    (RESULTS / "conversion-validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    convert()
