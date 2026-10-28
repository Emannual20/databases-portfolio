# Module 3: LLM Assisted SQL & Query Profiling

## 🎯 Learning Goals
This module gives you the opportunity to explore complex querying and query optimization and achieve competency in writing, profiling, and securing SQL.

By the end of this module, you can:

1. Build complex DQL queries: joins, aggregation with GROUP BY/HAVING, subqueries, and window functions.
2. Read EXPLAIN QUERY PLAN as primary evidence: say what the engine will do for a given query, tell a SCAN from a SEARCH, and a table lookup from a covering index.
3. Benchmark the effect of an index and explain when the planner ignores one.
4. Generate a query with an LLM, then verify it: correctness, performance, and edge cases.
5. Prevent SQL injection with bound parameters and demonstrate why string concatenation is exploitable.

This module gives you the opportunity to explore complex querying and query optimization and achieve competency in writing, profiling, and securing SQL.

## Tasks:

### Divide & Conquer Pod Study
Sanjay's repository serves as the central hub for our pod's shared workstream results. I took the "Clause Order" workstream, while my pod mates (Sanjay, Lin, and Isa) handled Relational Algebra, Clause Order, and Tuning/Security. 
* **Shared File:** [Pod's shared sql-notes.md](https://github.com/yajnas-crpto/databases_portfolio_sanjay/blob/main/Module03/sql-notes.md)

* **Detailed self study:** [My sql-notes.md](Module03/sql-notes.md)

### Task 1: LLM Generation & Query Profiling (Task 1)
Generated a complex aggregation query with Claude after predicting the execution plan, then verifying with `EXPLAIN QUERY PLAN` to check for full table scans.
* **Generated query, prediction and verification:** [Task 1 file](Module03/prediction_verification.md)

### Task 2: Index Benchmarking
LLM optimization by adding indexes, with benchmarks to determine if an i,provement actually occured. 
* **Database Setup:** [setup.sql](./setup.sql)
* **Results & Proof:** [benchmark.md](./benchmark-results.md)

### Task 3: Security: SQL Injection
Reproducing injection payload, showcasing how the vulnerability is fixed by using bound parameters (`?`) instead of manual string escaping.
* **Python file:** [injection_demo.py](./injection_demo.py) 
* **Explanation:** stored in [sql-notes](sql-notes.md)

### Task 4: One query, from algebra to plan
Rewriting  query in relational algebra expression
* **Explanation:** stored in [sql-notes](sql-notes.md)

### Stretcher Task (Task 5)
rewritten query using a Correlated Subquery and a modern Window Function (`OVER (PARTITION BY ...)`).
* **SQL and Explanation:** [rewrite_subquery.md]()

## Reflection 3
[Reflection 3](/Reflections/ref03.md)


