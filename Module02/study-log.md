**Task A: Study in your pod**

**Reference Links:**

From this source, I understood he definition of entities, attributes and relationships. An entity is a thing that contains facts (e.g. A student, A Computer), attribute describes an entity (e.g.Student has an ID, Computer has a Serial Number) A relationship lniks entities, usually a verb (.e.g Student **Attends** Math, Student **Owns** Computer) <br>

Entity Relationship Model: [Wiki Entity Relationship Model](https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model)<br>

Cardinality: https://en.wikipedia.org/wiki/Cardinality_(data_modeling)<br>

EER: https://en.wikipedia.org/wiki/Enhanced_entity%E2%80%93relationship_model<br>

Surrogate Key: https://en.wikipedia.org/wiki/Surrogate_key<br>


Things you googled — the term/question, what you found, and the source (URL). One line each.

**Google Searches:**<br>
_"What is a junction table in DataBases?"_
A junction table, also known as an associative entity or bridge table, is a database table used to resolve a many-to-many relationship between two other tables. It works by storing the primary keys of the associated tables as foreign keys, effectively creating two separate one-to-many relationships that link the respective records together.<br>
Source URL: https://en.wikipedia.org/wiki/Associative_entity<br>

_"What is a surrogate key and its purpose?"_<br>
A surrogate key is an artificially generated, unique identifier added to a database table to act as the primary key. Its primary purpose is to provide a stable, system-managed key that is independent of any business logic, ensuring reliable relationships between tables even if the underlying business data changes.<br>
Source URL: https://en.wikipedia.org/wiki/Surrogate_key<br>

Googled Questions:

Remarkable things — surprises, "aha"s, and counterexamples (e.g. "a name looked like a key but had duplicates").


LLM Q&A — for each prompt you tried: the prompt, a 2–3 line summary of the answer, and how you verified it (and where it was wrong).


Your two best found ER sketches — hunt down ER/EER example sketches that teach you the most, then compile down to the best two:


**Task B: From words to sketch**
All diagrams were self-made in draw.io

1:1 — A workshop keeps machines. Each machine has exactly one nameplate (serial number, manufacturer), and each nameplate belongs to exactly one machine. → Where does the key go? Is the nameplate a separate entity or an attribute of the machine?

![1:1](https://github.com/Emannual20/databases-portfolio/blob/main/Module02/pictures/1to1%20A%20Workshop%20Keeps%20machines.drawio.svg)

1:n — Each machine carries many sensors; every sensor is installed on exactly one machine. → Which side holds the foreign key?

![1:n](https://github.com/Emannual20/databases-portfolio/blob/main/Module02/pictures/1ton%20diagram.drawio.svg)

m:n — Work orders use many parts, and a part is used by many work orders; an order can list a given part only once. → What extra table do you need, and what is its key?

[1:1](Module02/pictures/Machine-Nameplate-Relationship-Model.png)

Entity vs. attribute vs. relationship — A maintenance job happens on one machine, is done by one technician on one date; a technician performs many jobs. → Is the job a relationship or an entity? Is the technician an entity or just a name?

Then prove one: write the CREATE TABLE for your favourite sketch, insert two rows, and show the COUNT query that demonstrates its cardinality.

-- Step 1: CREATE TABLES
CREATE TABLE machines (
    machine_id INT PRIMARY KEY,
    location VARCHAR(100) NOT NULL
);

CREATE TABLE sensors (
    sensor_id INT PRIMARY KEY,
    sensor_type VARCHAR(50) NOT NULL,
    machine_id INT NOT NULL,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

-- Step 2: INSERT DATA (1 Machine, 2 Sensors referencing that Machine)
INSERT INTO machines (machine_id, location) 
VALUES (101, 'Assembly Line A');

INSERT INTO sensors (sensor_id, sensor_type, machine_id) 
VALUES 
    (1, 'Vibration', 101),
    (2, 'Temperature', 101);

-- Step 3: COUNT QUERY TO PROVE CARDINALITY (1:n)
SELECT 
    m.machine_id,
    m.location,
    COUNT(s.sensor_id) AS total_sensors
FROM machines m
LEFT JOIN sensors s ON m.machine_id = s.machine_id
WHERE m.machine_id = 101
GROUP BY m.machine_id, m.location;

Portfolio evidence: your four sketches in module-02/study-log.md (or er-examples.md) plus the one CREATE TABLE + COUNT proof.

★ Task C: Explain & share with another pod (~15 minutes)
Pair with a neighbouring pod for about 15 minutes:

Explain to each other — each pod walks the other through its study log and its four sketches; ask questions and fill each other's gaps.
Agree on the 3–5 most noteworthy points and the learning you jointly stand behind (e.g. "a natural key without UNIQUE is not a key").
Clean up your documentation — update your study-log.md with what you learned from the other pod.
Agree on one image — the best example from either pod, or a new drawing the two pods make together — and post that one in our Discord channel, with a one-sentence note on why you chose it.
Each member adds a short “Agreed learning (pod discussion)” section — the shared points, plus any disagreement you left open — to their own module-02/study-log.md.
Portfolio evidence: your cleaned-up study-log.md (with the “Agreed learning (pod discussion)” section), and your pod-pair's single shared image posted in Discord.
