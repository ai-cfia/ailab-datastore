--Schema creation "fertiscan_0.0.16"
DO
$do$
BEGIN
IF (EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'fertiscan_0.0.16')) THEN


    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    CREATE TABLE "fertiscan_0.0.16"."users" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "email" text NOT NULL UNIQUE,
    "registration_date" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp
    );

    -- CREATE A TYPE FOR FRENCH/ENGLISH LANGUAGE
    CREATE TYPE "fertiscan_0.0.16".LANGUAGE AS ENUM ('fr', 'en');

    CREATE TABLE "fertiscan_0.0.16"."picture_set" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    "picture_set" json NOT NULL,
    "owner_id" uuid NOT NULL REFERENCES "fertiscan_0.0.16".users(id),
    "upload_date" date NOT NULL DEFAULT current_timestamp,
    "name" text
    );
        
    alter table "fertiscan_0.0.16".users ADD "default_set_id" uuid REFERENCES "fertiscan_0.0.16".picture_set(id);

    CREATE TABLE "fertiscan_0.0.16"."picture" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    "picture" json NOT NULL,
    "nb_obj" int,
    "picture_set_id" uuid NOT NULL REFERENCES "fertiscan_0.0.16".picture_set(id),
    "verified" boolean NOT NULL DEFAULT false,
    "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "fertiscan_0.0.16"."province" (
    "id" SERIAL PRIMARY KEY,
    "name" text UNIQUE NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.16"."region" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "province_id" int REFERENCES "fertiscan_0.0.16".province(id),
    "name" text NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.16"."location" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text,
    "address" text NOT NULL,
    "region_id" uuid REFERENCES "fertiscan_0.0.16".region(id)
    );    
    
    CREATE TABLE "fertiscan_0.0.16"."organization_information" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "name" text,
        "website" text,
        "phone_number" text,
        "location_id" uuid REFERENCES "fertiscan_0.0.16".location(id),
        "edited" boolean DEFAULT false
    );

    CREATE TABLE "fertiscan_0.0.16"."organization" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "information_id" uuid REFERENCES "fertiscan_0.0.16".organization_information(id),
    "main_location_id" uuid REFERENCES "fertiscan_0.0.16".location(id)
    );


    Alter table "fertiscan_0.0.16".location ADD "owner_id" uuid REFERENCES "fertiscan_0.0.16".organization(id);

    CREATE TABLE "fertiscan_0.0.16"."sample" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "number" uuid,
    "collection_date" date,
    "location" uuid REFERENCES "fertiscan_0.0.16".location(id)
    );

    CREATE TABLE "fertiscan_0.0.16"."unit" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "unit" text NOT NULL,
    "to_si_unit" float
    );

    CREATE TABLE "fertiscan_0.0.16"."element_compound" (
    "id" SERIAL PRIMARY KEY,
    "number" int NOT NULL,
    "name_fr" text NOT NULL,
    "name_en" text NOT NULL,
    "symbol" text NOT NULL UNIQUE
    );

    CREATE TABLE "fertiscan_0.0.16"."label_information" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "product_name" text,
    "lot_number" text,
    "npk" text,
    "registration_number" text,
    "n" float,
    "p" float,
    "k" float,
    "guaranteed_title_en" text,
    "guaranteed_title_fr" text,
    "title_is_minimal" boolean,
    "company_info_id" uuid REFERENCES "fertiscan_0.0.16".organization_information(id),
    "manufacturer_info_id" uuid REFERENCES "fertiscan_0.0.16".organization_information(id)
    );
    
    CREATE TABLE "fertiscan_0.0.16"."label_dimension" (
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

    CREATE TABLE "fertiscan_0.0.16"."time_dimension" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "date_value" date,
    "year" int,
    "month" int,
    "day" int,
    "month_name" text,
    "day_name" text
    );

    CREATE TABLE "fertiscan_0.0.16"."inspection_factual" (
    "inspection_id" uuid PRIMARY KEY,
    "inspector_id" uuid ,
    "label_info_id" uuid ,
    "time_id" uuid REFERENCES "fertiscan_0.0.16".time_dimension(id),
    "sample_id" uuid,
    "company_id" uuid,
    "manufacturer_id" uuid,
    "picture_set_id" uuid,
    "inspection_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "original_dataset" json
    );


    CREATE TYPE "fertiscan_0.0.16".metric_type as ENUM ('volume', 'weight','density');

    CREATE TABLE "fertiscan_0.0.16"."metric" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "value" float,
    "edited" boolean,
    "unit_id" uuid REFERENCES "fertiscan_0.0.16".unit(id),
    "metric_type" "fertiscan_0.0.16".metric_type,
    "label_id" uuid REFERENCES "fertiscan_0.0.16".label_information(id) ON DELETE CASCADE
    );

    CREATE TABLE "fertiscan_0.0.16"."sub_type" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "type_fr" text Unique NOT NULL,
        "type_en" text unique NOT NULL
    );


    CREATE TABLE "fertiscan_0.0.16"."specification" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "humidity" float,
    "ph" float,
    "solubility" float,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.16".label_information(id) ON DELETE CASCADE,
    "language" "fertiscan_0.0.16".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.16"."sub_label" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "text_content_fr" text NOT NULL DEFAULT '',
        "text_content_en" text NOT NULL DEFAULT '',
        "label_id" uuid NOT NULL REFERENCES "fertiscan_0.0.16"."label_information" ("id") ON DELETE CASCADE,
        "edited" boolean, --this is because with the current upsert we can not determine if it was edited or not
        "sub_type_id" uuid NOT NULL REFERENCES "fertiscan_0.0.16"."sub_type" ("id")
    );

    CREATE TABLE "fertiscan_0.0.16"."micronutrient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text,
    "value" float,
    "unit" text ,
    "element_id" int REFERENCES "fertiscan_0.0.16".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.0.16".label_information(id) ON DELETE CASCADE,
    "edited" boolean,
    "language" "fertiscan_0.0.16".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.16"."guaranteed" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text,
    "value" float ,
    "unit" text ,
    "language" "fertiscan_0.0.16".LANGUAGE,
    "element_id" int REFERENCES "fertiscan_0.0.16".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.0.16".label_information(id) ON DELETE CASCADE,
    "edited" boolean
    );

    CREATE TABLE "fertiscan_0.0.16"."ingredient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "organic" boolean,
    "active" boolean,
    "name" text,
    "value" float,
    "unit" text,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.16".label_information(id) ON DELETE CASCADE,
    "language" "fertiscan_0.0.16".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.16"."inspection" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "verified" boolean DEFAULT false,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "inspector_id" uuid NOT NULL REFERENCES "fertiscan_0.0.16".users(id),
    "label_info_id" uuid REFERENCES "fertiscan_0.0.16".label_information(id) ON DELETE CASCADE,
    "sample_id" uuid REFERENCES "fertiscan_0.0.16".sample(id),
    "picture_set_id" uuid REFERENCES "fertiscan_0.0.16".picture_set(id),
    "inspection_comment" text
    );

    CREATE TABLE "fertiscan_0.0.16"."fertilizer" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text UNIQUE NOT NULL,
    "registration_number" text,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "update_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "latest_inspection_id" uuid REFERENCES "fertiscan_0.0.16".inspection(id) ON DELETE CASCADE,
    "owner_id" uuid REFERENCES "fertiscan_0.0.16".organization(id)
    );

    Alter table "fertiscan_0.0.16".inspection ADD "fertilizer_id" uuid REFERENCES "fertiscan_0.0.16".fertilizer(id);

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
    BEFORE UPDATE ON  "fertiscan_0.0.16".users
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
    BEFORE UPDATE ON  "fertiscan_0.0.16".inspection
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
    BEFORE UPDATE ON  "fertiscan_0.0.16".fertilizer
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
    BEFORE UPDATE ON  "fertiscan_0.0.16".inspection_factual
    FOR EACH ROW
    EXECUTE FUNCTION update_inspection_original_dataset_protection();

    -- Insert the default types : [instruction, caution,first_aid, warranty]
    INSERT INTO "fertiscan_0.0.16".sub_type(type_fr,type_en) VALUES
    ('instructions','instructions'),
    ('mises_en_garde','cautions');
    --   ('premier_soin','first_aid'), -- We are not using this anymore
    --   ('garanties','warranties'); -- we are not using this anymore


    -- Utility views
    CREATE OR REPLACE VIEW "fertiscan_0.0.16".located_organization_information_view AS
    SELECT 
        org_info.id AS id,
        org_info.name AS name,
        loc.address AS address,
        org_info.website AS website,
        org_info.phone_number AS phone_number
    FROM 
        "fertiscan_0.0.16".organization_information org_info
    LEFT JOIN 
        "fertiscan_0.0.16".location loc 
    ON 
        org_info.location_id = loc.id;

        
    CREATE OR REPLACE VIEW "fertiscan_0.0.16".label_company_manufacturer_json_view AS
    SELECT 
        label_info.id AS label_id,
        jsonb_build_object(
            'id', company_info.id,
            'name', company_info.name,
            'address', company_info.address,
            'website', company_info.website,
            'phone_number', company_info.phone_number
        ) AS company,
        jsonb_build_object(
            'id', manufacturer_info.id,
            'name', manufacturer_info.name,
            'address', manufacturer_info.address,
            'website', manufacturer_info.website,
            'phone_number', manufacturer_info.phone_number
        ) AS manufacturer
    FROM 
        "fertiscan_0.0.16".label_information label_info
    LEFT JOIN 
        "fertiscan_0.0.16".located_organization_information_view company_info 
        ON label_info.company_info_id = company_info.id
    LEFT JOIN 
        "fertiscan_0.0.16".located_organization_information_view manufacturer_info 
        ON label_info.manufacturer_info_id = manufacturer_info.id;


    CREATE OR REPLACE VIEW "fertiscan_0.0.16".full_location_view AS
    SELECT
        location.id AS id,
        location.name AS name,
        location.address AS address,
        location.owner_id AS owner_id,
        region.id AS region_id,
        region.name AS region_name,
        province.id AS province_id,
        province.name AS province_name
    FROM
        "fertiscan_0.0.16".location
    LEFT JOIN
        "fertiscan_0.0.16".region ON location.region_id = region.id
    LEFT JOIN
        "fertiscan_0.0.16".province ON region.province_id = province.id;


    CREATE OR REPLACE VIEW "fertiscan_0.0.16".full_organization_view AS
    SELECT 
        organization.id, 
        information.name, 
        information.website, 
        information.phone_number,
        location.id AS location_id, 
        location.name AS location_name,
        location.address AS location_address,
        location.region_id AS region_id,
        location.region_name AS region_name,
        location.province_id AS province_id,
        location.province_name AS province_name
    FROM
        "fertiscan_0.0.16".organization AS organization
    LEFT JOIN
        "fertiscan_0.0.16".organization_information AS information 
        ON organization.information_id = information.id
    LEFT JOIN
        "fertiscan_0.0.16".full_location_view AS location 
        ON organization.main_location_id = location.id;


    CREATE OR REPLACE VIEW "fertiscan_0.0.16".full_guaranteed_view AS
    SELECT
        g.id, 
        g.read_name,
        g.value,
        g.unit,
        ec.name_fr as element_name_fr,
        ec.name_en as element_name_en,
        ec.symbol as element_symbol,
        g.edited,
        CONCAT(CAST(g.read_name AS TEXT), ' ', g.value, ' ', g.unit) AS reading
    FROM 
        "fertiscan_0.0.16".guaranteed g
    JOIN 
        "fertiscan_0.0.16".element_compound ec ON g.element_id = ec.id;

end if;
END
$do$;
