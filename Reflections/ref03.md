# Reflection 3 in Module 3

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

# Reflection 3 (25/10/2026)

**What is your take-away, what do you want to remember, what would be your advice? Take-away can be small summary, but better outstanding points.**

My takeaways from this module are Diagnosing EXPLAIN QEURY PLAN (e.g. SCAN vs SEARCH), understanding that SCAN revelas an expensive full table read caused by uninxdexed filters, while SEARCH confrism targeted index lookups. 
**What was good?**



**What was difficult, where did you struggle?**

I struggled to understand why creating indexes lke ix_orderline_product for full-year scans had not managed to speed up reads and actually was dead weight. It took soemtimesot understand when to create indexing, and when to use SCAN. After discovering that indexing is expensive becuase the program has to jump to each page everytime, which consumes a high amount of memeory as each page is about 4kb. For low selectvitiy requirements, it is better to use SCAN to save time and resources.

**Was there any good/fun “struggling”/exploration?**  
> Any show stoppers – anything where you should reach out to peers or instructors?

I enjoyed testing the parameters, and learning about the enforcement of bound parameters. Parameterized queries strcitly seperate SQL command structure from user input data, which completely prevents apostrophe based SQL injection. Protectign the databases from potential malicious injections or accidental inputs htta can break the system silently.


**How was your interaction with peers/instructors?**

I helped explain to the group the differences between the written order of SQL and the order in which they are evaluated. My teamamtes also discussed the different findings for our respective parts, and we were joined my new team member Isa, who helped us with relational algebra nad how to convert SQL commands into algebraic expressions.

## Help and extra work
**Who helped you, gave feedback, was it valuable?**

Sanjay helped us with the query plan terminology explanation, as well as the AI prompting which allowed us to better understnad the tasks in general. 

**Who did you help, gave feedback to?**

