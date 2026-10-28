### Task 2: Index benchmark

Insert optimized query here: (Screenshot)
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

**BASELINE (No Indexes)**
- Run 1: 0.010578
- Run 2: 0.010451
- Run 3: 0.008337 <br>
**Median Time:** 0.010451s
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

**TEST 1: Add Date Index**

``` sql
CREATE INDEX ix_orders_ordered_on ON orders(ordered_on);
```
- Run 1: 0.006315
- Run 2: 0.007317
- Run 3: 0.006744<br>
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
**TEST 2: Add Order Line Join Index**
``` sql
CREATE INDEX ix_orderline_order ON order_line(order_id);
```

- Run 1: 0.028166
- Run 2: 0.009181
- Run 3: 0.009787<br>
**Median time:** 0.009787s
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
**TEST 3: Add Product Index**
``` sql
CREATE INDEX ix_orderline_product ON order_line(product_id);
```
- Run 1: 0.013219
- Run 2: 0.010304
- Run 3: 0.009535<br>
**Median Time:** 0.010304s
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

**Test 1 Observation:** The plan remained identical, yet median execution time dropped from 10.45 ms to 6.74 ms. As the index ix_orders_ordered_on was not used by SQLite because scanning order_line sequentially was cheaper than probing an index for date filtering. The time speedup here is file cache warming across successive runs during the session. <br>

**Test 2 Observation:** Adding ix_orderline_order caused SQLite to change its outer table driving the join. Instead of SCAN ol, it switched to SEARCH o USING INDEX ix_orders_ordered_on first, followed by SEARCH ol USING INDEX ix_orderline_order. Shifting time taken to 9.79 ms as ix_orderline_order existed, SQLite could now filter orders by date first and hop into order_line by order_id.<br>

**Test 3 Observation:** The plan for Test 3 is identical to Test 2, and the execution time (10.30 ms) is virtually identical to Test 2 (9.79 ms). As ix_orderline_product is dead weight for this query. The query joins p.product_id = ol.product_id. Lookups go from order_line $\rightarrow$ product (using product's Primary Key). Searching order_line by product_id was never required.<br>


**STEP 4: Single-Day Lookup WITHOUT Indexes (Baseline)**
``` sql
EXPLAIN QUERY PLAN
SELECT c.city, COUNT(DISTINCT c.customer_id) AS customers, SUM(ol.qty * p.price) AS revenue
FROM customer c JOIN orders o ON o.customer_id = c.customer_id
JOIN order_line ol ON ol.order_id = o.order_id JOIN product p ON p.product_id = ol.product_id
WHERE o.ordered_on >= '2025-06-01' AND o.ordered_on < '2025-06-02'
GROUP BY c.city ORDER BY revenue DESC;
```
**Run 1000x Amortized Loop:**
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

**Time:** 38.665294/1000 = 0.038665294s

**Adding Index:**
``` sql
CREATE INDEX ix_orders_ordered_on ON orders(ordered_on);
```
**Time:** 0.871637/1000 = 0.0008716s

**Key Takeaways:** <br>
For the single-day query, filtering ordered_on >= '2025-06-01' AND ordered_on < '2025-06-02' targets a tiny fraction of total orders. The index allows SQLite to jump straight to those few matching records via B-Tree lookup rather than scanning all orders.<br>

**The Amortization Advantage:**<br> 
At 0.87 ms per execution, measuring a single run directly with .timer on would have landed right at the resolution floor of SQLite's timer (~1 ms), leading to noisy and unreliable numbers. Batching 1,000 runs brought total execution time to ~872 ms, giving a crystal-clear, accurate signal. <br>

**Core Takeaway for the Lab:**<br>
Selective filters love indexes: When a WHERE clause reduces the target dataset to a small fraction (e.g., 1 day out of 365), an index like ix_orders_ordered_on dramatically cuts down read operations.

Broad aggregations benefit less: When a query processes a large chunk of the entire dataset, sequential scans often perform similarly to or better than index lookups due to random I/O overhead.

**Summary of Results**

Selectivity (Step 3): Scanning a large fraction of a table sequentially is often as fast as or faster than index lookups because B-Tree traversal adds non-sequential memory/disk overhead.High Selectivity (Step 4): When a WHERE clause filters down to a small slice of data (a single day out of a full year), an index eliminates full-table scans and yields dramatic speedups (~44x).Query Plan Changes $\neq$ Guaranteed SpeedupAn index changing a plan from SCAN to SEARCH proves the query planner is using the index, but it does not guarantee a performance win. Always verify plan changes with timing measurements.Dead Weight Indexesix_orderline_product provided zero benefit to either query because primary key lookups on product(product_id) were already handled by SQLite's internal PK index. Unnecessary indexes should be dropped to avoid write overhead during INSERT/UPDATE operations.Measurement AccuracySub-millisecond queries (like Step 4) fall below standard timer resolution limits ($\sim 1\text{ ms}$). Amortizing across 1,000 runs isolates real performance gains from system noise.