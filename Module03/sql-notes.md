## Pod Study

**Pod Members:**
* Sanjay Maheshwari (Workstream 3 - Plan Vocabulary)
* Sebastian Soon (Workstream 2 - Clause order)
* Isa Babayev (Guest - Workstream 1 - Algebra ↔ SQL)
* Myo Min Lin (Workstream 4 -  Tuning & security)

**My Part:(Workstream 2 - Clause Order)**

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
> Only the first query plan changed. A technician has a new index created, it is changing to SEARCH function instead of SCAN

## Task B: Algebra check

Group Task Completed on Sanjay's Portfolio: [here](https://github.com/yajnas-crpto/databases_portfolio_sanjay/blob/main/Module03/sql-notes.md)

For Task B, we need to make mathematical equation. For SELECT * FROM maint_job WHERE technician = 'Beier'; command, Logic and sequanece should be like this: sigma technician (because we select from WHERE? from technician) equals 'Beier' is text value and (maint\_job) means this means we are doing filtering to the main_job table
$\sigma_{technician='Beier'}(maint\_job)$

LLM Comparison: I asked Gemini to translate the same query. We completely agreed on using the selection operator ($\sigma$) for the WHERE clause. The only difference in our approach was a minor learning point: the LLM pointed out that the projection operator ($\pi$) is usually omitted entirely when the SQL query uses SELECT *.

### Task C: Explain & share with another pod
* **Plan Comparison**: Our Windows SQLite plan matched the macOS SQLite plan from the neighboring pod; both correctly used SEARCH for direct equality matches.   
* **The Index Surprise (Our Pod)**: Wrapping an indexed column in a function (like upper(technician)) entirely defeats the index, forcing a full SCAN.   
* **The Index Surprise (Neighboring Pod)**: Leading wildcards (LIKE '%ei%') also force a SCAN because the engine cannot use the B-tree's alphabetical sorting. Also, asking for unindexed columns breaks a "covering" index, forcing the engine to visit the main table.   
* **Unresolved Question for Discord**: If functions and wildcards break indexes, how do we efficiently optimize case-insensitive searches or partial text matches in SQLite? 

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

- I predicted customer_id and order_id lookups will be SEARCH. I was correct for for c and o, because both are looked up by INTEGER PRIMARY KEY, but ol.order_id has no index, so order_line is the one that gets SCAN.

- I predicted city and qty will use SCAN, however as city and qty are columns, not plan lines. 
(nothing about product or temp B-trees)	SEARCH p and three USE TEMP B-TREE lines were missing

The main correction: In SQLite, the query plan centers on scanning `order_line` (`ol`) because its foreign keys allow direct primary key lookups (`SEARCH`) on `o`, `c`, and `p`, whereas starting from `customer` would force an unindexed scan for orders.

### Task 2: Index benchmark

Inser optimized query here: (Screenshot)
``` sql
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
```
--------------------------------------------------------------------------------
-- BASELINE (No Indexes)
--------------------------------------------------------------------------------
```
-- Run 1: 0.010578
-- Run 2: 0.010451
-- Run 3: 0.008337
```
**Mediant Time:** 0.010451
```
QUERY PLAN
|--SCAN ol
|--SEARCH o USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH p USING INTEGER PRIMARY KEY (rowid=?)
|--USE TEMP B-TREE FOR GROUP BY
|--USE TEMP B-TREE FOR count(DISTINCT)
`--USE TEMP B-TREE FOR ORDER BY
```
--------------------------------------------------------------------------------
-- TEST 1: Add Date Index
--------------------------------------------------------------------------------
``` sql
CREATE INDEX ix_orders_ordered_on ON orders(ordered_on);
```
```
-- Run 1: 0.006315
-- Run 2: 0.007317
-- Run 3: 0.006744
```
**Mediant Time:** 0.006744
```
QUERY PLAN
|--SCAN ol
|--SEARCH o USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH p USING INTEGER PRIMARY KEY (rowid=?)
|--USE TEMP B-TREE FOR GROUP BY
|--USE TEMP B-TREE FOR count(DISTINCT)
`--USE TEMP B-TREE FOR ORDER BY
```
--------------------------------------------------------------------------------
-- TEST 2: Add Order Line Join Index
--------------------------------------------------------------------------------
``` sql
CREATE INDEX ix_orderline_order ON order_line(order_id);
```
```
-- Run 1: 0.028166
-- Run 2: 0.009181
-- Run 3: 0.009787
```

Median time: 0.009787
```
QUERY PLAN
|--SEARCH o USING INDEX ix_orders_ordered_on (ordered_on>? AND ordered_on<?)
|--SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH ol USING INDEX ix_orderline_order (order_id=?)
|--SEARCH p USING INTEGER PRIMARY KEY (rowid=?)
|--USE TEMP B-TREE FOR GROUP BY
|--USE TEMP B-TREE FOR count(DISTINCT)
`--USE TEMP B-TREE FOR ORDER BY
```
--------------------------------------------------------------------------------
-- TEST 3: Add Product Index
--------------------------------------------------------------------------------
``` sql
CREATE INDEX ix_orderline_product ON order_line(product_id);
```
```
-- Run 1: 0.013219
-- Run 2: 0.010304
-- Run 3: 0.009535
```
Median Time: 0.010304
```
QUERY PLAN
|--SEARCH o USING INDEX ix_orders_ordered_on (ordered_on>? AND ordered_on<?)
|--SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH ol USING INDEX ix_orderline_order (order_id=?)
|--SEARCH p USING INTEGER PRIMARY KEY (rowid=?)
|--USE TEMP B-TREE FOR GROUP BY
|--USE TEMP B-TREE FOR count(DISTINCT)
`--USE TEMP B-TREE FOR ORDER BY
```

Test 1: Plan unchanged, but execution time dropped
Observation: The plan remained identical (SCAN ol first), yet median execution time dropped from 10.45 ms to 6.74 ms.
Why this happened: The index ix_orders_ordered_on was not used by SQLite because scanning order_line sequentially was cheaper than probing an index for date filtering. The time speedup here is a classic measurement artifact (file cache warming across successive runs during the session).

Test 2: Plan flipped completely
Observation: Adding ix_orderline_order caused SQLite to change its outer table driving the join.
Plan Shift: Instead of SCAN ol, it switched to SEARCH o USING INDEX ix_orders_ordered_on first, followed by SEARCH ol USING INDEX ix_orderline_order.
Performance Impact: The time shifted to 9.79 ms. Because ix_orderline_order existed, SQLite could now filter orders by date first and hop into order_line by order_id.

Test 3: Zero impact on plan or performance
Observation: The plan for Test 3 is identical to Test 2, and the execution time (10.30 ms) is virtually identical to Test 2 (9.79 ms).
Why this happened: ix_orderline_product is dead weight for this query. The query joins p.product_id = ol.product_id. Lookups go from order_line $\rightarrow$ product (using product's Primary Key). Searching order_line by product_id was never required.

--------------------------------------------------------------------------------
-- STEP 4A: Single-Day Lookup WITHOUT Indexes (Baseline)
--------------------------------------------------------------------------------
``` sql
EXPLAIN QUERY PLAN
SELECT c.city, COUNT(DISTINCT c.customer_id) AS customers, SUM(ol.qty * p.price) AS revenue
FROM customer c JOIN orders o ON o.customer_id = c.customer_id
JOIN order_line ol ON ol.order_id = o.order_id JOIN product p ON p.product_id = ol.product_id
WHERE o.ordered_on >= '2025-06-01' AND o.ordered_on < '2025-06-02'
GROUP BY c.city ORDER BY revenue DESC;
```

-- Run 1000x Amortized Loop:
``` sql
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
```

**Time:** 38.665294/1000 = 0.038665294

--------------------------------------------------------------------------------
-- STEP 4B: Add ix_orders_ordered_on
--------------------------------------------------------------------------------
``` sql
CREATE INDEX ix_orders_ordered_on ON orders(ordered_on);
```
**Time:** 0.871637/1000 = 0.0008716

Key Takeaways & Contrast with Step 3
Massive Efficiency Gain:

For the full-year query in Step 3, filtering by date covered a huge portion of the dataset (~240k rows), so probing an index didn't yield huge gains.

For the single-day query, filtering ordered_on >= '2025-06-01' AND ordered_on < '2025-06-02' targets a tiny fraction of total orders. The index allows SQLite to jump straight to those few matching records via B-Tree lookup rather than scanning all orders.

The Amortization Advantage:

At 0.87 ms per execution, measuring a single run directly with .timer on would have landed right at the resolution floor of SQLite's timer (~1 ms), leading to noisy and unreliable numbers. Batching 1,000 runs brought total execution time to ~872 ms, giving a crystal-clear, accurate signal.

Core Takeaway for the Lab:

Selective filters love indexes: When a WHERE clause reduces the target dataset to a small fraction (e.g., 1 day out of 365), an index like ix_orders_ordered_on dramatically cuts down read operations.

Broad aggregations benefit less: When a query processes a large chunk of the entire dataset, sequential scans often perform similarly to or better than index lookups due to random I/O overhead.

Summary of Results

Selectivity (Step 3): Scanning a large fraction of a table sequentially is often as fast as or faster than index lookups because B-Tree traversal adds non-sequential memory/disk overhead.High Selectivity (Step 4): When a WHERE clause filters down to a small slice of data (a single day out of a full year), an index eliminates full-table scans and yields dramatic speedups (~44x).Query Plan Changes $\neq$ Guaranteed SpeedupAn index changing a plan from SCAN to SEARCH proves the query planner is using the index, but it does not guarantee a performance win. Always verify plan changes with timing measurements.Dead Weight Indexesix_orderline_product provided zero benefit to either query because primary key lookups on product(product_id) were already handled by SQLite's internal PK index. Unnecessary indexes should be dropped to avoid write overhead during INSERT/UPDATE operations.Measurement AccuracySub-millisecond queries (like Step 4) fall below standard timer resolution limits ($\sim 1\text{ ms}$). Amortizing across 1,000 runs isolates real performance gains from system noise.

### Task 3: The Injection Drill

Insert python file here

**Output:**
```
normal   : [(1, 'Customer 1')]
injected : [(1, 'Customer 1'), (2, 'Customer 2'), (3, 'Customer 3')] ...
safe     : []
```

**Payload used:** ' OR '1'='1

Answer:
Escaping or filtering ` characters by hand is not a real fix as it only fixes the texts in quotation marks scenario for example O'Brien becomes O''Brien which fixes the carsh but only for this instance, escaping rules may not apply to different databases which leaves it vulnerable to attacks in another set up. 

It is also exposed to other contexts, for example if it is searching in columns with identifiers which follow a different set of rules, as well as a numeric contets which do not contain an apostrophe. 

Hand-escaping means checking every outside value that goes into a query and applying the correct escaping rule for its context and database, to stop it from breaking the query or being read as SQL. It’s fragile because one missed or wrong rule creates a hole, whereas bound parameters keep data and code separate automatically.

### Task 4: One query, from algebra to plan

**Original Query:**
``` sql
SELECT o.order_id, o.ordered_on, c.name
FROM orders o JOIN customer c ON c.customer_id = o.customer_id
WHERE o.ordered_on = '2026-02-14';
```

**Relational Algebra Expression:**
```
π order_id, ordered_on, name (
  σ ordered_on = '2026-02-14' (O)  ⋈ O.customer_id = C.customer_id  C
)
```
π reprersents the columns
σ represents the WHERE
⋈ represents the JOIN

### Task 5: Window functions and a subquery rewrite

**Original Query:**
``` sql
SELECT c.customer_id, c.name, COUNT(*) AS late_orders
FROM orders o
JOIN customer c ON c.customer_id = o.customer_id
WHERE o.status = 'late'
GROUP BY c.customer_id, c.name
ORDER BY late_orders DESC;
```

**Result:**
```
QUERY PLAN
|--SCAN o
|--SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
|--USE TEMP B-TREE FOR GROUP BY
`--USE TEMP B-TREE FOR ORDER BY
```

**LLM Rewritten with correlated subquery:**
``` sql
SELECT 
    c.customer_id, 
    c.name, 
    (
        SELECT COUNT(*) 
        FROM orders o 
        WHERE o.customer_id = c.customer_id 
          AND o.status = 'late'
    ) AS late_orders
FROM customer c
WHERE (
    SELECT COUNT(*) 
    FROM orders o 
    WHERE o.customer_id = c.customer_id 
      AND o.status = 'late'
) > 0
ORDER BY late_orders DESC; 
```
**Result:**
```
QUERY PLAN
|--SCAN c
|--CORRELATED SCALAR SUBQUERY 2
|  `--SCAN o
|--CORRELATED SCALAR SUBQUERY 1
|  `--SCAN o
`--USE TEMP B-TREE FOR ORDER BY
```

**LLM Rewritten with window function:**
``` sql
SELECT DISTINCT
    c.customer_id,
    c.name,
    COUNT(*) OVER (PARTITION BY c.customer_id) AS late_orders
FROM customer c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'late'
ORDER BY late_orders DESC;
```

```
QUERY PLAN
|--CO-ROUTINE (subquery-2)
|  |--CO-ROUTINE (subquery-3)
|  |  |--SCAN o
|  |  |--SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
|  |  `--USE TEMP B-TREE FOR ORDER BY
|  `--SCAN (subquery-3)
|--SCAN (subquery-2)
|--USE TEMP B-TREE FOR DISTINCT
`--USE TEMP B-TREE FOR ORDER BY
```
When prompted to perform simple aggregation or summary grouping across joined tables without specific structural constraints, LLMs default to the standard GROUP BY with an aggregate function (COUNT(*)) as the primary solution.

Reasoning: GROUP BY represents the idiomatic SQL pattern for relational aggregation, produces the cleanest query plan, and forms the core training baseline for SQL summary reports.

## Reflection 3
[Reflection 3](/Reflections/ref03.md)


