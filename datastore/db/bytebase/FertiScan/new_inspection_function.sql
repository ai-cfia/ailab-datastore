
CREATE OR REPLACE FUNCTION "fertiscan_0.0.13".new_inspection(user_id uuid, picture_set_id uuid, input_json jsonb)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    label_info_id uuid;
    sub_type_rec RECORD;
    fr_values jsonb;
    en_values jsonb;
    record jsonb;
    inspection_id_value uuid;
    company_id uuid;
    location_id uuid;
	weight_id uuid;
	density_id uuid;
	volume_id uuid;
	micronutrient_id uuid;
    manufacturer_location_id uuid;
    manufacturer_id uuid;
	ingredient_id uuid;
	guaranteed_analysis_id uuid;
	time_id uuid;
    unit_id uuid;
    specification_id uuid;
    sub_label_id uuid;
    metric_type_id uuid;
	key_string text;
    read_value text;
    read_unit text;
    read_language text;
    value_float float;
    ingredient_language text;
	micronutrient_language text;
	name_string text;
	address_string text;
	website_string text;
	phone_number_string text;
    result_json jsonb := '{}';
	guaranteed_analysis_language text;
BEGIN
	
-- COMPANY
	name_string := input_json->'company'->>'name';
	address_string := input_json->'company'->>'address';
	website_string := input_json->'company'->>'website';
	phone_number_string := input_json->'company'->>'phone_number';
	IF COALESCE(name_string, 
		address_string, 
		website_string, 
		phone_number_string,
		 '') <> ''
	THEN
		company_id := "fertiscan_0.0.13".new_organization_info_located(
			input_json->'company'->>'name',
			input_json->'company'->>'address',
			input_json->'company'->>'website',
			input_json->'company'->>'phone_number',
			FALSE
		);
	
		-- Update input_json with company_id
		input_json := jsonb_set(input_json, '{company,id}', to_jsonb(company_id));
	END IF;
-- COMPANY END

-- MANUFACTURER
	name_string := input_json->'manufacturer'->>'name';
	address_string := input_json->'manufacturer'->>'address';
	website_string := input_json->'manufacturer'->>'website';
	phone_number_string := input_json->'manufacturer'->>'phone_number';
	-- Check if any of the manufacturer fields are not null
	IF COALESCE(name_string, 
		address_string, 
		website_string, 
		phone_number_string,
		 '') <> '' 
	THEN
		manufacturer_id := "fertiscan_0.0.13".new_organization_info_located(
			input_json->'manufacturer'->>'name',
			input_json->'manufacturer'->>'address',
			input_json->'manufacturer'->>'website',
			input_json->'manufacturer'->>'phone_number',
			FALSE
		);
		-- Update input_json with company_id
		input_json := jsonb_set(input_json, '{manufacturer,id}', to_jsonb(manufacturer_id));
	end if;
	-- Manufacturer end

-- LABEL INFORMATION
	label_info_id := "fertiscan_0.0.13".new_label_information(
		input_json->'product'->>'name',
		input_json->'product'->>'lot_number',
		input_json->'product'->>'npk',
		input_json->'product'->>'registration_number',
		(input_json->'product'->>'n')::float,
		(input_json->'product'->>'p')::float,
		(input_json->'product'->>'k')::float,
		input_json->'product'->>'guaranteed_title',
		input_json->'product'->>'guaranteed_titre',
		(input_json->'product'->>'guaranteed_analysis_is_minimal')::boolean,
		company_id,
		manufacturer_id
	);
		
	-- Update input_json with company_id
	input_json := jsonb_set(input_json, '{product,label_id}', to_jsonb(label_info_id));

--LABEL END

--WEIGHT
	-- Loop through each element in the 'weight' array
    FOR record IN SELECT * FROM jsonb_array_elements(input_json-> 'product' -> 'metrics' -> 'weight')
    LOOP
        -- Extract the value and unit from the current weight record
        read_value := record->>'value';
       -- CHECK IF ANY FIELD IS NOT NULL
		IF COALESCE(read_value,
			record->>'unit',
			'') <> '' 
		THEN
			-- Insert the new weight
			weight_id = "fertiscan_0.0.13".new_metric_unit(
				read_value::float,
				record->>'unit',
				label_info_id,
				'weight'::"fertiscan_0.0.13".metric_type,
				FALSE
			);
		END IF;
	 END LOOP;
-- Weight end
	
--DENSITY
 	read_value := input_json -> 'product' -> 'metrics' ->'density'->> 'value';
 	read_unit := input_json -> 'product' -> 'metrics' -> 'density'->> 'unit';
	-- Check if density_value is not null and handle density_unit
	IF read_value IS NOT NULL THEN
	    --CHECK IS ANY FIELD IS NOT NULL
		IF COALESCE(read_value,
			read_unit,
			'') <> ''
		THEN
			density_id := "fertiscan_0.0.13".new_metric_unit(
				read_value::float,
				read_unit,
				label_info_id,
				'density'::"fertiscan_0.0.13".metric_type,
				FALSE
			);
		END IF;
	END IF;
-- DENSITY END

--VOLUME
 	read_value := input_json -> 'product' -> 'metrics' -> 'volume'->> 'value';
 	read_unit := input_json -> 'product' -> 'metrics' -> 'volume'->> 'unit';
	-- Check if density_value is not null and handle density_unit
	IF read_value IS NOT NULL THEN
		value_float = read_value::float;
	  	-- CHECK IF ANY FIELD IS NOT NULL
		IF COALESCE(read_value,
			read_unit,
			'') <> '' 
		THEN
			-- Insert the new volume
			volume_id := "fertiscan_0.0.13".new_metric_unit(
				value_float,
				read_unit,
				label_info_id,
				'volume'::"fertiscan_0.0.13".metric_type,
				FALSE
			);
		END IF;
	END IF;
-- Volume end
   
-- SPECIFICATION
--	FOR ingredient_language IN SELECT * FROM jsonb_object_keys(input_json->'specifications')
--	LOOP
--		FOR record IN SELECT * FROM jsonb_array_elements(input_json->'specifications'->ingredient_language)
--		LOOP
--			-- Check if any of the fields are not null
--			IF COALESCE(record->>'humidity', 
--				record->>'ph', 
--				record->>'solubility',
--				'') <> '' 
--			THEN
--				-- Insert the new specification
--				specification_id := "fertiscan_0.0.13".new_specification(
--					(record->>'humidity')::float,
--					(record->>'ph')::float,
--					(record->>'solubility')::float,
--					ingredient_language::"fertiscan_0.0.13".language,
--					label_info_id,
--					FALSE
--				);	
--			END IF;
--		END LOOP;
--	END LOOP;
-- SPECIFICATION END

-- INGREDIENTS
--
--	-- Loop through each language ('en' and 'fr')
--    FOR ingredient_language  IN SELECT * FROM jsonb_object_keys(input_json->'ingredients')
--	LOOP
--        -- Loop through each ingredient in the current language
--        FOR record IN SELECT * FROM jsonb_array_elements(input_json->'ingredients'->ingredient_language )
--        LOOP
-- -- Extract values from the current ingredient record
--	        read_value := record->> 'value';
-- 			read_unit := record ->> 'unit';
--			-- Check if ANY field is not null
--			IF COALESCE(record->>'name', 
--				read_value, 
--				read_unit,
--				'') <> '' 
--			THEN
--				-- Insert the new ingredient
--				ingredient_id := "fertiscan_0.0.13".new_ingredient(
--					record->>'name',
--					read_value::float,
--					read_unit,
--					label_info_id,
--					ingredient_language::"fertiscan_0.0.13".language,
--					NULL, --We cant tell atm
--					NULL,  --We cant tell atm
--					FALSE  --preset
--				);
--			END IF;
--		END LOOP;
--	END LOOP;
--INGREDIENTS ENDS

-- SUB LABELS
	-- Loop through each sub_type
    FOR sub_type_rec IN SELECT id,type_en FROM sub_type
    LOOP
		-- Extract the French and English arrays for the current sub_type

		key_string := sub_type_rec.type_en;
        en_values := input_json -> key_string -> 'en';
    	fr_values := input_json -> key_string -> 'fr';
		key_string := key_string || '_ids';
        -- Ensure both arrays are of the same length
        IF jsonb_array_length(fr_values) = jsonb_array_length(en_values) THEN
		  	FOR i IN 0..(jsonb_array_length(fr_values) - 1)
	   		LOOP
	   			sub_label_id := "fertiscan_0.0.13".new_sub_label(
					fr_values->>i,
					en_values->>i,
					label_info_id,
					sub_type_rec.id,
					FALSE
				);
			END LOOP;
		END IF;
   END LOOP;    
  -- SUB_LABEL END
  
  -- MICRO NUTRIENTS
--		-- Loop through each language ('en' and 'fr')
--    FOR micronutrient_language  IN SELECT * FROM jsonb_object_keys(input_json->'micronutrients')
--	LOOP
--		FOR record IN SELECT * FROM jsonb_array_elements(input_json->'micronutrients'->micronutrient_language)
--		LOOP
--			-- Check if any of the fields are not null
--			IF COALESCE(record->>'name', 
--				record->>'value', 
--				record->>'unit',
--				'') <> '' 
--			THEN
--				-- Insert the new Micronutrient
--				micronutrient_id := "fertiscan_0.0.13".new_micronutrient(
--					record->> 'name',
--					(record->> 'value')::float,
--					record->> 'unit',
--					label_info_id,
--					micronutrient_language::"fertiscan_0.0.13".language
--				);
--			END IF;
--		END LOOP;
--	END LOOP;
--MICRONUTRIENTS ENDS

-- GUARANTEED

		-- Loop through each language ('en' and 'fr')
    FOR guaranteed_analysis_language  IN SELECT * FROM jsonb_object_keys(input_json->'guaranteed_analysis')
	LOOP
		FOR record IN SELECT * FROM jsonb_array_elements(input_json->'guaranteed_analysis'->guaranteed_analysis_language)
		LOOP
			-- Check if any of the fields are not null
			IF COALESCE(record->>'name', 
				record->>'value', 
				record->>'unit',
				'') <> '' 
			THEN
				-- Insert the new guaranteed_analysis
				guaranteed_analysis_id := "fertiscan_0.0.13".new_guaranteed_analysis(
					record->>'name',
					(record->>'value')::float,
					record->>'unit',
					label_info_id,
					FALSE,
					NULL, -- We arent handeling element_id yet
					guaranteed_analysis_language::"fertiscan_0.0.13".language
				);
			END IF;
		END LOOP;
	END LOOP;
-- GUARANTEED END	

-- INSPECTION
    INSERT INTO "fertiscan_0.0.13".inspection (
        inspector_id, label_info_id, sample_id, picture_set_id
    ) VALUES (
        user_id, -- Assuming inspector_id is handled separately
        label_info_id,
        NULL, -- NOT handled yet
        picture_set_id  -- Assuming picture_set_id is handled separately
    )
    RETURNING id INTO inspection_id_value;
   
	-- Update input_json with company_id
	input_json := jsonb_set(input_json, '{inspection_id}', to_jsonb(inspection_id_value));

	-- Update the Inspection_factual entry with the json
	UPDATE "fertiscan_0.0.13".inspection_factual
	SET original_dataset = input_json
	WHERE inspection_factual."inspection_id" = inspection_id_value;

-- INSPECTION END
	RETURN input_json;

END;
$function$
