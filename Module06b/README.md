# Module 6b — Polyglot Persistence & the Decision

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
