"""Benchmark Module 5 dashboard queries on a database built by setup.sql.

Run from the repository root:
  .venv\\Scripts\\python.exe Module05\\benchmark.py
Optional paths: --db Module05/normalize_test.db --runs 9
"""
import argparse
import json
import sqlite3
import statistics
import time
from pathlib import Path

NORMALIZED = """SELECT m.machine_id, m.site, j.technician, SUM(p.part_price) AS cost
FROM job j
JOIN machine m ON m.machine_id = j.machine_id
JOIN job_part jp ON jp.job_id = j.job_id
JOIN part p ON p.part_no = jp.part_no
WHERE j.done_on >= date('2026-03-01')
GROUP BY m.machine_id, j.technician"""
DENORMALIZED = """SELECT machine_id, site, technician, SUM(part_price) AS cost
FROM report_jobpart
WHERE done_on >= date('2026-03-01')
GROUP BY machine_id, technician"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', type=Path, default=Path('Module05/normalize_test.db'))
    ap.add_argument('--runs', type=int, default=9)
    args = ap.parse_args()
    if not args.db.exists():
        raise SystemExit(f"Database missing: {args.db}; build it with setup.sql first")
    conn = sqlite3.connect(f"file:{args.db.resolve().as_posix()}?mode=ro", uri=True)
    queries = [('normalized', NORMALIZED), ('denormalized', DENORMALIZED)]
    # One unrecorded warm-up per query, then alternate order each round.
    results = {name: [] for name, _ in queries}
    warmup_rows = {}
    for name, sql in queries:
        warmup_rows[name] = conn.execute(sql).fetchall()
    for i in range(args.runs):
        order = queries if i % 2 == 0 else list(reversed(queries))
        for name, sql in order:
            start = time.perf_counter_ns()
            rows = conn.execute(sql).fetchall()
            elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
            results[name].append({'round': i + 1, 'elapsed_ms': elapsed_ms, 'rows': len(rows)})
    normalized_rows = conn.execute(NORMALIZED).fetchall()
    denormalized_rows = conn.execute(DENORMALIZED).fetchall()
    equivalent = sorted(normalized_rows) == sorted(denormalized_rows)
    plans = {name: [list(row) for row in conn.execute('EXPLAIN QUERY PLAN ' + sql)]
             for name, sql in queries}
    counts = {table: conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
              for table in ('flat_jobpart', 'machine', 'part', 'job', 'job_part', 'report_jobpart')}
    fk_violations = [list(row) for row in conn.execute('PRAGMA foreign_key_check')]
    # Verify actual enforcement on a new connection without retaining any test row.
    fk_test = sqlite3.connect(args.db)
    fk_test.execute('PRAGMA foreign_keys = ON')
    fk_enabled = fk_test.execute('PRAGMA foreign_keys').fetchone()[0] == 1
    fk_rejects_orphan = False
    try:
        fk_test.execute("INSERT INTO job_part(job_id, part_no) VALUES (-1, 'NO-SUCH-PART')")
    except sqlite3.IntegrityError:
        fk_rejects_orphan = True
    finally:
        fk_test.rollback()
        fk_test.close()
    relationship_sql = {
        'job_has_one_machine_technician_date': "SELECT COUNT(*) FROM (SELECT job_id FROM flat_jobpart GROUP BY job_id HAVING COUNT(DISTINCT machine_id)>1 OR COUNT(DISTINCT technician)>1 OR COUNT(DISTINCT done_on)>1)",
        'machine_has_one_site': "SELECT COUNT(*) FROM (SELECT machine_id FROM flat_jobpart GROUP BY machine_id HAVING COUNT(DISTINCT site)>1)",
        'part_has_one_price': "SELECT COUNT(*) FROM (SELECT part_no FROM flat_jobpart GROUP BY part_no HAVING COUNT(DISTINCT part_price)>1)",
        'job_part_key_unique': "SELECT COUNT(*) FROM (SELECT job_id,part_no FROM flat_jobpart GROUP BY job_id,part_no HAVING COUNT(*)>1)",
    }
    relationships = {name: conn.execute(sql).fetchone()[0] for name, sql in relationship_sql.items()}
    integrity = conn.execute('PRAGMA integrity_check').fetchone()[0]
    page_count = conn.execute('PRAGMA page_count').fetchone()[0]
    page_size = conn.execute('PRAGMA page_size').fetchone()[0]
    dbstat = None
    try:
        dbstat = {name: conn.execute('SELECT COALESCE(SUM(pgsize),0) FROM dbstat WHERE name=?',
                                     (name,)).fetchone()[0]
                  for name in ('flat_jobpart', 'machine', 'part', 'job', 'job_part', 'report_jobpart')}
        dbstat['indexes'] = conn.execute("SELECT name, COALESCE((SELECT SUM(pgsize) FROM dbstat WHERE name=sm.name),0) FROM sqlite_master sm WHERE type='index' AND tbl_name IN ('flat_jobpart','machine','part','job','job_part','report_jobpart') ORDER BY name").fetchall()
    except sqlite3.OperationalError as e:
        dbstat = {'unavailable': str(e)}
    summaries = {}
    for name, runs in results.items():
        samples = [r['elapsed_ms'] for r in runs]
        summaries[name] = {'median_ms': statistics.median(samples), 'min_ms': min(samples),
                           'max_ms': max(samples), 'spread_ms': max(samples)-min(samples)}
    report = {
        'database': str(args.db), 'sqlite_version': sqlite3.sqlite_version, 'runs': args.runs,
        'method': 'one warm-up per query; then interleaved, alternating query order; perf_counter_ns; full fetchall; milliseconds',
        'query_definitions': {'normalized': NORMALIZED, 'denormalized': DENORMALIZED},
        'row_counts': counts, 'result_rows': {k: len(v) for k,v in
            [('normalized', normalized_rows), ('denormalized', denormalized_rows)]},
        'results_equivalent': equivalent, 'foreign_key_violations': fk_violations,
        'foreign_keys_enabled_in_insert_test': fk_enabled, 'foreign_key_rejects_orphan_insert': fk_rejects_orphan,
        'relationship_violation_counts': relationships, 'integrity_check': integrity, 'raw_runs': results, 'summary': summaries,
        'plans': plans, 'database_file_bytes': args.db.stat().st_size,
        'page_count': page_count, 'page_size': page_size, 'dbstat': dbstat,
        'index_configuration': [list(r) for r in conn.execute("SELECT name,tbl_name,sql FROM sqlite_master WHERE type='index' ORDER BY tbl_name,name")],
    }
    out = args.db.with_name('benchmark-results.json')
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    if not equivalent or fk_violations or not fk_enabled or not fk_rejects_orphan or any(relationships.values()) or integrity != 'ok':
        raise SystemExit('Validation failed; inspect reported checks')


if __name__ == '__main__':
    main()


