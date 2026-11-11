1. Functional Dependency (FD) AnalysisA functional dependency $X \rightarrow Y$ states that if two rows match on attribute $X$, they must match on attribute $Y$.

Domain Facts (Guaranteed Rules):
- job_id -> machine_id: A specific maintenance job occurs on one machine.
- job_id -> technician: A single job is assigned to one technician.- machine_id -> site: A physical machine is located at one physical site.
- part_no -> part_price: A catalog part has a fixed unit price.
- (job_id, part_no) $\rightarrow$ Candidate Key for the flat row.

Merely Observed in Data (Accidental Artifacts of 5 Rows):
- technician -> machine_id: In this sample, tech-0 only worked on cnc-01 and tech-1 on cnc-02. In real operations, technicians service multiple machines.
- site -> technician / site -> machine_id: site is always Gütersloh across all 5 rows, making it look like a determinant, which is false in the broader domain.

Gate Question: "Which arrow disappears in the second diagram?"

Answer:

The transitive arrow job_id -> site disappears from the job level. site is now determined exclusively by machine_id in the machine table.

The partial dependency arrow (job_id, part_no) -> part_price disappears from the junction table. part_price is now determined exclusively by part_no in the part table.

# Module 05: Normalization vs Denormalization Notes

Functional Dependencies: If you know X, then Y is 100% fixed and predictable. Two rows with the exact same X can never have different Y values.

Example:
Rule: A physcial machine lives at only one factory location
Meaning: If you see machine cnc-01, it is definetly in Gütersloh, it cannot be in two cities at once.

Candidate Key: Minimal set of attributes to determine the full details.

Example: job_id is not enouhg information as one job can have multiple parts, we instead pair (job_id, part_no) a unique combination.

## Round 1: See It

My observations of the FDs:
- job_id -> machine_id
- job_id -> technician
- machine_id -> site
- part_no -> part_price
- technician -> machine_id

### Functional Dependencies
- `job_id -> machine_id` (Domain Fact)
- `job_id -> technician` (Domain Fact)
- `machine_id -> site` (Domain Fact)
- `part_no -> part_price` (Domain Fact)
- `technician -> machine_id` (Merely Observed in 5-row sample)
- Candidate Key: `(job_id, part_no)`

### Disappearing Arrows in 3NF
- Transitive arrow `job_id -> site` removed (moved to `machine` table via `machine_id -> site`).
- Partial arrow `part_no -> part_price` removed (moved to `part` table via `part_no -> part_price`).