# Key/value versus SQLite experiment

Run `python Module06b/kv_compare.py`. Both engines receive the same deterministic 50,000 keys and values and read them back in the same order. The script repeats the run, validates every value, records medians/min/max for writes, reads, combined time, and storage footprint, and records the actual `shelve` DBM backend. It also demonstrates an across-session relational query in SQLite.

The output is generated under `results/kv-results.csv` and `results/kv-results.json`. These measurements describe this machine and its DBM implementation, not a universal `shelve` performance ranking. SQLite's cross-row query is useful when session attributes must be searched or aggregated; a simple shelf's natural operation is lookup by key.

Observed result and engine choice: `[generated results; add your defended choice after reviewing them]`

Personal/pod interpretation: [STUDENT INPUT REQUIRED: State which result surprised you, which engine you would use, and why.]
