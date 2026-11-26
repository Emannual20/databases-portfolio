# Kortmann engine decision record

Evidence references are generated experiment files; run the module scripts before treating the result rows as measured. Network-user and instructor-dependent entries remain placeholders.

| Workload | Engine | Why | Evidence | Cost accepted | If the copy is stale |
|---|---|---|---|---|---|
| Sensor/job ingest, every 30 s, crash must not lose rows | SQLite (provisional) | Local transactional writes, constraints, and durable commits fit an operational source of truth. | Module 5 schema and SQLite behavior; no crash-injection test was run here. | Single-file write coordination and operational backup responsibility. | Not applicable to the primary store; do not serve ingest from a stale analytical copy. |
| Month-end report over two years | DuckDB reading Parquet | Full-history aggregation is a scan workload; 6a compares the same 2M rows and query results. | `Module06a/benchmark-results/sqlite-vs-duckdb.json` and `explain-analyze.txt` (populate by running). | Duplicate storage, refresh pipeline, and eventual staleness. | State snapshot timestamp; rerun or query the transactional source if the report needs fresher data. |
| Vendor metadata that gains fields | SQLite JSON column with validation and path index | Flexible optional metadata while retaining transactions and SQL; index known hot paths. | `results/json-experiment.json` and `json-query-plans.txt`; invalid JSON rejection is exercised. | JSON fields lack normal column typing and require deliberate path/index management. | Metadata remains in the source database; no separate stale copy. |
| Dashboard session state | SQLite pending measured outcome | SQL makes cross-session queries possible; compare timings and footprints with `shelve` before deciding if simpler key/value access is sufficient. | `results/kv-results.json`; actual backend and machine are recorded. | More schema/query machinery than direct key lookup, if only key access is needed. | Session state should not rely on an analytical copy; define expiry/replication separately if required. |
| Concurrent network users | [STUDENT INPUT REQUIRED: choose after actual instructor server exercise] | Client/server access can coordinate independent clients, with network and server operations costs. | [STUDENT INPUT REQUIRED: PostgreSQL observation from `server_comparison.md`] | [STUDENT INPUT REQUIRED] | [STUDENT INPUT REQUIRED] |

## If Kortmann could run only one engine, which would it be — and what would break first?

**Provisional engineering recommendation:** choose SQLite as the single operational engine because ingest must be transactional and the workload includes mutable records. The month-end scan would likely become slower and compete with operations as history grows; validate the actual 6a numbers and production scale before making that trade-off. If the report dominates and ingest is low-volume, DuckDB plus external transactional handling may be viable, but the course evidence does not test a single-engine production deployment.

## Defence and personal decision

