# PostgreSQL server comparison — manual exercise

No PostgreSQL connection is configured in this repository. This is a ready-to-run procedure for the instructor's actual server; it contains no assumed host, credentials, or fabricated observations.

## Connection model

Use the host, port, database, username, and password supplied by the instructor. A PostgreSQL client establishes a network connection to the server process, authenticates a role, and opens a database. Keep credentials in the approved client UI or environment variables; do not put passwords in this portfolio or Git. Typical client arguments are `host`, `port` (often 5432), `dbname`, and `user`; the server may require TLS or a VPN.

## Create comparable data

Run in the assigned database/schema:

```sql
CREATE TABLE IF NOT EXISTS module6_device (
    device_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    vendor TEXT NOT NULL,
    firmware TEXT NOT NULL
);

INSERT INTO module6_device(device_id, name, vendor, firmware) VALUES
    (1, 'cnc-01', 'Siemens', '4.2'),
    (2, 'cnc-02', 'Fanuc', '3.9'),
    (3, 'molder-07', 'Arburg', '8.1')
ON CONFLICT (device_id) DO UPDATE SET
    name=excluded.name, vendor=excluded.vendor, firmware=excluded.firmware;

SELECT vendor, COUNT(*) AS devices
FROM module6_device
GROUP BY vendor
ORDER BY vendor;
```

Record the actual output, SQL client, date, and any errors. Do not include secrets.

## Two concurrent writers

Open two authenticated sessions. In session A, begin a transaction and update one device without committing:

```sql
BEGIN;
UPDATE module6_device SET firmware='4.3' WHERE device_id=1;
```

In session B, update the same row to a different value and observe whether it waits, errors, or proceeds under the chosen isolation level. Commit or roll back A, then inspect B's result and the final row. Repeat with separate rows for comparison. Use disposable course data and clean up only if permitted by the instructor. Record actual isolation details shown by the server/client.

## Availability and observation record

Network reachability, firewall/VPN, DNS, server load, authentication, role permissions, and server maintenance can prevent connections. A process or network outage affects multiple remote clients; an embedded database does not depend on a separate database server/network hop, though it has its own host/storage failure modes.

- Host/port/database/role supplied (never password): `[STUDENT INPUT REQUIRED]`
- Connection and query actually succeeded?: `[STUDENT INPUT REQUIRED]`
- What got easier/harder?: `[STUDENT INPUT REQUIRED]`
- Two-writer observation and isolation level: `[STUDENT INPUT REQUIRED]`
- Server stop/recovery observed in class: `[STUDENT INPUT REQUIRED: Do not infer this if absent.]`
- Errors/time/date/client: `[STUDENT INPUT REQUIRED]`
