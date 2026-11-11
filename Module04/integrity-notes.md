Pod Study: Integrity Has Layers

Integrity Layers

| Layer | Question it answers | SQL mechanism |
|---|---|---|
| **Entity integrity** | Is every row identifiable and complete? | `PRIMARY KEY`, `NOT NULL`, `UNIQUE` |
| **Referential integrity** | Do relationships point at things that exist? | `FOREIGN KEY` (+ `ON DELETE`/`ON UPDATE`) |
| **Semantic (domain) integrity** | Does the value make sense? | `CHECK`, generated columns, triggers |


### Task A:

With an unconstrained table, the table accepts anything The declaration in the "create table" command is only a hint, but SQLite does not enforce it.

Self added insert: sqlite> INSERT INTO t VALUES (0,'sensor','9000'); 

sensor_id = 0
value = 9000 (string)

Table Output:
╭───────────┬────────┬────────╮
│ sensor_id │ metric │ value  │
╞═══════════╪════════╪════════╡
│         1 │ temp_c │ 9000.0 │
│         1 │ temp_c │ hot    │
│         2 │ bogus  │ -500.0 │
│         0 │ sensor │ 9000.0 │
╰───────────┴────────┴────────╯

CREATE TABLE t2 (
  reading_id INTEGER PRIMARY KEY,
  # We select the data type we want for that attrbute, followed  the rule it has to follow (e.g. PRIMARY KEY)
  sensor_id  INTEGER NOT NULL,
  # NOT NULL means the attribute cannot be empty
  metric     TEXT    NOT NULL CHECK (metric IN ('temp_c','vib_rms','spindle_load')),
  # CHECK sures values makes sense (allowed list/range)
  value      REAL    NOT NULL CHECK (value BETWEEN -273.15 AND 5000)
) STRICT; # stops words from going into the numbers column

Our original INSERT command no longer works:
sqlite> INSERT INTO t2 VALUES (1,'temp_c',9000), (1,'temp_c','hot'), (2,'bogus',-500);
Parse error near line 11: table t2 has 4 columns but 3 values were supplied

test command: 
sqlite> INSERT INTO t2(sensor_id, metric, value) VALUES (1, 'temp_c', 9000);

Error called out:
Error near line 1: CHECK constraint failed: value BETWEEN -273.15 AND 5000

Command that fulfills all rules:
sqlite> INSERT INTO t2(sensor_id, metric, value) VALUES (1, 'temp_c', 90); 

Resulting table out:
sqlite> SELECT * FROM t2;
╭────────────┬───────────┬────────┬───────╮
│ reading_id │ sensor_id │ metric │ value │
╞════════════╪═══════════╪════════╪═══════╡
│          1 │         1 │ temp_c │  90.0 │
╰────────────┴───────────┴────────┴───────╯

### Task B

## Task B: sharing with another pod

**Most surprising thing an unconstrained table accepted (our pod):**
The word 'hot' went into a REAL column with no error, and typeof() showed it
was stored as text. SQLite only *tries* to convert values to the declared type:
'7' becomes the integer 7, but 'abc' is kept as text. The declared type is a hint,
not a rule.

**Hardest constraint to get right:** CHECK with NULL.
[Replace this if your pod found a different one hardest.]
A column with CHECK (value BETWEEN -273.15 AND 5000) still accepts NULL, because
the check only rejects rows where the condition is false, and a comparison with
NULL is "unknown". The fix is to add NOT NULL.
Runners-up: UNIQUE (sensor_id, metric) accepted two rows with sensor_id NULL,
because NULLs count as distinct; and STRICT accepted the text '1.0' in an INTEGER
column by converting it, while rejecting 1.5.

**What the other pod reported:**
**Agreed points:**
- STRICT, NOT NULL, CHECK and UNIQUE each catch a different kind of bad row, so
  none replaces another.
- A CHECK on a nullable column does not stop NULL; pair it with NOT NULL.
- UNIQUE does not treat NULLs as duplicates.
- A range check blocks the impossible, not the implausible: 4999 °C still passes.

**Unresolved:**
- Should plausible ranges be set per metric, with a CHECK using CASE or a trigger?
- Is it acceptable that STRICT converts '1.0' to 1 for an INTEGER column?


### Task 1: 

sqlite> INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (1,'2026-03-01 08:00:01', 9000, 1);

**Error:**
Error near line 3: CHECK constraint failed: value >= -273.15 AND value <= 5000

sqlite> INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (1,'2026-03-01 08:00:02', 'hot', 1);
**Error:**
Error near line 4: cannot store TEXT value in REAL column reading.value

sqlite> INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (99,'2026-03-01 08:00:03', 40, 1);
**Initial Observation:**
In the beginning, this ran fine:
1. A foreign key in the schema isn’t enforced until each connection turns it on. SQLite checks REFERENCES rules only after PRAGMA foreign_keys = ON;, and the setting resets to off every time you open a new shell, so your insert for sensor 99 was silently accepted.
2. Turning it on doesn’t repair data that is already bad. The orphan row stays in the table until you find it with PRAGMA foreign_key_check; and delete it.

**How I fixed this issue:**
1. Switch it on and check: PRAGMA foreign_keys = ON; then PRAGMA foreign_keys; (it should print 1).
2. Remove the orphan row: DELETE FROM reading WHERE sensor_id = 99;
3. Run the insert again: now fails with FOREIGN KEY constraint failed.

**Result:**
sqlite> INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (99,'2026-03-01 08:00:03', 40, 1);
**Error:**
Error near line 9: FOREIGN KEY constraint failed

sqlite> INSERT INTO sensor VALUES (3,'cnc-01','temp_c','degC');
**Error:**
Error near line 10: UNIQUE constraint failed: sensor.machine_id, sensor.metric

**Generted energy_j vlue for vlid row:**
sqlite> SELECT reading_id, value, interval_s, energy_j FROM reading;
╭────────────┬───────┬────────────┬──────────╮
│ reading_id │ value │ interval_s │ energy_j │
╞════════════╪═══════╪════════════╪══════════╡
│          1 │  41.5 │          1 │     41.5 │
╰────────────┴───────┴────────────┴──────────╯

### Task 2: Idempotent edge ingestion with UPSET

sqlite> SELECT sql FROM sqlite_master WHERE name = 'ux_reading_sensor_ts';
╭────────────────────────────────────────────────────────────────────╮
│                                sql                                 │
╞════════════════════════════════════════════════════════════════════╡
│ CREATE UNIQUE INDEX ux_reading_sensor_ts ON reading(sensor_id, ts) │
╰────────────────────────────────────────────────────────────────────╯
sqlite> INSERT INTO reading(sensor_id, ts, value, interval_s)
   ...> VALUES (1,'2026-03-01 08:00:00', 41.7, 1)
   ...> ON CONFLICT(sensor_id, ts) DO UPDATE SET value = excluded.value;
sqlite> SELECT sensor_id, ts, value, energy_j FROM reading WHERE sensor_id = 1;
╭───────────┬─────────────────────┬───────┬──────────╮
│ sensor_id │         ts          │ value │ energy_j │
╞═══════════╪═════════════════════╪═══════╪══════════╡
│         1 │ 2026-03-01 08:00:00 │  41.7 │     41.7 │
╰───────────┴─────────────────────┴───────┴──────────╯

<br>
link python file here: 

o> & c:\Users\gamer\databases-portfolio\.venv\Scripts\python.exe c:/Users/gamer/databases-portfolio/Module04/ingest.py
file rows: 5 | table rows before: 1 | after: 5 | new rows: 4

### Task 3: Triggers for alarms and audit
Trigger File: Insert trigger file here

Insert Image of output here:
**Output:**

What is a trigger: A rule that fires itself based on the table, can have conditions that are optional.

When it fires	AFTER INSERT ON reading (alarm) and AFTER UPDATE OF value ON reading (audit)
A condition (optional)	WHEN NEW.value > 2.0 AND ...is vib_rms

### Task 4: Access control without a server

In SQLite, there is no GRANT to protect our data as it is a simple file running locally. 

We create a view to prevent people from dumping out all the raw sensor readings, instead we let them look through a window that only shows summary information.

cmod 444 which is a linux command puts a lock on the database file, turning it to read-only.

Powershell Command on windows to make database files Read-Only: Set-ItemProperty -Path Module04/edge.db -Name IsReadOnly -Value $true

''' sql
(databases-portfolio) PS C:\Users\gamer\databases-portfolio> sqlite3 "file:Module04/edge.db?mode=ro" "SELECT COUNT(*) FROM reading;"

"""mode=ro means read-only"""
╭──────────╮
│ COUNT(*) │
╞══════════╡
│    10000 │
╰──────────╯
'''

**Trying to delete a reading will throw an error**
(databases-portfolio) PS C:\Users\gamer\databases-portfolio> sqlite3 "file:Module04/edge.db?mode=ro" "DELETE FROM reading;"
Error in 2nd command line argument: attempt to write a readonly database

Insert Machine Health View here: (Picture of machien ehalth view)

How would this differ with PostgrSQL Server, and why is file-permission-based control acceptale here but not for a multi-tenant web app?

A PostgreSQL database engine manages internal authentication using SQL commands like CREATE ROLE and GRANT SELECT ON machine_health TO analyst, decoupling data permissions completely from the host operating system's file system. File-permission-based access control is acceptable for SQLite on an embedded IoT edge node because the database file runs in-process with a single application on an isolated physical device. In contrast, operating system file permissions cannot isolate individual application users sharing a multi-tenant web backend, as granting read access to the database file would expose all tenants' raw data to any system process. A server-based database uses fine-grained session authentication and Row-Level Security (RLS) to safely enforce data boundaries across thousands of concurrent web users.

### Task 5: 

Insert file link for phantom alarm test: (file link here)

sqlite3 Module04/edge.db ".read Module04/phantom_alarm_trigger.sql"

Error triggered the alarm:
(databases-portfolio) PS C:\Users\gamer\databases-portfolio> sqlite3 Module04/edge.db ".read Module04/phantom_alarm_trigger.sql"
Error near line 58 of Module04/phantom_alarm_trigger.sql: CHECK constraint failed: value >= -273.15 AND value <= 5000

But when printing the alarms, no new alarm was added

When `trg_vib_alarm` is defined as `BEFORE INSERT`, attempting to insert an invalid value (`value = 9000`, failing `CHECK <= 5000`) causes SQLite to execute the trigger write first, followed by a constraint failure on `reading`. 

Because SQLite enforces statement-level atomicity, the constraint error triggers an `ABORT` that rolls back the entire statement—discarding the trigger's write to `alarm`. Consequently, no alarm row is saved for the failed insertion attempt.

**Conclusion:** `AFTER INSERT` is the correct default for audit logs and alarms because it guarantees that side-effect records are only created for rows that pass all domain constraints and successfully persist to storage.