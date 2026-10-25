## Task A: Study in your pod

**Reference Links:**

From this source, I understood the definition of entities, attributes and relationships. An entity is a thing that contains facts (e.g. A student, A Computer), attribute describes an entity (e.g.Student has an ID, Computer has a Serial Number) A relationship lniks entities, usually a verb (.e.g Student **Attends** Math, Student **Owns** Computer) <br>

Entity Relationship Model: [Wiki Entity Relationship Model](https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model)<br>

Cardinality: [Wiki Cardinality](https://en.wikipedia.org/wiki/Cardinality_(data_modeling))<br>

EER: [Wiki Enhanced Entity Relationship](https://en.wikipedia.org/wiki/Enhanced_entity%E2%80%93relationship_model)<br>

Surrogate Key: [Wiki Surrogate Key](https://en.wikipedia.org/wiki/Surrogate_key)<br>

**Google Searches:**<br>
_"What is a junction table in DataBases?"_
A junction table, also known as an associative entity or bridge table, is a database table used to resolve a many-to-many relationship between two other tables. It works by storing the primary keys of the associated tables as foreign keys, effectively creating two separate one-to-many relationships that link the respective records together.<br>
Source URL: [Wiki Associative Entity](https://en.wikipedia.org/wiki/Associative_entity)<br>

_"What is a surrogate key and its purpose?"_<br>
A surrogate key is an artificially generated, unique identifier added to a database table to act as the primary key. Its primary purpose is to provide a stable, system-managed key that is independent of any business logic, ensuring reliable relationships between tables even if the underlying business data changes.<br>
Source URL: [Surrogate Key](https://en.wikipedia.org/wiki/Surrogate_key)<br>

Googled Questions:

"How do you draw an Entity Relationship Diagram in SQL": [How to Drw ER Digrms)https://www.geeksforgeeks.org/sql/how-to-draw-entity-relationship-diagrams/


Remarkable things — surprises, "aha"s, and counterexamples (e.g. "a name looked like a key but had duplicates").


LLM Q&A — for each prompt you tried: the prompt, a 2–3 line summary of the answer, and how you verified it (and where it was wrong).


Your two best found ER sketches — hunt down ER/EER example sketches that teach you the most, then compile down to the best two:

## Task B: From words to sketch
All diagrams were self-made in draw.io, with help from Geeks for Geeks<br>

1:1 — A workshop keeps machines. Each machine has exactly one nameplate (serial number, manufacturer), and each nameplate belongs to exactly one machine. → Key goes to the many side, and the nameplate is its own entity.

![1:1](https://github.com/Emannual20/databases-portfolio/blob/main/Module02/pictures/1to1%20A%20Workshop%20Keeps%20machines.drawio.svg)

1:n — Each machine carries many sensors; every sensor is installed on exactly one machine. → The many side holds the foreign key.

![1:n](https://github.com/Emannual20/databases-portfolio/blob/main/Module02/pictures/1ton%20diagram.drawio.svg)

m:n — Work orders use many parts, and a part is used by many work orders; an order can list a given part only once. → We need a junction table, and it holds foreign keys.

![m:n](https://github.com/Emannual20/databases-portfolio/blob/main/Module02/pictures/many%20to%20many.drawio.svg)

Entity vs. attribute vs. relationship — A maintenance job happens on one machine, is done by one technician on one date; a technician performs many jobs. → Is the job a relationship or an entity? Is the technician an entity or just a name?

Then prove one: write the CREATE TABLE for your favourite sketch, insert two rows, and show the COUNT query that demonstrates its cardinality.

-- Step 1: CREATE TABLES<br>
```
CREATE TABLE machines (
    machine_id INT PRIMARY KEY,
    location VARCHAR(100) NOT NULL
);

CREATE TABLE sensors (
    sensor_id INT PRIMARY KEY,
    sensor_type VARCHAR(50) NOT NULL,
    machine_id INT NOT NULL,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);
```
-- Step 2: INSERT DATA (1 Machine, 2 Sensors referencing that Machine)<br>
```
INSERT INTO machines (machine_id, location) 
VALUES (101, 'Assembly Line A');

INSERT INTO sensors (sensor_id, sensor_type, machine_id) 
VALUES 
    (1, 'Vibration', 101),
    (2, 'Temperature', 101);
```
-- Step 3: COUNT QUERY TO PROVE CARDINALITY (1:n)
```
SELECT 
    m.machine_id,
    m.location,
    COUNT(s.sensor_id) AS total_sensors
FROM machines m
LEFT JOIN sensors s ON m.machine_id = s.machine_id
WHERE m.machine_id = 101
GROUP BY m.machine_id, m.location;
```

**Task C: Explain & share with another pod**

### Post-Pod Key Takeaways

**SQLite's Silent Danger**

I was reminded today of just how dangerous SQLite’s default behavior can be. Leaving foreign keys turned off by default is a massive trap, especially when working with legacy schemas. If you aren't explicitly enforcing them at the connection level, orphan rows are bound to creep in—like assigning critical maintenance jobs to ghost machines without the system ever realising.

**The 1NF Comma Trap**

Storing lists of parts as comma-separated strings inside a single field is a habit that completely wrecks relational design. It makes clean `JOIN` operations impossible and leads to silent data loss the moment you try to query for individual part usage. Using proper junction tables isn't just best practice—it's non-negotiable.

**Natural Keys vs. Reality**

Relying on natural keys like part numbers or names as primary keys sounds good in theory, but it creates huge vulnerabilities in practice. If a supplier updates their part numbering format or someone changes their name, that change cascades across the entire database. I’m definitely leaning toward surrogate keys (`INTEGER PRIMARY KEY`) for internal references to keep structural integrity isolated from real-world changes.

**Drawing the Entity vs. Attribute Line**

A great rule of thumb that came out of our discussion: deciding whether something is an attribute or an entity usually comes down to its lifecycle. If a component—like a motor or a sensor—can be unbolted from one machine and installed on another, it has its own independent life and needs to be its own entity. If it’s permanently tied to the machine and gets scrapped with it, it’s just an attribute.

## Task 1: Reconstruct the ER model

**ER Audit File:** [er-audit.md](https://github.com/Emannual20/databases-portfolio/blob/main/Module02/er-audit.md)

## Task 2: Find the integrity efects with queries

-- Defect 1: orphan maintenance jobs (machine_name not in machine)<br>
SELECT m.job_id, m.machine_name
FROM maint_job m
LEFT JOIN machine x ON m.machine_name = x.machine_name
WHERE x.machine_name IS NULL;
```
╭────────┬──────────────╮
│ job_id │ machine_name │
╞════════╪══════════════╡
│      3 │ cnc-05       │
╰────────┴──────────────╯
```
What breaks in production: job 3 references `cnc-05`, which doesn't exist in `machine`, so the job can't be attributed to any machine or site, and maintenance cost and downtime reports will silently leave it out.

-- Defect 2: duplicate natural keys in part<br>
SELECT part_no, COUNT(*) AS copies
FROM part GROUP BY part_no HAVING COUNT(*) > 1;
```
╭─────────┬────────╮
│ part_no │ copies │
╞═════════╪════════╡
│ P-1003  │      2 │
╰─────────┴────────╯
```
P-1003 exists twice in part, so any join on part_no returns two rows for it, which double-counts job costs and parts usage, and a price lookup can return either copy with no way to tell which is right.

-- Defect 3: unit_price stored as text — a numeric comparison fails silently<br>
SELECT part_no, unit_price FROM part WHERE unit_price < '15';   -- 'text ordering', not money!
```
╭─────────┬────────────╮
│ part_no │ unit_price │
╞═════════╪════════════╡
│ P-1001  │ '12.50'    │
╰─────────┴────────────╯
```
unit_price is stored as text, so < '15' compares characters instead of numbers and wrongly includes or excludes parts ('100.00' counts as “under 15”, '9.99' doesn’t), which can produce wrong price filters, totals, and invoices without any error.

-- Defect 4: installed dates that are not dates<r>
SELECT machine_name, installed FROM machine
WHERE installed NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]';
```
╭──────────────┬───────────╮
│ machine_name │ installed │
╞══════════════╪═══════════╡
│ RANDOM-NAME  │ unknown   │
╰──────────────┴───────────╯
```
Installed column is free text, so RANDOM-NAME holds 'unknown' instead of a date. Date arithmetic on it returns NULL or sorts wrongly, so warranty expiry and service-interval calculations silently skip or misjudge that machine, and nothing flags it.

-- Defect 5: the m:n list only "joins" when it holds exactly one part<br>
SELECT j.job_id, p.description
FROM maint_job j
JOIN part p ON p.part_no = j.parts_used;   -- the list is not a key
-- Watch what happens: job 2 ('P-1003') and job 3 ('P-1001') match, but job 1
-- ('P-1001,P-1002') silently disappears. A naive join on the list loses every
-- multi-part job — and reports success while doing it. That silence is the defect.
```
╭────────┬───────────────────╮
│ job_id │    description    │
╞════════╪═══════════════════╡
│      2 │ Coolant filter    │
│      2 │ Coolant filter    │
│      3 │ Ball bearing 6203 │
╰────────┴───────────────────╯
```
parts_used holds a comma-separated list, so joining on it matches only single-part jobs: job 1 ('P-1001,P-1002') silently vanishes from parts reports, and job 2 is double-counted because P-1003 is duplicated, so parts usage and cost come out wrong while the query still reports success.

### Task 3: Write the data contract in code

Python File: [contract.py](https://github.com/Emannual20/databases-portfolio/blob/main/Module02/contract.py)

Emitted DDL File: [emitted-ddel.sql](https://github.com/Emannual20/databases-portfolio/blob/main/Module02/emitted-ddl.sql)

Field Validator is the Pydantic checker in the Python code that checks if the Srrial Number begins with SN_ and for SQLite enforces rules such as nullable=False (NOT NULL) jects the row if that column is empty. Other rules and explanations:<br>
UniqueConstraint("serial_no")	Looks through existing values and rejects a repeat <br>
primary_key=True	Same as unique, and the value must also be present <br>
Composite key on job_part	Rejects a second row with the same job and part pair <br>
ForeignKey(...)	Looks up the referenced table and rejects the row if the target doesn’t exist (only if switched on, see below) <br>

## Task 4: Model inheritance and prove it

Assumptions: A machine is a CNC mill or an injection molder, never both (disjoint).
**Attributes (from contract.py):** machine_id, serial_no, site, installed
**Extra attributes:**
**CNC mill:** spindle_rpm_max, axes<br>
**Injection molder:** shot_volume_cm3, drive_type (hydraulic / electric / hybrid)<br>

**Design A: one table with a discriminator column**
```
CREATE TABLE machine (
  machine_id      INTEGER PRIMARY KEY,
  serial_no       TEXT NOT NULL UNIQUE,
  site            TEXT NOT NULL,
  installed       TEXT NOT NULL,
  machine_type    TEXT NOT NULL CHECK (machine_type IN ('cnc_mill','injection_molder')),
  spindle_rpm_max INTEGER,
  axes            INTEGER,
  shot_volume_cm3 INTEGER,
  drive_type      TEXT CHECK (drive_type IN ('hydraulic','electric','hybrid')),
  CHECK (
    (machine_type = 'cnc_mill'
       AND spindle_rpm_max IS NOT NULL AND axes IS NOT NULL
       AND shot_volume_cm3 IS NULL AND drive_type IS NULL)
    OR
    (machine_type = 'injection_molder'
       AND shot_volume_cm3 IS NOT NULL AND drive_type IS NOT NULL
       AND spindle_rpm_max IS NULL AND axes IS NULL)
  )
);
```
machine_type is the discriminator. The subtype columns must allow NULL, because a mill row has no clamp or shot data. The table-level CHECK brings the strictness back: a mill must fill its own columns and leave the molder's empty, and the other way round.<br>
**Design B: separate tables**
```
CREATE TABLE cnc_mill (
  machine_id      INTEGER PRIMARY KEY REFERENCES machine(machine_id),
  spindle_rpm_max INTEGER NOT NULL,
  axes            INTEGER NOT NULL
);

CREATE TABLE injection_molder (
  machine_id      INTEGER PRIMARY KEY REFERENCES machine(machine_id),
  shot_volume_cm3 INTEGER NOT NULL,
  drive_type      TEXT NOT NULL CHECK (drive_type IN ('hydraulic','electric','hybrid'))
);
```
Each subtype table's primary key is also a foreign key to machine, which is how "a mill is a machine" is written in tables. Subtype columns can be NOT NULL, and nothing sits empty.

**Decision:** I would ship Design A<br>
**Rationale:** I would ship Design A because with only two extra columns per type, one table with a discriminator and a CHECK is the simplest schema that still makes a machine impossible to be both types, and it needs no joins.