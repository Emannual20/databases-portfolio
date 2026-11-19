# Module 5 benchmark and validation

## Reproduction

The benchmark uses a fresh database built from `setup.sql`; `normalize.db` is the original work database and was not changed.

```powershell
.venv\Scripts\python.exe -c "import sqlite3,pathlib; p=pathlib.Path('Module05/normalize_test.db'); c=sqlite3.connect(p); c.executescript(pathlib.Path('Module05/setup.sql').read_text(encoding='utf-8-sig')); c.close()"
.venv\Scripts\python.exe Module05\benchmark.py --db Module05\normalize_test.db --runs 9
```

The script performs one unrecorded warm-up per query, then alternates query order over nine rounds. It measures complete `fetchall()` wall-clock time with `perf_counter_ns`. Exact SQL, raw samples, plans, row counts, relationship checks, index definitions, database size, and `dbstat` page totals are saved in [benchmark-results.json](benchmark-results.json).

## Dataset and integrity

| Object | Rows |
|---|---:|
| `flat_jobpart` | 200,000 |
| `machine` | 50 |
| `part` | 10 |
| `job` | 20,000 |
| `job_part` | 200,000 |
| `report_jobpart` | 200,000 |

`PRAGMA foreign_key_check` returned 0 violations; `PRAGMA integrity_check` returned `ok`. A separate insert attempt with foreign keys enabled was rejected as expected. Relationship violation counts were all zero: job-to-machine/technician/date, machine-to-site, part-to-price, and duplicate job-part pairs. The flat, normalized junction, and reporting fact counts match at 200,000. Both dashboard queries returned 350 rows and their sorted results were equivalent.

## SQLite results

SQLite 3.53.1; warm-cache interleaved runs:

| Query | Nine raw runs (ms) | Median (ms) | Min-max (ms) | Spread (ms) |
|---|---|---:|---:|---:|
| Normalized joins | 91.6580, 91.0009, 85.7559, 108.3128, 81.3511, 88.1554, 100.2769, 86.1143, 91.1176 | 91.0009 | 81.3511-108.3128 | 26.9617 |
| Reporting table | 107.2007, 109.4273, 126.1986, 96.4397, 99.0126, 100.9469, 135.1394, 112.1616, 108.4596 | 108.4596 | 96.4397-135.1394 | 38.6997 |

The normalized query was faster in this run. This is one measurement on this dataset, software version, index configuration, and machine; it is not a general claim about denormalization.

## Query plans

**Normalized**

```text
SCAN jp
SEARCH j USING INTEGER PRIMARY KEY (rowid=?)
SEARCH m USING INDEX sqlite_autoindex_machine_1 (machine_id=?)
SEARCH p USING INDEX sqlite_autoindex_part_1 (part_no=?)
USE TEMP B-TREE FOR GROUP BY
```

SQLite scans `job_part`, then searches the job primary key and machine/part primary-key indexes. It creates a temporary B-tree for grouping.

**Denormalized**

```text
SCAN report_jobpart USING INDEX ix_report_machine
USE TEMP B-TREE FOR GROUP BY
```

SQLite scans the report table through `ix_report_machine` and creates a temporary grouping B-tree. The index is used for a full scan, not a selective search for this broad aggregation. SQLite documents `EXPLAIN QUERY PLAN` as a high-level description whose displayed format can change.

## Storage

SQLite `dbstat` reports allocated page bytes. In this test DB the normalized tables use 4,071,424 bytes and their primary-key indexes use 4,096,000 bytes (8,167,424 total). The reporting table uses 11,091,968 bytes and its index uses 2,990,080 bytes (14,082,048 total). The complete test database is 37,138,432 bytes, including the flat source and its index. Per-object details for all objects appear in the JSON artifact.

The validation Python build exposes `dbstat`; read-only inspection of the original `normalize.db` confirmed the same object allocations, row counts, 4,000-to-1 update fan-out, and 37,138,432-byte file size as the test database. Its inspected connection reported `PRAGMA foreign_keys = 0`, which is why the setup explicitly enables enforcement and the validator separately verifies that an orphan insert is rejected. The stored original database remains unchanged.

## Why the earlier figures differ

The notes' 570/683 ms and `duck_compare.py` transcript's 97.7/111.8 ms are preserved as historical results, not presented as this run. The DuckDB script used five runs grouped by scenario/engine, without a warm-up or interleaving. It also uses a plain ISO date string and explicitly groups by `site`; the official SQLite benchmark uses `date('2026-03-01')` and omits `site` from `GROUP BY` (SQLite permits the selected `site` because it is determined by `machine_id`). The two forms return the same results on this data but are not identical SQL. This benchmark alternates query order for nine rounds after warm-up. Earlier raw samples, exact host/database metadata, and comparable timing order were not saved, so cache/order and version effects cannot be isolated and the results cannot be reconciled exactly. The required SQLite workload has now been measured again with reproducible raw samples. DuckDB is an optional comparison and is not used to justify the SQLite recommendation.
