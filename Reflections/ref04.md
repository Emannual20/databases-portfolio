Reflection 04


We decided to work remotely this time, as the classroom was too packed from the previous session and it was difficult to get the professor's attention. Regardless, we made great progrss as a POD together at Lin's Place.

We firstly helped Pod member Htete catch up to the latest module we were working on, and made sure we all were standardized and on the same page. 


# Reflection 4 (11/11/2026)

**What is your take-away, what do you want to remember, what would be your advice? Take-away can be small summary, but better outstanding points.**

biggest takeaway from Module04 was the importance of proper constraints when inserting new values into our database, and how alarms and safety nets protect our databases, both in privacy and in keeping away unwanted values.

**What was good?**

We worked well together in a more conducive environment, allowing us to clarify and discuss with one another. For example in Task A, Jo Marie asked me why we could insert uncontrained values int o th table despite the delcaration. I explained to him that the delcaration command is only a hint bt SQLite does not enforce it.

**What was difficult, where did you struggle?**

The biggest difficulty I faced was trying to break the alarm system, even with the assitance of Gemini, we discovered that SQLite enforces statement-level atomicity, the constraint error triggers an `ABORT` that rolls back the entire statement—discarding the trigger's write to `alarm`. Consequently, no alarm row is saved for the failed insertion attempt.

Despite trying to break the alarm, SQLite rolls back the statement discarding the trigger completely and preventing it from being added as a new row in the alarms table.

**Was there any good/fun “struggling”/exploration?**  
> Any show stoppers – anything where you should reach out to peers or instructors?

The fun part was trying to break the table by entering different possible entries that should not be accepted, almost shocking to discover what the table was willing to accept. 

**How was your interaction with peers/instructors?**

I preferred working with the POD in a remote group setting, however due to the importance of attending lectures, it will unfortunately have to happen on another time when everyone can make it. I felt during the lectures, due to the size and setting of the classroom, it was difficult to get the Professor's attention.  

## Help and extra work
**Who helped you, gave feedback, was it valuable?**

Sanjay helped me with task 1 and task 4. In task one, i had dififcutly gettig the error to show n trying to insert sensor 99. The issue was the PRAGMA foreign_keys was set to "OFF" as I had opened a new terminal. I had to delete the row that was incorrectly added, and then set the PRAGMA foreign_keys = ON and rerun the insert again.

**Who did you help, gave feedback to?**

I helped Htete with his set up, to help him catch up on the progress of the group as he was behind. We helped him with the github installation, the uvc python environment set and library installations. 

I also helped Lin with understanding integrity layers, explaining to him the layers of integrity, the quetion t answers followed by the SQL mechanism.

** Did you present, implement, made a PR, or fix something that was crucial for the class in itself? **

No crucial for the class, but Lin faced a terminal issue whereby despite him running sqlite3 Module04/edge.db, he was unable to open the sqlite terminal. We managed to discover a workaround, simply working through the windows powershell isntead to run sqlite commands.
