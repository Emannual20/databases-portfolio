
# Module 3

This module gives you the opportunity to explore complex querying and query optimization and achieve competency in writing, profiling, and securing SQL.

By the end of this module, you can:

1. Build complex DQL queries: joins, aggregation with GROUP BY/HAVING, subqueries, and window functions.
2. Read EXPLAIN QUERY PLAN as primary evidence: say what the engine will do for a given query, tell a SCAN from a SEARCH, and a table lookup from a covering index.
3. Benchmark the effect of an index and explain when the planner ignores one.
4. Generate a query with an LLM, then verify it: correctness, performance, and edge cases.
5. Prevent SQL injection with bound parameters and demonstrate why string concatenation is exploitable.

Pod Study"

My Part: Clause Order

Written Order (Syntax) means the strict sequence we must write SQL query in the editor, or else a syntax eror will be thrown.

Logial Execution Order: <br>
  Clause:<br>
1) FROM & JOIN (Identifies the base tabls and joins them rtogether in a working virtual dataset)
2) WHERE (Filters individual raw rows based on conditions, e.g. "WHERE role = 'Butcher')
3) GROUP BY (Groups the remaining filtered rows into categroeis/buckets based on shared values)
4) HAVING (Filers grouped/aggregated buckets)
5) SELECT (Computes final expressions, evaluates functions and applies column aliases)
6) DISTINCT  

## Task A: Plan safari

Our predictions: 

SELECT * FROM maint_job WHERE technician = 'Beier';
We predicted SCAN
**Result:**  
```
QUERY PLAN
`--SCAN maint_job
```

SELECT * FROM machine WHERE machine_name = 'cnc-02';
We predicted SCAN
**Result**:
QUERY PLAN
`--SCAN machine

SELECT * FROM maint_job WHERE technician LIKE '%ei%';
We predicted SEARCH
**Result:**
QUERY PLAN
`--SCAN maint_job

> After adding the index:

**Result 1:**
```
QUERY PLAN
`--SEARCH maint_job USING INDEX ix_job_tech (technician=?)
```

**Result 2:**
```
QUERY PLAN
`--SCAN machine
```
**Result 3:**
```
QUERY PLAN
`--SCAN maint_job
```

Only the first query plan changed. A technician has a new index created, it is changing to SEARCH function instead of SCAN

## Task B: Algebra check

Group Task Completed on Sanjay's Portfolio: [here](https://github.com/yajnas-crpto/databases_portfolio_sanjay/blob/main/Module03/sql-notes.md)

For Task B, we need to make mathematical equation. For SELECT * FROM maint_job WHERE technician = 'Beier'; command, Logic and sequanece should be like this: sigma technician (because we select from WHERE? from technician) equals 'Beier' is text value and (maint\_job) means this means we are doing filtering to the main_job table
$\sigma_{technician='Beier'}(maint\_job)$

LLM Comparison: I asked Gemini to translate the same query. We completely agreed on using the selection operator ($\sigma$) for the WHERE clause. The only difference in our approach was a minor learning point: the LLM pointed out that the projection operator ($\pi$) is usually omitted entirely when the SQL query uses SELECT *.

Task C: Explain & share with another pod

Studio Lab: Generate, Profile and Secure 

The five marked lines

The note says each of these could be asked at your checkpoint, so try the experiments yourself first, then compare with these answers.

1. Where do 240,000 rows come from? From the recursive CTE, which generates the numbers instead of reading them from a table. It starts with one row (SELECT 1), then repeatedly adds a row with x+1, and stops when WHERE x < 240000 is false. n is a virtual table that exists only for that one statement, and the SELECT turns each x into a row of real data.

2. What if the query returns zero rows? Changing x <= 2000 to x <= 0 makes the SELECT return nothing (I confirmed the count is 0). The INSERT then inserts nothing, with no error. You’d have an empty customer table, and the later orders would silently point to customers that don’t exist, the same kind of orphan as defect 1 in your legacy data.

3. What guarantees the customer exists? Nothing in the schema. It holds only by construction: (x % 2000) + 1 always lands between 1 and 2000, and the customers are numbered 1 to 2000. I checked that: the range is 1 to 2000, with 0 orphans. If someone changed 2000 customers to 1000, orphans would appear with no warning. A FOREIGN KEY (Module 4) makes the database enforce it.

4. Why build the date modifier with ||? SQLite’s date modifiers are text strings like '+17 days', so the number has to be glued into a string: '+' joined with (x % 540) joined with ' days'. At x = 540, 540 % 540 is 0, so the modifier is '+0 days' and the date is 2025-01-01 again. The dates cycle every 540 days, from 2025-01-01 to 2026-06-24 (the maximum offset is 539).

5. What does printf('%05d', x) buy you? Zero-padding makes text sort in numeric order. I sorted four values both ways:

## Task ...

...

If the module is longer than 1 week, you might have several reflections within it. If not, delete this and the following.

## Reflection 3
[Reflection 3](/Reflections/ref03.md)


