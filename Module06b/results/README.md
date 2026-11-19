# Module 6b generated evidence

Run `json_bench.py` and `kv_compare.py` from the repository root. They create:

- `json-experiment.json`: actual JSON query values, plan rows, index check, and invalid-input result.
- `json-query-plans.txt`: actual SQLite `EXPLAIN QUERY PLAN` output for indexed and shorthand expressions.
- `kv-results.csv` and `kv-results.json`: machine-specific `shelve`/SQLite measurements, spread, storage footprint, environment, and integrity check.

The generator scripts overwrite only these derived outputs. Database and timing results are ignored by Git; no results are hardcoded.
