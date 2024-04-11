--Schema creation file test
DO
$do$
BEGIN
  IF (NOT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'nachet_0.0.5')) THEN
    CREATE SCHEMA "nachet_0.0.6";
    CREATE EXTENSION "uuid-ossp" WITH SCHEMA "nachet_0.0.6";
    --Table creation file
    CREATE TABLE "nachet_0.0.6".users (
        id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "nachet_0.0.6".picture_set (
        id uuid DEFAULT "nachet_0.0.6".uuid_generate_v4() PRIMARY KEY,
        picture_set JSON,
        owner_id uuid REFERENCES users(id),
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "nachet_0.0.6".pictures (
        id uuid DEFAULT "nachet_0.0.6".uuid_generate_v4() PRIMARY KEY,
        picture_set_id uuid REFERENCES picture_set(id),
        picture JSON,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "nachet_0.0.6".seeds (
        id uuid DEFAULT "nachet_0.0.6".uuid_generate_v4() PRIMARY KEY,
        metadata JSON,
        name VARCHAR(255) NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "nachet_0.0.6".picture_seed (
        id uuid DEFAULT "nachet_0.0.6".uuid_generate_v4() PRIMARY KEY,
        picture_id uuid REFERENCES picture(id),
        seed_id uuid REFERENCES seeds(id),
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ); 
  END IF;
END
$do$
