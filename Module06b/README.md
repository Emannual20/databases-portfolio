# Module 6b — Polyglot Persistence & the Decision

## 🎯 Learning Goals

This module explores flexible schemas, key-value access patterns, and choosing an engine for each workload. By the end, I can:

### Learning Goal 1
Store **semi-structured JSON** in SQLite and query it with `json_extract`/`json_each` and an **expression index**.
- [JSON experiment and index plans](./json_bench.py)
- [JSON experiment results](./json-experiment-results.md)

### Learning Goal 2
Implement and evaluate a **key-value access pattern** against SQLite.
- [Key-value comparison](./kv_compare.py)
- [Key-value experiment results](./kv-experiment-results.md)

### Learning Goal 3
Explain **ACID vs. BASE** and the **CAP theorem** in terms of the systems actually tested.
- [Theory notes](./theory.md)
- [Engine notes](./engine-notes.md)

### Learning Goal 4
Choose an engine per workload and **defend the choice with a measurement**.
- [Decision record](./decision-record.md)
- [JSON and key-value evidence](./json-experiment-results.md) · [Key-value results](./kv-experiment-results.md)

### Learning Goal 5
Describe what changes and what gets harder when the same data lives on a **server**.
- [PostgreSQL server comparison](./server_comparison.md)
- [Engine notes](./engine-notes.md)

## Reflection 6b
[Reflection 6b](../Reflections/ref06b.md)

<br>

## Task Inspirations (Notes & Evidence)

### **1. Store and query flexible JSON metadata**
Use SQLite JSON functions to inspect metadata, enforce valid JSON, and compare query plans with and without the matching expression index.

**Task evidence:** [json_bench.py](./json_bench.py) · [JSON experiment results](./json-experiment-results.md)

### **2. Compare key-value access with SQLite**
Run the same session workload through `shelve` and SQLite, record the timings and storage, then explain which option fits the workload.

**Task evidence:** [kv_compare.py](./kv_compare.py) · [Key-value experiment results](./kv-experiment-results.md)

### **3. Connect database theory to observed systems**
Use the systems from the course to explain ACID, BASE, and CAP, and record the real server observations.

**Task evidence:** [theory.md](./theory.md) · [server_comparison.md](./server_comparison.md) · [engine-notes.md](./engine-notes.md)

### **4. Choose an engine for each workload**
Complete the decision record with measurements or observations, then defend the choices and note any changes after discussion.

**Task evidence:** [decision-record.md](./decision-record.md) · [experiment notes](./engine-notes.md) · [Reflection 6b](../Reflections/ref06b.md)

<br>

This module implements SQLite JSON metadata constraints and indexing, benchmarks a 50,000-session `shelve` workload against SQLite, and records the evidence-backed engine decisions. PostgreSQL measurements and student/group experiences remain explicit placeholders until observed.

## Files

- `json_bench.py` creates `polyglot.db`, demonstrates JSON functions, checks invalid JSON rejection, compares expression-index plans, and saves plans/results.
- `kv_compare.py` compares repeated writes and reads for `shelve` and SQLite with reproducible 50,000-session input and result validation.
- `server_comparison.md` is the manual PostgreSQL procedure and observation template.
- `theory.md` explains ACID, BASE, CAP, and embedded/client-server trade-offs.
- `decision-record.md` is the course decision table, with evidence and student-input gaps marked.
- `engine-notes.md`, `json-experiment-results.md`, and `kv-experiment-results.md` explain the experiments and reserve room for personal/group input.
- `results/` contains generated plans and measurements; these files are ignored by Git.

## Requirements and commands

Python 3.14 is used; SQLite and `shelve` are standard library modules. Run from the repository root:

```powershell
uv run --with duckdb python Module06b/json_bench.py
uv run --with duckdb python Module06b/kv_compare.py
```

`duckdb` is only present in the first command to use the same available environment; Module 6b itself does not depend on it. No PostgreSQL credentials or server are configured by these scripts. The manual PostgreSQL exercise is in `server_comparison.md`.

## Outputs and interpretation

JSON validation and both query plans are written to `results/json-experiment.json` and `results/json-query-plans.txt`. The key/value benchmark writes `results/kv-results.csv` and `.json`, including median/min/max for write, read, total time, and observed storage size. Runs validate every value read back. `shelve` selects a platform-dependent DBM backend, so compare only results recorded with the same operating system and Python build.

## Input still required

The actual PostgreSQL server observations, pod/neighbouring-pod discussion, peer defence, personal choice, and personal reflections must be supplied by the student. This module does not create or edit `Reflections/ref06a.md` or `Reflections/ref06b.md`.
