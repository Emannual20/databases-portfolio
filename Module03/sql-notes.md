## Pod Study

**Pod Members:**
* Sanjay Maheshwari (Workstream 3 - Plan Vocabulary)
* Sebastian Soon (Workstream 2 - Clause order)
* Isa Babayev (Guest - Workstream 1 - Algebra ↔ SQL)
* Myo Min Lin (Workstream 4 -  Tuning & security)

**My Part: (Workstream 2 - Clause Order)**

Written Order (Syntax) means the strict sequence we must write SQL query in the editor, or else a syntax eror will be thrown.

Logial Execution Order: <br>
  Clause:<br>
1) FROM & JOIN (Identifies the base tables and joins them together in a working virtual dataset)
2) WHERE (Filters individual raw rows based on conditions, e.g. "WHERE role = 'Butcher')
3) GROUP BY (Groups the remaining filtered rows into categories/buckets based on shared values)
4) HAVING (Filters grouped/aggregated buckets)
5) SELECT (Computes final expressions, evaluates functions and applies column aliases)
6) DISTINCT

## Task A: Plan safari
**Our predictions: SCAN**
``` sql
SELECT * FROM maint_job WHERE technician = 'Beier';
```
**Result:**  
```
QUERY PLAN
`--SCAN maint_job
```
**Our predictions: SCAN**
``` sql
SELECT * FROM machine WHERE machine_name = 'cnc-02';
```
**Result**:
```
QUERY PLAN
`--SCAN machine
```
**Our predictions: SEARCH**
``` sql
SELECT * FROM maint_job WHERE technician LIKE '%ei%';
```
**Result:**
```
QUERY PLAN
`--SCAN maint_job
```
**After adding the index:**

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

For Task B, we need to make mathematical equation. For `SELECT * FROM maint_job WHERE technician = 'Beier';` command, Logic and sequence should be: $\sigma$ technician (because we select from `WHERE?` from technician) equals 'Beier' is text value and (maint\_job) means this means we are doing filtering to the main_job table. <br>
$\sigma_{technician='Beier'}(maint\_job)$

LLM Comparison: We asked Gemini to translate the same query. We completely agreed on using the selection operator ($\sigma$) for the WHERE clause. The only difference in our approach was a minor learning point: the LLM pointed out that the projection operator ($\pi$) is usually omitted entirely when the SQL query uses `SELECT` *.

### Task C: Explain & share with another pod
* **Plan Comparison**: Our Windows SQLite plan matched the macOS SQLite plan from the neighboring pod; both correctly used `SEARCH` for direct equality matches.   
* **The Index Surprise (Our Pod)**: Wrapping an indexed column in a function (like upper(technician)) entirely defeats the index, forcing a full `SCAN`.   
* **The Index Surprise (Neighboring Pod)**: Leading wildcards (LIKE '%ei%') also force a `SCAN` because the engine cannot use the B-tree's alphabetical sorting. Also, asking for unindexed columns breaks a "covering" index, forcing the engine to visit the main table.   
* **Unresolved Question for Discord**: If functions and wildcards break indexes, how do we efficiently optimize case-insensitive searches or partial text matches in SQLite? 

### Studio Lab: Generate, Profile and Secure 

1. Where do 240,000 rows come from? From the recursive CTE, which generates the numbers instead of reading them from a table. It starts with one row (SELECT 1), then repeatedly adds a row with x+1, and stops when WHERE x < 240000 is false. n is a virtual table that exists only for that one statement, and the SELECT turns each x into a row of real data.

2. What if the query returns zero rows? Changing x <= 2000 to x <= 0 makes the SELECT return nothing (I confirmed the count is 0). The INSERT then inserts nothing, with no error. You’d have an empty customer table, and the later orders would silently point to customers that don’t exist, the same kind of orphan as defect 1 in your legacy data.

3. What guarantees the customer exists? Nothing in the schema. It holds only by construction: (x % 2000) + 1 always lands between 1 and 2000, and the customers are numbered 1 to 2000. I checked that: the range is 1 to 2000, with 0 orphans. If someone changed 2000 customers to 1000, orphans would appear with no warning. A FOREIGN KEY (Module 4) makes the database enforce it.

4. Why build the date modifier with ||? SQLite’s date modifiers are text strings like '+17 days', so the number has to be glued into a string: '+' joined with (x % 540) joined with ' days'. At x = 540, 540 % 540 is 0, so the modifier is '+0 days' and the date is 2025-01-01 again. The dates cycle every 540 days, from 2025-01-01 to 2026-06-24 (the maximum offset is 539).

5. What does printf('%05d', x) buy you? Zero-padding makes text sort in numeric order.


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
- π reprersents the columns
- σ represents the WHERE
- ⋈ represents the JOIN