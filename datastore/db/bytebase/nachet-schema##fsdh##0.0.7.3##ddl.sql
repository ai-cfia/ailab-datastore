--Schema creation file test
DO
$do$
BEGIN
  IF (NOT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'nachet_0.0.7')) THEN
    CREATE SCHEMA "nachet_0.0.7";
    --Table creation file
    CREATE TABLE "nachet_0.0.7".users (
        id uuid DEFAULT "uuid_".uuid_generate_v4() PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "nachet_0.0.7".picture_set (
        id uuid DEFAULT "uuid_".uuid_generate_v4() PRIMARY KEY,
        picture_set JSON,
        owner_id uuid ,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        CONSTRAINT fk_owner
            FOREIGN KEY(owner_id) 
                REFERENCES "nachet_0.0.7".users(id)
    );

    CREATE TABLE "nachet_0.0.7".pictures (
        id uuid DEFAULT "uuid_".uuid_generate_v4() PRIMARY KEY,
        picture_set_id uuid,
        picture JSON,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        CONSTRAINT fk_picture_set
            FOREIGN KEY(picture_set_id) 
                REFERENCES "nachet_0.0.7".picture_set(id)
                ON DELETE CASCADE
    );

    CREATE TABLE "nachet_0.0.7".seeds (
        id uuid DEFAULT "uuid_".uuid_generate_v4() PRIMARY KEY,
        metadata JSON,
        name VARCHAR(255) NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "nachet_0.0.7".picture_seed (
        id uuid DEFAULT "uuid_".uuid_generate_v4() PRIMARY KEY,
        picture_id uuid REFERENCES "nachet_0.0.7".pictures(id),
        seed_id uuid REFERENCES "nachet_0.0.7".seeds(id),
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        CONSTRAINT fk_picture
            FOREIGN KEY(picture_id) 
                REFERENCES "nachet_0.0.7".pictures(id)
                ON DELETE CASCADE,
        CONSTRAINT fk_seed
            FOREIGN KEY(seed_id) 
                REFERENCES "nachet_0.0.7".seeds(id)
                ON DELETE CASCADE
    ); 
  END IF;
END
$do$
