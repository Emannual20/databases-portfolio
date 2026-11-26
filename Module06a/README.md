# Module 6a — The Analytical Engine

## 🎯 Learning Goals

This module explores analytical engines and moving a workload to the right engine. By the end, I can:

### Learning Goal 1
Move a table out of SQLite into **Parquet** reproducibly, from a script.
- [Build the analytical history](./prepare.py)
- [Convert the report data to Parquet](./to_parquet.py)

### Learning Goal 2
Run the **same aggregate** in SQLite and DuckDB and report the difference honestly using interleaved runs and the median.
- [SQLite and DuckDB benchmark](./race.py)
- [Benchmark notes and evidence](./duckdb-notes.md)

### Learning Goal 3
Read **`EXPLAIN ANALYZE`** and identify the operator and row count that dominate.
- [Capture and summarize DuckDB plans](./explain.py)
- [Plan notes](./duckdb-notes.md)

### Learning Goal 4
State, with a number, **where DuckDB is the wrong engine**.
- [Transactional boundary benchmark](./boundary.py)
- [Workload decision](./decision.md)

### Learning Goal 5
Recommend **what moves to the analytical copy** and how that copy stays fresh.
- [Workload decision](./decision.md)
- [Analytical engine notes](./duckdb-notes.md)

## Reflection 6a
[Reflection 6a](../Reflections/ref06a.md)

<br>

## Task Inspirations (Notes & Evidence)

### **1. Build and convert the analytical copy**
The scripts build a two-million-row history from the Module 5 data, export the base CSV, and convert it to Parquet. The conversion script checks the resulting data against SQLite before any timing comparison.

**Task evidence:** [prepare.py](./prepare.py) · [to_parquet.py](./to_parquet.py)

### **2. Compare equivalent analytical queries**
The race script warms both engines, interleaves equivalent queries, and reports medians and run ranges. Record the results and what they show in the notes.

**Task evidence:** [race.py](./race.py) · [duckdb-notes.md](./duckdb-notes.md)

### **3. Explain the query plan**
Capture DuckDB's actual plan and use its operators and row counts to explain the measured difference.

**Task evidence:** [explain.py](./explain.py) · [duckdb-notes.md](./duckdb-notes.md)

### **4. Find the transactional boundary**
Compare inserts, point lookups, and selective reads to identify where the analytical engine is not the right fit.

**Task evidence:** [boundary.py](./boundary.py) · [decision.md](./decision.md)

### **5. Make and defend the placement decision**
Recommend which workload belongs in the analytical copy and how it should be refreshed. Pod discussion, peer defence, and personal judgment are evidence to add to the notes yourself.

**Task evidence:** [decision.md](./decision.md) · [duckdb-notes.md](./duckdb-notes.md) · [Reflection 6a](../Reflections/ref06a.md)

<br>

This module builds a reproducible two-million-row analytical copy from the real `Module05/normalize.db` dataset, exports a base CSV, converts it to Parquet with DuckDB, compares equivalent queries across SQLite and DuckDB, captures DuckDB plans, and benchmarks transactional boundaries.

## Files

- `prepare.py` builds `history.db` with ten 91-day copies and exports the 200,000-row source as `report_jobpart.csv`.
- `to_parquet.py` expands that CSV with DuckDB into `report_history.parquet` and validates row counts and aggregates against SQLite.
- `race.py` runs two interleaved, warmed analytical workloads and writes machine-specific CSV/JSON results.
- `explain.py` saves actual `EXPLAIN ANALYZE` plans and a summary alongside benchmark evidence.
- `boundary.py` compares single inserts, batched inserts, point lookups, and small selective reads.
- `decision.md` records workload placement and refresh trade-offs; `duckdb-notes.md` is the evidence and discussion notebook.
- `benchmark-results/` contains generated, machine-specific evidence. The files are created by the scripts and ignored by Git.

## Requirements and commands

Python 3.14 and DuckDB are used. SQLite comes from Python's standard library. DuckDB is already available in this repository's `.venv`; this repository currently has `uv.lock` but no `pyproject.toml`, so use the active virtual environment or invoke `uv run --with duckdb` if needed.

From the repository root, run in order:

```powershell
uv run --with duckdb python Module06a/prepare.py
uv run --with duckdb python Module06a/to_parquet.py
uv run --with duckdb python Module06a/race.py
uv run --with duckdb python Module06a/explain.py
uv run --with duckdb python Module06a/boundary.py
```

The scripts resolve all paths relative to their own files. Re-running rebuilds derived outputs; the original `Module05/normalize.db` is read-only input and is never modified. No DuckDB extensions or network access are needed.

## Outputs and interpretation

`history.db` and `report_history.parquet` each contain 2,000,000 rows. `report_jobpart.csv` contains the original 200,000-row base dataset; DuckDB applies the same ten-copy expansion. `to_parquet.py` checks count, price sum, date bounds, and distinct month count before benchmarks. Benchmark scripts validate result sets before recording times. The median is the primary comparison; min/max show run spread. Ratios are specific to this machine, versions, cache state, and query shape.

The boundary results are expected to favor SQLite for small transactional requests, but the measurements determine the conclusion. In-memory tests measure engine/API work and do not model durable disk writes or multi-process concurrency.

## Input still required

Pod discussion, peer defence, the student's personal judgment, and any instructor or neighbouring-pod observations remain for the student. Use explicit placeholders in `duckdb-notes.md`; no personal reflection file is generated by these scripts.
