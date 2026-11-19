# ACID, BASE, CAP and engine placement

## ACID

- **Atomicity:** a transaction commits all of its changes or none of them.
- **Consistency:** committed transactions preserve declared constraints and application invariants; the database cannot invent missing business rules.
- **Isolation:** concurrent transactions behave according to the engine's isolation guarantees, limiting interference between in-flight work.
- **Durability:** after a successful commit, changes survive the failures covered by the engine's durability configuration and storage assumptions.

The module's SQLite JSON `CHECK` constraint is a small consistency rule: malformed JSON is rejected at write time. The session benchmark uses a SQLite transaction for the write batch. These local experiments do not test crash recovery or production durability settings.

## BASE

**Basically Available, Soft state, Eventual consistency** is a family of design ideas commonly associated with distributed systems that accept temporarily stale or changing replicas to remain responsive and converge later. It is not a replacement acronym that makes every NoSQL database non-ACID; real products provide different transaction and consistency guarantees. The refreshed Parquet copy in 6a is intentionally stale between refreshes, but the experiment does not establish a distributed BASE service.

## CAP in practical terms

CAP concerns a distributed service during a network partition: it cannot guarantee both a linearizable view of one shared state and a successful response from every reachable side for every request. Partition tolerance is not an optional feature when the network can split; systems must define what they do during that condition. A **CP** behavior preserves the consistency guarantee by rejecting, blocking, or timing out some requests. An **AP** behavior continues answering on reachable sides, potentially with stale or conflicting values that need reconciliation. Outside a partition, systems may provide both availability and strong consistency. CAP does not mean a system can freely select any two properties in all operating conditions, and it is not a label for every local database decision.

SQLite and DuckDB are embedded in-process engines in these exercises. They avoid a database-server network partition for a single local process, while still depending on the host, filesystem, and access coordination. PostgreSQL is client/server: it enables shared network access and independent clients but adds server, network, authentication, and operations failure modes. The class PostgreSQL observations are deliberately left blank until made.

## Consistency, availability and partition tolerance

- **Consistency** here means reads observe a state that respects the promised ordering/transaction rules (CAP's strong consistency is commonly formalized as linearizability); it is distinct from merely satisfying a schema constraint.
- **Availability** in CAP means every request to a non-failed node receives a response, not that the response is fresh or correct for a stronger consistency model.
- **Partition tolerance** means the design continues to define behavior despite dropped or delayed communication between parts of a distributed system.

## Why these engines serve different work

SQLite stores relational rows and indexes for local transactional reads/writes. The 6b experiment tests JSON stored as text with validity enforcement and a path-specific expression index; flexible JSON still needs a designed contract, documented fields, and deliberate indexes. DuckDB is an embedded analytical engine suited to vectorized scans and grouped aggregates. Parquet is a compressed columnar file format that supports reading only needed columns; the 6a benchmark measures this workload rather than claiming DuckDB is universally faster. `shelve` suits simple key-to-object persistence when that access pattern is sufficient, but its backend is platform-dependent and it lacks SQLite's SQL joins and cross-session aggregation.

## Evidence boundary

Use the generated Module 6a/6b CSV and JSON for local timing conclusions. The benchmark environment is one Python/SQLite/DuckDB build and one machine. PostgreSQL concurrency, class shutdown behavior, and group discussions require actual class access and remain placeholders in this repository.
