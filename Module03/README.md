# Module 3: LLM-Assisted SQL & Query Profiling

## 🎯 Learning Goals
This module explores complex querying, query optimization, and SQL security, building competency in writing, profiling, and securing queries.

### Learning Goal 1:
Build complex DQL queries using joins, aggregation with GROUP BY / HAVING, subqueries, and window functions.
- [Task 1: Ask the LLM, then check the plan](prediction_verification.md#generated-query-and-actual-result) - Wrote a multi-table aggregation with joins, date filtering, grouping, and distinct counts.
- [Task 4: One query, from algebra to plan](sql-notes.md#relational-algebra-expression) - Traced a joined and filtered query through relational algebra.
- [Task 5: Window functions and a subquery rewrite](rewrite_subquery.md#window-function-rewrite-and-plan) - Compared grouped aggregation with correlated-subquery and window-function rewrites.

### Learning Goal 2:
Read EXPLAIN QUERY PLAN as primary evidence: explain SCAN versus SEARCH and table lookups versus covering-index access.
- [Task A: Plan safari](sql-notes.md#equality-after-adding-an-index-search) - Predicted plans, checked SQLite output, and observed which predicates used an index.
- [Task 1: Prediction and verification](prediction_verification.md#plan-correction) - Compared my predictions with the actual multi-table plan.
- [Task 2: Index benchmark](benchmark.md#annual-aggregation-index-comparisons) - Recorded plan changes and the temporary B-trees used for grouping, distinct counts, and ordering.

### Learning Goal 3:
Benchmark the effect of an index and explain when the planner ignores one.
- [Task 2: Index benchmark](benchmark.md#selective-single-day-lookup-and-amortized-timing) - Compared plans and measured a selective single-day query before and after adding indexes.
- [Task A: Leading wildcard example](sql-notes.md#leading-wildcard-index-still-cannot-narrow-the-search) - Saw that an equality index enabled SEARCH while a leading-wildcard predicate still scanned.

### Learning Goal 4:
Generate a query with an LLM, then verify its correctness, performance, and edge cases.
- [Task 1: Ask the LLM, then check the plan](prediction_verification.md#plan-correction) - Compared the generated query and its plan against my own prediction.
- [Task 2: Index benchmark](benchmark.md#annual-aggregation-index-comparisons) - Measured proposed indexing changes rather than assuming they improved performance.
- [Task 5: Window functions and a subquery rewrite](rewrite_subquery.md#correlated-subquery-rewrite-and-plan) - Compared alternative query plans for the same result.

### Learning Goal 5:
Prevent SQL injection with bound parameters and demonstrate why string concatenation is exploitable.
- [Task 3: The Injection Drill](sql-notes.md#why-bound-parameters-stop-the-payload) - Ran a normal input, the `' OR '1'='1` payload, and a parameterized query to compare the results.
- [injection_demo.py](injection_demo.py) - Reproducible Python demonstration of vulnerable and safe query construction.

## Reflection 3
[Reflection 3](../Reflections/ref03.md)

## Task Inspirations (Notes & Evidence)

## **1. Build complex DQL queries**
I used joins, filters, grouping, distinct counts, and revenue calculations in the city-level order query. I then explored three ways to report late-order counts per customer: GROUP BY, a correlated subquery, and a window function. Comparing these forms helped me see how SQL expresses the same question through different query structures.

**Task Evidence:**
> **Task 1:** [Multi-table aggregation query](prediction_verification.md#generated-query-and-actual-result)
> **Task 4:** [Query from algebra to plan](sql-notes.md#relational-algebra-expression)
> **Task 5:** [Subquery and window-function rewrites](rewrite_subquery.md#window-function-rewrite-and-plan)

## **2. Read EXPLAIN QUERY PLAN**
I predicted which operations SQLite would use and checked the plan output. The plan safari showed that equality on an indexed column could change a SCAN to a SEARCH, while a leading wildcard still required a scan. For the larger aggregation, the plan also revealed the join order, primary-key lookups, and temporary B-trees that my first prediction missed.

**Task Evidence:**
> **Task A:** [Plan safari](sql-notes.md#equality-after-adding-an-index-search)
> **Task 1:** [Prediction and plan verification](prediction_verification.md#plan-correction)
> **Task 2:** [Benchmark plans](benchmark.md#annual-aggregation-index-comparisons)

## **3. Benchmark indexes and planner choices**
The benchmark showed that an index is useful when it narrows a query to a small subset, as in the single-day lookup. For the broad annual aggregation, SQLite initially kept scanning `order_line`; adding an order-line index changed the join order and plan. An additional product index did not change the plan or produce a meaningful improvement for that query, showing why each index needs to be measured against the actual workload.

**Task Evidence:**
> **Task 2:** [Index benchmark results](benchmark.md#annual-aggregation-index-comparisons)
> **Task A:** [Index and predicate plan comparisons](sql-notes.md#equality-after-adding-an-index-search)

## **4. Generate and verify LLM queries**
I treated the generated aggregation as a proposal: I compared its output with the requested result and checked its execution plan against my prediction. The benchmark and rewrite tasks continued that verification by checking measured timings and comparing the plans of alternative SQL forms.

**Task Evidence:**
> **Task 1:** [Generated query, prediction, and verification](prediction_verification.md#plan-correction)
> **Task 2:** [Measured index changes](benchmark.md#annual-aggregation-index-comparisons)
> **Task 5:** [Compared rewrite plans](rewrite_subquery.md#window-function-rewrite-and-plan)

## **5. Prevent SQL injection with bound parameters**
In the injection drill, concatenating the payload `' OR '1'='1` into the query returned multiple customers. Binding the same input as a parameter returned no matches because SQLite treated it as data rather than executable SQL. This demonstrated the difference directly and showed why manual escaping is fragile.

**Task Evidence:**
> **Task 3:** [Injection drill notes and output](sql-notes.md#why-bound-parameters-stop-the-payload)
> - [Python demonstration](injection_demo.py)
