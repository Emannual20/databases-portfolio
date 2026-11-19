# Module 6a — Evidence and notes

## Reproducible evidence

- Source: `Module05/normalize.db`, table `report_jobpart` (200,000 rows); no fallback data was used.
- Expansion: ten copies separated by 91 days, producing 2,000,000 rows in `history.db` and Parquet.
- Validation: row counts, date bounds, sum of `part_price`, and number of distinct months are checked before analytical timings.
- Commands and generated evidence are documented in [README](README.md) and [benchmark-results/README](benchmark-results/README.md).

## Actual results

Populate this section from generated `benchmark-results/sqlite-vs-duckdb.json`, `explain-analyze.txt`, and `boundary-results.csv` after running the pipeline. Do not transfer workbook sample timings.

- Dashboard: `[generated median, spread, speedup]`
- Monthly: `[generated median, spread, speedup]`
- Boundary: `[generated results by transactional workload]`
- Plan: `[operator and observed input/output rows from the actual DuckDB plan]`

## Discussion and personal decision

- Pod discussion / what surprised the pod: [STUDENT INPUT REQUIRED: Enter your actual pod discussion here.]
- Neighbouring-pod results: [STUDENT INPUT REQUIRED: Record actual comparison and differences here.]
- Peer defence feedback and changes: [STUDENT INPUT REQUIRED: Record actual feedback and any resulting change here.]
- What I learned, what was difficult, and what I would choose as an engineer: [STUDENT INPUT REQUIRED: Write your own reflection and defended judgment here.]
- Instructor observations, if any: [STUDENT INPUT REQUIRED: Record only observations you personally made in class.]
