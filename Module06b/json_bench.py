"""Exercise SQLite JSON functions, validity constraints and expression indexing."""
from __future__ import annotations

import json
import sqlite3

from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "polyglot.db"
RESULTS = HERE / "results"
DEVICES = [
    ("cnc-01", {"vendor": "Siemens", "firmware": "4.2", "calibrated": "2026-01-10"}),
    ("cnc-02", {"vendor": "Fanuc", "firmware": "3.9"}),
    ("molder-07", {"vendor": "Arburg", "firmware": "8.1", "calibrated": "2025-11-02", "nozzle_mm": 2.5}),
]


def run() -> dict[str, object]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    try:
        con.execute("DROP TABLE IF EXISTS device")
        con.execute("""CREATE TABLE device(
            device_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            meta TEXT NOT NULL CHECK (json_valid(meta))
        ) STRICT""")
        con.executemany("INSERT INTO device(name, meta) VALUES (?, ?)",
                        [(name, json.dumps(meta, separators=(",", ":"))) for name, meta in DEVICES])
        con.commit()
        extracts = con.execute("SELECT name, json_extract(meta, '$.vendor') AS vendor FROM device ORDER BY name").fetchall()
        firmware = con.execute("SELECT name, meta ->> '$.firmware' FROM device ORDER BY name").fetchall()
        expanded = con.execute("""SELECT d.name, j.key, j.value
            FROM device AS d, json_each(d.meta) AS j WHERE d.name=? ORDER BY j.key""", ("cnc-01",)).fetchall()
        if dict(extracts) != {name: meta["vendor"] for name, meta in DEVICES}:
            raise AssertionError("json_extract returned unexpected vendor values")
        if len(firmware) != len(DEVICES) or len(expanded) != 3:
            raise AssertionError("JSON operator/json_each output failed validation")

        con.execute("CREATE INDEX ix_device_vendor ON device(json_extract(meta, '$.vendor'))")
        indexed_sql = "SELECT name FROM device WHERE json_extract(meta, '$.vendor') = ? ORDER BY name"
        shorthand_sql = "SELECT name FROM device WHERE meta ->> '$.vendor' = ? ORDER BY name"
        indexed_rows = con.execute(indexed_sql, ("Fanuc",)).fetchall()
        shorthand_rows = con.execute(shorthand_sql, ("Fanuc",)).fetchall()
        if indexed_rows != shorthand_rows or indexed_rows != [("cnc-02",)]:
            raise AssertionError("Indexed and shorthand JSON expressions returned different values")
        indexed_plan = con.execute("EXPLAIN QUERY PLAN " + indexed_sql, ("Fanuc",)).fetchall()
        shorthand_plan = con.execute("EXPLAIN QUERY PLAN " + shorthand_sql, ("Fanuc",)).fetchall()
        index_used = any("USING INDEX ix_device_vendor" in str(row) for row in indexed_plan)
        shorthand_scans = any("SCAN device" in str(row) for row in shorthand_plan)
        if not index_used:
            raise AssertionError(f"Expected indexed JSON expression to use index: {indexed_plan}")

        invalid_rejected = False
        try:
            con.execute("INSERT INTO device(name, meta) VALUES (?, ?)", ("invalid", "{nope"))
            con.commit()
        except sqlite3.IntegrityError:
            con.rollback()
            invalid_rejected = True
        if not invalid_rejected:
            raise AssertionError("CHECK(json_valid(meta)) accepted invalid JSON")

        result = {"sqlite_version": sqlite3.sqlite_version, "strict_table": True,
                  "device_count": len(DEVICES), "json_extract": extracts, "arrow_text": firmware,
                  "json_each_cnc01": expanded, "indexed_query_rows": indexed_rows,
                  "queries_equivalent": indexed_rows == shorthand_rows,
                  "indexed_expression_uses_ix_device_vendor": index_used,
                  "shorthand_plan_scans_table": shorthand_scans,
                  "invalid_json_rejected": invalid_rejected,
                  "indexed_plan": indexed_plan, "shorthand_plan": shorthand_plan}
    finally:
        con.close()
    serializable = json.loads(json.dumps(result, default=str))
    (RESULTS / "json-experiment.json").write_text(json.dumps(serializable, indent=2), encoding="utf-8")
    (RESULTS / "json-query-plans.txt").write_text(
        "Indexed expression plan:\n" + "\n".join(map(str, indexed_plan)) +
        "\n\n->> shorthand plan:\n" + "\n".join(map(str, shorthand_plan)) + "\n", encoding="utf-8")
    print(json.dumps(serializable, indent=2))
    return serializable


if __name__ == "__main__":
    run()
