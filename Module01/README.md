# Module 1
By the end of this module, you can:

1. Explain how this class works — the CBL/PBL philosophy, the portfolio-based Kombinationsprüfung, and the "moving bar" of a first-time course.
2. Set up your personal GitHub portfolio from the course template, with a clean first commit and a .gitignore that keeps databases and secrets out of Git.
3. Set up the entire toolchain reproducibly with uv — one fixed Python plus SQLite, DuckDB, Datasette, and more — on Windows, macOS, or Linux, and verify it.
4. Explain — with a measurement, not a slide — the difference between an embedded database and a client/server database, and why most local apps should not run a server.
5. Load real rows into SQLite and query them from Python using bound parameters.
6. Take a first LLM-generated query, run it, and begin the habit that defines this course: verify before you trust.

Day 1

Forming Taks Pod

1. My skills: Python, Object Oriented Programming, Some Basci micro controller knowledge

I expect to learn about databases, MYSQL, possibly docker if there is time

Task 1:

Did not really understand part 3, as i was confused between the Program Github CLI and the Github desktop application which i already had isntalled.

Using gemini for help, I managed to clone it via the temranial, since that is the main tool that will be sued for future lectures. Understnading how to utilize the command prompt on windows will be useful for the future moduels to come as we will mainly be working on there.


Could not find the instructors GitHub Username, team member Sanjay had to help me with locating the usename and adding the professor as a collaborator

I found the .help command the most helpful as it showed me all the commands i needed to use

Task 4: Which dot command I found most helpful

.schema reading 
as it allows me to directly read from the database in the command prompt, to verify the data inside

Task 7: LLM asissted-SQL Profitiling task

First Prompt used:

"Here is my SQLite table: readings(ts TEXT, machine TEXT, temp_c REAL, vib_rms REAL, spindle_load REAL). Write a query that returns, for each machine, the average spindle load for readings taken overnight (after 18:00), ordered by average load descending."

Response:
(Insert pictures of response here)

Output result of prompt: 

(databases-portfolio) PS C:\Users\gamer\databases-portfolio> uv run sqlite-utils query Module01\telemetry.db "SELECT machine, AVG(spindle_load) AS avg_spindle_load FROM readings WHERE CAST(strftime('%H', ts) AS INTEGER) >= 18 GROUP BY machine ORDER BY avg_spindle_load DESC" --table
machine      avg_spindle_load
---------  ------------------
cnc-03                60.4332
cnc-01                60.367
cnc-02                60.3559

Response:
(Insert picture of response here)

The intial prompt made the model believe the Query would only last from 18::00 to 00:00, it did not consider for the fact that overnight meant 18:00 - 06:00

When trying to break the QUERY however, Claude managed to catch itself and fix the error, thus I was unable to break the LLM and get a false QUERY from it.

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
