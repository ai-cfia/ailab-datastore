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
				ingredient_language::"fertiscan_0.0.10".language,
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
                ingredient_language::"fertiscan_0.0.10".language
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
			'fr'::"fertiscan_0.0.10".language
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
$function$;

-- Function to upsert location information based on location_id and address
CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".upsert_location(location_id uuid, address text)
RETURNS uuid AS $$
DECLARE
    new_location_id uuid;
BEGIN
    -- Upsert the location
    INSERT INTO "fertiscan_0.0.10".location (id, address)
    VALUES (COALESCE(location_id, "fertiscan_0.0.10".uuid_generate_v4()), address)
    ON CONFLICT (id) -- Specify the unique constraint column for conflict handling
    DO UPDATE SET address = EXCLUDED.address
    RETURNING id INTO new_location_id;

    RETURN new_location_id;
END;
$$ LANGUAGE plpgsql;


-- Function to upsert organization information
CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".upsert_organization_info(input_org_info jsonb)
RETURNS uuid AS $$
DECLARE
    organization_info_id uuid;
    location_id uuid;
BEGIN
    -- Fetch location_id from the address if it exists
    SELECT id INTO location_id
    FROM "fertiscan_0.0.10".location
    WHERE address = input_org_info->>'address'
    LIMIT 1;

    -- Use upsert_location to insert or update the location
    location_id := "fertiscan_0.0.10".upsert_location(location_id, input_org_info->>'address');

    -- Extract the organization info ID from the input JSON or generate a new UUID if not provided
    organization_info_id := COALESCE(NULLIF(input_org_info->>'id', '')::uuid, "fertiscan_0.0.10".uuid_generate_v4());

    -- Upsert organization information
    INSERT INTO "fertiscan_0.0.10".organization_information (id, name, website, phone_number, location_id)
    VALUES (
        organization_info_id,
        input_org_info->>'name',
        input_org_info->>'website',
        input_org_info->>'phone_number',
        location_id
    )
    ON CONFLICT (id) DO UPDATE
    SET name = EXCLUDED.name,
        website = EXCLUDED.website,
        phone_number = EXCLUDED.phone_number,
        location_id = EXCLUDED.location_id
    RETURNING id INTO organization_info_id;

    RETURN organization_info_id;
END;
$$ LANGUAGE plpgsql;


-- Function to upsert label information
CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".upsert_label_information(
    input_label jsonb,
    company_info_id uuid,
    manufacturer_info_id uuid
)
RETURNS uuid AS $$
DECLARE
    label_id uuid;
BEGIN
    -- Extract or generate the label ID
    label_id := COALESCE(NULLIF(input_label->>'id', '')::uuid, "fertiscan_0.0.10".uuid_generate_v4());

    -- Upsert label information
    INSERT INTO "fertiscan_0.0.10".label_information (
        id, lot_number, npk, registration_number, n, p, k, company_info_id, manufacturer_info_id
    )
    VALUES (
        label_id,
        input_label->>'lot_number',
        input_label->>'npk',
        input_label->>'registration_number',
        (NULLIF(input_label->>'n', '')::float),
        (NULLIF(input_label->>'p', '')::float),
        (NULLIF(input_label->>'k', '')::float),
        company_info_id,
        manufacturer_info_id
    )
    ON CONFLICT (id) DO UPDATE
    SET lot_number = EXCLUDED.lot_number,
        npk = EXCLUDED.npk,
        registration_number = EXCLUDED.registration_number,
        n = EXCLUDED.n,
        p = EXCLUDED.p,
        k = EXCLUDED.k,
        company_info_id = EXCLUDED.company_info_id,
        manufacturer_info_id = EXCLUDED.manufacturer_info_id
    RETURNING id INTO label_id;

    RETURN label_id;
END;
$$ LANGUAGE plpgsql;


-- Function to update metrics: delete old and insert new
CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".update_metrics(
    p_label_id uuid,
    metrics jsonb
)
RETURNS void AS $$
DECLARE
    metric_record jsonb;
    metric_type text;
    metric_value float;
    metric_unit text;
    unit_id uuid;
BEGIN
    -- Delete existing metrics for the given label_id
    DELETE FROM "fertiscan_0.0.10".metric WHERE label_id = p_label_id;

    -- Handle weight metrics separately
    IF metrics ? 'weight' THEN
        FOR metric_record IN SELECT * FROM jsonb_array_elements(metrics->'weight')
        LOOP
            metric_value := NULLIF(metric_record->>'value', '')::float;
            metric_unit := metric_record->>'unit';
            
            -- Proceed only if the value is not NULL
            IF metric_value IS NOT NULL THEN
                -- Fetch or insert the unit ID
                SELECT id INTO unit_id FROM "fertiscan_0.0.10".unit WHERE unit = metric_unit LIMIT 1;
                IF unit_id IS NULL THEN
                    INSERT INTO "fertiscan_0.0.10".unit (unit) VALUES (metric_unit) RETURNING id INTO unit_id;
                END IF;

                -- Insert metric record for weight
                INSERT INTO "fertiscan_0.0.10".metric (id, value, unit_id, metric_type, label_id)
                VALUES ("fertiscan_0.0.10".uuid_generate_v4(), metric_value, unit_id, 'weight'::"fertiscan_0.0.10".metric_type, p_label_id);
            END IF;
        END LOOP;
    END IF;

    -- Handle density and volume metrics
    FOREACH metric_type IN ARRAY ARRAY['density', 'volume']
    LOOP
        IF metrics ? metric_type THEN
            metric_record := metrics->metric_type;
            metric_value := NULLIF(metric_record->>'value', '')::float;
            metric_unit := metric_record->>'unit';

            -- Proceed only if the value is not NULL
            IF metric_value IS NOT NULL THEN
                -- Fetch or insert the unit ID
                SELECT id INTO unit_id FROM "fertiscan_0.0.10".unit WHERE unit = metric_unit LIMIT 1;
                IF unit_id IS NULL THEN
                    INSERT INTO "fertiscan_0.0.10".unit (unit) VALUES (metric_unit) RETURNING id INTO unit_id;
                END IF;

                -- Insert metric record
                INSERT INTO "fertiscan_0.0.10".metric (id, value, unit_id, metric_type, label_id)
                VALUES ("fertiscan_0.0.10".uuid_generate_v4(), metric_value, unit_id, metric_type::"fertiscan_0.0.10".metric_type, p_label_id);
            END IF;
        END IF;
    END LOOP;

END;
$$ LANGUAGE plpgsql;


-- Function to update specifications: delete old and insert new
CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".update_specifications(
    p_label_id uuid,
    new_specifications jsonb
)
RETURNS void AS $$
DECLARE
    spec_language text;
    spec_record jsonb;
BEGIN
    -- Delete existing specifications for the given label_id
    DELETE FROM "fertiscan_0.0.10".specification WHERE label_id = p_label_id;

    -- Insert new specifications
    FOR spec_language IN SELECT * FROM jsonb_object_keys(new_specifications)
    LOOP
        FOR spec_record IN SELECT * FROM jsonb_array_elements(new_specifications -> spec_language)
        LOOP
            -- Insert each specification record
            INSERT INTO "fertiscan_0.0.10".specification (
                humidity, ph, solubility, edited, label_id, language
            )
            VALUES (
                (spec_record->>'humidity')::float,
                (spec_record->>'ph')::float,
                (spec_record->>'solubility')::float,
                FALSE,  -- not handled
                p_label_id,
                spec_language::"fertiscan_0.0.10".language
            );
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- Function to update ingredients: delete old and insert new
CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".update_ingredients(
    p_label_id uuid,
    new_ingredients jsonb
)
RETURNS void AS $$
DECLARE
    ingredient_language text;
    ingredient_record jsonb;
BEGIN
    -- Delete existing ingredients for the given label_id
    DELETE FROM "fertiscan_0.0.10".ingredient WHERE label_id = p_label_id;

    -- Insert new ingredients
    FOR ingredient_language IN SELECT * FROM jsonb_object_keys(new_ingredients)
    LOOP
        FOR ingredient_record IN SELECT * FROM jsonb_array_elements(new_ingredients -> ingredient_language)
        LOOP
            -- Insert each ingredient record
            INSERT INTO "fertiscan_0.0.10".ingredient (
                organic, active, name, value, unit, edited, label_id, language
            )
            VALUES (
                NULL, -- not yet handled
                NULL, -- not yet handled
                ingredient_record->>'name',
                NULLIF(ingredient_record->>'value', '')::float,
                ingredient_record->>'unit',
                FALSE, -- not yet handled
                p_label_id,
                ingredient_language::"fertiscan_0.0.10".language
            );
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- Function to update micronutrients: delete old and insert new
CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".update_micronutrients(
    p_label_id uuid,
    new_micronutrients jsonb
)
RETURNS void AS $$
DECLARE
    nutrient_language text;
    nutrient_record jsonb;
BEGIN
    -- Delete existing micronutrients for the given label_id
    DELETE FROM "fertiscan_0.0.10".micronutrient WHERE label_id = p_label_id;

    -- Insert new micronutrients
    FOR nutrient_language IN SELECT * FROM jsonb_object_keys(new_micronutrients)
    LOOP
        FOR nutrient_record IN SELECT * FROM jsonb_array_elements(new_micronutrients -> nutrient_language)
        LOOP
            -- Insert each micronutrient record
            INSERT INTO "fertiscan_0.0.10".micronutrient (
                read_name, value, unit, edited, label_id, language
            )
            VALUES (
                nutrient_record->>'name',
                NULLIF(nutrient_record->>'value', '')::float,
                nutrient_record->>'unit',
                FALSE,  -- not handled
                p_label_id,
                nutrient_language::"fertiscan_0.0.10".language
            );
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- Function to update guaranteed analysis: delete old and insert new
CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".update_guaranteed(
    p_label_id uuid,
    new_guaranteed jsonb
)
RETURNS void AS $$
DECLARE
    guaranteed_record jsonb;
BEGIN
    -- Delete existing guaranteed analysis for the given label_id
    DELETE FROM "fertiscan_0.0.10".guaranteed WHERE label_id = p_label_id;

    -- Insert new guaranteed analysis
    FOR guaranteed_record IN SELECT * FROM jsonb_array_elements(new_guaranteed)
    LOOP
        -- Insert each guaranteed analysis record
        INSERT INTO "fertiscan_0.0.10".guaranteed (
            read_name, value, unit, edited, label_id
        )
        VALUES (
            guaranteed_record->>'name',
            NULLIF(guaranteed_record->>'value', '')::float,
            guaranteed_record->>'unit',
            FALSE,  -- not handled
            p_label_id
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- Function to update sub labels: delete old and insert new
CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".update_sub_labels(
    p_label_id uuid,
    new_sub_labels jsonb
)
RETURNS void AS $$
DECLARE
    sub_type_rec RECORD;
    fr_values jsonb;
    en_values jsonb;
    i int;
BEGIN
    -- Delete existing sub labels for the given label_id
    DELETE FROM "fertiscan_0.0.10".sub_label WHERE label_id = p_label_id;

    -- Loop through each sub_type
    FOR sub_type_rec IN SELECT id, type_en FROM "fertiscan_0.0.10".sub_type
    LOOP
        -- Extract the French and English arrays for the current sub_type
        fr_values := new_sub_labels->sub_type_rec.type_en->'fr';
        en_values := new_sub_labels->sub_type_rec.type_en->'en';
        
        -- Ensure both arrays are of the same length
        IF jsonb_array_length(fr_values) = jsonb_array_length(en_values) THEN
            FOR i IN 0..(jsonb_array_length(fr_values) - 1)
            LOOP
                -- Insert sub label record
                INSERT INTO "fertiscan_0.0.10".sub_label (
                    text_content_fr, text_content_en, label_id, edited, sub_type_id
                )
                VALUES (
                    fr_values->>i,
                    en_values->>i,
                    p_label_id,
                    FALSE,  -- not handled
                    sub_type_rec.id
                );
            END LOOP;
        ELSE
            RAISE NOTICE 'Mismatch in number of French and English sub-labels for type %', sub_type_rec.type_en;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- Function to upsert inspection information
CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".upsert_inspection(
    p_inspection_id uuid,
    p_label_info_id uuid,
    p_inspector_id uuid,
    p_sample_id uuid,
    p_picture_set_id uuid,
    p_verified boolean
)
RETURNS uuid AS $$
DECLARE
    inspection_id uuid;
BEGIN
    -- Use provided inspection_id or generate a new one if not provided
    inspection_id := COALESCE(p_inspection_id, "fertiscan_0.0.10".uuid_generate_v4());

    -- Upsert inspection information
    INSERT INTO "fertiscan_0.0.10".inspection (
        id, label_info_id, inspector_id, sample_id, picture_set_id, verified, upload_date, updated_at
    )
    VALUES (
        inspection_id,
        p_label_info_id,
        p_inspector_id,
        NULL,  -- not handled yet
        p_picture_set_id,
        p_verified,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (id) DO UPDATE
    SET 
        label_info_id = EXCLUDED.label_info_id,
        inspector_id = EXCLUDED.inspector_id,
        sample_id = NULL,  -- not handled yet
        picture_set_id = EXCLUDED.picture_set_id,
        verified = EXCLUDED.verified,
        updated_at = CURRENT_TIMESTAMP  -- Update timestamp on conflict
    RETURNING id INTO inspection_id;

    RETURN inspection_id;
END;
$$ LANGUAGE plpgsql;


-- Function to upsert fertilizer information based on unique fertilizer name
CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".upsert_fertilizer(
    p_name text,
    p_registration_number text,
    p_owner_id uuid,
    p_latest_inspection_id uuid
)
RETURNS uuid AS $$
DECLARE
    fertilizer_id uuid;
BEGIN
    -- Upsert fertilizer information
    INSERT INTO "fertiscan_0.0.10".fertilizer (
        name, registration_number, upload_date, update_at, owner_id, latest_inspection_id
    )
    VALUES (
        p_name,
        p_registration_number,
        CURRENT_TIMESTAMP,  -- Set upload date to current timestamp
        CURRENT_TIMESTAMP,  -- Set update date to current timestamp
        p_owner_id,
        p_latest_inspection_id
    )
    ON CONFLICT (name) DO UPDATE
    SET
        registration_number = EXCLUDED.registration_number,
        update_at = CURRENT_TIMESTAMP,  -- Update the update_at timestamp
        owner_id = EXCLUDED.owner_id,
        latest_inspection_id = EXCLUDED.latest_inspection_id
    RETURNING id INTO fertilizer_id;

    RETURN fertilizer_id;
END;
$$ LANGUAGE plpgsql;


-- Function to update inspection data and related entities, returning an updated JSON
CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".update_inspection(
    p_inspection_id uuid,
    p_inspector_id uuid,
    p_input_json jsonb
)
RETURNS jsonb AS $$
DECLARE
    inspection_id uuid := p_inspection_id;
    json_inspection_id uuid;
    company_info_id uuid;
    manufacturer_info_id uuid;
    label_info_id uuid;
    organization_id uuid;
    updated_json jsonb := p_input_json;
    fertilizer_name text;
    registration_number text;
    verified boolean;
    existing_inspector_id uuid;
BEGIN
    -- Check if the provided inspection_id matches the one in the input JSON
    json_inspection_id := (p_input_json->>'inspection_id')::uuid;
    IF json_inspection_id IS NOT NULL AND json_inspection_id != inspection_id THEN
        RAISE EXCEPTION 'Inspection ID mismatch: % vs %', inspection_id, json_inspection_id;
    END IF;

    -- Check if the provided inspector_id matches the existing one
    SELECT inspector_id INTO existing_inspector_id
    FROM "fertiscan_0.0.10".inspection
    WHERE id = p_inspection_id;
    IF existing_inspector_id IS NULL OR existing_inspector_id != p_inspector_id THEN
        RAISE EXCEPTION 'Unauthorized: Inspector ID mismatch or inspection not found';
    END IF;

    -- Upsert company information and get the ID
    company_info_id := "fertiscan_0.0.10".upsert_organization_info(p_input_json->'company');
    updated_json := jsonb_set(updated_json, '{company,id}', to_jsonb(company_info_id));

    -- Upsert manufacturer information and get the ID
    manufacturer_info_id := "fertiscan_0.0.10".upsert_organization_info(p_input_json->'manufacturer');
    updated_json := jsonb_set(updated_json, '{manufacturer,id}', to_jsonb(manufacturer_info_id));

    -- Upsert label information and get the ID
    label_info_id := "fertiscan_0.0.10".upsert_label_information(
        p_input_json->'product',
        company_info_id,
        manufacturer_info_id
    );
    updated_json := jsonb_set(updated_json, '{product,id}', to_jsonb(label_info_id));

    -- Update metrics related to the label
    PERFORM "fertiscan_0.0.10".update_metrics(label_info_id, p_input_json->'product'->'metrics');

    -- Update specifications related to the label
    PERFORM "fertiscan_0.0.10".update_specifications(label_info_id, p_input_json->'specifications');

    -- Update ingredients related to the label
    PERFORM "fertiscan_0.0.10".update_ingredients(label_info_id, p_input_json->'ingredients');

    -- Update micronutrients related to the label
    PERFORM "fertiscan_0.0.10".update_micronutrients(label_info_id, p_input_json->'micronutrients');

    -- Update guaranteed analysis related to the label
    PERFORM "fertiscan_0.0.10".update_guaranteed(label_info_id, p_input_json->'guaranteed_analysis');

    -- Update sub labels related to the label
    PERFORM "fertiscan_0.0.10".update_sub_labels(label_info_id, p_input_json->'sub_labels');

    -- Update the inspection record
    verified := (p_input_json->'product'->>'verified')::boolean;
    inspection_id := "fertiscan_0.0.10".upsert_inspection(
        p_inspection_id,
        label_info_id,
        p_inspector_id,
        COALESCE(p_input_json->>'sample_id', NULL)::uuid,
        COALESCE(p_input_json->>'picture_set_id', NULL)::uuid,
        verified
    );

    -- Update the inspection ID in the output JSON
    updated_json := jsonb_set(updated_json, '{inspection_id}', to_jsonb(inspection_id));

    -- Check if the verified field is true, and upsert fertilizer if so
    IF verified THEN
        fertilizer_name := p_input_json->'product'->>'name';
        registration_number := p_input_json->'product'->>'registration_number';

        -- Insert organization and get the organization_id
        INSERT INTO "fertiscan_0.0.10".organization (information_id, main_location_id)
        VALUES (company_info_id, NULL) -- main_location_id not yet handled
        RETURNING id INTO organization_id;

        -- Upsert the fertilizer record
        PERFORM "fertiscan_0.0.10".upsert_fertilizer(
            fertilizer_name,
            registration_number,
            organization_id,
            inspection_id
        );
    END IF;

    -- Return the updated JSON without fertilizer_id
    RETURN updated_json;

END;
$$ LANGUAGE plpgsql;

END
$do$
