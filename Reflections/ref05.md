# Reflection 5 — Continuation from Module04 (Working in Class on 11/11/2026)

**Session date:** [11/11/2026]

# Reflection 4 in Module 4

### Key Take-Away & Advice

- Database integrity must be enforced inside the schema itself across all three layers—Entity, Referential, and Semantic—rather than relying solely on application code. Combining `STRICT` tables, `CHECK` constraints, generated columns (`energy_j`), and `AFTER` triggers ensures invalid sensor data is caught at the storage boundary.
- Always run `PRAGMA foreign_keys = ON;` at the start of every new SQLite session, and benchmark triggers under bulk-insert loads so per-row execution overhead does not unexpectedly double write latency.

### What Was Good?

- Building `edge.db` with `STRICT` tables, `CHECK` constraints, and a generated column (`energy_j`) cleanly eliminated silent type coercion and rejected out-of-range sensor readings automatically.
- Implementing `trg_reading_audit` and `trg_vib_alarm` demonstrated how SQLite can automate value-change auditing and vibration threshold alerts without external background scripts.
- Running the 10,000-row bulk ingestion benchmark provided concrete timing evidence (~14 ms without triggers vs. ~28 ms with triggers) to quantify the real write cost of per-row trigger logic.

### What Was Difficult & Where Did I Struggle?

- Forgetting that `PRAGMA foreign_keys` defaults back to `OFF` in every new SQLite terminal connection allowed an orphan row to slip through during testing until I re-enabled it and cleaned up the table.
- Hitting syntax and execution errors when defining triggers before their prerequisite target tables (`reading_audit` and `alarm_log`) existed taught me to structure DDL initialization scripts in strict dependency order.
- Adapting to SQLite's serverless access-control model—using OS-level file permissions and read-only URI connections (`mode=ro`) instead of traditional `GRANT`/`REVOKE` database user roles—took some adjustment.

### Interesting Exploration

- Comparing `BEFORE INSERT` and `AFTER INSERT` triggers clarified why `AFTER INSERT` is critical for `trg_vib_alarm`: firing only after the row passes all table constraints prevents logging "phantom" alarms if an insert fails and rolls back.
- Measuring the 2x ingestion slowdown (~14 ms to ~28 ms across 10,000 rows) showed how per-row subqueries inside triggers scale linearly and why edge ingestion pipelines must balance automated auditing against throughput.

### Peer Interaction & Teamwork

- Collaborated with Sanjay and Htet during the initial Pod Study tasks (Tasks A and B) to test the unconstrained table and classify defects across Entity, Referential, and Semantic integrity.
- Debugged the `PRAGMA foreign_keys` connection-reset issue together with Sanjay in a fresh terminal session, removed the stray row that bypassed enforcement, and re-verified the constraint before moving on to the individual `edge.db` tasks.

### Help & Extra Work

Sanjay helped me with the indentifying anf fixing of the foreign-key settings issue in my new connection. While I jelped Sanjay with the understnading of integrity rules and debug issues. There was an instance wehre we were testing foreign key enformcement, When an orphan row unexpectedly bypassed a foreign-key constraint in a new SQLite terminal session, troubleshooting with Sanjay revealed that `PRAGMA foreign_keys` defaults back to `OFF` per connection—allowing us to re-enable it, remove the invalid row, and verify the constraint blocked the insert. During Pod Study Tasks A and B with Sanjay and Htet helped separate Entity, Referential, and Semantic integrity defects in practice rather than treating them as generic bad data.

**Contributions:** Built and verified `edge.db` with `STRICT` schemas and generated columns (`energy_j`), implemented `trg_vib_alarm` and `trg_reading_audit`, benchmarked 10,000-row ingest latency, and documented read-only (`mode=ro`) access controls.