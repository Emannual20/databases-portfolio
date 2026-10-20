# Module 1
By the end of this module, you can:

1. Explain how this class works — the CBL/PBL philosophy, the portfolio-based Kombinationsprüfung, and the "moving bar" of a first-time course.
2. Set up your personal GitHub portfolio from the course template, with a clean first commit and a .gitignore that keeps databases and secrets out of Git.
3. Set up the entire toolchain reproducibly with uv — one fixed Python plus SQLite, DuckDB, Datasette, and more — on Windows, macOS, or Linux, and verify it.
4. Explain — with a measurement, not a slide — the difference between an embedded database and a client/server database, and why most local apps should not run a server.
5. Load real rows into SQLite and query them from Python using bound parameters.
6. Take a first LLM-generated query, run it, and begin the habit that defines this course: verify before you trust.

### Task 1: [My portfolio](https://github.com/Emannual20/databases-portfolio)
My skills: Python, Object Oriented Programming, Some Basci micro controller knowledge<br>
Expectations: I expect to learn about databases, MYSQL, possibly docker if there is time

### Task 2:
My partners:
- Sanjay, [portfolio link](https://github.com/yajnas-crpto)
- Jo Marie, [portfolio link](https://github.com/jmanuel08/database-jomportfolio)
- Myomin Lin, [portfolio link](https://github.com/mmlin801597/database-portfolio)

### Task 3:
> **Difficulties Faced :**
> 1. Did not really understand part 3, as i was confused between the Program Github CLI and the Github desktop application which i already had isntalled.<br>
> **Solution:** Using gemini for help, I managed to clone it via the terminal, since that is the main tool that will be used for future lectures. Understanding how to utilize the command prompt on windows will be useful for the future modules to come as we will mainly be working on there.
> 2. Could not find the instructors GitHub Username, team member Sanjay had to help me with locating the usename and adding the professor as a collaborator.<br>
> **Solution :** No shame in asking for help!

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
SQL game progress and reflectioncan be found here: [sql-island.md](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/sql-island.md)

### Task 6:
Generator Script: [generate_telemetry.py](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/generate_telemetry.py)

Queries, File Size, Row Count and answers: [Queries, Size & Row Count, Answer](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/query_results.txt)

### Task 7: LLM asissted-SQL Profitiling task

**First Prompt used :**
"Here is my SQLite table: readings(ts TEXT, machine TEXT, temp_c REAL, vib_rms REAL, spindle_load REAL). Write a query that returns, for each machine, the average spindle load for readings taken overnight (after 18:00), ordered by average load descending." <br>

**Output result of prompt :** 
![Response](https://github.com/Emannual20/databases-portfolio/blob/main/Module01/pictures/Claude_Prompt_Response.png)

> Notes:
> The intial prompt made the model believe the Query would only last from 18::00 to 00:00, it did not consider for the fact that overnight meant 18:00 - 06:00

**Executing in Terminal:** 
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

Set the over-night definition to 18:00:00 - 06:00:00 <br>

**Executing in Terminal:**
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

**Second prompt:**
EXPLAIN QUERY PLAN "Here is my SQLite table: readings(ts TEXT, machine TEXT, temp_c REAL, vib_rms REAL, spindle_load REAL). Write a query that returns, for each machine, the average spindle load for readings taken overnight (after 18:00), ordered by average load descending." <br>

**Claude's Response:**
QUERY PLAN
|--SCAN readings
|--USE TEMP B-TREE FOR GROUP BY
`--USE TEMP B-TREE FOR ORDER BY

**Attempting to break Claude (Broken Prompt):**
"Here is my SQLite table: readings(ts TEXT, machine TEXT, temp_c REAL, vib_rms REAL, spindle_load REAL). Write a query that returns, for each machine, the average spindle load for readings ts > %18%, ordered by average load descending."

(insert picture here)

## Task Inspirations

- Inspiration 1
- Inspiration 2

## Task Personal Profile

## Task What is IoT

Domains and included areas:

-
-


Commonly used (data) protocols:

-
-

Typical devices (appliance or micro controller):

-
-

Challenges:

-
-

## Reflection 1
[Reflection 1](/Reflections/ref01.md)
