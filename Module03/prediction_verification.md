## Task 1: Ask the LLM, then check the plan

> "SQLite schema: customer(customer_id, name, city), product(product_id, sku, price), orders(order_id, customer_id, ordered_on, status), order_line(order_id, product_id, qty). Write a query that returns, for each city, the number of distinct customers and the total revenue (sum of qty*price) of orders placed in 2025, ordered by revenue descending."

**My prediction:**
- Customer_id will be index so it will be `SEARCH`, same for the order_id
- For the city it will use `SCAN` and qty as well

Insert Claude Response here: (Screenshot)

Insert query result here: (Screenshot)

- My prediction was correct for for c and o, because both are looked up by `INTEGER` PRIMARY KEY, but ol.order_id has no index, so order_line is the one that gets `SCAN`.

- My prediction was wrong as city and qty are columns, not plan lines. (nothing about product or temp B-trees)	SEARCH p and three USE TEMP B-TREE lines were missing

**The main correction:** In SQLite, the query plan centers on scanning `order_line` (`ol`) because its foreign keys allow direct primary key lookups (`SEARCH`) on `o`, `c`, and `p`, whereas starting from `customer` would force an unindexed scan for orders.