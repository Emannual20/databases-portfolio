# Workload and freshness decision

## Placement

- **SQLite:** sensor/job ingest, constraints, and updates that need transactional durability and low-latency point access. The history builder reads the original database without changing it.
- **DuckDB and Parquet:** month-end and dashboard analysis that scans a large share of historical rows and needs only selected columns. Confirm the speedup and scan operators in `benchmark-results/` before treating it as a local conclusion.
- **Parquet:** a compact, immutable analytical snapshot that can be versioned or replaced as a unit. It is not the transactional source of truth.

## Refresh and staleness

The reproducible refresh is `prepare.py` followed by `to_parquet.py`; publish the new database and Parquet file only after row counts and aggregate checks pass. For a month-end report, a nightly refresh is a practical starting point; reports can be up to one refresh interval stale. For operational dashboards that require near-real-time values, query SQLite or shorten the refresh interval after measuring its cost. The course dataset is static, so it provides no evidence about production change capture or refresh duration.

Validate row count, min/max dates, total part price, and selected workload results on every refresh. For stronger production guarantees, add a content hash or partition-level reconciliation and publish a manifest with a generation timestamp. Keep both files generated from the same source snapshot; do not refresh one independently.

## Costs accepted

The analytical copy duplicates storage and introduces refresh work, monitoring, and an explicit staleness window. In return, Parquet's columnar layout and DuckDB's vectorized aggregation can serve scan-heavy reports without competing with transactional writes. SQLite stays simpler for local transactions and single-file operation. The measured comparison in this portfolio is specific to the recorded machine and dataset size; it is not a universal engine ranking.
