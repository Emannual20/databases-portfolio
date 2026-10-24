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
# Task 5: Mermaid ER Diagram Lab

## 2. Reconstructed ER Diagram

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

## 3. Cardinality Findings

The database contains:
- **Machines:** 4 rows
- **Parts:** 4 rows, but only 3 distinct part numbers because P-1003 is duplicated.
- **Maintenance jobs:** 4 rows
- **Jobs using multiple parts:** Job 1 uses P-1001 and P-1002, so at least one job has multiple parts.
- **Invalid machine reference:** Job 3 refers to cnc-05, which is not present in the machine table.

## 2. Schema-to-Diagram and Diagram-to-Schema

### Schema to Diagram

I used the corrected maintenance schema as the source for the first diagram. The main entities are `MACHINE`, `TECHNICIAN`, `MAINTENANCE_JOB`, `PART`, and `JOB_PART`.

The diagram shows the intended relationships, but the cardinalities must be checked against the schema and actual data. A foreign key can establish a relationship, but it does not prove that every parent has a child or that every parent has multiple children.

### Diagram to Schema

The first diagram can be converted into SQL tables using primary keys, foreign keys, and a junction table. The `JOB_PART` table uses a composite primary key consisting of `job_id` and `part_no`.

After generating the SQL, the schema can be tested in SQLite and inspected with `.schema`.

### Round-Trip Findings

The main entities and relationships can survive a diagram-to-schema round trip when primary keys and foreign keys are explicitly defined. However, a diagram may not preserve every business rule, such as valid dates, positive prices, or the exact number of parts allowed in a job. An AI-generated schema may also invent attributes or constraints that were never present in the original design. Therefore, the generated schema must be checked against the original requirements.

## 3. Cardinality Overuse

Cardinality describes how many instances of one entity can relate to instances of another entity. A car may normally have four wheels, but that number is often a business rule rather than a general relationship cardinality. A car can have a spare wheel, a trailer, or a different wheel configuration. A general one-to-many relationship is more flexible, while a rule requiring exactly four standard wheels can be enforced through application validation or database constraints where appropriate. Exact cardinality is suitable when the rule is genuinely mandatory and stable, rather than merely describing a common situation.

## 4. Inheritance Overuse

### Vehicle Hierarchy

```mermaid
classDiagram
    Vehicle <|-- Car
    Vehicle <|-- Truck

    class Vehicle {
        +int vehicle_id
        +string registration
    }

    class Car {
        +int passenger_capacity
    }

    class Truck {
        +decimal load_capacity
    }
```

A separate inheritance hierarchy can be useful when different vehicle types have many distinct attributes and behaviors. However, it can become unnecessarily complex when the types differ only by a label or a small number of optional attributes.

For example, a customer may also be an employee and a student. Creating separate inheritance branches for every possible combination can produce complicated tables and duplicate information. A simpler design may use a `PERSON` table with related `CUSTOMER`, `EMPLOYEE`, and `STUDENT` roles, depending on the requirements.

Compared with the machine inheritance exercise, separate subtype tables are useful when subtype-specific attributes are substantial. If the differences are small, a single table with a `type` column and suitable constraints may be simpler.

## 5. Best Find to Share

**My choice:** The maintenance system with the `JOB_PART` junction table.

**Lesson:** A many-to-many relationship should be modeled explicitly instead of hiding several related identifiers inside a text column.

Mermaid source: see Diagram 1 above.
