"""Compare 50k session key reads/writes in shelve and SQLite, with validation."""
from __future__ import annotations

import csv
import dbm
import json
import platform
import shelve
import sqlite3
import statistics
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
N = 50_000
RUNS = 5


def value_for(i: int) -> str:
    return f"user-{i % 100}:filter=city:{i % 4}"


def tree_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def one_shelve(directory: Path) -> dict[str, float | int]:
    base = directory / "sessions"
    start = time.perf_counter()
    with shelve.open(str(base)) as db:
        for i in range(N):
            db[f"session-{i}"] = value_for(i)
    write_s = time.perf_counter() - start
    start = time.perf_counter()
    with shelve.open(str(base), flag="r") as db:
        values = [db[f"session-{i}"] for i in range(N)]
    read_s = time.perf_counter() - start
    if values != [value_for(i) for i in range(N)]:
        raise AssertionError("shelve returned incorrect session data")
    return {"write_s": write_s, "read_s": read_s, "total_s": write_s + read_s,
            "storage_bytes": tree_bytes(directory), "backend": dbm.whichdb(str(base)) or "unknown"}


def one_sqlite(directory: Path) -> dict[str, float | int]:
    dbpath = directory / "sessions.sqlite"
    con = sqlite3.connect(dbpath)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("CREATE TABLE session(k TEXT PRIMARY KEY, user_id INTEGER NOT NULL, city INTEGER NOT NULL, v TEXT NOT NULL) STRICT")
    start = time.perf_counter()
    con.executemany("INSERT INTO session(k,user_id,city,v) VALUES (?,?,?,?)",
                    ((f"session-{i}", i % 100, i % 4, value_for(i)) for i in range(N)))
    con.commit()
    write_s = time.perf_counter() - start
    start = time.perf_counter()
    values = [con.execute("SELECT v FROM session WHERE k=?", (f"session-{i}",)).fetchone()[0]
              for i in range(N)]
    read_s = time.perf_counter() - start
    if values != [value_for(i) for i in range(N)]:
        raise AssertionError("SQLite returned incorrect session data")
    cross_session = con.execute("SELECT COUNT(*) FROM session WHERE city=? AND user_id=?", (2, 6)).fetchone()[0]
    # Both conditions are represented as explicit columns and queried relationally.
    if cross_session != sum(1 for i in range(N) if i % 4 == 2 and i % 100 == 6):
        raise AssertionError("SQLite cross-session query returned the wrong count")
    con.close()
    return {"write_s": write_s, "read_s": read_s, "total_s": write_s + read_s,
            "storage_bytes": dbpath.stat().st_size, "cross_session_query_count": cross_session}


def summarize(values: list[float]) -> dict[str, float]:
    return {"median": statistics.median(values), "min": min(values), "max": max(values)}


def run(runs: int = RUNS) -> dict[str, object]:
    if runs < 3:
        raise ValueError("Use at least three independent benchmark runs")
    RESULTS.mkdir(parents=True, exist_ok=True)
    observations = {"shelve": [], "sqlite": []}
    for i in range(runs):
        for engine in (("shelve", "sqlite") if i % 2 == 0 else ("sqlite", "shelve")):
            with tempfile.TemporaryDirectory(prefix=f"kv-{engine}-", dir=RESULTS) as temp:
                directory = Path(temp)
                observations[engine].append(one_shelve(directory) if engine == "shelve" else one_sqlite(directory))
    metrics = ("write_s", "read_s", "total_s", "storage_bytes")
    summary = {}
    for engine, items in observations.items():
        summary[engine] = {metric: summarize([float(item[metric]) for item in items]) for metric in metrics}
    cross = observations["sqlite"][-1]["cross_session_query_count"]
    result = {"workload": "50,000 sessions; same deterministic key/value generation and sequential readback",
              "runs": runs, "sessions_per_run": N,
              "environment": {"platform": platform.platform(), "python": platform.python_version(),
                              "shelve_backend": observations["shelve"][0]["backend"],
                              "sqlite": sqlite3.sqlite_version},
              "measurements": summary,
              "sqlite_cross_session_query": {"description": "count sessions where city=2 and user_id=6", "count": cross},
              "values_validated_each_run": True,
              "note": "shelve's dbm backend and file layout vary by operating system; compare only measurements from the recorded platform."}
    (RESULTS / "kv-results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    with (RESULTS / "kv-results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(("engine", "metric", "median", "min", "max", "unit"))
        for engine, rows in summary.items():
            for metric, values in rows.items():
                writer.writerow((engine, metric, values["median"], values["min"], values["max"], "bytes" if metric == "storage_bytes" else "seconds"))
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
