DO
$do$
BEGIN
  IF (NOT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'nachet_0.0.5')) THEN
    CREATE SCHEMA "nachet_0.0.5";
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "nachet_0.0.5";
  END IF;
END
$do$
