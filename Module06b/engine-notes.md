# Module 6b — Engine notes

## Technical observations from executable experiments

- SQLite enforces the JSON text contract with `CHECK (json_valid(meta))` while allowing optional vendor keys.
- An expression index is tied to the indexed expression. Compare actual indexed and `->>` plans in `results/json-query-plans.txt`; a semantically similar expression may not match the index expression.
- SQLite can query across session attributes in a relational table. The key/value `shelve` access pattern is a direct key lookup and does not provide that relational query interface.
- `shelve`'s DBM implementation and physical layout vary by platform. Use the backend and machine recorded in `results/kv-results.json` when interpreting results.

## Server, pod and personal observations

- PostgreSQL: [STUDENT INPUT REQUIRED: Record what actually became easier and harder when connecting to the class server.]
- Server failure observed in class: [STUDENT INPUT REQUIRED: Enter an observation only if you personally saw it.]
- Pod discussion / surprise: [STUDENT INPUT REQUIRED: Record your pod's actual discussion.]
- Neighbouring pod comparison: [STUDENT INPUT REQUIRED: Record actual findings and differences.]
- Peer defence feedback and changes: [STUDENT INPUT REQUIRED: Record actual feedback and resulting changes.]
- What I learned, found difficult, and would choose as an engineer: [STUDENT INPUT REQUIRED: Write your own judgment.]
