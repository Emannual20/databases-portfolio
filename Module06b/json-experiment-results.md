# JSON experiment

Run `python Module06b/json_bench.py` (or the command in [README](README.md)). The script recreates its derived `polyglot.db`, inserts the three course devices, and produces the actual JSON extraction/operator examples, `json_each` rows, expression-index plans, equivalence check, and invalid-JSON rejection evidence under `results/`.

The intended result is that the query written with the exact indexed `json_extract(meta, '$.vendor')` expression can use `ix_device_vendor`. The `->>` spelling is a different expression to the planner unless SQLite can prove equivalence; inspect the captured plans rather than assuming. The test fails if the indexed expression does not use the index or if the query results differ.

Current execution results: `[generated in results/json-experiment.json; summarize after running]`

Personal/pod explanation: [STUDENT INPUT REQUIRED: Explain in your own words why expression spelling affects index use and what your pod noticed.]
