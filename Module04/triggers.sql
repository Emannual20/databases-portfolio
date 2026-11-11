-- Module04/triggers.sql
-- Complete standalone schema, triggers, test verification, and benchmark script.

PRAGMA foreign_keys = ON;

-- Clean slate for repeatable execution
DROP TRIGGER IF EXISTS trg_reading_audit;
DROP TRIGGER IF EXISTS trg_vib_alarm;
DROP TABLE IF EXISTS audit;
DROP TABLE IF EXISTS alarm;
DROP TABLE IF EXISTS reading;
DROP TABLE IF EXISTS sensor;

-- ============================================================================
-- 1. BASE SCHEMA & SEED DATA
-- ============================================================================

CREATE TABLE sensor(
    sensor_id   INTEGER PRIMARY KEY,
    machine_id  TEXT    NOT NULL,
    metric      TEXT    NOT NULL CHECK (metric IN ('temp_c','vib_rms','spindle_load')),
    unit        TEXT    NOT NULL,
    UNIQUE (machine_id, metric)
) STRICT;

CREATE TABLE reading(
    reading_id  INTEGER PRIMARY KEY,
    sensor_id   INTEGER NOT NULL REFERENCES sensor(sensor_id),
    ts          TEXT    NOT NULL,
    value       REAL    NOT NULL,
    interval_s  INTEGER NOT NULL CHECK (interval_s > 0),
    energy_j    REAL    GENERATED ALWAYS AS (value * interval_s) VIRTUAL,
    CHECK (value >= -273.15 AND value <= 5000)
) STRICT;

-- Seed required sensor record for testing (sensor_id = 2)
INSERT INTO sensor (sensor_id, machine_id, metric, unit) 
VALUES (2, 'cnc-01', 'vib_rms', 'mm/s');

-- ============================================================================
-- 2. TASK 3 TABLES
-- ============================================================================

CREATE TABLE alarm(
    alarm_id  INTEGER PRIMARY KEY,
    sensor_id INTEGER NOT NULL REFERENCES sensor(sensor_id),
    ts        TEXT NOT NULL,
    value     REAL NOT NULL,
    reason    TEXT NOT NULL
) STRICT;

CREATE TABLE audit(
    audit_id   INTEGER PRIMARY KEY,
    reading_id INTEGER NOT NULL,
    old_value  REAL,
    new_value  REAL,
    changed_at TEXT NOT NULL DEFAULT (datetime('now'))
) STRICT;

-- ============================================================================
-- 3. TRIGGER DEFINITIONS
-- ============================================================================

-- Trigger 1: Raise alarm on high vibration (> 2.0 mm/s)
CREATE TRIGGER trg_vib_alarm
AFTER INSERT ON reading
FOR EACH ROW
WHEN NEW.value > 2.0 AND (SELECT metric FROM sensor WHERE sensor_id = NEW.sensor_id) = 'vib_rms'
BEGIN
    INSERT INTO alarm(sensor_id, ts, value, reason)
    VALUES (NEW.sensor_id, NEW.ts, NEW.value, 'vibration over 2.0 mm/s');
END;

-- Trigger 2: Record immutable audit log on value update
CREATE TRIGGER trg_reading_audit
AFTER UPDATE OF value ON reading
FOR EACH ROW
BEGIN
    INSERT INTO audit(reading_id, old_value, new_value)
    VALUES (NEW.reading_id, OLD.value, NEW.value);
END;

-- ============================================================================
-- 4. EXERCISE TRIGGERS & VERIFY OUTPUTS
-- ============================================================================

-- Insert reading that triggers an alarm
INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (2, '2026-03-01 09:00:00', 2.7, 1);

-- Update reading value to trigger an audit record
UPDATE reading SET value = 1.4 WHERE sensor_id = 2;

-- Display target tables
SELECT * FROM alarm;
SELECT * FROM audit;

-- ============================================================================
-- 5. BENCHMARK: 10,000-ROW INGEST COST TEST
-- ============================================================================

-- Test 1: Ingest 10,000 rows WITHOUT the alarm trigger
DROP TRIGGER IF EXISTS trg_vib_alarm;
DELETE FROM reading;
DELETE FROM alarm;

BEGIN TRANSACTION;
.timer on
WITH RECURSIVE cnt(x) AS (
    SELECT 1 UNION ALL SELECT x + 1 FROM cnt WHERE x < 10000
)
INSERT INTO reading (sensor_id, ts, value, interval_s)
SELECT 2, '2026-03-01 09:00:00', 2.7, 1 FROM cnt;
.timer off
COMMIT;

-- Re-create Trigger for Test 2
CREATE TRIGGER trg_vib_alarm
AFTER INSERT ON reading
FOR EACH ROW
WHEN NEW.value > 2.0 AND (SELECT metric FROM sensor WHERE sensor_id = NEW.sensor_id) = 'vib_rms'
BEGIN
    INSERT INTO alarm(sensor_id, ts, value, reason)
    VALUES (NEW.sensor_id, NEW.ts, NEW.value, 'vibration over 2.0 mm/s');
END;

-- Test 2: Ingest 10,000 rows WITH the alarm trigger
DELETE FROM reading;
DELETE FROM alarm;

BEGIN TRANSACTION;
.timer on
WITH RECURSIVE cnt(x) AS (
    SELECT 1 UNION ALL SELECT x + 1 FROM cnt WHERE x < 10000
)
INSERT INTO reading (sensor_id, ts, value, interval_s)
SELECT 2, '2026-03-01 09:00:00', 2.7, 1 FROM cnt;
.timer off
COMMIT;