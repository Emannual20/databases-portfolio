### Task 1: Reconstruct the ER Model

**Identified Entities & Intended Keys**

1. Machine
* **Attributes:** `machine_id` (Surrogate Key / candidate), `machine_name`, `serial_no`, `site`, `installed_date`
* **Intended Primary Key:** `serial_no` (Natural Key) or `machine_name` (Business Key).
  * *Audit Notes:* Currently lacks a `PRIMARY KEY` constraint or `NOT NULL` constraints. Using `machine_name` as a key is fragile if names change or are entered as placeholders (e.g., `'RANDOM-NAME'`). `installed` contains free-text values like `'unknown'`.

2. Part
* **Attributes:** `part_id` (Surrogate Key / candidate), `part_no`, `description`, `unit_price`
* **Intended Primary Key:** `part_no` (Natural Key).
  * *Audit Notes:* Lacks a `UNIQUE` or `PRIMARY KEY` constraint, leading to duplicate records in the legacy data (e.g., two entries for `'P-1003'`). `unit_price` is improperly typed as `TEXT` instead of `DECIMAL`/`NUMERIC`.

3. Technician
* **Attributes:** `technician_id` (Surrogate Key / candidate), `technician_name`
* **Intended Primary Key:** `technician_id` (or `technician_name` as a natural text key).
  * *Audit Notes:* Currently embedded as a plain `TEXT` attribute inside `maint_job`. It should be extracted into its own entity table to avoid text redundancy and typos.

4. Maintenance Job
* **Attributes:** `job_id`, `machine_id` (FK), `technician_id` (FK), `done_on`
* **Intended Primary Key:** `job_id` (Surrogate Key).
  * *Audit Notes:* Stores `machine_name` instead of a foreign key, resulting in orphaned records (e.g., job references `'cnc-05'`, which does not exist in `machine`). `done_on` is stored as text.

5. Maintenance Job Part (Junction Entity)
* **Attributes:** `job_id` (FK), `part_no` (FK), `quantity`
* **Intended Composite Primary Key:** `(job_id, part_no)`
  * *Audit Notes:* Currently represented as a comma-separated string in `maint_job.parts_used` (e.g., `'P-1001,P-1002'`), violating First Normal Form (1NF). Must be unnested into a proper $m:n$ junction table.

2. **Reconstructed ER Diagram**

```mermaid
erDiagram
    MACHINE ||--o{ MAINTENANCE_JOB : has
    TECHNICIAN ||--o{ MAINTENANCE_JOB : performs
    MAINTENANCE_JOB ||--o{ JOB_PART : includes
    PART ||--o{ JOB_PART : used_in

    MACHINE {
        string machine_name PK
        string serial_no
        string site
        date installed
    }

    TECHNICIAN {
        string technician_name PK
    }

    MAINTENANCE_JOB {
        int job_id PK
        string machine_name FK
        string technician_name FK
        date done_on
    }

    PART {
        string part_no PK
        string description
        decimal unit_price
    }

    JOB_PART {
        int job_id PK, FK
        string part_no PK, FK
    }
```

3. **Cardinality Findings**

The database contains:
- **Machines:** 4 rows
- **Parts:** 4 rows, but only 3 distinct part numbers because P-1003 is duplicated.
- **Maintenance jobs:** 4 rows
- **Jobs using multiple parts:** Job 1 uses P-1001 and P-1002, so at least one job has multiple parts.
- **Invalid machine reference:** Job 3 refers to cnc-05, which is not present in the machine table.

4. Legacy schema models and hidden 



