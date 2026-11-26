# Reflection 6 in Module 5 (12/11/2026)

- What is your take-away, what do you want to remember, what would be your advice?
  Take-away can be small summary, but better outstanding points.
- What was good?
- What was difficult, where did you struggle?
- Was there any good/fun “struggling”/exploration?
  Any show stoppers – anything where you should reach out to peers or instructors? 
- How was your interaction with peers/instructors?
- Help and extra work
  - Who helped you, gave feedback, was it valuable?
  - Who did you help, gave feedback to?
  - Did you present, implement, made a PR, or fix something that was crucial for the class in itself?

# Reflection 6 (19/11/2026)

**What is your take-away, what do you want to remember, what would be your advice? Take-away can be small summary, but better outstanding points.**

From this POD discussion, I understod how functionl dependencies work, s well s understnding the use of cndidte ey. I also understood normalized vs denomralized query.
- Denormalized Query is a large book with eevery detail repeated on every page, taking up more space but contained only in one boo
- Normalized Query is splitting it into smallerbooks, taking less storage but wasting time to match the ID's

**What was good?**

During our discussion, at frist I thoght the assumptions for domain gaurantees were definite on my side, but i realsied that there were big differences between my POD mates and I. For exampl,e Isa had actually ideintified a new row, creating a relationship betwen job_id and done_on, matching the job id and the date it was perfromed, which is a domain gauranteed functionl dependency as every job must have been completed on a certai n date.  

**What was difficult, where did you struggle?**



> **Difficulties Faced :**

Understanding the problem in Task 7 with the SQL Command: SELECT DISTINCT:
```sql
INSERT INTO job SELECT DISTINCT job_id, machine_id, technician, done_on
```
The command silently assumes each job has exactly one technician. If historical logs assigned two technicians to one job_id, SELECT DISTINCT would return two rows for that job_id, causing SQLite's PRIMARY KEY (job_id) constraint to fail during insertion.

**Was there any good/fun “struggling”/exploration?**  
> Any show stoppers – anything where you should reach out to peers or instructors?

The fun part of this session was exploring the coercion trap. In unnormalized tables, numeric attributes often degrade into text strings, requiring explicit CAST(part_price AS REAL) during 3NF extraction.

As a pod, we tried to break printf() to test and discovered the inputs usually turned into text strings, resulting in all being accepted.

**How was your interaction with peers/instructors?**


## Help and extra work
**Who helped you, gave feedback, was it valuable?**


**Who did you help, gave feedback to?**


** Did you present, implement, made a PR, or fix something that was crucial for the class in itself? **

