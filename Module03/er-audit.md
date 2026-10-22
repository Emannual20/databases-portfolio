cat <<'EOF' > module-02/er-audit.md
# Entity & Data Quality Audit: legacy.db

## Identified Entities & Intended Keys

### 1. Machine
* **Attributes:** `machine_id` (Surrogate Key / candidate), `machine_name`, `serial_no`, `site`, `installed_date`
* **Intended Primary Key:** `serial_no` (Natural Key) or `machine_name` (Business Key).
  * *Audit Notes:* Currently lacks a `PRIMARY KEY` constraint or `NOT NULL` constraints. Using `machine_name` as a key is fragile if names change or are entered as placeholders (e.g., `'RANDOM-NAME'`). `installed` contains free-text values like `'unknown'`.

### 2. Part
* **Attributes:** `part_id` (Surrogate Key / candidate), `part_no`, `description`, `unit_price`
* **Intended Primary Key:** `part_no` (Natural Key).
  * *Audit Notes:* Lacks a `UNIQUE` or `PRIMARY KEY` constraint, leading to duplicate records in the legacy data (e.g., two entries for `'P-1003'`). `unit_price` is improperly typed as `TEXT` instead of `DECIMAL`/`NUMERIC`.

### 3. Technician
* **Attributes:** `technician_id` (Surrogate Key / candidate), `technician_name`
* **Intended Primary Key:** `technician_id` (or `technician_name` as a natural text key).
  * *Audit Notes:* Currently embedded as a plain `TEXT` attribute inside `maint_job`. It should be extracted into its own entity table to avoid text redundancy and typos.

### 4. Maintenance Job
* **Attributes:** `job_id`, `machine_id` (FK), `technician_id` (FK), `done_on`
* **Intended Primary Key:** `job_id` (Surrogate Key).
  * *Audit Notes:* Stores `machine_name` instead of a foreign key, resulting in orphaned records (e.g., job references `'cnc-05'`, which does not exist in `machine`). `done_on` is stored as text.

### 5. Maintenance Job Part (Junction Entity)
* **Attributes:** `job_id` (FK), `part_no` (FK), `quantity`
* **Intended Composite Primary Key:** `(job_id, part_no)`
  * *Audit Notes:* Currently represented as a comma-separated string in `maint_job.parts_used` (e.g., `'P-1001,P-1002'`), violating First Normal Form (1NF). Must be unnested into a proper $m:n$ junction table.
