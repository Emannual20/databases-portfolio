**Commands Ran:**

Importing a CSV without any Python:<br>
sqlite3 Module01/scratch.db
CREATE TABLE readings (...);
.mode csv
.import --skip 1 Module01/telemetry.csv readings
SELECT COUNT(*) FROM readings;

Running the SQL file for reusability:<br>
sqlite3 Module01/telemetry.db ".read Module01/queries.sql"

"""sqlite3 Module01/telemetry.db < Module01/queries.sql Fails in Microsoft Powershell, error says the '<' operator is reserved>"""

Different Output Modes:
Why is there a LIMIT 1, if not it will print all 172,800 rows in the terminal 💀

sqlite> .mode box
sqlite> SELECT * FROM readings LIMIT 1;

sqlite> .mode json
sqlite> SELECT * FROM readings LIMIT 1;

sqlite> .mode markdown
sqlite> SELECT * FROM readings LIMIT 1;

sqlite> .mode insert
sqlite> SELECT * FROM readings LIMIT 1;

sqlite> .once Module01/result.json

Owning the file:
sqlite> .backup Module01/backup.db
sqlite> VACUUM INTO 'Module01/compact.db';

Working accross files:
sqlite> .mode box
sqlite> SELECT x.machine,
   ...>        x.vib AS tour_vib,
   ...>        ROUND(AVG(r.vib_rms), 3) AS avg_logged_vib
   ...> FROM t.reading AS x
   ...> JOIN main.readings AS r ON r.machine = x.machine
   ...> GROUP BY x.machine, x.vib;