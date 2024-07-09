--Schema creation "fertiscan_0.0.6"
DO
$do$
BEGIN
IF (EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'fertiscan_0.0.6')) THEN


    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    CREATE TABLE "fertiscan_0.0.6"."users" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "email" text NOT NULL UNIQUE,
    "registration_date" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp
    );

    CREATE TABLE "fertiscan_0.0.6"."picture_set" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    "picture_set" json NOT NULL,
    "owner_id" uuid NOT NULL REFERENCES "fertiscan_0.0.6".users(id),
    "upload_date" date NOT NULL DEFAULT current_timestamp,
    "name" text
    );
        
    CREATE TABLE "fertiscan_0.0.6"."picture" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    "picture" json NOT NULL,
    "picture_set_id" uuid NOT NULL REFERENCES "fertiscan_0.0.6".picture_set(id),
    "verified" boolean NOT NULL DEFAULT false,
    "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "fertiscan_0.0.6"."province" (
    "id" SERIAL PRIMARY KEY,
    "name" text UNIQUE NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.6"."region" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "province_id" int REFERENCES "fertiscan_0.0.6".province(id),
    "name" text NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.6"."location" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text,
    region_id uuid References "fertiscan_0.0.6".region(id),
    "address" text NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.6"."responsable" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text NOT NULL,
    "website" text,
    "phone_number" text,
    "location_id" uuid REFERENCES "fertiscan_0.0.6".location(id)
    );

    CREATE TABLE "fertiscan_0.0.6"."sample" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "number" uuid,
    "collection_date" date,
    "location" uuid REFERENCES "fertiscan_0.0.6".location(id)
    );

    CREATE TABLE "fertiscan_0.0.6"."specification" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "humidity" float,
    "ph" float,
    "solubility" float,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.6".label_information(id)
    );

    CREATE TABLE "fertiscan_0.0.6"."unit" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "unit" text NOT NULL,
    "to_si_unit" float
    );

    CREATE TABLE "fertiscan_0.0.6"."metric" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "value" float NOT NULL,
    "unit_id" uuid REFERENCES "fertiscan_0.0.6".unit(id),
    "edited" boolean
    );

    CREATE TABLE "fertiscan_0.0.6"."element_compound" (
    "id" SERIAL PRIMARY KEY,
    "number" int NOT NULL,
    "name_fr" text NOT NULL,
    "name_en" text NOT NULL,
    "symbol" text NOT NULL UNIQUE
    );

    CREATE TABLE "fertiscan_0.0.6"."label_information" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "lot_number" text,
    "npk" text,
    "registration_number" text,
    "n" float,
    "p" float,
    "k" float,
    "weight" uuid REFERENCES "fertiscan_0.0.6".metric(id),
    "density" uuid REFERENCES "fertiscan_0.0.6".metric(id),
    "volume" uuid REFERENCES "fertiscan_0.0.6".metric(id)
    );

        CREATE TABLE "fertiscan_0.0.6"."first_aid" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "first_aid_fr" text,
    "first_aid_en" text,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.6".label_information(id)
    );

    CREATE TABLE "fertiscan_0.0.6"."warranty" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "warranty_fr" text,
    "warranty_en" text,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.6".label_information(id)
    );

    CREATE TABLE "fertiscan_0.0.6"."instruction" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "instruction_fr" text,
    "instruction_en" text,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.6".label_information(id)
    );

    CREATE TABLE "fertiscan_0.0.6"."caution" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "caution_fr" text,
    "caution_en" text,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.6".label_information(id)
    );

    CREATE TABLE "fertiscan_0.0.6"."micronutrient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text NOT NULL,
    "value" float NOT NULL,
    "unit" text NOT NULL,
    "element_id" int REFERENCES "fertiscan_0.0.6".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.0.6".label_information(id),
    "edited" boolean
    );

    CREATE TABLE "fertiscan_0.0.6"."guaranteed" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text NOT NULL,
    "value" float NOT NULL,
    "unit" text NOT NULL,
    "element_id" int REFERENCES "fertiscan_0.0.6".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.0.6".label_information(id),
    "edited" boolean
    );

    CREATE TABLE "fertiscan_0.0.6"."ingredient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "organic" boolean NOT NULL,
    "name" text NOT NULL,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.6".label_information(id)
    );

    CREATE TABLE "fertiscan_0.0.6"."analysis" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "user_id" uuid REFERENCES "fertiscan_0.0.6".users(id),
    "verified" boolean DEFAULT false,
    "label_info" uuid REFERENCES "fertiscan_0.0.6".label_information(id),
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "fertilizer_id" uuid REFERENCES "fertiscan_0.0.6".fertilizer(id),
    "sample_id" uuid REFERENCES "fertiscan_0.0.6".sample(id),
    "company_id" uuid REFERENCES "fertiscan_0.0.6".responsable(id),
    "manufacturer_id" uuid REFERENCES "fertiscan_0.0.6".responsable(id),
    "picture_set_id" uuid REFERENCES "fertiscan_0.0.6".picture_set(id)
    );

    CREATE TABLE "fertiscan_0.0.6"."fertilizer" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text UNIQUE NOT NULL,
    "registration_number" text,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "update_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "latest_analysis" uuid REFERENCES "fertiscan_0.0.6".analysis,
    "respo_id" uuid REFERENCES "fertiscan_0.0.6".responsable(id)
    );

    -- Trigger function for the `user` table
    CREATE OR REPLACE FUNCTION update_user_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Trigger for the `user` table
    CREATE TRIGGER user_update_before
    BEFORE UPDATE ON  "fertiscan_0.0.6".users
    FOR EACH ROW
    EXECUTE FUNCTION update_user_timestamp();

    -- Trigger function for the `analysis` table
    CREATE OR REPLACE FUNCTION update_analysis_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Trigger for the `analysis` table
    CREATE TRIGGER analysis_update_before
    BEFORE UPDATE ON  "fertiscan_0.0.6".analysis
    FOR EACH ROW
    EXECUTE FUNCTION update_analysis_timestamp();

    -- Trigger function for the `fertilizer` table
    CREATE OR REPLACE FUNCTION update_fertilizer_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
    NEW.update_at = CURRENT_TIMESTAMP;
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Trigger for the `fertilizer` table
    CREATE TRIGGER fertilizer_update_before
    BEFORE UPDATE ON  "fertiscan_0.0.6".fertilizer
    FOR EACH ROW
    EXECUTE FUNCTION update_fertilizer_timestamp();
END
$do$
