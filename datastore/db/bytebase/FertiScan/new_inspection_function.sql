-- Function to register a new inspection
CREATE OR REPLACE FUNCTION new_inspection(user_id uuid,picture_set_id uuid,input_json jsonb)
RETURNS uuid AS $$
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
    manufacturer_id uuid;
    label_info_id uuid;
    read_value text;
    read_unit text;
    metric_type_id uuid;
    value_float float;
   unit_id uuid;
  org_id uuid;
  i int;
BEGIN
	
-- COMPANY
	-- Check if company location exists by address
    SELECT id INTO location_id
    FROM "fertiscan_0.0.7".location
    WHERE address ILIKE input_json->'company'->>'address'
    LIMIT 1;
   
   IF location_id NULL THEN 
        INSERT INTO "fertiscan_0.0.7".location (address)
        VALUES (
            input_json->'company'->>'address'
        )
        RETURNING id INTO location_id;
       
	INSERT INTO "fertiscan_0.0.7".organization_information (name,website,phone_number,location_id)
	VALUES (
	        input_json->'company'->>'name',
            input_json->'company'->>'website',
            input_json->'company'->>'phone_number',
            location_id
	)
	RETURNING id INTO company_id;
-- COMPANY END

-- MANUFACTURER
	-- Check if company location exists by address
    SELECT id INTO location_id
    FROM "fertiscan_0.0.7".location
    WHERE address ILIKE input_json->'manufacturer'->>'address'
    LIMIT 1;
   
   IF location_id NULL THEN 
        INSERT INTO "fertiscan_0.0.7".location (address)
        VALUES (
            input_json->'manufacturer'->>'address'
        )
        RETURNING id INTO location_id;
       
	INSERT INTO "fertiscan_0.0.7".organization_information (name,website,phone_number,location_id)
	VALUES (
	        input_json->'manufacturer'->>'name',
            input_json->'manufacturer'->>'website',
            input_json->'manufacturer'->>'phone_number',
            location_id
	)
	RETURNING id INTO manufacturer_id;
-- Manufacturer end

--LABEL INFORMATION
    INSERT INTO "fertiscan_0.0.7".label_information (
        lot_number, npk, registration_number, n, p, k, weight, density, volume
    ) VALUES (
        input_json->'product'->>'lot_number',
        input_json->'product'->>'npk',
        input_json->'product'->>'registration_number',
        (input_json->'product'->>'n')::float,
        (input_json->'product'->>'p')::float,
        (input_json->'product'->>'k')::float,
    )
    RETURNING id INTO label_info_id;

    RETURN label_id;
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
	    SELECT id INTO unit_id FROM "fertiscan_0.0.6".unit WHERE unit = read_unit;
	   
	   -- If unit_id is null, the unit does not exist
	    IF unit_id IS NULL THEN
	        -- Insert the new unit
	        INSERT INTO "fertiscan_0.0.6".unit (unit, to_si_unit)
	        VALUES (read_unit, null) -- Adjust to_si_unit value as necessary
	        RETURNING id INTO unit_id;
	    END IF;
	   
	   SELECT id INTO metric_type_id FROM "fertiscan_0.0.6".metric_type WHERE type ILIKE 'weight';
	   
	   	 -- Insert into metric for weight
	    INSERT INTO "fertiscan_0.0.6".metric (value, unit_id, edited,metric_type_id,label_id)
	    VALUES (value_float, unit_id, FALSE,metric_type_id,label_id);
-- Weight end
	
--DENSITY
 	read_value := input_json -> 'product' -> 'density'->> 'value'
 	read_unit := := input_json -> 'product' -> 'density'->> 'unit'
	-- Check if density_value is not null and handle density_unit
	IF read_value IS NOT NULL THEN
		value_float = read_value::float
	    -- Check if the density_unit exists in the unit table
	    SELECT id INTO unit_id FROM "fertiscan_0.0.6".unit WHERE unit = read_unit;
	
	    -- If unit_id is null, the unit does not exist
	    IF unit_id IS NULL THEN
	        -- Insert the new unit
	        INSERT INTO "fertiscan_0.0.6".unit (unit, to_si_unit)
	        VALUES (read_unit, null) -- Adjust to_si_unit value as necessary
	        RETURNING id INTO unit_id;
	    END IF;
	
	   SELECT id INTO metric_type_id FROM "fertiscan_0.0.6".metric_type WHERE type ILIKE 'density';
	  
	   	 -- Insert into metric for weight
	    INSERT INTO "fertiscan_0.0.6".metric (value, unit_id, edited,metric_type_id,label_id)
	    VALUES (value_float, unit_id, FALSE,metric_type_id,label_id);
	END IF;
-- DENSITY END

--VOLUME
 	read_value := input_json -> 'product' -> 'volume'->> 'value'
 	read_unit := := input_json -> 'product' -> 'volume'->> 'unit'
	-- Check if density_value is not null and handle density_unit
	IF read_value IS NOT NULL THEN
		value_float = read_value::float
	    -- Check if the density_unit exists in the unit table
	    SELECT id INTO unit_id FROM "fertiscan_0.0.6".unit WHERE unit = read_unit;
	
	    -- If unit_id is null, the unit does not exist
	    IF unit_id IS NULL THEN
	        -- Insert the new unit
	        INSERT INTO "fertiscan_0.0.6".unit (unit, to_si_unit)
	        VALUES (read_unit, null) -- Adjust to_si_unit value as necessary
	        RETURNING id INTO unit_id;
	    END IF;
	
	   SELECT id INTO metric_type_id FROM "fertiscan_0.0.6".metric_type WHERE type ILIKE 'volume';
	  
	   	 -- Insert into metric for weight
	    INSERT INTO "fertiscan_0.0.6".metric (value, unit_id, edited,metric_type_id,label_id)
	    VALUES (value_float, unit_id, FALSE,metric_type_id,label_id);
	END IF;
-- Volume end
   
 -- SPECIFICATION
    INSERT INTO "fertiscan_0.0.6".specification (humidity, ph, solubility, edited,LANGUAGE,label_id)
    VALUES (
 			input_json->'specifications'->'en'->>'humidity',
    		input_json->'specifications'->'en'->>'ph',
   			input_json->'specifications'->'en'->>'solubility',
   			FALSE,
   			'en',
   			label_id
    )
    RETURNING id INTO specification_id;
-- SPECIFICATION END

-- INGREDIENTS
   --ORGANIC
   -- Loop through each language ('en' and 'fr')
    FOR ingredient_language  IN SELECT * FROM jsonb_object_keys(input_json->'organic_ingredients')
    LOOP
        -- Loop through each ingredient in the current language
        FOR record IN SELECT * FROM jsonb_array_elements(input_json->'organic_ingredients'->ingredient_language )
        LOOP
            -- Extract values from the current ingredient record
	        read_value := record->> 'value'
 			read_unit := := record ->> 'unit'
 			float_value := read_value::float
	        INSERT INTO "fertiscan_0.0.7".ingredient (organic, name, value, unit, edited, label_id, language)
            VALUES (
                TRUE,  -- Assuming all are organic ingredients
                record->>'nutrient',
                float_value,
                read_unit,
                FALSE, -- Assuming edited status
                label_id,  
                ingredient_language
            );
        END LOOP;
    END LOOP;
   -- INORGANIC
      -- Loop through each language ('en' and 'fr')
    FOR ingredient_language  IN SELECT * FROM jsonb_object_keys(input_json->'organic_ingredients')
    LOOP
    	-- Loop through each ingredient in the current language
        FOR read_value IN SELECT * FROM jsonb_array_elements_text(input_json->'organic_ingredients'->ingredient_language )
        LOOP
        	INSERT INTO "fertiscan_0.0.7".ingredient (organic, name, value, unit, edited, label_id, language)
            VALUES (
                TRUE,  -- Assuming all are organic ingredients
                read_value,
                NULL,
                NULL,
                FALSE, -- Assuming edited status
                label_id,  
                ingredient_language
            );
        END LOOP;
    END LOOP;
--INGREDIENTS ENDS

-- SUB LABELS
	-- Loop through each sub_type
    FOR sub_type_rec IN SELECT type_en FROM sub_type
    LOOP
    	-- Extract the French and English arrays for the current sub_type
        fr_values := input_json->sub_type_rec.type_en->'fr';
        en_values := input_json->sub_type_rec.type_en->'en';
        -- Ensure both arrays are of the same length
        IF jsonb_array_length(fr_values) = jsonb_array_length(en_values) THEN
		  	FOR i IN 0..cardinality(jsonb_array_elements_text(fr_values)-1)
	   		LOOP
	   			INSERT INTO "fertiscan_0.0.7".sub_label (text_content_fr,text_content_en, label_id, edited, sub_type_id)
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
-- TODO: MIght not be the same!!!---------------------------------------------------
    IF jsonb_array_length(fr_values) = jsonb_array_length(en_values) THEN
		FOR record IN jsonb_array_elements(en_values)
	   	LOOP
	   		INSERT INTO "fertiscan_0.0.7".micronutrient (read_name, value, unit, edited, label_id,language)
			VALUES (
				record->> 'nutrient',
	            (record->> 'value')::float,
	            record->> 'unit',
				FALSE,
				label_id,
				'en'
			);
		END LOOP;
		FOR read_value IN jsonb_array_elements(fr_values)
			INSERT INTO "fertiscan_0.0.7".micronutrient (read_name, value, unit, edited, label_id,language)
			VALUES (
				record->> 'nutrient',
	            (record->> 'value')::float,
	            record->> 'unit',
				FALSE,
				label_id,
				'fr'
			);
		END LOOP;
	END IF;
--MICRONUTRIENTS ENDS

-- GUARANTEED
	FOR record IN jsonb_array_elements(input_json->'guaranteed_analysis')
	LOOP
		INSERT INTO "fertiscan_0.0.7".micronutrient (read_name, value, unit, edited, label_id)
			VALUES (
				record->> 'nutrient',
	            (record->> 'value')::float,
	            record->> 'unit',
				FALSE,
				label_id
			);
	END LOOP;
-- GUARANTEED END	

-- INSPECTION
    INSERT INTO "fertiscan_0.0.7".inspection (
        inspector_id, label_info_id, sample_id, company_id, manufacturer_id, picture_set_id
    ) VALUES (
        user_id, -- Assuming inspector_id is handled separately
        label_id,
        NULL, -- NOT handled yet
        NULL, -- Updated once the org info ARE confirmed
        NULL, -- Updated once the org info ARE confirmed
        picture_set_id  -- Assuming picture_set_id is handled separately
    )
    RETURNING id INTO inspection_id;

    RETURN inspection_id;
END;
$$ LANGUAGE plpgsql;
