One sqlite-utils insert command replaced CREATE TABLE, .mode csv and .import, but you lose control over the schema (no NOT NULL, no explicit types unless you ask with --type).
--detect-types doesn’t exist in newer versions because detection is now the default.
PowerShell showed blank lines between CSV rows because of the Windows line endings, which also made Select-Object -First 10 show fewer rows than expected.

Inter Datasette Lite Screenshot here