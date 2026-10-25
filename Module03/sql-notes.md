## Task A

Our predictions: 
```
SELECT * FROM maint_job WHERE technician = 'Beier';
```
We predicted SCAN
**Result:**  
```
QUERY PLAN
`--SCAN maint_job
```
```
SELECT * FROM machine WHERE machine_name = 'cnc-02';
```
We predicted SCAN
**Result**:
```
QUERY PLAN
`--SCAN machine
```
```
SELECT * FROM maint_job WHERE technician LIKE '%ei%';
```
We predicted SEARCH
**Result:**
```
QUERY PLAN
`--SCAN maint_job
```

After adding the index: CREATE INDEX ix_job_tech ON maint_job(technician);<br>
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
Only the first query plan changed. A technician has a new index created, it is changing to SEARCH function instead of SCAN.


## Task B

Group tasks done on Sanjay's Github: 
[Module03 Group Tasks](https://github.com/yajnas-crpto/databases_portfolio_sanjay/blob/main/Module03/sql-notes.md)


## Task 1: Ask LLM, then check the plan

customer(customer_id, name city)

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
## Task A

Our predictions: 

SELECT * FROM maint_job WHERE technician = 'Beier';
We predicted SCAN
**Result:**  
QUERY PLAN
`--SCAN maint_job

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

After adding the index:

**Result 1:**
QUERY PLAN
`--SEARCH maint_job USING INDEX ix_job_tech (technician=?)

**Result 2:**
QUERY PLAN
`--SCAN machine

**Result 3:**
QUERY PLAN
`--SCAN maint_job

Only the first query plan changed. A technician has a new index created, it is changing ti SEARCH function instead of SCAN

## Task ...

This task was executed by my partner. The implementation was about ... 
It is [here](https://github.com/partner/iot-portfolio/Module02/Readme.md#task-2).

## Reflection 2
[Reflection 2](/Reflections/ref02.md)

## Task ...

...

If the module is longer than 1 week, you might have several reflections within it. If not, delete this and the following.

## Reflection 3
[Reflection 3](/Reflections/ref03.md)


