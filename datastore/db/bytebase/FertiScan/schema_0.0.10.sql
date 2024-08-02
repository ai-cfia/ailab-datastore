--Schema creation "fertiscan_0.0.10"
DO
$do$
BEGIN
IF (EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'fertiscan_0.0.10')) THEN


    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    CREATE TABLE "fertiscan_0.0.10"."users" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "email" text NOT NULL UNIQUE,
    "registration_date" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp
    );

    -- CREATE A TYPE FOR FRENCH/ENGLISH LANGUAGE
    CREATE TYPE "fertiscan_0.0.10".LANGUAGE AS ENUM ('fr', 'en');

    CREATE TABLE "fertiscan_0.0.10"."picture_set" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    "picture_set" json NOT NULL,
    "owner_id" uuid NOT NULL REFERENCES "fertiscan_0.0.10".users(id),
    "upload_date" date NOT NULL DEFAULT current_timestamp,
    "name" text
    );
        
    alter table "fertiscan_0.0.10".users ADD "default_set_id" uuid REFERENCES "fertiscan_0.0.10".picture_set(id);

    CREATE TABLE "fertiscan_0.0.10"."picture" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    "picture" json NOT NULL,
    "nb_obj" int,
    "picture_set_id" uuid NOT NULL REFERENCES "fertiscan_0.0.10".picture_set(id),
    "verified" boolean NOT NULL DEFAULT false,
    "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "fertiscan_0.0.10"."province" (
    "id" SERIAL PRIMARY KEY,
    "name" text UNIQUE NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.10"."region" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "province_id" int REFERENCES "fertiscan_0.0.10".province(id),
    "name" text NOT NULL
    );

    CREATE TABLE "fertiscan_0.0.10"."location" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text,
    "address" text NOT NULL,
    "region_id" uuid References "fertiscan_0.0.10".region(id)
    );    
    
    CREATE TABLE "fertiscan_0.0.10"."organization_information" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "name" text NOT NULL,
        "website" text,
        "phone_number" text,
        "location_id" uuid REFERENCES "fertiscan_0.0.10".location(id)
    );

    CREATE TABLE "fertiscan_0.0.10"."organization" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "information_id" uuid REFERENCES "fertiscan_0.0.10".organization_information(id),
    "main_location_id" uuid REFERENCES "fertiscan_0.0.10".location(id)
    );


    Alter table "fertiscan_0.0.10".location ADD "owner_id" uuid REFERENCES "fertiscan_0.0.10".organization(id);

    CREATE TABLE "fertiscan_0.0.10"."sample" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "number" uuid,
    "collection_date" date,
    "location" uuid REFERENCES "fertiscan_0.0.10".location(id)
    );

    CREATE TABLE "fertiscan_0.0.10"."unit" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "unit" text NOT NULL,
    "to_si_unit" float
    );

    CREATE TABLE "fertiscan_0.0.10"."element_compound" (
    "id" SERIAL PRIMARY KEY,
    "number" int NOT NULL,
    "name_fr" text NOT NULL,
    "name_en" text NOT NULL,
    "symbol" text NOT NULL UNIQUE
    );

    CREATE TABLE "fertiscan_0.0.10"."label_information" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "lot_number" text,
    "npk" text,
    "registration_number" text,
    "n" float,
    "p" float,
    "k" float,
    "company_info_id" uuid REFERENCES "fertiscan_0.0.10".organization_information(id),
    "manufacturer_info_id" uuid REFERENCES "fertiscan_0.0.10".organization_information(id)
    );

    CREATE TYPE "fertiscan_0.0.10".metric_type as ENUM ('volume', 'weight','density');

    CREATE TABLE "fertiscan_0.0.10"."metric" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "value" float NOT NULL,
    "edited" boolean,
    "unit_id" uuid REFERENCES "fertiscan_0.0.10".unit(id),
    "metric_type" metric_type,
    "label_id" uuid REFERENCES "fertiscan_0.0.10".label_information(id)
    );

    CREATE TABLE "fertiscan_0.0.10"."sub_type" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "type_fr" text Unique NOT NULL,
        "type_en" text unique NOT NULL
    );


    CREATE TABLE "fertiscan_0.0.10"."specification" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "humidity" float,
    "ph" float,
    "solubility" float,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.10".label_information(id),
    "language" "fertiscan_0.0.10".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.10"."sub_label" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "text_content_fr" text NOT NULL DEFAULT '',
        "text_content_en" text NOT NULL DEFAULT '',
        "label_id" uuid NOT NULL REFERENCES "fertiscan_0.0.10"."label_information" ("id"),
        "edited" boolean NOT NULL,
        "sub_type_id" uuid NOT NULL REFERENCES "fertiscan_0.0.10"."sub_type" ("id")
    );

    CREATE TABLE "fertiscan_0.0.10"."micronutrient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text NOT NULL,
    "value" float NOT NULL,
    "unit" text NOT NULL,
    "element_id" int REFERENCES "fertiscan_0.0.10".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.0.10".label_information(id),
    "edited" boolean,
    "language" "fertiscan_0.0.10".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.10"."guaranteed" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "read_name" text NOT NULL,
    "value" float NOT NULL,
    "unit" text NOT NULL,
    "element_id" int REFERENCES "fertiscan_0.0.10".element_compound(id),
    "label_id" uuid REFERENCES "fertiscan_0.0.10".label_information(id),
    "edited" boolean
    );

    CREATE TABLE "fertiscan_0.0.10"."ingredient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "organic" boolean,
    "active" boolean,
    "name" text NOT NULL,
    "value" float,
    "unit" text,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.10".label_information(id),
    "language" "fertiscan_0.0.10".LANGUAGE
    );

    CREATE TABLE "fertiscan_0.0.10"."inspection" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "verified" boolean DEFAULT false,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "inspector_id" uuid NOT NULL REFERENCES "fertiscan_0.0.10".users(id),
    "label_info_id" uuid REFERENCES "fertiscan_0.0.10".label_information(id),
    "sample_id" uuid REFERENCES "fertiscan_0.0.10".sample(id),
    "picture_set_id" uuid REFERENCES "fertiscan_0.0.10".picture_set(id)
    );

    CREATE TABLE "fertiscan_0.0.10"."fertilizer" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" text UNIQUE NOT NULL,
    "registration_number" text,
    "upload_date" timestamp DEFAULT CURRENT_TIMESTAMP,
    "update_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "latest_inspection_id" uuid REFERENCES "fertiscan_0.0.10".inspection(id),
    "owner_id" uuid REFERENCES "fertiscan_0.0.10".organization(id)
    );

    Alter table "fertiscan_0.0.10".inspection ADD "fertilizer_id" uuid REFERENCES "fertiscan_0.0.10".fertilizer(id);

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
    BEFORE UPDATE ON  "fertiscan_0.0.10".users
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
    BEFORE UPDATE ON  "fertiscan_0.0.10".inspection
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
    BEFORE UPDATE ON  "fertiscan_0.0.10".fertilizer
    FOR EACH ROW
    EXECUTE FUNCTION update_fertilizer_timestamp();

    -- Insert the default types : [instruction, caution,first_aid, warranty]
    INSERT INTO "fertiscan_0.0.10".sub_type(type_fr,type_en) VALUES
    ('Instruction','Instruction'),
    ('Mise en garde','Caution'),
    ('Premier soin','First aid'),
    ('Garantie','Warranty');

 CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".new_inspection(user_id uuid, picture_set_id uuid, input_json jsonb)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    label_id uuid;
    sub_type_rec RECORD;
    fr_values jsonb;
    en_values jsonb;
    read_language text;
    record jsonb;
    inspection_id uuid;
    company_id uuid;
    location_id uuid;
    manufacturer_location_id uuid;
    manufacturer_id uuid;
    read_value text;
    read_unit text;
    metric_type_id uuid;
    value_float float;
    unit_id uuid;
    specification_id uuid;
    sub_label_id uuid;
    ingredient_language text;
    result_json jsonb := '{}';
BEGIN
	
-- COMPANY
	-- Check if company location exists by address
    SELECT id INTO location_id
    FROM location
    WHERE address ILIKE input_json->'company'->>'address'
    LIMIT 1;
   
	IF location_id IS NULL THEN 
        INSERT INTO location (address)
        VALUES (
            input_json->'company'->>'address'
        )
        RETURNING id INTO location_id;
    END IF;   
	INSERT INTO organization_information (name,website,phone_number,location_id)
	VALUES (
	        input_json->'company'->>'name',
            input_json->'company'->>'website',
            input_json->'company'->>'phone_number',
            location_id
	)
	RETURNING id INTO company_id;
	
	-- Update input_json with company_id
	input_json := jsonb_set(input_json, '{company,id}', to_jsonb(company_id));

-- COMPANY END

-- MANUFACTURER
	-- Check if company location exists by address
    SELECT id INTO location_id
    FROM location
    WHERE address ILIKE input_json->'manufacturer'->>'address'
	LIMIT 1;
   
	IF location_id IS NULL THEN 
        INSERT INTO location (address)
        VALUES (
            input_json->'manufacturer'->>'address'
        )
        RETURNING id INTO location_id;
    END IF;
	INSERT INTO organization_information (name,website,phone_number,location_id)
	VALUES (
	        input_json->'manufacturer'->>'name',
            input_json->'manufacturer'->>'website',
            input_json->'manufacturer'->>'phone_number',
            location_id
	)
	RETURNING id INTO manufacturer_id;
	
	-- Update input_json with company_id
	input_json := jsonb_set(input_json, '{manufacturer,id}', to_jsonb(manufacturer_id));
-- Manufacturer end

-- LABEL INFORMATION
    INSERT INTO label_information (
        lot_number, npk, registration_number, n, p, k, company_info_id, manufacturer_info_id
    ) VALUES (
        input_json->'product'->>'lot_number',
        input_json->'product'->>'npk',
        input_json->'product'->>'registration_number',
        (input_json->'product'->>'n')::float,
        (input_json->'product'->>'p')::float,
        (input_json->'product'->>'k')::float,
		company_id,
		manufacturer_id
    )
    RETURNING id INTO label_id;
		
	-- Update input_json with company_id
	input_json := jsonb_set(input_json, '{product,id}', to_jsonb(label_id));

--LABEL END

--WEIGHT
	-- Loop through each element in the 'weight' array
    FOR record IN SELECT * FROM jsonb_array_elements(input_json->'weight')
    LOOP
        -- Extract the value and unit from the current weight record
        read_value := record->>'value';
        read_unit := record->>'unit';

        -- Convert the weight value to float
        value_float := read_value::float;
       
       -- Check if the weight_unit exists in the unit table
	    SELECT id INTO unit_id FROM unit WHERE unit = read_unit;
	   
	   -- If unit_id is null, the unit does not exist
	    IF unit_id IS NULL THEN
	        -- Insert the new unit
	        INSERT INTO unit (unit, to_si_unit)
	        VALUES (read_unit, null) -- Adjust to_si_unit value as necessary
	        RETURNING id INTO unit_id;
	    END IF;
	   
	   	 -- Insert into metric for weight
	    INSERT INTO metric (value, unit_id, edited,metric_type_id,label_id)
	    VALUES (value_float, unit_id, FALSE,'weight'::"fertiscan_0.0.10".metric_type,label_id);
	 END LOOP;
-- Weight end
	
--DENSITY
 	read_value := input_json -> 'product' -> 'density'->> 'value';
 	read_unit := input_json -> 'product' -> 'density'->> 'unit';
	-- Check if density_value is not null and handle density_unit
	IF read_value IS NOT NULL THEN
		value_float = read_value::float;
	    -- Check if the density_unit exists in the unit table
	    SELECT id INTO unit_id FROM unit WHERE unit = read_unit;
	
	    -- If unit_id is null, the unit does not exist
	    IF unit_id IS NULL THEN
	        -- Insert the new unit
	        INSERT INTO unit (unit, to_si_unit)
	        VALUES (read_unit, null) -- Adjust to_si_unit value as necessary
	        RETURNING id INTO unit_id;
	    END IF;
	  
	   	 -- Insert into metric for weight
	    INSERT INTO metric (value, unit_id, edited,metric_type_id,label_id)
	    VALUES (value_float, unit_id, FALSE,'density'::"fertiscan_0.0.10".metric_type,label_id);
	END IF;
-- DENSITY END

--VOLUME
 	read_value := input_json -> 'product' -> 'volume'->> 'value';
 	read_unit := input_json -> 'product' -> 'volume'->> 'unit';
	-- Check if density_value is not null and handle density_unit
	IF read_value IS NOT NULL THEN
		value_float = read_value::float;
	    -- Check if the density_unit exists in the unit table
	    SELECT id INTO unit_id FROM unit WHERE unit = read_unit;
	
	    -- If unit_id is null, the unit does not exist
	    IF unit_id IS NULL THEN
	        -- Insert the new unit
	        INSERT INTO unit (unit, to_si_unit)
	        VALUES (read_unit, null) -- Adjust to_si_unit value as necessary
	        RETURNING id INTO unit_id;
	    END IF;

	   	 -- Insert into metric for weight
	    INSERT INTO metric (value, unit_id, edited,metric_type_id,label_id)
	    VALUES (value_float, unit_id, FALSE,'volume'::"fertiscan_0.0.10".metric_type,label_id);
	END IF;
-- Volume end
   
 -- SPECIFICATION
	FOR ingredient_language IN SELECT * FROM jsonb_object_keys(input_json->'specifications')
	LOOP
		FOR record IN SELECT * FROM jsonb_array_elements(input_json->'specifications'->ingredient_language)
		LOOP
			INSERT INTO specification (humidity, ph, solubility, edited,LANGUAGE,label_id)
			VALUES (
				(record->>'humidity')::float,
				(record->>'ph')::float,
				(record->>'solubility')::float,
				FALSE,
				ingredient_language::"nachet_0.0.10".language,
				label_id
			);
		END LOOP;
	END LOOP;
-- SPECIFICATION END

-- INGREDIENTS

	-- Loop through each language ('en' and 'fr')
    FOR ingredient_language  IN SELECT * FROM jsonb_object_keys(input_json->'ingredients')
	LOOP
        -- Loop through each ingredient in the current language
        FOR record IN SELECT * FROM jsonb_array_elements(input_json->'ingredients'->ingredient_language )
        LOOP
 -- Extract values from the current ingredient record
	        read_value := record->> 'value';
 			read_unit := record ->> 'unit';
 			value_float := read_value::float;
	        INSERT INTO ingredient (organic, active, name, value, unit, edited, label_id, language)
            VALUES (
                Null,  -- we cant tell
				Null,  -- We cant tell
                record->>'name',
                value_float,
                read_unit,
                FALSE, -- Assuming edited status
                label_id,  
                ingredient_language::"nachet_0.0.10".language
            );
		END LOOP;
	END LOOP;
--INGREDIENTS ENDS

-- SUB LABELS
	-- Loop through each sub_type
    FOR sub_type_rec IN SELECT id,type_en FROM sub_type
    LOOP
    	-- Extract the French and English arrays for the current sub_type
        fr_values := input_json->sub_type_rec.type_en->'fr';
        en_values := input_json->sub_type_rec.type_en->'en';
        -- Ensure both arrays are of the same length
        IF jsonb_array_length(fr_values) = jsonb_array_length(en_values) THEN
		  	FOR i IN 0..(jsonb_array_length(fr_values) - 1)
	   		LOOP
	   			INSERT INTO sub_label (text_content_fr,text_content_en, label_id, edited, sub_type_id)
	            VALUES (
	                fr_values->>i,
					en_values->>i,
					label_id,
					FALSE,
					sub_type_id
	            );
			END LOOP;
		END IF;
   END LOOP;    
  -- SUB_LABEL END
  
  -- MICRO NUTRIENTS
    	-- Extract the French and English arrays for the current 
	fr_values := input_json->sub_type_rec.type_en->'fr';
	en_values := input_json->sub_type_rec.type_en->'en';
	-- Ensure both arrays are of the same length
    --IF jsonb_array_length(fr_values) <> jsonb_array_length(en_values) THEN
	--	RAISE EXCEPTION 'French and English micronutrient arrays must be of the same length';
	FOR record IN SELECT * FROM jsonb_array_elements(en_values)
	LOOP
		INSERT INTO micronutrient (read_name, value, unit, edited, label_id,language)
		VALUES (
			record->> 'name',
	        (record->> 'value')::float,
	        record->> 'unit',
			FALSE,
			label_id,
			'en':: "fertiscan_0.0.10".language
		);
	END LOOP;
	FOR record IN SELECT * FROM jsonb_array_elements(fr_values)
	LOOP
		INSERT INTO micronutrient (read_name, value, unit, edited, label_id,language)
		VALUES (
			record->> 'name',
	        (record->> 'value')::float,
	        record->> 'unit',
			FALSE,
			label_id,
			'fr'::"nachet_0.0.10".language
		);
	END LOOP;
--MICRONUTRIENTS ENDS

-- GUARANTEED
	FOR record IN SELECT * FROM jsonb_array_elements(input_json->'guaranteed_analysis')
	LOOP
		INSERT INTO micronutrient (read_name, value, unit, edited, label_id)
			VALUES (
				record->> 'name',
	            (record->> 'value')::float,
	            record->> 'unit',
				FALSE,
				label_id
			);
	END LOOP;
-- GUARANTEED END	

-- INSPECTION
    INSERT INTO inspection (
        inspector_id, label_info_id, sample_id, picture_set_id
    ) VALUES (
        user_id, -- Assuming inspector_id is handled separately
        label_id,
        NULL, -- NOT handled yet
        picture_set_id  -- Assuming picture_set_id is handled separately
    )
    RETURNING id INTO inspection_id;
   
	-- Update input_json with company_id
	input_json := jsonb_set(input_json, '{inspection_id}', to_jsonb(inspection_id));

	RETURN input_json;

END;
$function$

END
$do$
