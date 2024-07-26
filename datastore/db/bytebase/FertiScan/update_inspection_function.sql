-- Function to upsert location information based on location_id and address
CREATE OR REPLACE FUNCTION "fertiscan_0.0.8".upsert_location(location_id uuid, address text)
RETURNS uuid AS $$
DECLARE
    new_location_id uuid;
BEGIN
    -- Upsert the location
    INSERT INTO "fertiscan_0.0.8".location (id, address)
    VALUES (COALESCE(location_id, "fertiscan_0.0.8".uuid_generate_v4()), address)
    ON CONFLICT (id) -- Specify the unique constraint column for conflict handling
    DO UPDATE SET address = EXCLUDED.address
    RETURNING id INTO new_location_id;

    RETURN new_location_id;
END;
$$ LANGUAGE plpgsql;


-- Function to upsert organization information
CREATE OR REPLACE FUNCTION "fertiscan_0.0.8".upsert_organization_info(input_org_info jsonb)
RETURNS uuid AS $$
DECLARE
    organization_info_id uuid;
    location_id uuid;
BEGIN
    -- Fetch location_id from the address if it exists
    SELECT id INTO location_id
    FROM "fertiscan_0.0.8".location
    WHERE address = input_org_info->>'address'
    LIMIT 1;

    -- Use upsert_location to insert or update the location
    location_id := "fertiscan_0.0.8".upsert_location(location_id, input_org_info->>'address');

    -- Extract the organization info ID from the input JSON or generate a new UUID if not provided
    organization_info_id := COALESCE(NULLIF(input_org_info->>'id', '')::uuid, "fertiscan_0.0.8".uuid_generate_v4());

    -- Upsert organization information
    INSERT INTO "fertiscan_0.0.8".organization_information (id, name, website, phone_number, location_id)
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
CREATE OR REPLACE FUNCTION "fertiscan_0.0.8".upsert_label_information(
    input_label jsonb,
    company_info_id uuid,
    manufacturer_info_id uuid
)
RETURNS uuid AS $$
DECLARE
    label_id uuid;
BEGIN
    -- Extract or generate the label ID
    label_id := COALESCE(NULLIF(input_label->>'id', '')::uuid, "fertiscan_0.0.8".uuid_generate_v4());

    -- Upsert label information
    INSERT INTO "fertiscan_0.0.8".label_information (
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
CREATE OR REPLACE FUNCTION "fertiscan_0.0.8".update_metrics(
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
    DELETE FROM "fertiscan_0.0.8".metric WHERE label_id = p_label_id;

    -- Handle weight metrics separately
    IF metrics ? 'weight' THEN
        FOR metric_unit IN SELECT * FROM jsonb_object_keys(metrics->'weight')
        LOOP
            metric_value := NULLIF(metrics->'weight'->>metric_unit, '')::float;
            
            -- Proceed only if the value is not NULL
            IF metric_value IS NOT NULL THEN
                -- Fetch or insert the unit ID
                SELECT id INTO unit_id FROM "fertiscan_0.0.8".unit WHERE unit = metric_unit LIMIT 1;
                IF unit_id IS NULL THEN
                    INSERT INTO "fertiscan_0.0.8".unit (unit) VALUES (metric_unit) RETURNING id INTO unit_id;
                END IF;

                -- Insert metric record for weight
                INSERT INTO "fertiscan_0.0.8".metric (id, value, unit_id, metric_type, label_id)
                VALUES ("fertiscan_0.0.8".uuid_generate_v4(), metric_value, unit_id, 'weight', p_label_id);
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
                SELECT id INTO unit_id FROM "fertiscan_0.0.8".unit WHERE unit = metric_unit LIMIT 1;
                IF unit_id IS NULL THEN
                    INSERT INTO "fertiscan_0.0.8".unit (unit) VALUES (metric_unit) RETURNING id INTO unit_id;
                END IF;

                -- Insert metric record
                INSERT INTO "fertiscan_0.0.8".metric (id, value, unit_id, metric_type, label_id)
                VALUES ("fertiscan_0.0.8".uuid_generate_v4(), metric_value, unit_id, metric_type::"fertiscan_0.0.8".metric_type, p_label_id);
            END IF;
        END IF;
    END LOOP;

END;
$$ LANGUAGE plpgsql;


-- Function to update specifications: delete old and insert new
CREATE OR REPLACE FUNCTION "fertiscan_0.0.8".update_specifications(
    p_label_id uuid,
    new_specifications jsonb
)
RETURNS void AS $$
DECLARE
    spec_language text;
    spec_record jsonb;
BEGIN
    -- Delete existing specifications for the given label_id
    DELETE FROM "fertiscan_0.0.8".specification WHERE label_id = p_label_id;

    -- Insert new specifications
    FOR spec_language IN SELECT * FROM jsonb_object_keys(new_specifications)
    LOOP
        FOR spec_record IN SELECT * FROM jsonb_array_elements(new_specifications -> spec_language)
        LOOP
            -- Insert each specification record
            INSERT INTO "fertiscan_0.0.8".specification (
                humidity, ph, solubility, edited, label_id, language
            )
            VALUES (
                (spec_record->>'humidity')::float,
                (spec_record->>'ph')::float,
                (spec_record->>'solubility')::float,
                FALSE,  -- Assuming default for edited status
                p_label_id,
                spec_language::"fertiscan_0.0.8".LANGUAGE
            );
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- Function to update ingredients: delete old and insert new
CREATE OR REPLACE FUNCTION "fertiscan_0.0.8".update_ingredients(
    p_label_id uuid,
    new_ingredients jsonb,
    is_organic boolean
)
RETURNS void AS $$
DECLARE
    ingredient_language text;
    ingredient_record jsonb;
BEGIN
    -- Delete existing ingredients for the given label_id and organic flag
    DELETE FROM "fertiscan_0.0.8".ingredient 
    WHERE label_id = p_label_id AND organic = is_organic;

    -- Insert new ingredients
    FOR ingredient_language IN SELECT * FROM jsonb_object_keys(new_ingredients)
    LOOP
        FOR ingredient_record IN SELECT * FROM jsonb_array_elements(new_ingredients -> ingredient_language)
        LOOP
            -- Insert each ingredient record
            INSERT INTO "fertiscan_0.0.8".ingredient (
                organic, name, value, unit, edited, label_id, language
            )
            VALUES (
                is_organic,
                ingredient_record->>'nutrient',
                (ingredient_record->>'value')::float,
                ingredient_record->>'unit',
                FALSE, -- Assuming default for edited status
                p_label_id,
                ingredient_language::"fertiscan_0.0.8".LANGUAGE
            );
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- Function to update micronutrients: delete old and insert new
CREATE OR REPLACE FUNCTION "fertiscan_0.0.8".update_micronutrients(
    p_label_id uuid,
    new_micronutrients jsonb
)
RETURNS void AS $$
DECLARE
    nutrient_language text;
    nutrient_record jsonb;
BEGIN
    -- Delete existing micronutrients for the given label_id
    DELETE FROM "fertiscan_0.0.8".micronutrient WHERE label_id = p_label_id;

    -- Insert new micronutrients
    FOR nutrient_language IN SELECT * FROM jsonb_object_keys(new_micronutrients)
    LOOP
        FOR nutrient_record IN SELECT * FROM jsonb_array_elements(new_micronutrients -> nutrient_language)
        LOOP
            -- Insert each micronutrient record
            INSERT INTO "fertiscan_0.0.8".micronutrient (
                read_name, value, unit, edited, label_id, language
            )
            VALUES (
                nutrient_record->>'nutrient',
                NULLIF(nutrient_record->>'value', '')::float,
                nutrient_record->>'unit',
                FALSE,  -- Assuming default for edited status
                p_label_id,
                nutrient_language::"fertiscan_0.0.8".LANGUAGE
            );
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- Function to update guaranteed analysis: delete old and insert new
CREATE OR REPLACE FUNCTION "fertiscan_0.0.8".update_guaranteed(
    p_label_id uuid,
    new_guaranteed jsonb
)
RETURNS void AS $$
DECLARE
    guaranteed_record jsonb;
BEGIN
    -- Delete existing guaranteed analysis for the given label_id
    DELETE FROM "fertiscan_0.0.8".guaranteed WHERE label_id = p_label_id;

    -- Insert new guaranteed analysis
    FOR guaranteed_record IN SELECT * FROM jsonb_array_elements(new_guaranteed)
    LOOP
        -- Insert each guaranteed analysis record
        INSERT INTO "fertiscan_0.0.8".guaranteed (
            read_name, value, unit, edited, label_id
        )
        VALUES (
            guaranteed_record->>'nutrient',
            NULLIF(guaranteed_record->>'value', '')::float,
            guaranteed_record->>'unit',
            FALSE,  -- Assuming default for edited status
            p_label_id
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

