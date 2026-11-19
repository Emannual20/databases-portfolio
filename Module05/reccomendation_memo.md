Executive Recommendation Memo
MEMORANDUM

TO: Operations Lead

FROM: Lead Database Engineer

DATE: March 1, 2026

SUBJECT: Architecture Recommendation: Transactional 3NF vs. Reporting Schema

We recommend retaining 3NF normalization for all operational transactional tables (job, job_part, part, machine) while serving analytics from a separate asynchronous reporting table (report_jobpart). Benchmark testing on 200,000 maintenance rows reveals that flat denormalization provides zero read advantage on warm, in-memory datasets (~570 ms normalized vs. ~683 ms denormalized) while increasing storage overhead from 3.5 MB to 9.8 MB (a 2.8x footprint expansion). More critically, updating master machine data in a flat table requires modifying 4,000 rows per event compared to 1 row in 3NF, creating severe update anomaly risks and database write locks. To prevent reporting data staleness without degrading transactional write speed, we recommend populating report_jobpart via an off-peak scheduled nightly rebuild or using an AFTER INSERT / AFTER UPDATE database trigger for near-real-time updates. This hybrid strategy preserves absolute transactional data integrity at 3NF while providing fast, isolated read access for operations dashboards.
---

## Corrected recommendation — verified Module 5 run

The original draft above is retained for its history, but its timing and storage claims are superseded by the reproducible evidence in [benchmark.md](benchmark.md). On the separate validation database, the 3NF query returned the same 350 groups as the reporting query and measured 126.6697 ms median (118.0173–147.9173 ms). The report query measured 149.1518 ms median (139.3138–183.1243 ms). For this specified workload, keep the transactional tables in 3NF and do not claim the report table is faster.

The report copy remains an option only if a real dashboard workload justifies its maintenance cost. In this generated database, the normalized tables and their indexes occupy 8,167,424 allocated bytes; the report table and its index occupy 14,082,048 bytes. A site change updates one machine row in 3NF but 4,000 rows in the report copy for `cnc-02`.

For a dashboard that needs a report table, use a scheduled atomic rebuild after each completed batch (build a replacement, then swap it in a transaction). Dashboard data can then be stale by at most one refresh interval; display the last successful refresh time and rerun the refresh after a failed build. This avoids synchronously updating thousands of duplicated rows in the operational write path, at the cost of bounded staleness. If the dashboard requires immediate consistency, query the normalized tables or implement and validate a transactionally maintained reporting view/table instead.
