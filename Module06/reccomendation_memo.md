Executive Recommendation Memo
MEMORANDUM

TO: Operations Lead

FROM: Lead Database Engineer

DATE: March 1, 2026

SUBJECT: Architecture Recommendation: Transactional 3NF vs. Reporting Schema

We recommend retaining 3NF normalization for all operational transactional tables (job, job_part, part, machine) while serving analytics from a separate asynchronous reporting table (report_jobpart). Benchmark testing on 200,000 maintenance rows reveals that flat denormalization provides zero read advantage on warm, in-memory datasets (~570 ms normalized vs. ~683 ms denormalized) while increasing storage overhead from 3.5 MB to 9.8 MB (a 2.8x footprint expansion). More critically, updating master machine data in a flat table requires modifying 4,000 rows per event compared to 1 row in 3NF, creating severe update anomaly risks and database write locks. To prevent reporting data staleness without degrading transactional write speed, we recommend populating report_jobpart via an off-peak scheduled nightly rebuild or using an AFTER INSERT / AFTER UPDATE database trigger for near-real-time updates. This hybrid strategy preserves absolute transactional data integrity at 3NF while providing fast, isolated read access for operations dashboards.