# Module 05: Normalization vs Denormalization Notes
[Official Module 5 specification](../Course_Materials/05-normalization-vs-denormalization.md)
## Round 1: Functionl Dependencies
**Functional Dependencies:** If you know X, then Y is 100% fixed and predictable. Two rows with the exact same X can never have different Y values.

>**Example:**<br>
>Rule: A physcial machine lives at only one factory location. <br>
>Meaning: If you see machine cnc-01, it is definetly in Gütersloh, it cannot be in two cities at once.

Candidate Key: Minimal set of attributes to determine the full details.

>**Example:**<br>
> job_id is not enough information as one job can have multiple parts. Instead we pair (job_id, part_no) a unique combination.

**Group Member Discussion:**
> Isa explained normalization, denormalization, and indexing. (Classroom discussion; no separate evidence file was present in this repository.)

# Table of Assumptions & Observations
| Functional dependency | Assumptions | Reason |
|---|---|---|
| `job_id -> machine_id` | Domain Guaranteed | A speicfic maintenance job occurs to one machine. |
| `job_id → technician` | Domain Guaranteed | A single job is assigned to one technician. |
| `machine_id → site` | Domain Guaranteed | Each machine can only exist at one site at a time. |
| `part_no → part_price` | Domain Guaranteed | A catalog part has a fixed unit price. |
| `job_id → site` | Merely observed | All `job_id`s happen to occur at site `Gütersloh`, but `Gütersloh` may not be the only working site.|
| `technician → machine_id` | Merely observed | Obsereved tech-0 only worked exlusively on cc-01 and tech-1 on cnc-02, but the 5 rows may not be sufficient to deem this as a fact. |

**Bonus Functional dependency Observed by Isa:** [Isa Normalization Notes](https://github.com/isa-babayev-ibabayev/databases-portfolio/blob/main/Module05/normalization-notes.md)

| `job_id → done_on` | Domain assumption in the full schema | A job has one completion date. |

(job_id, part_no) is a candidate key. Individually, the information on job_id is insufficient in identifying the full information of the row. Together the two attributes determine the job attributes, the machine site, and the part price.

Original design ER sketch: [table.drawio](table.drawio).

Proposed normalized ER sketch: [proposed_schema.drawio](proposed_schema.drawio).

Gate Question: "Which arrow disappears in the second diagram?"

- The transitive arrow job_id -> site disappears from the job level. site is now determined exclusively by machine_id in the machine table.

- The partical dependency arrow (job_id, part_no) -> part_price disappears from the junction table. part_price is now determined exclusively by part_no in the part table.

**Gemini Response:**
# Functional Dependencies
- `job_id -> machine_id` (Domain Fact)
- `job_id -> technician` (Domain Fact)
- `machine_id -> site` (Domain Fact)
- `part_no -> part_price` (Domain Fact)
- `technician -> machine_id` (Merely Observed in 5-row sample)
- Candidate Key: `(job_id, part_no)`
'''
technician observed as mere observation

### Disappearing Arrows in 3NF
- Transitive arrow `job_id -> site` removed (moved to `machine` table via `machine_id -> site`).
- Partial arrow `part_no -> part_price` removed (moved to `part` table via `part_no -> part_price`).

### Task 2: Break it 

1. Update Anomaly<br>
- SQLite updates 3 rows just to move 'cnc-01' to another city
- If two technicians edit the database at the same time, 'cnc-01' will exist in two different cities. This is known a a concurrency failure.

2. Insert Anomaly
The executable five-row example and statements are included below.

Since job_id, machine_id, site and technician did not have 'NOT NULL' constraints, they are all forced to be NULL and added into the table.

The flat table has nullable columns, so a part can be inserted with NULL job fields; see the SQL below.


'''sql
sqlite> DELETE FROM flat5 WHERE job_id = 2;
'''
The SQL and lost part fact are described below.

- **SQL for Asset Loss:** `DELETE FROM flat5 WHERE job_id = 2;`
  - **Flaw:** Deleting Job 2 silently erases all existence records for machine `cnc-02` and technician `tech-1` from the system.
- **SQL for Part Loss:** `DELETE FROM flat5 WHERE job_id = 1;`
  - **Flaw:** Deleting Job 1 silently erases part `P-0002` from the catalog because it was the only job referencing it.

### Task 3: Built it

Verified row counts and integrity results are recorded in [benchmark.md](benchmark.md).

Gate Question: Show your row counts to a neighbor and ask: "Why does part have 10 rows, not 40?"

Answer: In the CTE generator p(k) AS (SELECT 1 UNION ALL SELECT k+1 FROM p WHERE k < 10), k only loops from 1 to 10. Even though printf('%04d', (k % 40) + 1) uses % 40, k never exceeds 10. Thus, only 10 unique part IDs (P-0002 through P-0011) are ever generated across all 200,000 rows.

## Round 4: Race It — Performance Benchmark Results

Normalized Query: Like reading 4 small books to answer a question. Takes less room on the bookshelf but wastes tume flipping between books to match IDs

Denormalized Query: One huge master book wiht every detail repeated on every page. Takes up more space but only opens one book.

Warm Cache: Always run untimed test queiries before measuring speed, as comparing Cold vs warm metrics distorts the benchmark.

Query A (4-way normalized join) ran in 0.570s, beating Query B (denormalized single table) at 0.683s.

| Design Schema | Execution Time (ms) | Table Scanned | Execution Plan Mechanism |
| :--- | :--- | :--- | :--- |
| **Normalized (3NF Join)** | ~570 ms | `job_part` + 3 joins | Join on 50 machines / 10 parts in cache |
| **Denormalized (`report_jobpart`)** | ~683 ms | `report_jobpart` | Wide table scan + index fetch overhead |

### Key Takeaway
Denormalization does not automatically make reads faster. On in-memory datasets where join tables are narrow (storing small integers) and the denormalized table is wide (repeating large text strings), the normalized join incurs a smaller memory footprint and lower scan cost.


### Task 5: 


| Design | Dashboard query (ms) | Rows changed by one site update | Storage (KB) | Redundancy? |
|---|---|---|---|---|
| Normalized (3NF) | | | | none |
| Denormalized (report) | | | | site/technician/price repeated |

## Round 5: Price It — Storage & Write Amplification Results

| Design Schema | Dashboard Query (ms) | Rows Touched by 1 Site Update | Storage Size (KB) | Redundancy Present? |
| :--- | :--- | :--- | :--- | :--- |
| **Normalized (3NF)** | ~570 ms | **1 row** | ~3,500 KB (compact) | None |
| **Denormalized (`report_jobpart`)** | ~683 ms | **4,000 rows** | ~9,800 KB (bloated) | Repeated `site`, `technician`, `price` strings |

### Key Takeaways
1. **Write Amplification:** Updating a single machine location requires **4,000 row modifications** in the denormalized table versus **1 row modification** in 3NF.
2. **Storage Tax:** The denormalized table consumes nearly **3x the storage space** of all 4 3NF tables combined due to repeating text strings across 200,000 rows.
3. **Index Overhead:** Unnecessary indexes on denormalized analytics tables can hurt scan performance by forcing two-stage page lookups instead of single sequential scans.

## Round 6: Decide and Defend — Architecture Recommendation

### Recommendation Summary
- **Transactional Core:** Retain 3NF (`machine`, `part`, `job`, `job_part`). Protects against write anomalies and limits site updates to 1 row.
- **Reporting Engine:** Separate `report_jobpart` table populated via scheduled batch rebuild or `AFTER INSERT` triggers.
- **Key Metrics:** 
  - Read Speed: Normalized 570 ms vs. Denormalized 683 ms.
  - Update Cost: 1 row vs. 4,000 rows.
  - Storage Footprint: 3.5 MB (3NF) vs. 9.8 MB (Denormalized).

[Recommendation memo](reccomendation_memo.md).

### Task 7: 

The Curiosities Harvest

Scanning through the code and benchmarks of Module 05 reveals several subtle SQL mechanics and architectural edge cases worth noting:
- Cartesian Multiplication via CROSS JOIN:
j(n) (20,000 rows) $\times$ p(k) (10 rows) creates a full Cartesian product of 200,000 rows. It generates exactly 10 line items for every single job ID cleanly without needing explicit loops.
- Type Coercion Trap with printf():
printf('%.2f', 5 + (k % 40)) formats numbers into string text (e.g., '6.00'). In unnormalized tables, numeric attributes often degrade into text strings, requiring explicit CAST(part_price AS REAL) during 3NF extraction.
- The Hidden Assumption in SELECT DISTINCT:
INSERT INTO job SELECT DISTINCT job_id, machine_id, technician, done_on silently assumes each job has exactly one technician. If historical logs assigned two technicians to one job_id, SELECT DISTINCT would return two rows for that job_id, causing SQLite's PRIMARY KEY (job_id) constraint to fail during insertion.
- Read-Amplification of Wide Rows:report_jobpart was slower than the 4-table normalized join (~683 ms vs ~570 ms) because repeating site and technician text across 200,000 rows widened each row. Scanning wide rows forces the engine to move 3x more disk pages into memory.
- Secondary Index Overhead:CREATE INDEX ix_report_machine ON report_jobpart(machine_id) forced SQLite to traverse index B-Trees and then perform random pointers into the main table B-Tree, adding lookup overhead that surpassed a simple sequential scan.

### Task 7: DuckDB

[Optional DuckDB comparison script](duck_compare.py); the transcript below is historical and its raw runs were not saved.

(databases-portfolio) PS C:\Users\gamer\databases-portfolio> uv run --with duckdb python module05/duck_compare.py
copied job: 20000 rows
copied job_part: 200000 rows
copied machine: 50 rows
copied part: 10 rows
copied report_jobpart: 200000 rows

median of 5 runs, milliseconds (the copy into DuckDB is not timed)
scenario                             SQLite     DuckDB   rows (SQLite / DuckDB)
normalized (joins)                     97.7       14.3   350 / 350
denormalized (report table)           111.8       11.2   350 / 350


On 200,000 rows, DuckDB ran the normalized four-way join in 14.3 ms versus 97.7 ms in SQLite, and it was about 8x faster than SQLite even on the denormalized table (111.8 ms), so for this dashboard query a columnar engine makes the denormalized table unnecessary for speed, though on this small, cached dataset I can’t say whether that holds at production size.

## Verified correction and completion (fresh validation database)

The diagrams above are the two existing source sketches. `table.drawio` names the flat relation, composite key, and partial/transitive dependencies. `proposed_schema.drawio` names `machine`, `part`, `job`, and `job_part` with their key attributes. The links open their editable diagrams.

### Attributes, dependencies, and candidate key

For the relation `flat_jobpart(job_id, machine_id, site, technician, part_no, part_price, done_on)`, the domain assumptions used in this design are:

- `job_id → machine_id, technician, done_on`: a job is for one machine, assigned to one technician, and has one completion date.
- `machine_id → site`: each machine has one current site.
- `part_no → part_price`: each catalog part has one current price.
- Therefore `(job_id, part_no)` determines every attribute in a job-part row.

`(job_id, part_no)` is minimal: `job_id` alone repeats for jobs with multiple parts, and `part_no` alone repeats across jobs. Neither subset identifies a row. These are stated domain assumptions; a finite generated dataset can check consistency with them but cannot establish them as universal facts. `technician → machine_id` and `job_id → site` are not assumed. The latter follows for a particular row through `job_id → machine_id → site`, rather than being an independent domain rule.

### Normal forms and anomalies removed

- **1NF:** each row contains one job/part pair and each column one value; a comma-separated part list would violate this. The junction row gives each part its own record and makes it queryable. The five-row `flat5` teaching relation is atomic already, so 1NF does not itself remove the duplicated site or price facts in that example.
- **2NF:** the relation is in 1NF and each non-key attribute depends on the whole composite key. `part_no → part_price` is a partial dependency on only part of `(job_id, part_no)`. Moving price to `part` removes repeated prices and the associated price update anomaly; `job` facts move to `job` because they depend on `job_id` alone.
- **3NF:** the relation is in 2NF and has no non-key attribute depending transitively on the key through another non-key attribute. `job_id → machine_id → site` makes site transitively dependent on a job-part key. Moving site to `machine` removes repeated site values and the risk of inconsistent site updates.

### Concrete anomaly statements

Run these independently on the five sample rows in `flat5` from setup.sql:

```sql
-- Update anomaly: three rows for cnc-01 in this five-row sample must change.
UPDATE flat5 SET site = 'Bielefeld' WHERE machine_id = 'cnc-01';

-- Insert anomaly: record a catalog part despite having no job that uses it.
INSERT INTO flat5(job_id, machine_id, site, technician, part_no, part_price)
VALUES (NULL, NULL, NULL, NULL, 'P-0004', 9.50);

-- Delete anomaly: P-0002 has no other row, so this also erases its only price fact.
DELETE FROM flat5 WHERE job_id = 1;
```

The 3-row update count is for the five-row example only. In the generated 200,000-row dataset, changing `cnc-02`’s site in the report copy affects 4,000 fact rows, while changing the machine row in 3NF affects one row. The previous note about a guaranteed two-session concurrency failure was too strong: conflicting updates can overwrite one another, but concurrency behavior depends on transaction timing and must not be claimed from this single-row example.

### Reconciled benchmark and validation

The previously recorded 570/683 ms and 97.7/111.8 ms values remain historical results. Their raw samples, exact host/database version, and comparable timing order were not saved, so they cannot be reconciled exactly. The current interleaved nine-run measurement and all evidence are in [benchmark.md](benchmark.md) and [benchmark-results.json](benchmark-results.json). In this validation run the normalized query measured 126.6697 ms median and the reporting query 149.1518 ms median. Do not interpret this as a universal advantage; it describes the specified dataset, SQLite version, query plans, indexes, and warm-cache run.

### Curiosities: sourced facts and questions

- **Documented fact:** the two recursive CTEs produce the Cartesian product of 20,000 jobs and 10 part ordinals; SQLite documents recursive CTE behavior in [The WITH Clause](https://www.sqlite.org/lang_with.html). **Question from this dataset:** why are there only 10 distinct part numbers even though the expression contains `% 40`?
- **Documented fact:** SQLite’s `printf()` returns formatted text here, which is why the flat table stores a text price and the normalized load casts it to `REAL`. **Observation:** the formatted string looks numeric but its declared storage is text.
- **Documented fact:** SQLite requires each application connection to enable foreign-key enforcement with `PRAGMA foreign_keys = ON`; see [SQLite Foreign Key Support](https://www.sqlite.org/foreignkeys.html). **Question:** what failures would be possible if the application forgot that pragma?
- **Documented fact:** `EXPLAIN QUERY PLAN` gives a high-level strategy, and SQLite warns that its displayed format can change; see [EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html). **Observation:** the report index is scanned in full and still requires a temporary grouping B-tree in this workload.
- **Documented fact:** `dbstat` must be enabled in the SQLite build; see [SQLite virtual table documentation](https://www.sqlite.org/vtab.html). **Question:** how should storage evidence be reported when a build lacks this optional virtual table?

The verified SQLite run above reports the storage results for its build; the earlier Python SQLite build used to inspect `normalize.db` lacked `dbstat`.
