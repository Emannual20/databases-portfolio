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
