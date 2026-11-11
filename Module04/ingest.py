"""Replay-safe ingestion: load a CSV of readings into edge.db with UPSERT.

Run twice on the same file -- the row count must not change the second time.

    uv run python Module04/ingest.py                 # uses readings_batch.csv
    uv run python Module04/ingest.py other_file.csv
"""
import csv
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).parent
DB = HERE / "edge.db"

UPSERT = """
INSERT INTO reading(sensor_id, ts, value, interval_s)
VALUES (?, ?, ?, ?)
ON CONFLICT(sensor_id, ts) DO UPDATE SET value = excluded.value
"""


def load_rows(csv_path: Path) -> list[tuple]:
    """Read the CSV and convert each field to the type the table expects."""
    with csv_path.open(newline="") as f:
        return [
            (int(r["sensor_id"]), r["ts"], float(r["value"]), int(r["interval_s"]))
            for r in csv.DictReader(f)
        ]


def main() -> None:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "readings_batch.csv"
    if not DB.exists():
        raise SystemExit(f"{DB} not found - run the Module 4 setup first")

    rows = load_rows(csv_path)

    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")      # per connection, off by default

    def count() -> int:
        return conn.execute("SELECT COUNT(*) FROM reading").fetchone()[0]

    before = count()
    with conn:                                    # commit on success, roll back on error
        conn.executemany(UPSERT, rows)
    after = count()
    conn.close()

    print(f"file rows: {len(rows)} | table rows before: {before} | "
          f"after: {after} | new rows: {after - before}")


if __name__ == "__main__":
    main()