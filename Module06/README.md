# Module 6: Choosing Engines for Analytical and Flexible Data

## ðŸŽ¯ Learning Goals
This module compares SQLite, DuckDB, Parquet, JSON columns, and key/value storage to decide which data and workloads belong in each engine. Module 6a covers analytical copies; Module 6b covers flexible metadata, key/value access, and the broader engine decision.

## Reflection 6
[Reflection 6](../Reflections/ref06.md)

### Learning Goal 1:
Move a table from SQLite into Parquet reproducibly and validate the analytical copy.
- [Module 6a README](../Module06a/README.md) - Documents the pipeline and generated outputs.
- [prepare.py](../Module06a/prepare.py) - Builds the history dataset and exports the source CSV.
- [to_parquet.py](../Module06a/to_parquet.py) - Creates Parquet and checks counts and aggregates against SQLite.

### Learning Goal 2:
Compare equivalent aggregate queries in SQLite and DuckDB using interleaved runs and medians.
- [Module 6a README](../Module06a/README.md) - Gives the reproducible command sequence and interpretation limits.
- [race.py](../Module06a/race.py) - Runs warmed, interleaved analytical workloads and writes results.
- [Benchmark results folder](../Module06a/benchmark-results/README.md) - Describes machine-specific evidence outputs.

### Learning Goal 3:
Read DuckDB EXPLAIN ANALYZE and identify the operators and row counts that dominate a query.
- [explain.py](../Module06a/explain.py) - Captures actual plans and a summary for review.
- [Module 6a evidence notes](../Module06a/duckdb-notes.md) - Defines the result fields to summarize after running the pipeline.

### Learning Goal 4:
Identify where DuckDB is the wrong engine by measuring small transactional operations.
- [boundary.py](../Module06a/boundary.py) - Compares single inserts, batched inserts, point lookups, and selective reads.
- [Module 6a README](../Module06a/README.md) - Explains what the boundary measurements can and cannot show.

### Learning Goal 5:
Choose what belongs in an analytical copy and specify how that copy stays fresh.
- [Workload and freshness decision](../Module06a/decision.md) - Describes workload placement, validation, refresh, and staleness costs.
- [Module 6a README](../Module06a/README.md) - Documents the SQLite source, DuckDB/Parquet copy, and refresh pipeline.

### Learning Goal 6:
Enforce a JSON data contract in SQLite and verify how expression indexes affect query plans.
- [JSON experiment](../Module06b/json-experiment-results.md) - Documents JSON validity checks, extraction, and expression-index plan comparisons.
- [json_bench.py](../Module06b/json_bench.py) - Runs the checks and records results under `results/`.

### Learning Goal 7:
Compare key/value storage with SQLite for direct lookups and relational queries, then use evidence in an engine decision.
- [Key/value experiment](../Module06b/kv-experiment-results.md) - Describes the deterministic workload, result validation, timings, storage, and DBM backend.
- [kv_compare.py](../Module06b/kv_compare.py) - Runs the `shelve` versus SQLite comparison.
- [Decision record](../Module06b/decision-record.md) - Connects workloads to evidence while marking student decisions and server observations still needed.

### Learning Goal 8:
Explain ACID, BASE, and CAP in relation to embedded and client/server engines.
- [Theory notes](../Module06b/theory.md) - Defines the concepts and discusses what the local experiments do and do not establish.
- [Server comparison](../Module06b/server_comparison.md) - Manual PostgreSQL exercise and observation template.

## Task Inspirations (Notes & Evidence)

## **1. Build and validate an analytical copy**
In Module 6a, the pipeline starts from the normalized SQLite database, expands the reporting data, and writes a Parquet copy. The scripts check row counts and selected aggregates before timing queries, keeping the analytical snapshot tied to the same source data.

**Task Evidence:**
> **Module 6a:** [Pipeline guide](../Module06a/README.md)
> - [Source preparation](../Module06a/prepare.py)
> - [Parquet export and validation](../Module06a/to_parquet.py)

## **2. Compare analytical queries and inspect plans**
The benchmark scripts are designed to run equivalent SQLite and DuckDB workloads with warm-up and interleaved measurement. The EXPLAIN ANALYZE script captures the actual DuckDB plans. The notes correctly leave the measurements and dominant operators to be filled from generated output after the pipeline runs.

**Task Evidence:**
> - [Interleaved benchmark](../Module06a/race.py)
> - [Plan capture](../Module06a/explain.py)
> - [Result and discussion notes](../Module06a/duckdb-notes.md)

## **3. Measure transactional boundaries and plan refreshes**
The boundary experiment compares small write and lookup operations with large analytical scans. The decision notes recommend SQLite for local transactional work and DuckDB/Parquet for scan-heavy reports, with the analytical copy published only after validation. The refresh interval sets how stale reports can become.

**Task Evidence:**
> - [Boundary measurements](../Module06a/boundary.py)
> - [Workload placement and freshness](../Module06a/decision.md)

## **4. Test JSON and key/value workloads**
Module 6b checks malformed JSON rejection and compares query plans for an indexed JSON extraction expression. It also benchmarks `shelve` and SQLite on the same key/value workload, validates reads, records the DBM backend, and demonstrates SQLite's additional cross-row query ability. These experiments support workload-specific decisions rather than a general engine ranking.

**Task Evidence:**
> - [JSON experiment](../Module06b/json-experiment-results.md)
> - [Key/value experiment](../Module06b/kv-experiment-results.md)
> - [Module 6b scripts](../Module06b/README.md)

## **5. Explain engine trade-offs and record a decision**
The theory notes connect transaction guarantees and distributed-system trade-offs to the embedded and server engines. The decision record distinguishes measured local evidence from items that still need the actual PostgreSQL exercise, pod discussion, peer defense, and personal judgment; those observations remain for me to complete.

**Task Evidence:**
> - [ACID, BASE, CAP, and engine placement](../Module06b/theory.md)
> - [PostgreSQL server exercise](../Module06b/server_comparison.md)
> - [Engine decision record](../Module06b/decision-record.md)

