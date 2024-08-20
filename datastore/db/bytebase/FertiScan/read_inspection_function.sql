CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".fetch_organization_info(organization_id UUID)
RETURNS JSONB AS $$
DECLARE
    organization_record RECORD;
    organization_json JSONB;
BEGIN
    -- Fetch organization details from organization_information and location tables
    SELECT
        oi.id,
        oi.name,
        l.address,
        oi.website,
        oi.phone_number
    INTO organization_record
    FROM "fertiscan_0.0.10".organization_information oi
    JOIN "fertiscan_0.0.10".location l ON oi.location_id = l.id
    WHERE oi.id = organization_id;

    -- If no organization is found, return NULL
    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    -- Construct the organization JSON
    organization_json := jsonb_build_object(
        'id', organization_record.id,
        'name', organization_record.name,
        'address', organization_record.address,
        'website', organization_record.website,
        'phone_number', organization_record.phone_number
    );

    RETURN organization_json;
END;
$$ LANGUAGE plpgsql;








CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".fetch_product_info(p_label_info_id UUID)
RETURNS JSONB AS $$
DECLARE
    product_record RECORD;
    product_json JSONB;
    metrics JSONB;
BEGIN
    -- Fetch the basic product information including the name from the fertilizer table
    SELECT
        li.id,
        li.n,
        li.p,
        li.k,
        li.npk,
        li.lot_number,
        li.registration_number,
        i.verified,
        f.name
    INTO product_record
    FROM "fertiscan_0.0.10".label_information li
    LEFT JOIN "fertiscan_0.0.10".inspection i ON li.id = i.label_info_id
    LEFT JOIN "fertiscan_0.0.10".fertilizer f ON f.latest_inspection_id = i.id
    WHERE li.id = p_label_info_id;

    -- Fetch product metrics (volume, weight, density)
    metrics := (
        SELECT jsonb_build_object(
            'volume', (
                SELECT jsonb_build_object(
                    'unit', u.unit,
                    'value', m.value
                )
                FROM "fertiscan_0.0.10".metric m
                JOIN "fertiscan_0.0.10".unit u ON m.unit_id = u.id
                WHERE m.label_id = p_label_info_id AND m.metric_type = 'volume'
                LIMIT 1
            ),
            'weight', (
                SELECT jsonb_agg(jsonb_build_object(
                    'unit', u.unit,
                    'value', m.value
                ))
                FROM "fertiscan_0.0.10".metric m
                JOIN "fertiscan_0.0.10".unit u ON m.unit_id = u.id
                WHERE m.label_id = p_label_info_id AND m.metric_type = 'weight'
            ),
            'density', (
                SELECT jsonb_build_object(
                    'unit', u.unit,
                    'value', m.value
                )
                FROM "fertiscan_0.0.10".metric m
                JOIN "fertiscan_0.0.10".unit u ON m.unit_id = u.id
                WHERE m.label_id = p_label_info_id AND m.metric_type = 'density'
                LIMIT 1
            )
        )
    );

    -- Construct the product JSON with a placeholder for warranty
    product_json := jsonb_build_object(
        'id', product_record.id,
        'name', product_record.name,
        'n', product_record.n,
        'p', product_record.p,
        'k', product_record.k,
        'npk', product_record.npk,
        'lot_number', product_record.lot_number,
        'registration_number', product_record.registration_number,
        'verified', product_record.verified,
        'metrics', metrics,
        'warranty', 'Placeholder for warranty text'
    );

    RETURN product_json;
END;
$$ LANGUAGE plpgsql;












CREATE OR REPLACE FUNCTION "fertiscan_0.0.10".read_inspection(p_inspection_id UUID)
RETURNS JSONB AS $$
DECLARE
    -- Variables to store intermediate data
    inspection_data RECORD;
    company_info JSONB;
    manufacturer_info JSONB;
    product_info JSONB;
    instructions JSONB;
    cautions JSONB;
    first_aid JSONB;
    ingredients JSONB;
    micronutrients JSONB;
    specifications JSONB;
    guaranteed_analysis JSONB;
    result JSONB := '{}';
BEGIN
    -- Step 1: Fetch basic inspection data
    SELECT
        i.company_info_id,
        i.manufacturer_info_id,
        i.label_info_id,
        i.inspector_id,
        i.sample_id,
        i.picture_set_id,
        i.verified
    INTO inspection_data
    FROM "fertiscan_0.0.10".inspection i
    WHERE i.id = p_inspection_id;

    -- Step 2: Fetch company information using the unified function
    company_info := "fertiscan_0.0.10".fetch_organization_info(inspection_data.company_info_id);

    -- Step 3: Fetch manufacturer information using the unified function
    manufacturer_info := "fertiscan_0.0.10".fetch_organization_info(inspection_data.manufacturer_info_id);

    -- Step 4: Fetch product information
    product_info := "fertiscan_0.0.10".fetch_product_info(inspection_data.label_info_id);

    -- Step 5: Fetch additional details
    instructions := "fertiscan_0.0.10".fetch_instructions(inspection_data.label_info_id);
    cautions := "fertiscan_0.0.10".fetch_cautions(inspection_data.label_info_id);
    first_aid := "fertiscan_0.0.10".fetch_first_aid(inspection_data.label_info_id);
    ingredients := "fertiscan_0.0.10".fetch_ingredients(inspection_data.label_info_id);
    micronutrients := "fertiscan_0.0.10".fetch_micronutrients(inspection_data.label_info_id);
    specifications := "fertiscan_0.0.10".fetch_specifications(inspection_data.label_info_id);
    guaranteed_analysis := "fertiscan_0.0.10".fetch_guaranteed_analysis(inspection_data.label_info_id);

    -- Step 6: Construct and return the result JSON
    result := jsonb_set(result, '{company}', company_info);
    result := jsonb_set(result, '{manufacturer}', manufacturer_info);
    result := jsonb_set(result, '{product}', product_info);
    result := jsonb_set(result, '{instructions}', instructions);
    result := jsonb_set(result, '{cautions}', cautions);
    result := jsonb_set(result, '{first_aid}', first_aid);
    result := jsonb_set(result, '{ingredients}', ingredients);
    result := jsonb_set(result, '{micronutrients}', micronutrients);
    result := jsonb_set(result, '{specifications}', specifications);
    result := jsonb_set(result, '{guaranteed_analysis}', guaranteed_analysis);

    -- Return the final result
    RETURN result;
END;
$$ LANGUAGE plpgsql;
