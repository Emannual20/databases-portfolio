"""Build a deterministic 2,000,000-row history from the original Module 5 data."""
from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path

from common import CSV_PATH, DAYS_PER_QUARTER, EXPECTED_ROWS, HISTORY_DB, QUARTERS, SOURCE_DB, HERE, require_source, write_csv_from_history


def build_history() -> dict[str, object]:
    """Build derived history safely; never modify the Module 5 source database."""
    source_rows = require_source()
    if source_rows * QUARTERS != EXPECTED_ROWS:
        raise RuntimeError(f"Expected {EXPECTED_ROWS:,} rows from ten copies, got {source_rows * QUARTERS:,}")
    fd, tmp_name = tempfile.mkstemp(prefix="history-", suffix=".db", dir=HERE)
    os.close(fd)
    tmp_db = Path(tmp_name)
    try:
        with sqlite3.connect(tmp_db) as con:
            con.execute("PRAGMA journal_mode=DELETE")
            con.execute("ATTACH DATABASE ? AS m5", (str(SOURCE_DB),))
            con.execute("""CREATE TABLE report_history(
                job_id INTEGER NOT NULL, machine_id TEXT NOT NULL, site TEXT NOT NULL,
                technician TEXT NOT NULL, part_no TEXT NOT NULL, part_price REAL NOT NULL,
                done_on TEXT NOT NULL)""")
            con.execute("""WITH RECURSIVE quarter(k) AS (
                SELECT 0 UNION ALL SELECT k+1 FROM quarter WHERE k < ?)
                INSERT INTO report_history
                SELECT r.job_id + quarter.k * 1000000, r.machine_id, r.site,
                       r.technician, r.part_no, r.part_price,
                       date(r.done_on, '+' || (quarter.k * ?) || ' days')
                FROM m5.report_jobpart AS r CROSS JOIN quarter""", (QUARTERS - 1, DAYS_PER_QUARTER))
            con.execute("CREATE INDEX ix_history_done_on ON report_history(done_on)")
            con.execute("CREATE INDEX ix_history_machine ON report_history(machine_id)")
            con.commit()
            count, min_date, max_date, total = con.execute(
                "SELECT COUNT(*), MIN(done_on), MAX(done_on), ROUND(SUM(part_price),2) FROM report_history"
            ).fetchone()
            if count != EXPECTED_ROWS or not min_date or not max_date or total is None:
                raise RuntimeError(f"History validation failed: rows={count}, dates={min_date}..{max_date}, sum={total}")
            if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("SQLite integrity_check failed for generated history")
        con.close()
        os.replace(tmp_db, HISTORY_DB)
    finally:
        tmp_db.unlink(missing_ok=True)

    csv_rows = write_csv_from_history()
    if csv_rows != source_rows:
        raise RuntimeError(f"Base CSV validation failed: wrote {csv_rows:,} rows, expected {source_rows:,}")
    stats = {"source_rows": source_rows, "history_rows": count, "csv_rows": csv_rows,
             "min_date": min_date, "max_date": max_date, "sum_price": total,
             "history_db_bytes": HISTORY_DB.stat().st_size, "csv_bytes": CSV_PATH.stat().st_size}
    print("Historical dataset built from Module05/normalize.db/report_jobpart")
    for key, value in stats.items():
        print(f"{key}: {value:,}" if isinstance(value, int) else f"{key}: {value}")
    return stats


if __name__ == "__main__":
    build_history()
