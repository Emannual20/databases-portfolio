# Module 5 — Normalization vs. Denormalization

This module records the functional dependencies, anomalies, 3NF decomposition, and measured reporting trade-offs for the maintenance job/part dataset.

## Evidence

- [Normalization notes](normalization-notes.md)
- [Reproducible setup script](setup.sql)
- [SQLite benchmark method, raw-result link, query plans, and storage](benchmark.md)
- [Machine-readable raw runs and validation results](benchmark-results.json)
- [DuckDB comparison script](duck_compare.py)
- [Current-state ER sketch](table.drawio)
- [Proposed 3NF ER sketch](proposed_schema.drawio)
- [Recommendation memo](reccomendation_memo.md)
- [Module 5 reflection](../Reflections/ref05.md)

To rebuild the dataset, use a separate file such as `Module05/normalize_test.db`; preserve `normalize.db` as the original work database.
