-- Module04/phantom_alarm_trigger.sql
-- Task 5: Demonstrating phantom alarms with a BEFORE INSERT trigger

PRAGMA foreign_keys = ON;

-- Clean slate
DROP TRIGGER IF EXISTS trg_vib_alarm;
DROP TABLE IF EXISTS alarm;
DROP TABLE IF EXISTS reading;
DROP TABLE IF EXISTS sensor;

-- 1. Schema Setup
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
    CHECK (value >= -273.15 AND value <= 5000)  -- Rejects values > 5000
) STRICT;

CREATE TABLE alarm(
    alarm_id  INTEGER PRIMARY KEY,
    sensor_id INTEGER NOT NULL REFERENCES sensor(sensor_id),
    ts        TEXT NOT NULL,
    value     REAL NOT NULL,
    reason    TEXT NOT NULL
) STRICT;

INSERT INTO sensor (sensor_id, machine_id, metric, unit) 
VALUES (2, 'cnc-01', 'vib_rms', 'mm/s');

-- 2. BROKEN TRIGGER: Defined as BEFORE INSERT instead of AFTER INSERT
CREATE TRIGGER trg_vib_alarm
BEFORE INSERT ON reading
FOR EACH ROW
WHEN NEW.value > 2.0 AND (SELECT metric FROM sensor WHERE sensor_id = NEW.sensor_id) = 'vib_rms'
BEGIN
    INSERT INTO alarm(sensor_id, ts, value, reason)
    VALUES (NEW.sensor_id, NEW.ts, NEW.value, 'vibration over 2.0 mm/s');
END;

-- 3. Valid Insert (Value 2.7 > 2.0)
INSERT INTO reading(sensor_id, ts, value, interval_s) 
VALUES (2, '2026-03-01 09:00:00', 2.7, 1);

-- 4. Invalid Insert (Value 9000 fails CHECK constraint value <= 5000)
-- Because of BEFORE INSERT, the alarm fires FIRST, then the reading insert aborts!
INSERT INTO reading(sensor_id, ts, value, interval_s) 
VALUES (2, '2026-03-01 10:00:00', 9000, 1);