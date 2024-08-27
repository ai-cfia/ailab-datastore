--Schema creation "fertiscan_0.0.13"
DO
$do$
BEGIN
IF (EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'fertiscan_0.0.13')) THEN


    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    CREATE TABLE "fertiscan_0.0.13"."users" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "email" text NOT NULL UNIQUE,
    "registration_date" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp
    );

    -- CREATE A TYPE FOR FRENCH/ENGLISH LANGUAGE
    CREATE TYPE "fertiscan_0.0.13".LANGUAGE AS ENUM ('fr', 'en');

    CREATE TABLE "fertiscan_0.0.13"."picture_set" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    "picture_set" json NOT NULL,
    "owner_id" uuid NOT NULL REFERENCES "fertiscan_0.0.13".users(id),
    "upload_date" date NOT NULL DEFAULT current_timestamp,
    "name" text
    );
        
    alter table "fertiscan_0.0.13".users ADD "default_set_id" uuid REFERENCES "fertiscan_0.0.13".picture_set(id);

    CREATE TABLE "fertiscan_0.0.13"."picture" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    "picture" json NOT NULL,
    "nb_obj" int,
    "picture_set_id" uuid NOT NULL REFERENCES "fertiscan_0.0.13".picture_set(id),
    "verified" boolean NOT NULL DEFAULT false,
    "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "fertiscan_0.0.13"."province" (
    "id" SERIAL PRIMARY KEY,
    "name" text UNIQUE NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.13"."region" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "province_id" int REFERENCES "fertiscan_0.0.13".province(id),
    "name" text NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.13"."location" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text,
    "address" text NOT NULL,
    "region_id" uuid References "fertiscan_0.0.13".region(id)
    );    
    
    CREATE TABLE "fertiscan_0.0.13"."organization_information" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "name" text NOT NULL,
        "website" text,
        "phone_number" text,
        "location_id" uuid REFERENCES "fertiscan_0.0.13".location(id),
        "edited" boolean DEFAULT false
    );

    CREATE TABLE "fertiscan_0.0.13"."organization" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "information_id" uuid REFERENCES "fertiscan_0.0.13".organization_information(id),
    "main_location_id" uuid REFERENCES "fertiscan_0.0.13".location(id)
    );


    Alter table "fertiscan_0.0.13".location ADD "owner_id" uuid REFERENCES "fertiscan_0.0.13".organization(id);

    CREATE TABLE "fertiscan_0.0.13"."sample" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "number" uuid,
    "collection_date" date,
    "location" uuid REFERENCES "fertiscan_0.0.13".location(id)
    );

    CREATE TABLE "fertiscan_0.0.13"."unit" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "unit" text NOT NULL,
    "to_si_unit" float
    );

    CREATE TABLE "fertiscan_0.0.13"."element_compound" (
    "id" SERIAL PRIMARY KEY,
    "number" int NOT NULL,
    "name_fr" text NOT NULL,
    "name_en" text NOT NULL,
    "symbol" text NOT NULL UNIQUE
    );

    CREATE TABLE "fertiscan_0.0.13"."label_information" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "product_name" text,
    "lot_number" text,
    "npk" text,
    "registration_number" text,
    "n" float,
    "p" float,
    "k" float,
    "warranty" text,
    "company_info_id" uuid REFERENCES "fertiscan_0.0.13".organization_information(id),
    "manufacturer_info_id" uuid REFERENCES "fertiscan_0.0.13".organization_information(id)
    );
    
    CREATE TABLE "fertiscan_0.0.13"."label_dimension" (
    "label_id" uuid PRIMARY KEY,
    "company_info_id" uuid REFERENCES "fertiscan_0.0.13".organization_information(id),
    "company_location_id" uuid REFERENCES "fertiscan_0.0.13".location(id),
    "manufacturer_info_id" uuid REFERENCES "fertiscan_0.0.13".organization_information(id),
    "manufacturer_location_id" uuid REFERENCES "fertiscan_0.0.13".location(id),
    "instructions_ids" uuid[] DEFAULT '{}',
    "cautions_ids" uuid[] DEFAULT '{}',
    "first_aid_ids" uuid[] DEFAULT '{}',
    "warranties_ids" uuid[] DEFAULT '{}',
    "specification_ids" uuid[] DEFAULT '{}',
    "ingredient_ids" uuid[] DEFAULT '{}',
    "micronutrient_ids" uuid[] DEFAULT '{}',
    "guaranteed_ids" uuid[] DEFAULT '{}',
    "weight_ids" uuid[] DEFAULT '{}',
    "volume_ids" uuid[] DEFAULT '{}',
    "density_ids" uuid[] DEFAULT '{}'
    );

    CREATE TABLE "fertiscan_0.0.13"."time_dimension" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "date_value" date,
    "year" int,
    "month" int,
    "day" int,
    "month_name" text,
    "day_name" text
    );

    CREATE TABLE "fertiscan_0.0.13"."inspection_factual" (
    "inspection_id" uuid PRIMARY KEY,
    "inspector_id" uuid REFERENCES "fertiscan_0.0.13".users(id),
    "label_info_id" uuid REFERENCES "fertiscan_0.0.13".label_information(id),
    "time_id" uuid REFERENCES "fertiscan_0.0.13".time_dimension(id),
    "sample_id" uuid REFERENCES "fertiscan_0.0.13".sample(id),
    "company_id" uuid REFERENCES "fertiscan_0.0.13".organization(id),
    "manufacturer_id" uuid REFERENCES "fertiscan_0.0.13".organization(id),
    "picture_set_id" uuid,
    "inspection_date" timestamp DEFAULT CURRENT_TIMESTAMP
    );


    CREATE TYPE "fertiscan_0.0.13".metric_type as ENUM ('volume', 'weight','density');

    CREATE TABLE "fertiscan_0.0.13"."metric" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "value" float NOT NULL,
    "edited" boolean,
    "unit_id" uuid REFERENCES "fertiscan_0.0.13".unit(id),
    "metric_type" "fertiscan_0.0.13".metric_type,
    "label_id" uuid REFERENCES "fertiscan_0.0.13".label_information(id) ON DELETE CASCADE
    );

    CREATE TABLE "fertiscan_0.0.13"."sub_type" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "type_fr" text Unique NOT NULL,
        "type_en" text unique NOT NULL
    );


    CREATE TABLE "fertiscan_0.0.13"."specification" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "humidity" float,
    "ph" float,
    "solubility" float,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.13".label_information(id) ON DELETE CASCADE,
    "language" "fertiscan_0.0.13".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.13"."sub_label" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "text_content_fr" text NOT NULL DEFAULT '',
        "text_content_en" text NOT NULL DEFAULT '',
        "label_id" uuid NOT NULL REFERENCES "fertiscan_0.0.13".label_information("id") ON DELETE CASCADE,
        "edited" boolean NOT NULL,
        "sub_type_id" uuid NOT NULL REFERENCES "fertiscan_0.0.13"."sub_type" ("id")
    );

    CREATE TABLE "fertiscan_0.0.13"."micronutrient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text NOT NULL,
    "value" float NOT NULL,
    "unit" text NOT NULL,
    "element_id" int REFERENCES "fertiscan_0.0.13".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.0.13".label_information(id) ON DELETE CASCADE,
    "edited" boolean,
    "language" "fertiscan_0.0.13".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.13"."guaranteed" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text NOT NULL,
    "value" float NOT NULL,
    "unit" text NOT NULL,
    "element_id" int REFERENCES "fertiscan_0.0.13".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.0.13".label_information(id) ON DELETE CASCADE,
    "edited" boolean
    );

    CREATE TABLE "fertiscan_0.0.13"."ingredient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "organic" boolean,
    "active" boolean,
    "name" text NOT NULL,
    "value" float,
    "unit" text,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.13".label_information(id) ON DELETE CASCADE,
    "language" "fertiscan_0.0.13".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.13"."inspection" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "verified" boolean DEFAULT false,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "inspector_id" uuid NOT NULL REFERENCES "fertiscan_0.0.13".users(id),
    "label_info_id" uuid REFERENCES "fertiscan_0.0.13".label_information(id) ON DELETE CASCADE,
    "sample_id" uuid REFERENCES "fertiscan_0.0.13".sample(id),
    "picture_set_id" uuid REFERENCES "fertiscan_0.0.13".picture_set(id)
    );

    CREATE TABLE "fertiscan_0.0.13"."fertilizer" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text UNIQUE NOT NULL,
    "registration_number" text,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "update_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "latest_inspection_id" uuid REFERENCES "fertiscan_0.0.13".inspection(id),
    "owner_id" uuid REFERENCES "fertiscan_0.0.13".organization(id)
    );

    Alter table "fertiscan_0.0.13".inspection ADD "fertilizer_id" uuid REFERENCES "fertiscan_0.0.13".fertilizer(id);

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
    BEFORE UPDATE ON  "fertiscan_0.0.13".users
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
    BEFORE UPDATE ON  "fertiscan_0.0.13".inspection
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
    BEFORE UPDATE ON  "fertiscan_0.0.13".fertilizer
    FOR EACH ROW
    EXECUTE FUNCTION update_fertilizer_timestamp();

    -- Insert the default types : [instruction, caution,first_aid, warranty]
    INSERT INTO "fertiscan_0.0.13".sub_type(type_fr,type_en) VALUES
    ('instructions','instructions'),
    ('mises_en_garde','cautions'),
    ('premier_soin','first_aid'),
    ('garanties','warranties');
end if;
END
$do$;