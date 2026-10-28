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