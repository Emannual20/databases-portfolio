# Module 3

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


SELECT * FROM machine WHERE machine_name = 'cnc-02';
We predicted SCAN

SELECT * FROM maint_job WHERE technician LIKE '%ei%';
We predicted SEARCH


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


