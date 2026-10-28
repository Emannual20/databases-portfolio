
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

### Task C: Explain & share with another pod

Studio Lab: Generate, Profile and Secure 

1. Where do 240,000 rows come from? From the recursive CTE, which generates the numbers instead of reading them from a table. It starts with one row (SELECT 1), then repeatedly adds a row with x+1, and stops when WHERE x < 240000 is false. n is a virtual table that exists only for that one statement, and the SELECT turns each x into a row of real data.

2. What if the query returns zero rows? Changing x <= 2000 to x <= 0 makes the SELECT return nothing (I confirmed the count is 0). The INSERT then inserts nothing, with no error. You’d have an empty customer table, and the later orders would silently point to customers that don’t exist, the same kind of orphan as defect 1 in your legacy data.

3. What guarantees the customer exists? Nothing in the schema. It holds only by construction: (x % 2000) + 1 always lands between 1 and 2000, and the customers are numbered 1 to 2000. I checked that: the range is 1 to 2000, with 0 orphans. If someone changed 2000 customers to 1000, orphans would appear with no warning. A FOREIGN KEY (Module 4) makes the database enforce it.

4. Why build the date modifier with ||? SQLite’s date modifiers are text strings like '+17 days', so the number has to be glued into a string: '+' joined with (x % 540) joined with ' days'. At x = 540, 540 % 540 is 0, so the modifier is '+0 days' and the date is 2025-01-01 again. The dates cycle every 540 days, from 2025-01-01 to 2026-06-24 (the maximum offset is 539).

5. What does printf('%05d', x) buy you? Zero-padding makes text sort in numeric order. I sorted four values both ways:

## Task 1: Ask the LLM, then check the plan

"SQLite schema: customer(customer_id, name, city), product(product_id, sku, price), orders(order_id, customer_id, ordered_on, status), order_line(order_id, product_id, qty). Write a query that returns, for each city, the number of distinct customers and the total revenue (sum of qty*price) of orders placed in 2025, ordered by revenue descending."

**My prediction:**
- Customer_id will be index so it will be SEARCh, same for the order_id
- For the city it will use SCAN and qty 

Insert Claude Response here: (Screenshot)

Insert query result here: (Screenshot)

I predicted Customer and order lookups will be SEARCH	Right for c and o, because both are looked up by INTEGER PRIMARY KEY
“Same for the order_id”	Half right. o.order_id is a primary key (SEARCH o), but ol.order_id has no index, so order_line is the one that gets SCAN

I predicted “City will use SCAN", however that is not how plans work. City is a column, and a plan line is about a table
qty	Same issue: a column, not a plan line
(nothing about product or temp B-trees)	SEARCH p and three USE TEMP B-TREE lines were missing

The main correction: each plan line describes how SQLite reaches one table (using the alias from the query: ol, o, c, p). Columns like city and qty don’t get their own lines. Ask “which tables, and how is each reached?” Then list the extra sorting steps separately.

Why order_line is the one scanned: it’s the only table from which every other table can be reached through a primary key. Starting at customer would mean finding its orders by orders.customer_id, which has no index.

### Task 2: Index benchmark

Inser optimized query here: (Screenshot)

.timer on

-- 0. RESET STATE
DROP INDEX IF EXISTS ix_orders_ordered_on;
DROP INDEX IF EXISTS ix_orderline_order;
DROP INDEX IF EXISTS ix_orderline_product;

--------------------------------------------------------------------------------
-- BASELINE (No Indexes)
--------------------------------------------------------------------------------
EXPLAIN QUERY PLAN
SELECT c.city,
       COUNT(DISTINCT c.customer_id) AS customers,
       SUM(ol.qty * p.price)          AS revenue
FROM customer   AS c
JOIN orders     AS o  ON o.customer_id = c.customer_id
JOIN order_line AS ol ON ol.order_id    = o.order_id
JOIN product    AS p  ON p.product_id  = ol.product_id
WHERE o.ordered_on >= '2025-01-01'
  AND o.ordered_on <  '2026-01-01'
GROUP BY c.city
ORDER BY revenue DESC;

-- Run 1: 0.010578
-- Run 2: 0.010451
-- Run 3: 0.008337

Mediant Time: 0.010451
Plan:
QUERY PLAN
|--SCAN ol
|--SEARCH o USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH p USING INTEGER PRIMARY KEY (rowid=?)
|--USE TEMP B-TREE FOR GROUP BY
|--USE TEMP B-TREE FOR count(DISTINCT)
`--USE TEMP B-TREE FOR ORDER BY

--------------------------------------------------------------------------------
-- TEST 1: Add Date Index
--------------------------------------------------------------------------------
CREATE INDEX ix_orders_ordered_on ON orders(ordered_on);

-- Run 1: 0.006315
-- Run 2: 0.007317
-- Run 3: 0.006744

Mediant Time: 0.006744
Plan:
QUERY PLAN
|--SCAN ol
|--SEARCH o USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH p USING INTEGER PRIMARY KEY (rowid=?)
|--USE TEMP B-TREE FOR GROUP BY
|--USE TEMP B-TREE FOR count(DISTINCT)
`--USE TEMP B-TREE FOR ORDER BY

--------------------------------------------------------------------------------
-- TEST 2: Add Order Line Join Index
--------------------------------------------------------------------------------
CREATE INDEX ix_orderline_order ON order_line(order_id);

-- Run 1: 0.028166
-- Run 2: 0.009181
-- Run 3: 0.009787

Median time: 0.009787
-- Plan:
QUERY PLAN
|--SEARCH o USING INDEX ix_orders_ordered_on (ordered_on>? AND ordered_on<?)
|--SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH ol USING INDEX ix_orderline_order (order_id=?)
|--SEARCH p USING INTEGER PRIMARY KEY (rowid=?)
|--USE TEMP B-TREE FOR GROUP BY
|--USE TEMP B-TREE FOR count(DISTINCT)
`--USE TEMP B-TREE FOR ORDER BY


--------------------------------------------------------------------------------
-- TEST 3: Add Product Index
--------------------------------------------------------------------------------
CREATE INDEX ix_orderline_product ON order_line(product_id);

-- Run 1: 0.013219
-- Run 2: 0.010304
-- Run 3: 0.009535
Median Time: 0.010304

Plan:
QUERY PLAN
|--SEARCH o USING INDEX ix_orders_ordered_on (ordered_on>? AND ordered_on<?)
|--SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH ol USING INDEX ix_orderline_order (order_id=?)
|--SEARCH p USING INTEGER PRIMARY KEY (rowid=?)
|--USE TEMP B-TREE FOR GROUP BY
|--USE TEMP B-TREE FOR count(DISTINCT)
`--USE TEMP B-TREE FOR ORDER BY

Key Takeaways from Your Data1. 
Test 1: Plan unchanged, but execution time droppedObservation: The plan remained identical (SCAN ol first), yet median execution time dropped from 10.45 ms to 6.74 ms.Why this happened: The index ix_orders_ordered_on was not used by SQLite because scanning order_line sequentially was cheaper than probing an index for date filtering. The time speedup here is a classic measurement artifact (file cache warming across successive runs during the session).

Test 2: Plan flipped completelyObservation: Adding ix_orderline_order caused SQLite to change its outer table driving the join.Plan Shift: Instead of SCAN ol, it switched to SEARCH o USING INDEX ix_orders_ordered_on first, followed by SEARCH ol USING INDEX ix_orderline_order.Performance Impact: The time shifted to 9.79 ms. Because ix_orderline_order existed, SQLite could now filter orders by date first and hop into order_line by order_id.

Test 3: Zero impact on plan or performanceObservation: The plan for Test 3 is identical to Test 2, and the execution time (10.30 ms) is virtually identical to Test 2 (9.79 ms).Why this happened: ix_orderline_product is dead weight for this query. The query joins p.product_id = ol.product_id. Lookups go from order_line $\rightarrow$ product (using product's Primary Key). Searching order_line by product_id was never required.

.timer on

-- Clean setup: reset indexes to test state
DROP INDEX IF EXISTS ix_orders_ordered_on;
DROP INDEX IF EXISTS ix_orderline_order;
DROP INDEX IF EXISTS ix_orderline_product;

--------------------------------------------------------------------------------
-- STEP 4A: Single-Day Lookup WITHOUT Indexes (Baseline)
--------------------------------------------------------------------------------
EXPLAIN QUERY PLAN
SELECT c.city, COUNT(DISTINCT c.customer_id) AS customers, SUM(ol.qty * p.price) AS revenue
FROM customer c JOIN orders o ON o.customer_id = c.customer_id
JOIN order_line ol ON ol.order_id = o.order_id JOIN product p ON p.product_id = ol.product_id
WHERE o.ordered_on >= '2025-06-01' AND o.ordered_on < '2025-06-02'
GROUP BY c.city ORDER BY revenue DESC;

-- Run 1000x Amortized Loop:
WITH RECURSIVE cnt(x) AS (
  SELECT 1
  UNION ALL
  SELECT x + 1 FROM cnt WHERE x < 1000
)
SELECT COUNT(*) FROM (
  SELECT cnt.x, c.city, COUNT(DISTINCT c.customer_id) AS customers, SUM(ol.qty * p.price) AS revenue
  FROM cnt
  CROSS JOIN customer c
  JOIN orders o ON o.customer_id = c.customer_id
  JOIN order_line ol ON ol.order_id = o.order_id
  JOIN product p ON p.product_id = ol.product_id
  WHERE o.ordered_on >= '2025-06-01' AND o.ordered_on < '2025-06-02'
  GROUP BY cnt.x, c.city
);

time: 38.665294/1000 = 0.038665294

--------------------------------------------------------------------------------
-- STEP 4B: Add ix_orders_ordered_on
--------------------------------------------------------------------------------
CREATE INDEX ix_orders_ordered_on ON orders(ordered_on);

time: 0.871637/1000 = 0.0008716

-- Run 1000x Amortized Loop again and record total time / 1000

Key Takeaways & Contrast with Step 3
Massive Efficiency Gain:

For the full-year query in Step 3, filtering by date covered a huge portion of the dataset (~240k rows), so probing an index didn't yield huge gains.

For the single-day query, filtering ordered_on >= '2025-06-01' AND ordered_on < '2025-06-02' targets a tiny fraction of total orders. The index allows SQLite to jump straight to those few matching records via B-Tree lookup rather than scanning all orders.

The Amortization Advantage:

At 0.87 ms per execution, measuring a single run directly with .timer on would have landed right at the resolution floor of SQLite's timer (~1 ms), leading to noisy and unreliable numbers. Batching 1,000 runs brought total execution time to ~872 ms, giving a crystal-clear, accurate signal.

Core Takeaway for the Lab:

Selective filters love indexes: When a WHERE clause reduces the target dataset to a small fraction (e.g., 1 day out of 365), an index like ix_orders_ordered_on dramatically cuts down read operations.

Broad aggregations benefit less: When a query processes a large chunk of the entire dataset, sequential scans often perform similarly to or better than index lookups due to random I/O overhead.

Summary of ResultsQuery WorkloadBaseline TimeBest Index / StrategyBest TimeSpeedupKey MechanismStep 3: Full-Year Dashboard (~240k rows)10.45 msix_orders_ordered_on6.74 ms~1.5xBroad range scan; table scanning is already near-optimal due to sequential I/O.Step 4: Single-Day Lookup (< 1% of data)38.67 msix_orders_ordered_on0.87 ms~44.4xHigh selectivity; B-Tree search skips >99% of unneeded rows instantly.Core Engineering TakeawaysSelectivity Dictates Index ValueLow Selectivity (Step 3): Scanning a large fraction of a table sequentially is often as fast as or faster than index lookups because B-Tree traversal adds non-sequential memory/disk overhead.High Selectivity (Step 4): When a WHERE clause filters down to a small slice of data (a single day out of a full year), an index eliminates full-table scans and yields dramatic speedups (~44x).Query Plan Changes $\neq$ Guaranteed SpeedupAn index changing a plan from SCAN to SEARCH proves the query planner is using the index, but it does not guarantee a performance win. Always verify plan changes with timing measurements.Dead Weight Indexesix_orderline_product provided zero benefit to either query because primary key lookups on product(product_id) were already handled by SQLite's internal PK index. Unnecessary indexes should be dropped to avoid write overhead during INSERT/UPDATE operations.Measurement AccuracySub-millisecond queries (like Step 4) fall below standard timer resolution limits ($\sim 1\text{ ms}$). Amortizing across 1,000 runs isolates real performance gains from system noise.

### Task 3: The Injection Drill

Insert python file here

**Output:**
```
normal   : [(1, 'Customer 1')]
injected : [(1, 'Customer 1'), (2, 'Customer 2'), (3, 'Customer 3')] ...
safe     : []
```



## Reflection 3
[Reflection 3](/Reflections/ref03.md)


