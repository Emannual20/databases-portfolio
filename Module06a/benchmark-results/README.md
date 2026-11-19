# Module 6a generated evidence

Run the scripts from the repository root to create these machine-specific files:

- `sqlite-vs-duckdb.csv` and `.json`: seven interleaved runs by default, medians, min/max, speedup, result equivalence, and environment details.
- `explain-analyze.txt`: actual DuckDB plans for dashboard and monthly aggregations.
- `explain-summary.json`: plan operator/cardinality extraction and comparison to the benchmark when it has been run.
- `boundary-results.csv` and `.json`: transactional workload timing ranges and validation.
- `conversion-validation.json`: source/output aggregate parity and measured file sizes.

The CSV and JSON files are generated from local execution and are not checked in. Do not copy example timing numbers from the course workbook into this directory.
