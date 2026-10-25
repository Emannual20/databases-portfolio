# Module 1
By the end of this module, you can:

1. Explain how this class works — the CBL/PBL philosophy, the portfolio-based Kombinationsprüfung, and the "moving bar" of a first-time course.
2. Set up your personal GitHub portfolio from the course template, with a clean first commit and a .gitignore that keeps databases and secrets out of Git.
3. Set up the entire toolchain reproducibly with uv — one fixed Python plus SQLite, DuckDB, Datasette, and more — on Windows, macOS, or Linux, and verify it.
4. Explain — with a measurement, not a slide — the difference between an embedded database and a client/server database, and why most local apps should not run a server.
5. Load real rows into SQLite and query them from Python using bound parameters.
6. Take a first LLM-generated query, run it, and begin the habit that defines this course: verify before you trust.

## Task Inspirations

**1. How this class works**
The course is problem-based: I had to find answers and explanations myself, by reading documentation, asking an LLM, comparing against my team members (Sanjay, Jo Marie and Lin), and fixing my own mistakes. My portfolio (Task 1, 2 and 3) is the evidence so every task has visible proof, such as commands, outputs and screenshots.

**2. Personal GitHub portfolio and .gitignore**
Cloning the course template through the terminal, instead of GitHub Desktop, was the habit the later modules needed. The `.gitignore` taught me a practical lesson keeping databases and secrets our of Git. In Task 11: it blocked `.db` files, so I had to force-add `telemetry.db` to make it reachable by Datasette Lite. That showed me that keeping databases out of Git is a deliberate choice that can be overridden.

**3. Reproducible toolchain with uv**
`uv-check.py`, `pyproject.toml` and `uv.lock` pin one Python and the packages so that anyone can rebuild my setup. I used the same tool later with `uvx` to run Datasette and `sqlite-utils` without installing them permanently. (Tasks 3, 10, 11)

**4. Embedded vs. client/server, with a measurement**
Embedded server means a locally run on a machine, it keeps its own data locally. In Task 6 I measured instead of assuming: `telemetry.db` holds 172,800 rows in about 10 MB, queried with no server running. In Task 9, copying it with `.backup` gave the same 10,280 KB, which showed that the whole database is just one file.

**5. Loading rows into SQLite and querying them from Python**
I loaded the same CSV three ways: a Python loader using `?` placeholders for bound parameters, the `sqlite3` shell with `.import`, and `sqlite-utils insert`. Comparing them showed me the trade-off between keystrokes and control over the schema (for example, `sqlite-utils` left out the `NOT NULL` constraints). (Tasks 6, 9, 11)

**6. Verify before you trust an LLM query**
In Task 7, the model assumed "overnight" meant 18:00 to midnight, and running both versions showed different averages. Adding `OR time(ts) < '06:00:00'` fixed the definition. I also checked the query plan with `EXPLAIN QUERY PLAN`, and I tried to break the prompt on purpose, which showed me that the model catches invalid SQL but not vague wording. (Task 7)

## Task Personal Profile
My skills: Python, Object Oriented Programming, Some Basci micro controller knowledge<br>
Expectations: I expect to learn about databases, MYSQL, possibly docker if there is time

### Task 1: [My portfolio](https://github.com/Emannual20/databases-portfolio)

### Task 2:
My partners:
- Sanjay, [Sanjay portfolio link](https://github.com/yajnas-crpto/databases_portfolio_sanjay)
- Jo Marie, [Jo Marie portfolio link](https://github.com/jmanuel08/database-jomportfolio)
- Myomin Lin, [Myomin Lin portfolio link](https://github.com/mmlin801597/database-portfolio)

### Task 3:

UV Verififcation: [uv-check.py](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/uv-check.py)<br>
Committed PyProject: [Pyproject.toml](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/pyproject.toml)<br>
UV Lock: [uv.lock](https://github.com/Emannual20/databases-portfolio/blob/main/uv.lock)<br>

### Task 4: Which dot command I found most helpful
Shell Tour: [Shell-Tour.txt](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/shell-tour.txt)<br>
Tour: [Tour.sql](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/tour.sql)<br>

Which dot command did you find the most helpful?<br>
I found the .help command the most helpful as it showed me all the commands i needed to use. And I also found .schema reading helpful as it allows me to directly read from the database in the command prompt, to verify the data inside.

>**Dificulties faced :** 
> The first run, my shell-tour.txt file would not have the right output and my SQL shell had gotten stuck. By troubleshooting with Claude, I discovered it was a simple syntax error of forgetting to place the ";" at the ned of the SELECT command. (Guess I continued the habit from OOPs 😝)

### Task 5: 
SQL game progress and reflection can be found here: [sql-island.md](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/sql-island.md)

### Task 6:
Generator Script: [generate_telemetry.py](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/generate_telemetry.py)

Queries, File Size, Row Count and answers: [Queries, Size & Row Count, Answer](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/query_results.txt)

### Task 7: LLM asissted-SQL Profitiling task

**First Prompt used :**
"Here is my SQLite table: readings(ts TEXT, machine TEXT, temp_c REAL, vib_rms REAL, spindle_load REAL). Write a query that returns, for each machine, the average spindle load for readings taken overnight (after 18:00), ordered by average load descending." <br>

**Output result of prompt :** 
![Response](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/pictures/Claude_Prompt_Response.png)

> Notes:<br>
> The intial prompt made the model believe the Query would only last from 18::00 to 00:00, it did not consider for the fact that overnight meant 18:00 - 06:00

**Executing in Terminal:** 
```
sqlite> SELECT
   ...>     machine,
   ...>     AVG(spindle_load) AS avg_spindle_load
   ...> FROM readings
   ...> WHERE time(ts) > '18:00:00'
   ...> GROUP BY machine
   ...> ORDER BY avg_spindle_load DESC;
╭─────────┬────────────────────╮
│ machine │  avg_spindle_load  │
╞═════════╪════════════════════╡
│ cnc-03  │ 60.434039449923603 │
│ cnc-01  │ 60.368453951937767 │
│ cnc-02  │ 60.357216280038891 │
╰─────────┴────────────────────╯
```
Set the over-night definition to 18:00:00 - 06:00:00 <br>

**Executing in Terminal:**
```
sqlite> SELECT
   ...>     machine,
   ...>     AVG(spindle_load) AS avg_spindle_load
   ...> FROM readings
   ...> WHERE time(ts) > '18:00:00' OR time(ts) < '06:00:00'
   ...> GROUP BY machine
   ...> ORDER BY avg_spindle_load DESC;
╭─────────┬────────────────────╮
│ machine │  avg_spindle_load  │
╞═════════╪════════════════════╡
│ cnc-02  │ 60.205972636988683 │
│ cnc-03  │ 60.202878672130012 │
│ cnc-01  │ 60.185554552399474 │
╰─────────┴────────────────────╯
```
**Second prompt:**
EXPLAIN QUERY PLAN "Here is my SQLite table: readings(ts TEXT, machine TEXT, temp_c REAL, vib_rms REAL, spindle_load REAL). Write a query that returns, for each machine, the average spindle load for readings taken overnight (after 18:00), ordered by average load descending." <br>

**Claude's Response:**
```
QUERY PLAN
|--SCAN readings
|--USE TEMP B-TREE FOR GROUP BY
`--USE TEMP B-TREE FOR ORDER BY
```
**Attempting to break Claude (Broken Prompt):**
"Here is my SQLite table: readings(ts TEXT, machine TEXT, temp_c REAL, vib_rms REAL, spindle_load REAL). Write a query that returns, for each machine, the average spindle load for readings ts > %18%, ordered by average load descending."<br>

**Claude's Response:**
![Claude Response to Broken Prompt](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/pictures/broken_prompt_response.png)

**Verification Paragraph:**
In the initial prompt, the model decided that overnight implied 18:00:00 - 00:00:00, and made its own assumption. However, it gave a suggestion to change the timeframe to suit the 18:00:00 - 06:00:00 timeframe as the real overnight definition. By running both commands, we can identify the difference and catch the discrepancy of using the wrong prompt with poor boundaries set. <br>
When trying to break the prompt, Claude managed to catch the error befoire running, such as correctly idenfitfying ts>%18% was not valid SQLite, and corrected itself before returning the commands to be used. <br>

### Task 8: Publish your data with Datasette

25 rows where machine contains "cnc-01", spindle_load ≥ 60 and temp_c ≥ 46.5 sorted by machine
![Exported Filtered Readings](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/pictures/Exported_filtered.png)

Exported CSV File: [Filtered.csv](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/exported_filtered.csv)

### Task 9: sqlite3 shell power moves

“Because telemetry.db already contained a populated readings table from earlier Python work, I ran the CSV import into a separate scratch.db so that CREATE TABLE wouldn’t fail or .import wouldn’t duplicate the 172,800 existing rows, which left my original database untouched for the later steps"<br>

Keeping SQL in a file, reduces having to manually type repeated commands, we can create a reusable file with the commands we will use and run the entire file instead, saving time.<br>

Different output modes like .mode box or .mode json are simply different ways to present the data visually in the terminal.<br>

**Box Mode:**<br>
![Box Mode](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/pictures/box_mode.png)

**Json Mode:**<br>
![Json Mode](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/pictures/json_mode.png)

**Markdown Mode:**<br>
![Markdown Mode](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/pictures/markdown_mode.png)

**Insert Mode:**<br>
![Intert Mode](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/pictures/insert_mode.png)

Result.json file here: [result.json](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/result.json)
<br>

Size of Back Up File: 10280KB
Size of Compact File: 10280KB

Comparing file sizes between backup.db and compact.db, the file sizes are identical.

**Claude Explanation:**
.backup copies the database page for page and VACUUM INTO only removes unused free space, so because telemetry.db was loaded once and never had anything deleted, there was no wasted space to remove and both files came out the same size.

Output from joining Tables:
(Insert image of output from joining tables)

**Suprising Command:**
Surprisingly, VACUUM is a compaction tool that had nothing to compact: the database had never had a single row deleted, so it contained zero wasted space, and the “compacted” copy came out byte-for-byte the same size as the original.

### Task 10: Datasette - Facets, filters, and the JSON API

Base URL: http://127.0.0.1:8001/telemetry/readings
57,600 rows where machine = "cnc-01" sorted by rowid: http://127.0.0.1:8001/telemetry/readings?_sort=rowid&machine__exact=cnc-01

Facet By temperature where machine = "cnc-01":
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

### Task 11:

Insert file for toolbox.md here

Insert Screenshot here

sqlite-utils took the fewest keystrokes: one insert command created the table, guessed the column types, and loaded all 172,800 rows, where the sqlite3 shell needed a CREATE TABLE plus .mode csv and .import, and Python needed a whole script. The Python loader was the clearest, because the schema, including the NOT NULL constraints that sqlite-utils left out, is written down explicitly, and the script can be rerun and kept in version control. I would use sqlite-utils for quickly exploring a CSV, the sqlite3 shell for one-off inspection and ad-hoc queries, and Python when the load is part of a repeatable pipeline that needs control over the schema or data cleaning.

## Reflection 1
[Reflection 1](https://github.com/Emannual20/databases-portfolio/blob/main/Reflections/ref01.md)
