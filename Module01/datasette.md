1. Base URL: http://127.0.0.1:8001/telemetry/readings

2. 57,600 rows where machine = "cnc-01" sorted by rowid: http://127.0.0.1:8001/telemetry/readings?_sort=rowid&machine__exact=cnc-01

Facet By temperature where machine = "cnc-01": http://127.0.0.1:8001/telemetry/readings?machine__exact=cnc-01&_sort=rowid&_facet=temp_c

**Page Result:**<br>
```
temp_c >30 ✖

44.52 126
44.26 121
44.67 120
44.76 120
44.35 119
44.36 118 
...
```

Query: http://127.0.0.1:8001/telemetry?sql=SELECT+machine%2C%0D%0A+++++++COUNT%28*%29+AS+n%2C%0D%0A+++++++MAX%28vib_rms%29+AS+peak_vib%2C%0D%0A+++++++SUM%28vib_rms+%3E+2.0%29+AS+alarms%0D%0AFROM+readings%0D%0AGROUP+BY+machine%3B <br>

CSV File: (Insert telemetry csv file here) <br>
Json File: (Insert telemetry json file here) <br>

(databases-portfolio) PS C:\Users\gamer\databases-portfolio> curl.exe "http://127.0.0.1:8001/telemetry/readings.json?_size=5"
{"database": "telemetry", "table": "readings", "is_view": false, "human_description_en": "", "rows": [[1, "2026-01-05 06:00:00", "cnc-01", 41.91, 1.186, 59.7], [2, "2026-01-05 06:00:00", "cnc-02", 42.42, 1.125, 54.3], [3, "2026-01-05 06:00:00", "cnc-03", 41.87, 1.209, 60.7], [4, "2026-01-05 06:00:03", "cnc-01", 42.7, 1.241, 64.2], [5, "2026-01-05 06:00:03", "cnc-02", 42.15, 1.309, 60.2]], "truncated": false, "filtered_table_rows_count": 172800, "expanded_columns": [], "expandable_columns": [], "columns": ["rowid", "ts", "machine", "temp_c", "vib_rms", "spindle_load"], "primary_keys": [], "units": {}, "query": {"sql": "select rowid, ts, machine, temp_c, vib_rms, spindle_load from readings order by rowid limit 6", "params": {}}, "facet_results": {}, "suggested_facets": [{"name": "ts", "type": "date", "toggle_url": "http://127.0.0.1:8001/telemetry/readings.json?_size=5&_facet_date=ts"}], "next": "5", "next_url": "http://127.0.0.1:8001/telemetry/readings.json?_size=5&_next=5", "private": false, "allow_execute_sql": true, "query_ms": 668.4970000005706}


