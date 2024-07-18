--Schema creation "fertiscan_0.0.7"
DO
$do$
BEGIN
IF (EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'fertiscan_0.0.7')) THEN


    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    CREATE TABLE "fertiscan_0.0.7"."users" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "email" text NOT NULL UNIQUE,
    "registration_date" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp
    );

    CREATE TABLE "fertiscan_0.0.7"."picture_set" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    "picture_set" json NOT NULL,
    "owner_id" uuid NOT NULL REFERENCES "fertiscan_0.0.7".users(id),
    "upload_date" date NOT NULL DEFAULT current_timestamp,
    "name" text
    );
        
    alter table "fertiscan_0.0.7".users ADD "default_set_id" uuid REFERENCES "fertiscan_0.0.7".picture_set(id);

    CREATE TABLE "fertiscan_0.0.7"."picture" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    "picture" json NOT NULL,
    "picture_set_id" uuid NOT NULL REFERENCES "fertiscan_0.0.7".picture_set(id),
    "verified" boolean NOT NULL DEFAULT false,
    "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "fertiscan_0.0.7"."province" (
    "id" SERIAL PRIMARY KEY,
    "name" text UNIQUE NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.7"."region" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "province_id" int REFERENCES "fertiscan_0.0.7".province(id),
    "name" text NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.7"."location" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text,
    "address" text NOT NULL,
    "region_id" uuid References "fertiscan_0.0.7".region(id)
    );    
    
    CREATE TABLE "fertiscan_0.0.7"."organization_information" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "name" text NOT NULL,
        "website" text,
        "phone_number" text,
    );

    CREATE TABLE "fertiscan_0.0.7"."organization" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text NOT NULL,
    "information_id" uuid REFERENCES "fertiscan_0.0.7".organization_contact(id),
    "main_location_id" uuid REFERENCES "fertiscan_0.0.7".location(id)
    );


    Alter table "fertiscan_0.0.7".location ADD "owner_id" uuid REFERENCES "fertiscan_0.0.7".organization(id);

    CREATE TABLE "fertiscan_0.0.7"."sample" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "number" uuid,
    "collection_date" date,
    "location" uuid REFERENCES "fertiscan_0.0.7".location(id)
    );

    CREATE TABLE "fertiscan_0.0.7"."unit" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "unit" text NOT NULL,
    "to_si_unit" float
    );

    CREATE TABLE "fertiscan_0.0.7"."element_compound" (
    "id" SERIAL PRIMARY KEY,
    "number" int NOT NULL,
    "name_fr" text NOT NULL,
    "name_en" text NOT NULL,
    "symbol" text NOT NULL UNIQUE
    );

    CREATE TABLE "fertiscan_0.0.7"."label_information" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "lot_number" text,
    "npk" text,
    "registration_number" text,
    "n" float,
    "p" float,
    "k" float,
    "company_info_id" uuid REFERENCES "fertiscan_0.0.7".organization_information(id),
    "manufacturer_info_id" uuid REFERENCES "fertiscan_0.0.7".organization_information(id)
    );

    CREATE TABLE "fertiscan_0.0.7"."metric_type" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "type" text NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.7"."metric" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "value" float NOT NULL,
    "edited" boolean,
    "unit_id" uuid REFERENCES "fertiscan_0.0.7".unit(id),
    "metric_type_id" uuid REFERENCES "fertiscan_0.0.7".metric_type(id),
    label_id uuid REFERENCES "fertiscan_0.0.7".label_information(id)
    );

    CREATE TABLE "fertiscan_0.0.7"."sub_type" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "type_fr" text Unique NOT NULL,
        "type_en" text unique NOT NULL
    );

    -- CREATE A TYPE FOR FRENCH/ENGLISH LANGUAGE
    CREATE TYPE AS LANGUAGE (
        "fr" text,
        "en" text
    );

    CREATE TABLE "fertiscan_0.0.7"."specification" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "humidity" float,
    "ph" float,
    "solubility" float,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.7".label_information(id),
    "language" LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.7"."sub_label" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "text_content_fr" text NOT NULL DEFAULT '',
        "text_content_en" text NOT NULL DEFAULT '',
        "label_id" uuid NOT NULL REFERENCES "fertiscan_0.0.7"."label_information" ("id"),
        "edited" boolean NOT NULL,
        "sub_type_id" uuid NOT NULL REFERENCES "fertiscan_0.0.7"."sub_type" ("id")
    );

    CREATE TABLE "fertiscan_0.0.7"."micronutrient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text NOT NULL,
    "value" float NOT NULL,
    "unit" text NOT NULL,
    "element_id" int REFERENCES "fertiscan_0.0.7".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.0.7".label_information(id),
    "edited" boolean,
    "language" LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.7"."guaranteed" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text NOT NULL,
    "value" float NOT NULL,
    "unit" text NOT NULL,
    "element_id" int REFERENCES "fertiscan_0.0.7".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.0.7".label_information(id),
    "edited" boolean
    );

    CREATE TABLE "fertiscan_0.0.7"."ingredient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "organic" boolean NOT NULL,
    "name" text NOT NULL,
    "value" float,
    "unit" text,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.7".label_information(id)
    "language" LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.7"."inspection" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "verified" boolean DEFAULT false,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "inspector_id" uuid REFERENCES "fertiscan_0.0.7".users(id),
    "label_info_id" uuid REFERENCES "fertiscan_0.0.7".label_information(id),
    "sample_id" uuid REFERENCES "fertiscan_0.0.7".sample(id),
    "picture_set_id" uuid REFERENCES "fertiscan_0.0.7".picture_set(id)
    );

    CREATE TABLE "fertiscan_0.0.7"."fertilizer" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text UNIQUE NOT NULL,
    "registration_number" text,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "update_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "latest_inspection_id" uuid REFERENCES "fertiscan_0.0.7".inspection,
    "owner_id" uuid REFERENCES "fertiscan_0.0.7".organization(id)
    );

    Alter table "fertiscan_0.0.7".inspection ADD "fertilizer_id" uuid REFERENCES "fertiscan_0.0.7".fertilizer(id);

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
    BEFORE UPDATE ON  "fertiscan_0.0.7".users
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
    BEFORE UPDATE ON  "fertiscan_0.0.7".inspection
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
    BEFORE UPDATE ON  "fertiscan_0.0.7".fertilizer
    FOR EACH ROW
    EXECUTE FUNCTION update_fertilizer_timestamp();

    -- Insert the default types : [instruction, caution,first_aid, warranty]
    INSERT INTO "fertiscan_0.0.7".sub_type(type_fr,type_en) VALUES
    ('Instruction','Instruction'),
    ('Mise en garde','Caution'),
    ('Premier soin','First aid'),
    ('Garantie','Warranty');
END
$do$
