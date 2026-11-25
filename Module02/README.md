# Module 2: Data Contracts & Reading Legacy Schemas (ERD Audits)

## 🎯 Learning Goals
This module explores conceptual data modeling and requirements analysis, building competency in reading, critiquing, and formalizing a data model.

### Learning Goal 1:
Reconstruct an ER/EER model (entities, attributes, keys, relationships, and cardinalities) from an undocumented SQL schema.
- [Task B: From words to sketch](study-log.md#cardinality-1n-machine-and-sensors) - Drew 1:1, 1:n, and m:n examples and proved a 1:n relationship with tables and a COUNT query.
- [Task 1: Reconstruct the ER model](er-audit.md#entities-and-intended-keys) - Identified the legacy entities and keys, drew the model, and recorded cardinality findings.
- [Task 5: Mermaid ER diagrams](study-log.md#good-example-library-loans) - Compared clear, ternary, and confusing diagram examples.

### Learning Goal 2:
Identify integrity defects—missing foreign keys, orphan rows, duplicate keys, invalid types, and normalization violations—with queries.
- [Task 2: Find integrity defects with queries](study-log.md#defect-orphan-maintenance-job) - Queried for orphan jobs, duplicate part numbers, text prices, invalid dates, and comma-separated part lists.
- [ER audit](er-audit.md) - Documents the schema and data issues found in the legacy database.

### Learning Goal 3:
Distinguish an entity from an attribute, and a surrogate key from a natural key, and justify the choices.
- [Task A: Study in your pod](study-log.md#entities-attributes-relationships-and-keys) - Notes on entities, attributes, relationships, and key types.
- [Task B: Entity versus attribute example](study-log.md#entity-vs-attribute-maintenance-job-and-technician) - Used a maintenance-job example to discuss whether a job and technician should be modeled as entities.
- [Task 1: Reconstruct the ER model](er-audit.md#entities-and-intended-keys) - Compared intended natural keys with surrogate-key candidates in the legacy schema.

### Learning Goal 4:
Express a schema as a code-first data contract (Pydantic / SQLAlchemy) that an application can enforce.
- [Task 3: Write the data contract in code](study-log.md#code-first-validation-and-constraints) - Defined validation and relational constraints in Python and linked the emitted DDL.
- [contract.py](contract.py) - Code-first contract and field validation.
- [emitted-ddl.sql](emitted-ddl.sql) - SQL generated from the contract.

### Learning Goal 5:
Write the requirements the schema forgot: the business rules nobody encoded.
- [Task 2: Find integrity defects with queries](study-log.md#defect-orphan-maintenance-job) - Explained the production impact of orphan references, duplicates, malformed values, and non-relational part lists.
- [Task 3: Write the data contract in code](study-log.md#code-first-validation-and-constraints) - Turned requirements such as valid serial numbers, uniqueness, required fields, and valid references into constraints.
- [Task 4: Model inheritance and prove it](study-log.md#disjoint-subtype-rule) - Expressed the disjoint machine-subtype rule in the schema design.

## Reflection 2
[Reflection 2](../Reflections/ref02.md)

## Task Inspirations (Notes & Evidence)

## **1. Reconstruct an ER/EER model**
In Task B, I translated written scenarios into 1:1, 1:n, and m:n diagrams, then checked the 1:n example in SQL by inserting one machine and two sensors and counting them. In Task 1, I applied those modeling ideas to the undocumented legacy schema and identified the intended entities, keys, and relationships. The stretcher task extended this by comparing diagram examples, including a ternary relationship that needs its own associative entity.

**Task Evidence:**
> **Task B:** [From words to sketch](study-log.md#cardinality-1n-machine-and-sensors)
> **Task 1:** [Reconstruct the ER model](er-audit.md#entities-and-intended-keys)
> **Task 5:** [Mermaid ER diagrams](study-log.md#good-example-library-loans)

## **2. Find integrity defects with queries**
I used queries to expose defects that can look valid at a glance: a maintenance job for a missing machine, a duplicated part number, prices stored as text, an invalid installation date, and a comma-separated list that cannot be joined as a proper relationship. The query outputs showed how these defects can silently distort reports and totals.

**Task Evidence:**
> **Task 2:** [Comma-separated parts defect and query result](study-log.md#defect-comma-separated-parts-do-not-form-a-relationship)
> **ER audit:** [Legacy schema audit](er-audit.md)

## **3. Distinguish entities, attributes, and key types**
The pod study and sketch exercise helped me decide what deserves its own entity. A technician who performs many jobs should be represented independently, while a component that can move between machines has a separate lifecycle. The legacy audit also showed why a natural-looking key such as `part_no` is not reliable unless the schema enforces its uniqueness, and why a surrogate key can provide a stable internal reference.

**Task Evidence:**
> **Task A:** [Pod study and modeling notes](study-log.md#entities-attributes-relationships-and-keys)
> **Task B:** [Entity versus attribute example](study-log.md#entity-vs-attribute-maintenance-job-and-technician)
> **Task 1:** [Reconstructed entities and key findings](er-audit.md#entities-and-intended-keys)

## **4. Express a schema as a code-first data contract**
In Task 3, I represented validation rules and database constraints in Python, then linked the generated DDL. The contract demonstrates how requirements such as a valid serial-number format, required values, uniqueness, composite keys, and foreign-key references can be checked instead of remaining informal expectations.

**Task Evidence:**
> **Task 3:** [Code-first data contract](study-log.md#code-first-validation-and-constraints)
> - [Python contract](contract.py)
> - [Emitted DDL](emitted-ddl.sql)

## **5. Write the business rules the schema forgot**
The audit made implicit rules visible: every job must refer to an existing machine, part numbers should not be duplicated, prices and dates must use valid representations, and a job's parts need a proper junction table. I also modeled the rule that a machine is either a CNC mill or an injection molder, never both, and compared two ways to enforce it.

**Task Evidence:**
> **Task 2:** [Integrity defects and their production impact](study-log.md#defect-orphan-maintenance-job)
> **Task 3:** [Constraints in the code-first contract](study-log.md#code-first-validation-and-constraints)
> **Task 4:** [Model inheritance and prove it](study-log.md#disjoint-subtype-rule)
