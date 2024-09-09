--Schema creation "fertiscan_0.0.12"
DO
$do$
BEGIN
IF (EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'fertiscan_0.0.12')) THEN


    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    CREATE TABLE "fertiscan_0.0.12"."users" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "email" text NOT NULL UNIQUE,
    "registration_date" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp
    );

    -- CREATE A TYPE FOR FRENCH/ENGLISH LANGUAGE
    CREATE TYPE "fertiscan_0.0.12".LANGUAGE AS ENUM ('fr', 'en');

    CREATE TABLE "fertiscan_0.0.12"."picture_set" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    "picture_set" json NOT NULL,
    "owner_id" uuid NOT NULL REFERENCES "fertiscan_0.0.12".users(id),
    "upload_date" date NOT NULL DEFAULT current_timestamp,
    "name" text
    );
        
    alter table "fertiscan_0.0.12".users ADD "default_set_id" uuid REFERENCES "fertiscan_0.0.12".picture_set(id);

    CREATE TABLE "fertiscan_0.0.12"."picture" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    "picture" json NOT NULL,
    "nb_obj" int,
    "picture_set_id" uuid NOT NULL REFERENCES "fertiscan_0.0.12".picture_set(id),
    "verified" boolean NOT NULL DEFAULT false,
    "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "fertiscan_0.0.12"."province" (
    "id" SERIAL PRIMARY KEY,
    "name" text UNIQUE NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.12"."region" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "province_id" int REFERENCES "fertiscan_0.0.12".province(id),
    "name" text NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.12"."location" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text,
    "address" text,
    "region_id" uuid References "fertiscan_0.0.12".region(id)
    );    
    
    CREATE TABLE "fertiscan_0.0.12"."organization_information" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "name" text,
        "website" text,
        "phone_number" text,
        "location_id" uuid REFERENCES "fertiscan_0.0.12".location(id),
        "edited" boolean DEFAULT false
    );

    CREATE TABLE "fertiscan_0.0.12"."organization" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "information_id" uuid REFERENCES "fertiscan_0.0.12".organization_information(id),
    "main_location_id" uuid REFERENCES "fertiscan_0.0.12".location(id)
    );


    Alter table "fertiscan_0.0.12".location ADD "owner_id" uuid REFERENCES "fertiscan_0.0.12".organization(id);

    CREATE TABLE "fertiscan_0.0.12"."sample" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "number" uuid,
    "collection_date" date,
    "location" uuid REFERENCES "fertiscan_0.0.12".location(id)
    );

    CREATE TABLE "fertiscan_0.0.12"."unit" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "unit" text NOT NULL,
    "to_si_unit" float
    );

    CREATE TABLE "fertiscan_0.0.12"."element_compound" (
    "id" SERIAL PRIMARY KEY,
    "number" int NOT NULL,
    "name_fr" text NOT NULL,
    "name_en" text NOT NULL,
    "symbol" text NOT NULL UNIQUE
    );

    CREATE TABLE "fertiscan_0.0.12"."label_information" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "product_name" text,
    "lot_number" text,
    "npk" text,
    "registration_number" text,
    "n" float,
    "p" float,
    "k" float,
    "warranty" text,
    "company_info_id" uuid REFERENCES "fertiscan_0.0.12".organization_information(id),
    "manufacturer_info_id" uuid REFERENCES "fertiscan_0.0.12".organization_information(id)
    );
    
    CREATE TABLE "fertiscan_0.0.12"."label_dimension" (
    "label_id" uuid PRIMARY KEY,
    "company_info_id" uuid ,
    "company_location_id" uuid ,
    "manufacturer_info_id" uuid,
    "manufacturer_location_id" uuid ,
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

    CREATE TABLE "fertiscan_0.0.12"."time_dimension" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "date_value" date,
    "year" int,
    "month" int,
    "day" int,
    "month_name" text,
    "day_name" text
    );

    CREATE TABLE "fertiscan_0.0.12"."inspection_factual" (
    "inspection_id" uuid PRIMARY KEY,
    "inspector_id" uuid ,
    "label_info_id" uuid ,
    "time_id" uuid References "fertiscan_0.0.12".time_dimension(id),
    "sample_id" uuid,
    "company_id" uuid,
    "manufacturer_id" uuid,
    "picture_set_id" uuid,
    "inspection_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "original_dataset" json
    );


    CREATE TYPE "fertiscan_0.0.12".metric_type as ENUM ('volume', 'weight','density');

    CREATE TABLE "fertiscan_0.0.12"."metric" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "value" float,
    "edited" boolean,
    "unit_id" uuid REFERENCES "fertiscan_0.0.12".unit(id),
    "metric_type" "fertiscan_0.0.12".metric_type,
    "label_id" uuid REFERENCES "fertiscan_0.0.12".label_information(id)
    );

    CREATE TABLE "fertiscan_0.0.12"."sub_type" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "type_fr" text Unique NOT NULL,
        "type_en" text unique NOT NULL
    );


    CREATE TABLE "fertiscan_0.0.12"."specification" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "humidity" float,
    "ph" float,
    "solubility" float,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.12".label_information(id),
    "language" "fertiscan_0.0.12".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.12"."sub_label" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "text_content_fr" text NOT NULL DEFAULT '',
        "text_content_en" text NOT NULL DEFAULT '',
        "label_id" uuid NOT NULL REFERENCES "fertiscan_0.0.12"."label_information" ("id"),
        "edited" boolean NOT NULL,
        "sub_type_id" uuid NOT NULL REFERENCES "fertiscan_0.0.12"."sub_type" ("id")
    );

    CREATE TABLE "fertiscan_0.0.12"."micronutrient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text,
    "value" float,
    "unit" text ,
    "element_id" int REFERENCES "fertiscan_0.0.12".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.0.12".label_information(id),
    "edited" boolean,
    "language" "fertiscan_0.0.12".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.12"."guaranteed" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text,
    "value" float ,
    "unit" text ,
    "element_id" int REFERENCES "fertiscan_0.0.12".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.0.12".label_information(id),
    "edited" boolean
    );

    CREATE TABLE "fertiscan_0.0.12"."ingredient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "organic" boolean,
    "active" boolean,
    "name" text,
    "value" float,
    "unit" text,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.12".label_information(id),
    "language" "fertiscan_0.0.12".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.12"."inspection" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "verified" boolean DEFAULT false,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "inspector_id" uuid NOT NULL REFERENCES "fertiscan_0.0.12".users(id),
    "label_info_id" uuid REFERENCES "fertiscan_0.0.12".label_information(id),
    "sample_id" uuid REFERENCES "fertiscan_0.0.12".sample(id),
    "picture_set_id" uuid REFERENCES "fertiscan_0.0.12".picture_set(id),
    "original_dataset" json
    );

    CREATE TABLE "fertiscan_0.0.12"."fertilizer" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text UNIQUE NOT NULL,
    "registration_number" text,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "update_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "latest_inspection_id" uuid REFERENCES "fertiscan_0.0.12".inspection(id),
    "owner_id" uuid REFERENCES "fertiscan_0.0.12".organization(id)
    );

    Alter table "fertiscan_0.0.12".inspection ADD "fertilizer_id" uuid REFERENCES "fertiscan_0.0.12".fertilizer(id);

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
    BEFORE UPDATE ON  "fertiscan_0.0.12".users
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
    BEFORE UPDATE ON  "fertiscan_0.0.12".inspection
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
    BEFORE UPDATE ON  "fertiscan_0.0.12".fertilizer
    FOR EACH ROW
    EXECUTE FUNCTION update_fertilizer_timestamp();

    -- Trigger function for the `inspection` table
    CREATE OR REPLACE FUNCTION update_inspection_original_dataset_protection()
    RETURNS TRIGGER AS $$
    BEGIN
    IF (TG_OP = 'UPDATE') AND (OLD.original_dataset IS NULL) THEN
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') AND (OLD.original_dataset IS NOT NULL) THEN
        -- Protect the original dataset from being updated
        NEW.original_dataset = OLD.original_dataset;
        RETURN NEW;
    END IF;
    END;
    $$ LANGUAGE plpgsql;

    -- Trigger for the `inspection` table
    CREATE TRIGGER inspection_update_protect_original_dataset
    BEFORE UPDATE ON  "fertiscan_0.0.12".inspection_factual
    FOR EACH ROW
    EXECUTE FUNCTION update_inspection_original_dataset_protection();

    -- Insert the default types : [instruction, caution,first_aid, warranty]
    INSERT INTO "fertiscan_0.0.12".sub_type(type_fr,type_en) VALUES
    ('instructions','instructions'),
    ('mises_en_garde','cautions'),
    ('premier_soin','first_aid'),
    ('garanties','warranties');
end if;
END
$do$;
