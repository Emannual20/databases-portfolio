# Module 05: Normalization vs Denormalization Notes
[link](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/06a-duckdb-analytical-engine.md#-story--the-report-that-outgrew-sqlite)
## Round 1: Functionl Dependencies
**Functional Dependencies:** If you know X, then Y is 100% fixed and predictable. Two rows with the exact same X can never have different Y values.

>**Example:**<br>
>Rule: A physcial machine lives at only one factory location. <br>
>Meaning: If you see machine cnc-01, it is definetly in Gütersloh, it cannot be in two cities at once.

Candidate Key: Minimal set of attributes to determine the full details.

>**Example:**<br>
> job_id is not enough information as one job can have multiple parts. Instead we pair (job_id, part_no) a unique combination.

**Group Member Discussion:**
>Isa explined to me Normliztion nd Denormliztion, as well as the indexing. [Include Clssroom Discussion file, link portfolios of reflections to one nother for dditionl evidence nd portfolios to Module 05]

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

Original Design: ![Insert ER Sketch Table]

Insert ER sketch Proposed Schema

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
[Insert Anomaly Image here]

Since job_id, machine_id, site and technician did not have 'NOT NULL' constraints, they are all forced to be NULL and added into the table.

[Insert Full table image here]


'''sql
sqlite> DELETE FROM flat5 WHERE job_id = 2;
'''
[insert image of deleted job_id2]

- **SQL for Asset Loss:** `DELETE FROM flat5 WHERE job_id = 2;`
  - **Flaw:** Deleting Job 2 silently erases all existence records for machine `cnc-02` and technician `tech-1` from the system.
- **SQL for Part Loss:** `DELETE FROM flat5 WHERE job_id = 1;`
  - **Flaw:** Deleting Job 1 silently erases part `P-0002` from the catalog because it was the only job referencing it.

### Task 3: Built it

[Insert Integrity check image here]

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

[Inseet link to recccomendation memo here]

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

[insert lnik to duckdb file here]

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
