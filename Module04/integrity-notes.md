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
Error near line 3: CHECK constraint failed: value >= -273.15 AND value <= 5000

sqlite> INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (1,'2026-03-01 08:00:02', 'hot', 1);
Error near line 4: cannot store TEXT value in REAL column reading.value

sqlite> INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (99,'2026-03-01 08:00:03', 40, 1);

In the beginning, this ran fine:
1. A foreign key in the schema isn’t enforced until each connection turns it on. SQLite checks REFERENCES rules only after PRAGMA foreign_keys = ON;, and the setting resets to off every time you open a new shell, so your insert for sensor 99 was silently accepted.
2. Turning it on doesn’t repair data that is already bad. The orphan row stays in the table until you find it with PRAGMA foreign_key_check; and delete it.

**How I fixed this issue:**
1. Switch it on and check: PRAGMA foreign_keys = ON; then PRAGMA foreign_keys; (it should print 1).
2. Remove the orphan row: DELETE FROM reading WHERE sensor_id = 99;
3. Run the insert again: now fails with FOREIGN KEY constraint failed.

**Result:**
sqlite> INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (99,'2026-03-01 08:00:03', 40, 1);
Error near line 9: FOREIGN KEY constraint failed

sqlite> INSERT INTO sensor VALUES (3,'cnc-01','temp_c','degC');
Error near line 10: UNIQUE constraint failed: sensor.machine_id, sensor.metric

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

What is a trigger: A rule that fires itself based on the table, can have conditions that are optional.

When it fires	AFTER INSERT ON reading (alarm) and AFTER UPDATE OF value ON reading (audit)
A condition (optional)	WHEN NEW.value > 2.0 AND ...is vib_rms
What it does	An INSERT into alarm or audit

