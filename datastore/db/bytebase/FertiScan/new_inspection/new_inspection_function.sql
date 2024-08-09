CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".new_inspection(user_id uuid, picture_set_id uuid, input_json jsonb)
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
	weight_id uuid;
	density_id uuid;
	volume_id uuid;
	micronutrient_id uuid;
    manufacturer_location_id uuid;
    manufacturer_id uuid;
	ingredient_id uuid;
	key_string text;
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
	company_id := "fertiscan_0.0.11".new_organization_located(
		input_json->'company'->>'name',
		input_json->'company'->>'address',
		input_json->'company'->>'website',
		input_json->'company'->>'phone_number'
	)
	
	-- Update input_json with company_id
	input_json := jsonb_set(input_json, '{company,id}', to_jsonb(company_id));

-- COMPANY END

-- MANUFACTURER
	manufacturer_id := "fertiscan_0.0.11".new_organization_located(
		input_json->'manufacturer'->>'name',
		input_json->'manufacturer'->>'address',
		input_json->'manufacturer'->>'website',
		input_json->'manufacturer'->>'phone_number'
	)
	
	-- Update input_json with company_id
	input_json := jsonb_set(input_json, '{manufacturer,id}', to_jsonb(manufacturer_id));
-- Manufacturer end

-- LABEL INFORMATION
	label_id := "fertiscan_0.0.11".new_label_information(
		input_json->'product'->>'name',
		input_json->'product'->>'lot_number',
		input_json->'product'->>'npk',
		input_json->'product'->>'registration_number',
		(input_json->'product'->>'n')::float,
		(input_json->'product'->>'p')::float,
		(input_json->'product'->>'k')::float,
		company_id,
		manufacturer_id
	)
		
	-- Update input_json with company_id
	input_json := jsonb_set(input_json, '{product,label_id}', to_jsonb(label_id));

--LABEL END

--WEIGHT
	-- Loop through each element in the 'weight' array
    FOR record IN SELECT * FROM jsonb_array_elements(input_json->'weight')
    LOOP
        -- Extract the value and unit from the current weight record
        read_value := record->>'value';
       
       weight_id = "fertiscan_0.0.11".new_metric_unit(
			read_value::float,
			record->>'unit',
			label_id,
			'weight'::"fertiscan_0.0.11".metric_type
		);
	 END LOOP;
-- Weight end
	
--DENSITY
 	read_value := input_json -> 'product' -> 'density'->> 'value';
 	read_unit := input_json -> 'product' -> 'density'->> 'unit';
	-- Check if density_value is not null and handle density_unit
	IF read_value IS NOT NULL THEN
	    
		density_id := "fertiscan_0.0.11".new_metric_unit(
			read_value::float,
			read_unit,
			label_id,
			'density'::"fertiscan_0.0.11".metric_type
		);

	END IF;
-- DENSITY END

--VOLUME
 	read_value := input_json -> 'product' -> 'volume'->> 'value';
 	read_unit := input_json -> 'product' -> 'volume'->> 'unit';
	-- Check if density_value is not null and handle density_unit
	IF read_value IS NOT NULL THEN
		value_float = read_value::float;
	  
		volume_id := "fertiscan_0.0.11".new_metric_unit(
			value_float,
			read_unit,
			label_id,
			'volume'::"fertiscan_0.0.11".metric_type
		);

	END IF;
-- Volume end
   
 -- SPECIFICATION
	FOR ingredient_language IN SELECT * FROM jsonb_object_keys(input_json->'specifications')
	LOOP
		FOR record IN SELECT * FROM jsonb_array_elements(input_json->'specifications'->ingredient_language)
		LOOP
			specification_id := "fertiscan_0.0.11".new_specification(
				(record->>'humidity')::float,
				(record->>'ph')::float,
				(record->>'solubility')::float,
				ingredient_language::"fertiscan_0.0.11".language,
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
	        
			ingredient_id := "fertiscan_0.0.11".new_ingredient(
				record->>'name',
				read_value::float,
				read_unit,
				label_id,
				ingredient_language::"fertiscan_0.0.11".language,
				NULL, --We cant tell atm
				NULL  --We cant tell atm
			);
		END LOOP;
	END LOOP;
--INGREDIENTS ENDS

-- SUB LABELS
	-- Loop through each sub_type
    FOR sub_type_rec IN SELECT id,type_en FROM sub_type
    LOOP
		-- Extract the French and English arrays for the current sub_type
        
		key_string := sub_type_rec.type_en + '_' + 'fr';
    	fr_values := input_json->key_string;

		key_string := sub_type_rec.type_en + '_' + 'en';
        en_values := input_json->key_string;

        -- Ensure both arrays are of the same length
        IF jsonb_array_length(fr_values) = jsonb_array_length(en_values) THEN
		  	FOR i IN 0..(jsonb_array_length(fr_values) - 1)
	   		LOOP
	   				sub_label_id := "fertiscan_0.0.11".new_sub_label(
						fr_values->>i,
						en_values->>i,
						label_id,
						sub_type_rec.id
					);
			END LOOP;
		END IF;
   END LOOP;    
  -- SUB_LABEL END
  
  -- MICRO NUTRIENTS
	en_values := input_json->'micronutrients_en';
	fr_values := input_json->'micronutrients_fr';
	--	RAISE EXCEPTION 'French and English micronutrient arrays must be of the same length';
	FOR record IN SELECT * FROM jsonb_array_elements(en_values)
	LOOP
		micronutrient_id := "fertiscan_0.0.11".new_micronutrient(
			record->> 'name',
			(record->> 'value')::float,
			record->> 'unit',
			label_id,
			'en'::"fertiscan_0.0.11".language
		);
	END LOOP;
	FOR record IN SELECT * FROM jsonb_array_elements(fr_values)
	LOOP
		micronutrient_id := "fertiscan_0.0.11".new_micronutrient(
			record->> 'name',
			(record->> 'value')::float,
			record->> 'unit',
			label_id,
			'fr'::"fertiscan_0.0.11".language
		);
	END LOOP;
--MICRONUTRIENTS ENDS

-- GUARANTEED
	FOR record IN SELECT * FROM jsonb_array_elements(input_json->'guaranteed_analysis')
	LOOP
		"fertiscan_0.0.11".new_guaranteed_analysis(
			record->>'name',
			(record->>'value')::float,
			record->>'unit',
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
