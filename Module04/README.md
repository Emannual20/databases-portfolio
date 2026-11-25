# Module 4: Data Integrity, Constraints & Edge Triggers

## 🎯 Learning Goals
This module explores data definition, manipulation, and integrity, with a focus on enforcing rules where the data lives.

### Learning Goal 1:
Create tables with constraints including NOT NULL, UNIQUE, CHECK, PRIMARY KEY, FOREIGN KEY, and STRICT typing.
- [Task A: Constraints and invalid values](integrity-notes.md#task-a) - Compared an unconstrained table with a STRICT table and observed how constraints reject invalid rows.
- [Task 1: Constraint checks](integrity-notes.md#task-1) - Tested range and type checks, foreign-key enforcement, and uniqueness.
- [Schema setup](setup.sql) - Defines constrained sensor and reading tables.

### Learning Goal 2:
Use generated columns to derive values in the database engine.
- [Task 1: Generated energy value](integrity-notes.md#task-1) - Verified the generated `energy_j` value for a valid reading.
- [Schema setup](setup.sql) - Defines `energy_j` as a generated column.

### Learning Goal 3:
Write triggers that enforce domain rules and maintain audit or rollup tables automatically.
- [Task 3: Triggers for alarms and audit](integrity-notes.md#task-3-triggers-for-alarms-and-audit) - Describes the high-vibration alarm and update audit triggers.
- [Trigger definitions and verification](triggers.sql) - Creates the triggers, exercises them, and includes a 10,000-row ingest comparison.
- [Task 5: Phantom alarm test](integrity-notes.md#task-5) - Compared a BEFORE trigger with an invalid insert and explained why the statement rollback removed the alarm.

### Learning Goal 4:
Use DML correctly, including UPSERT (ON CONFLICT) for idempotent edge ingestion.
- [Task 2: Idempotent edge ingestion with UPSERT](integrity-notes.md#task-2-idempotent-edge-ingestion-with-upset) - Loaded a CSV and checked the before/after row counts.
- [ingest.py](ingest.py) - Uses bound values and `ON CONFLICT` so rerunning the same batch does not add duplicate readings.

### Learning Goal 5:
Reason about access control: who may read or write, and how server GRANTs map to an embedded, local-first database.
- [Task 4: Access control without a server](integrity-notes.md#task-4-access-control-without-a-server) - Compared a summary view and read-only file access with server-side roles and grants.

## Reflection 4
[Reflection 4](../Reflections/ref04.md)

## Task Inspirations (Notes & Evidence)

## **1. Enforce integrity with table constraints**
The unconstrained table accepted values that did not match the intended data, including text in a numeric field. Adding STRICT typing, NOT NULL, CHECK, UNIQUE, and foreign-key rules made the database reject several invalid inserts. I also learned to enable `PRAGMA foreign_keys = ON` for each SQLite connection; declaring a foreign key alone did not reject the orphan while enforcement was off.

**Task Evidence:**
> **Task A:** [Constraint comparison and invalid-value examples](integrity-notes.md#task-a)
> **Task 1:** [Constraint checks and foreign-key behavior](integrity-notes.md#task-1)
> - [Table definitions](setup.sql)

## **2. Derive values with generated columns**
The reading table computes `energy_j` from `value * interval_s`. Querying a valid row showed the database-generated value, keeping this derived field consistent with its source values.

**Task Evidence:**
> **Task 1:** [Generated energy value](integrity-notes.md#task-1)
> - [Generated-column definition](setup.sql)

## **3. Automate alarms and audit records with triggers**
The trigger work records an alarm when vibration crosses the threshold and writes the old and new values to an audit table after an update. The phantom-alarm exercise showed why trigger timing matters: a BEFORE trigger can write a side effect before a later CHECK failure aborts the statement, and the statement rollback removes that side effect.

**Task Evidence:**
> **Task 3:** [Alarm and audit trigger notes](integrity-notes.md#task-3-triggers-for-alarms-and-audit)
> **Task 5:** [Phantom alarm test and conclusion](integrity-notes.md#task-5)
> - [Trigger SQL and verification](triggers.sql)
> - [BEFORE-trigger test](phantom_alarm_trigger.sql)

## **4. Make edge ingestion replay-safe with UPSERT**
The CSV loader applies an UPSERT keyed by sensor and timestamp. Running the same batch again updates matching readings instead of creating duplicate rows, which makes a retry safe. The loader also enables foreign-key enforcement on its connection and commits the batch as a transaction.

**Task Evidence:**
> **Task 2:** [Idempotent edge ingestion notes](integrity-notes.md#task-2-idempotent-edge-ingestion-with-upset)
> - [Python loader](ingest.py)
> - [Input batch](readings_batch.csv)

## **5. Apply access control in an embedded database**
SQLite does not provide server roles and GRANT statements. The exercise used a restricted view for summary access and read-only database access to demonstrate file-level controls, then compared that model with PostgreSQL's server-managed permissions for multiple users.

**Task Evidence:**
> **Task 4:** [Access control without a server](integrity-notes.md#task-4-access-control-without-a-server)
