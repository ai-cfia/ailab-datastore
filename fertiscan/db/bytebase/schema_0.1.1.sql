

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    CREATE TABLE "fertiscan_0.1.1".roles (
        "id" int PRIMARY KEY,
        "name" text NOT NULL
    );

    CREATE TABLE "fertiscan_0.1.1".permission (
        "id" int PRIMARY KEY,
        "name" text NOT NULL
    );

    INSERT INTO "fertiscan_0.1.1".roles (id, name) VALUES
    (1, 'dev'),
    (2, 'admin'),
    (3, 'team leader'),
    (4, 'inspector');

    INSERT INTO "fertiscan_0.1.1".permission (id, name) VALUES
    (1, 'read'),
    (2, 'write'),
    (3, 'owner');


    CREATE TABLE "fertiscan_0.1.1"."users" (
    "id" uuid PRIMARY KEY DEFAULT uuid_.uuid_generate_v4(),
    "email" text NOT NULL UNIQUE,
    "registration_date" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp,
    "role_id" INT NOT NULL DEFAULT 4 REFERENCES "fertiscan_0.1.1".roles(id)
    );

    Create table "fertiscan_0.1.1"."groups" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "name" text NOT NULL,
        "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "created_by_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".users(id)
    );

    Create table "fertiscan_0.1.1"."user_group" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "user_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".users(id) ON DELETE CASCADE,
        "group_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".groups(id) ON DELETE CASCADE,
        "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "assigned_by_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".users(id),
        "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "permission_id" INT NOT NULL DEFAULT 1 REFERENCES "fertiscan_0.1.1".permission(id),
        UNIQUE ("user_id", "group_id")
    );

    CREATE TABLE "fertiscan_0.1.1"."container" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "name" text,
        "is_public" boolean NOT NULL DEFAULT false,
        "storage_prefix" text default 'user',
        "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "created_by_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".users(id) ON DELETE SET NULL,
        "last_updated_by_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".users(id)
    );

    CREATE TABLE "fertiscan_0.1.1"."container_user" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "user_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".users(id) ON DELETE cascade,
        "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "created_by_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".users(id) ON DELETE SET NULL,
        "last_updated_by_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".users(id) ON DELETE SET NULL,
        "container_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".container(id) ON DELETE CASCADE,
        "permission_id" INT NOT NULL DEFAULT 1 REFERENCES "fertiscan_0.1.1".permission(id),
        UNIQUE ("user_id", "container_id")
    );

    CREATE TABLE "fertiscan_0.1.1"."container_group" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "group_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".groups(id) ON DELETE cascade,
        "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "created_by_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".users(id) ON DELETE SET NULL,
        "last_updated_by_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".users(id) ON DELETE SET NULL,
        "container_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".container(id) ON DELETE CASCADE,
        "permission_id" INT NOT NULL DEFAULT 1 REFERENCES "fertiscan_0.1.1".permission(id),
        UNIQUE ("group_id", "container_id")
    );

    CREATE TABLE "fertiscan_0.1.1"."picture_set" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "picture_set" json NOT NULL,
        "owner_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".users(id),
        "upload_date" date NOT NULL DEFAULT current_timestamp,
        "name" text NOT NULL,
        "container_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".container(id) ON DELETE CASCADE,
        "parent_id" uuid REFERENCES "fertiscan_0.1.1".picture_set(id) ON DELETE CASCADE
    );
    
    CREATE TABLE "fertiscan_0.1.1"."picture" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "picture" json NOT NULL,
        "picture_set_id" uuid NOT null,
        "nb_obj" integer NOT NULL,
        "verified" boolean NOT NULL DEFAULT false,
        "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY ("picture_set_id") REFERENCES "fertiscan_0.1.1"."picture_set"(id) ON DELETE CASCADE
    );

    -- CREATE A TYPE FOR FRENCH/ENGLISH LANGUAGE
    CREATE TYPE "fertiscan_0.1.1".LANGUAGE AS ENUM ('fr', 'en');

    CREATE TABLE "fertiscan_0.1.1"."province" (
    "id" SERIAL PRIMARY KEY,
    "name" text UNIQUE NOT NULL
    );

    CREATE TABLE "fertiscan_0.1.1"."region" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "province_id" int REFERENCES "fertiscan_0.1.1".province(id),
    "name" text NOT NULL
    );

    CREATE TABLE "fertiscan_0.1.1"."unit" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "unit" text NOT NULL,
    "to_si_unit" float
    );

    CREATE TABLE "fertiscan_0.1.1"."element_compound" (
    "id" SERIAL PRIMARY KEY,
    "number" int NOT NULL,
    "name_fr" text NOT NULL,
    "name_en" text NOT NULL,
    "symbol" text NOT NULL UNIQUE
    );

    CREATE TABLE "fertiscan_0.1.1"."label_information" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "product_name" text,
    "lot_number" text,
    "npk" text,
    "n" float,
    "p" float,
    "k" float,
    "guaranteed_title_en" text,
    "guaranteed_title_fr" text,
    "title_is_minimal" boolean,
    "record_keeping" boolean
    );
    
    CREATE TABLE "fertiscan_0.1.1"."label_dimension" (
    "label_id" uuid PRIMARY KEY,
    "organization_info_ids" uuid[] DEFAULT '{}',
    "instructions_ids" uuid[] DEFAULT '{}',
    "cautions_ids" uuid[] DEFAULT '{}',
    "first_aid_ids" uuid[] DEFAULT '{}',
    "warranties_ids" uuid[] DEFAULT '{}',
    "specification_ids" uuid[] DEFAULT '{}',
    "ingredient_ids" uuid[] DEFAULT '{}',
    "micronutrient_ids" uuid[] DEFAULT '{}',
    "guaranteed_ids" uuid[] DEFAULT '{}',
    "registration_number_ids" uuid[] DEFAULT '{}',
    "weight_ids" uuid[] DEFAULT '{}',
    "volume_ids" uuid[] DEFAULT '{}',
    "density_ids" uuid[] DEFAULT '{}'
    );

    CREATE TABLE "fertiscan_0.1.1"."time_dimension" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "date_value" date,
    "year" int,
    "month" int,
    "day" int,
    "month_name" text,
    "day_name" text
    );

    CREATE TABLE "fertiscan_0.1.1"."inspection_factual" (
    "inspection_id" uuid PRIMARY KEY,
    "inspector_id" uuid ,
    "label_info_id" uuid ,
    "time_id" uuid REFERENCES "fertiscan_0.1.1".time_dimension(id),
    "sample_id" uuid,
    "picture_set_id" uuid,
    "inspection_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "original_dataset" json
    );

    CREATE TABLE "fertiscan_0.1.1"."organization_information" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "name" text,
        "website" text,
        "phone_number" text,
        "address" text,
        "edited" boolean DEFAULT false,
        "label_id" uuid REFERENCES "fertiscan_0.1.1".label_information(id) ON DELETE CASCADE,
        "is_main_contact" boolean DEFAULT false NOT NULL,
        CONSTRAINT check_not_all_null CHECK (
            (name IS NOT NULL)::integer +
            (website IS NOT NULL)::integer +
            (phone_number IS NOT NULL)::integer +
            (address IS NOT NULL)::integer >= 1)
    );
   
   
    CREATE TABLE "fertiscan_0.1.1"."location" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text,
    "address" text NOT NULL,
    "address_number" text,
    "city" text,
    "postal_code" text,
    "region_id" uuid REFERENCES "fertiscan_0.1.1".region(id)
    );    
   
    CREATE TABLE "fertiscan_0.1.1"."organization" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text UNIQUE NOT NULL,
    "website" text,
    "phone_number" text,
    "address" text,
    "main_location_id" uuid REFERENCES "fertiscan_0.1.1".location(id),
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
    );
   
    Alter table "fertiscan_0.1.1".location ADD "organization_id" uuid REFERENCES "fertiscan_0.1.1".organization(id);

    CREATE TABLE "fertiscan_0.1.1"."sample" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "number" uuid,
    "collection_date" date,
    "location" uuid REFERENCES "fertiscan_0.1.1".location(id)
    );
   
    CREATE TYPE "fertiscan_0.1.1".metric_type as ENUM ('volume', 'weight','density');

    CREATE TABLE "fertiscan_0.1.1"."metric" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "value" float,
    "edited" boolean,
    "unit_id" uuid REFERENCES "fertiscan_0.1.1".unit(id),
    "metric_type" "fertiscan_0.1.1".metric_type,
    "label_id" uuid REFERENCES "fertiscan_0.1.1".label_information(id) ON DELETE CASCADE,
    CONSTRAINT check_not_all_null CHECK (
        (value IS NOT NULL)::integer +
        (unit_id IS NOT NULL)::integer >= 1)
    );

    CREATE TABLE "fertiscan_0.1.1"."sub_type" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "type_fr" text Unique NOT NULL,
        "type_en" text unique NOT NULL
    );

    CREATE TABLE "fertiscan_0.1.1"."registration_number_information" (
        "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        "identifier" text NOT NULL,
        "name" text,
        "is_an_ingredient" BOOLEAN,
        "label_id" uuid REFERENCES "fertiscan_0.1.1".label_information(id) ON DELETE CASCADE,
        "edited" BOOLEAN DEFAULT FALSE
    );

    CREATE TABLE "fertiscan_0.1.1"."specification" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "humidity" float,
    "ph" float,
    "solubility" float,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.1.1".label_information(id) ON DELETE CASCADE,
    "language" "fertiscan_0.1.1".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.1.1"."sub_label" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "text_content_fr" text NOT NULL DEFAULT '',
        "text_content_en" text NOT NULL DEFAULT '',
        "label_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1"."label_information" ("id") ON DELETE CASCADE,
        "edited" boolean, --this is because with the current upsert we can not determine if it was edited or not
        "sub_type_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1"."sub_type" ("id"),
        CONSTRAINT check_not_all_null CHECK (
            (COALESCE(sub_label.text_content_en, '') <> '') OR
            (COALESCE(sub_label.text_content_fr, '') <> '')
        )
    );

    CREATE TABLE "fertiscan_0.1.1"."micronutrient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text,
    "value" float,
    "unit" text ,
    "element_id" int REFERENCES "fertiscan_0.1.1".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.1.1".label_information(id) ON DELETE CASCADE,
    "edited" boolean,
    "language" "fertiscan_0.1.1".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.1.1"."guaranteed" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text,
    "value" float ,
    "unit" text ,
    "language" "fertiscan_0.1.1".LANGUAGE,
    "element_id" int REFERENCES "fertiscan_0.1.1".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.1.1".label_information(id) ON DELETE CASCADE,
    "edited" boolean,
    CONSTRAINT check_not_all_null CHECK (
        (read_name IS NOT NULL)::integer +
        (value IS NOT NULL)::integer +
        (unit IS NOT NULL)::integer >= 1)
    );

    CREATE TABLE "fertiscan_0.1.1"."ingredient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "organic" boolean,
    "active" boolean,
    "name" text,
    "value" float,
    "unit" text,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.1.1".label_information(id) ON DELETE CASCADE,
    "language" "fertiscan_0.1.1".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.1.1"."inspection" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "verified" boolean DEFAULT false,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "inspector_id" uuid NOT NULL REFERENCES "fertiscan_0.1.1".users(id),
    "label_info_id" uuid REFERENCES "fertiscan_0.1.1".label_information(id) ON DELETE CASCADE,
    "sample_id" uuid REFERENCES "fertiscan_0.1.1".sample(id),
    "container_id" uuid REFERENCES "fertiscan_0.1.1".container(id),
    "picture_set_id" uuid REFERENCES "fertiscan_0.1.1".picture_set(id),
    "inspection_comment" text,
    "verified_date" timestamp default null
    );

    CREATE TABLE "fertiscan_0.1.1"."fertilizer" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text UNIQUE NOT NULL,
    "registration_number" text,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "update_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "latest_inspection_id" uuid REFERENCES "fertiscan_0.1.1".inspection(id) ON DELETE SET NULL,
    "main_contact_id" uuid REFERENCES "fertiscan_0.1.1".organization(id) ON DELETE SET NULL 
    );-- It should actually try to seek if there are any other organization that can be found under the latest_inspection organisation_information instead of setting it to null

    Alter table "fertiscan_0.1.1".inspection ADD "fertilizer_id" uuid REFERENCES "fertiscan_0.1.1".fertilizer(id);

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
    BEFORE UPDATE ON  "fertiscan_0.1.1".users
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
    BEFORE UPDATE ON  "fertiscan_0.1.1".inspection
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
    BEFORE UPDATE ON  "fertiscan_0.1.1".fertilizer
    FOR EACH ROW
    EXECUTE FUNCTION update_fertilizer_timestamp();

    -- Trigger function for the `organization` table
    CREATE OR REPLACE FUNCTION update_organization_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Trigger for the `organization` table
    CREATE TRIGGER organization_update_before
    BEFORE UPDATE ON  "fertiscan_0.1.1".organization
    FOR EACH ROW
    EXECUTE FUNCTION update_organization_timestamp();

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
    BEFORE UPDATE ON  "fertiscan_0.1.1".inspection_factual
    FOR EACH ROW
    EXECUTE FUNCTION update_inspection_original_dataset_protection();

    -- Insert the default types : [instruction, caution,first_aid, warranty]
    INSERT INTO "fertiscan_0.1.1".sub_type(type_fr,type_en) VALUES
    ('instructions','instructions'),
    ('mises_en_garde','cautions');
 --   ('premier_soin','first_aid'), -- We are not using this anymore
 --   ('garanties','warranties'); -- we are not using this anymore
