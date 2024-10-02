-- Function that evaluates the inspection compared to the original_dataset
CREATE OR REPLACE FUNCTION inspection_evaluation(
    id UUID
) RETURNS VOID 
LANGUAGE plpgsql
AS $function$
DECLARE
    original_dataset_json JSONB;
    dataset_json JSONB;
    item_json JSONB;
    label_id UUID;
    levenshtein_distance int;
    source_str TEXT;
    target_str TEXT;
    language_str TEXT;
    sub_label_key TEXT;
    source_nb int;
    target_nb int;
    score_value int;
    label_info_lev_total int,
    label_name_lev int,
    label_reg_num_lev int,
    label_lot_num_lev int,
    metrics_lists_edited boolean,
    metrics_lists_modif int,
    metrics_lev int,
    manufacturer_field_edited int,
    manufacturer_lev_total int,
    company_field_edited int,
    company_lev_total int,
    org_lev_total int,
    instructions_lists_modif int,
    instruction_lists_edit int,
    instructions_lev int,
    cautions_lists_modif int,
    cautions_lists_edit int,
    cautions_lev int,
    guaranteeds_en_lists_modif int,
    guaranteeds_fr_lists_modif int,
    guaranteeds_en_lev int
    guaranteeds_fr_lev int,
BEGIN
    -- fetch the original dataset
    levenstein_distance = 0;
    label_info_lev_total = 0
    SELECT original_dataset,label_info_id INTO original_dataset_json, label_id
    FROM "fertiscan_0.0.12".inspection_factual
    WHERE inspection_id = id;

    -- Evaluate the inspection
        -- Evaluate the label
            -- Fetch the label information json
                SELECT "fertiscan_0.0.12".get_label_information_json(label_id) INTO dataset_json;
                label_info_lev_total := 0;   
            -- Evaluate the label name
                source_str := '';
                target_str := '';
                label_name_lev := 0;
                IF jsonb_typeof(original_dataset_json-> 'product'->'name') IS NOT NULL THEN  
                    source_str := original_dataset_json-> "product"->>'name';
                END IF;
                IF jsonb_typeof(dataset_json->> 'name') IS NOT NULL THEN
                    target_str := dataset_json->> 'name';
                END IF;

                IF (source_str = '' AND target_str = '') OR (source_str ILIKE target_str) THEN
                    label_name_lev := 0;
                ELSE
                    SELECT levenshtein(source_str, target_str) INTO label_name_lev;
                END IF;
                label_info_lev_total := label_info_lev_total + label_name_lev;
            -- Evaluate the registration number
                source_str := '';
                target_str := '';
                label_reg_num_lev := 0;
                IF jsonb_typeof(original_dataset_json-> 'product'->'registration_number') IS NOT NULL THEN
                    source_str := original_dataset_json-> "product"->>'registration_number';
                END IF;
                IF jsonb_typeof(dataset_json->> 'registration_number') IS NOT NULL THEN
                    target_str := dataset_json->> 'registration_number';
                END IF;

                IF (source_str = '' AND target_str = '') OR (source_str ILIKE target_str) THEN
                    label_reg_num_lev := 0;
                ELSE
                    SELECT levenshtein(source_str, target_str) INTO label_reg_num_lev;
                END IF;
                label_info_lev_total := label_info_lev_total + label_reg_num_lev;
            -- Evaluate the lot number
                source_str := '';
                target_str := '';
                label_lot_num_lev := 0;
                IF jsonb_typeof(original_dataset_json-> 'product'->'lot_number') IS NOT NULL THEN
                    source_str := original_dataset_json-> "product"->>'lot_number';
                END IF;
                IF jsonb_typeof(dataset_json->> 'lot_number') IS NOT NULL THEN
                    target_str := dataset_json->> 'lot_number';
                END IF;

                IF (source_str = '' AND target_str = '') OR (source_str ILIKE target_str) THEN
                    label_lot_num_lev := 0;
                ELSE
                    SELECT levenshtein(source_str, target_str) INTO label_lot_num_lev;
                END IF;
                label_info_lev_total := label_info_lev_total + label_lot_num_lev;
            -- Evaluate NPK
                source_str := '';
                target_str := '';
                IF jsonb_typeof(original_dataset_json-> 'product'->'npk') IS NOT NULL THEN
                    source_str := original_dataset_json-> "product"->>'npk';
                END IF;
                IF jsonb_typeof(dataset_json->'npk') IS NOT NULL THEN
                    target_str := dataset_json->'npk';
                END IF;
                IF source_str ILIKE target_str THEN
                    label_info_lev_total := label_info_lev_total + 0;
                ELSE
                    SELECT levenshtein(source_str, target_str) INTO levenshtein_distance;
                    label_info_lev_total := label_info_lev_total + levenshtein_distance;
                END IF;
        -- Evaluate the metrics
            metrics_lev :=0;
            -- Fetch the metrics JSON
                SELECT "fertiscan_0.0.12".get_metrics_information_json(label_id) INTO dataset_json;
            -- Evaluate the metrics lists
                -- loop through the weigth metrics lists to build source_str and target_str 
                    source_str := '';
                    target_str := '';
                    source_nb:= jsonb_array_length(original_dataset_json->'product'->'weight'); -- associated with source
                    target_nb:= jsonb_array_length(dataset_json->'metrics'->'weight'); -- associated with target
                    FOR i IN 0 .. source_nb - 1 LOOP
                        item_json := original_dataset_json->'product'->'weight'->i;
                        source_str := source_str || COALESCE(item_json->>'value', '') || COALESCE(item_json->>'unit', '') || ' ';
                    END LOOP;    
                    FOR i IN 0 .. target_nb - 1 LOOP
                        item_json := dataset_json->'metrics'->'weight'->i;
                        target_str := target_str || COALESCE(item_json->>'value', '') || COALESCE(item_json->>'unit', '') || ' ';
                    END LOOP;            
                -- include the volume metrics data
                    IF jsonb_typeof(original_dataset_json->'product'->'metrics'->'volume') IS NOT NULL THEN
                        item_json := original_dataset_json->'product'->'metrics'->'volume';
                        source_str := source_str || COALESCE(item_json->>'value', '') || COALESCE(item_json->>'unit', '') || ' ';
                        source_nb := source_nb + 1;
                    END IF; 
                    IF jsonb_typeof(dataset_json->'metrics'->'volume') IS NOT NULL THEN
                        item_json := dataset_json->'metrics'->'volume';
                        target_str := target_str || COALESCE(item_json->>'value', '') || COALESCE(item_json->>'unit', '') || ' ';
                        target_nb := target_nb + 1;
                    END IF;
                -- include the density metrics
                    IF jsonb_typeof(original_dataset_json->'product'->'metrics'->'density') IS NOT NULL THEN
                        item_json := original_dataset_json->'product'->'metrics'->'density';
                        source_str := source_str || COALESCE(item_json->>'value', '') || c || ' ';
                        source_nb := source_nb + 1;
                    END IF;
                    IF jsonb_typeof(dataset_json->'metrics'->'density') IS NOT NULL THEN
                        item_json := dataset_json->'metrics'->'density';
                        target_str := target_str || COALESCE(item_json->>'value', '') || COALESCE(item_json->>'unit', '') || ' ';
                        target_nb := target_nb + 1;
                    END IF;
                
                metrics_lists_modif:= target_nb - source_nb;
                
                SELECT levenshtein(source_str, target_str) INTO metrics_lev;
        -- Evaluate the organizations
            source_str := '';
            target_str := '';
            -- Fetch the organizations JSON
                SELECT "fertiscan_0.0.12".get_organizations_information_json(label_id) INTO dataset_json 
            -- Evaluate the company 
                source_str := '';
                target_str := '';
                source_nb:= 0;
                target_nb:= 0;
                IF jsonb_typeof(original_dataset_json ->'company') IS NOT NULL THEN
                    IF jsonb_typeof(original_dataset_json ->'company'->>'name') IS NOT NULL THEN
                        source_str := original_dataset_json ->'company'->>'name';
                        source_nb := source_nb + 1;
                    END IF;
                    IF jsonb_typeof(original_dataset_json ->'company'->>'address') IS NOT NULL THEN
                        source_str := source_str || original_dataset_json ->'company'->>'address';
                        source_nb := source_nb + 1;
                    END IF;
                    IF jsonb_typeof(original_dataset_json ->'company'->>'phone_number') IS NOT NULL THEN
                        source_str := source_str || original_dataset_json ->'company'->>'phone_number';
                        source_nb := source_nb + 1;
                    END IF;
                    IF jsonb_typeof(original_dataset_json ->'company'->>'website') IS NOT NULL THEN
                        source_str := source_str || original_dataset_json ->'company'->>'website';
                        source_nb := source_nb + 1;
                    END IF;
                END IF;
                IF jsonb_typeof(dataset_json->'company') IS NOT NULL THEN
                    IF jsonb_typeof(dataset_json->'company'->>'name') IS NOT NULL THEN
                        target_str := dataset_json->'company'->>'name';
                        target_nb := target_nb + 1;
                    END IF;
                    IF jsonb_typeof(dataset_json->'company'->>'address') IS NOT NULL THEN
                        target_str := target_str || dataset_json->'company'->>'address';
                        target_nb := target_nb + 1;
                    END IF;
                    IF jsonb_typeof(dataset_json->'company'->>'phone_number') IS NOT NULL THEN
                        target_str := target_str || dataset_json->'company'->>'phone_number';
                        target_nb := target_nb + 1;
                    END IF;
                    IF jsonb_typeof(dataset_json->'company'->>'website') IS NOT NULL THEN
                        target_str := target_str || dataset_json->'company'->>'website';
                        target_nb := target_nb + 1;
                    END IF;
                END IF;

                company_field_edited := target_nb - source_nb;

                SELECT levenshtein(source_str, target_str) INTO company_lev_total;
            -- Evaluate the manufacturer
                source_str := '';
                target_str := '';
                source_nb:= 0;
                target_nb:= 0;
                IF jsonb_typeof(original_dataset_json ->'manufacturer') IS NOT NULL THEN
                    IF jsonb_typeof(original_dataset_json ->'manufacturer'->>'name') IS NOT NULL THEN
                        source_str := original_dataset_json ->'manufacturer'->>'name';
                        source_nb := source_nb + 1;
                    END IF;
                    IF jsonb_typeof(original_dataset_json ->'manufacturer'->>'address') IS NOT NULL THEN
                        source_str := source_str || original_dataset_json ->'manufacturer'->>'address';
                        source_nb := source_nb + 1;
                    END IF;
                    IF jsonb_typeof(original_dataset_json ->'manufacturer'->>'phone_number') IS NOT NULL THEN
                        source_str := source_str || original_dataset_json ->'manufacturer'->>'phone_number';
                        source_nb := source_nb + 1;
                    END IF;
                    IF jsonb_typeof(original_dataset_json ->'manufacturer'->>'website') IS NOT NULL THEN
                        source_str := source_str || original_dataset_json ->'manufacturer'->>'website';
                        source_nb := source_nb + 1;
                    END IF;
                END IF;
                IF jsonb_typeof(dataset_json->'manufacturer') IS NOT NULL THEN
                    IF jsonb_typeof(dataset_json->'manufacturer'->>'name') IS NOT NULL THEN
                        target_str := dataset_json->'manufacturer'->>'name';
                        target_nb := target_nb + 1;
                    END IF;
                    IF jsonb_typeof(dataset_json->'manufacturer'->>'address') IS NOT NULL THEN
                        target_str := target_str || dataset_json->'manufacturer'->>'address';
                        target_nb := target_nb + 1;
                    END IF;
                    IF jsonb_typeof(dataset_json->'manufacturer'->>'phone_number') IS NOT NULL THEN
                        target_str := target_str || dataset_json->'manufacturer'->>'phone_number';
                        target_nb := target_nb + 1;
                    END IF;
                    IF jsonb_typeof(dataset_json->'manufacturer'->>'website') IS NOT NULL THEN
                        target_str := target_str || dataset_json->'manufacturer'->>'website';
                        target_nb := target_nb + 1;
                    END IF;
                END IF;

                manufacturer_field_edited := target_nb - source_nb;

                SELECT levenshtein(source_str, target_str) INTO manufacturer_lev_total;

        -- Evaluate the Guaranteed_Analysis
            source_str := '';
            target_str := '';
            source_nb:= 0;
            target_nb:= 0;
            -- Fetch the Guaranteed_Analysis JSON
                SELECT "fertiscan_0.0.12".get_guaranteed_analysis_json(label_id) INTO dataset_json;
            -- Evaluate the Guaranteed_Analysis lists
                -- Loop for each language
            FOR language_str IN ARRAY['fr', 'en']
	        LOOP    
                IF jsonb_array_length(original_dataset_json->'guaranteed_analysis'->language_str) > 0 THEN
                    source_nb := jsonb_array_length(original_dataset_json->'guaranteed_analysis');
                    For i IN 0 .. source_nb - 1 LOOP
                        item_json := (original_dataset_json->'guaranteed_analysis'->language_str->i);
                        source_str := source_str || COALESCE(item_json->>'read_name', '') || COALESCE(item_json->>'unit', '') || COALESCE(item_json->>'value', '') || ' ';
                    END LOOP;
                END IF;

                IF jsonb_array_length(dataset_json->'guaranteed_analysis') > 0 THEN
                    target_nb := jsonb_array_length(dataset_json->'guaranteed_analysis'->language_str);
                    For i IN 0 .. target_nb - 1 LOOP
                        item_json := (dataset_json->'guaranteed_analysis'->language_str->i);
                        target_str := target_str || COALESCE(item_json->>'read_name', '') || COALESCE(item_json->>'unit', '') || COALESCE(item_json->>'value', '') || ' ';
                    END LOOP;
                END IF;
                
                IF language_str = 'fr' THEN
                    SELECT levenshtein(source_str, target_str) INTO guaranteeds_fr_lev;
                    guaranteeds_fr_lists_modif := target_nb - source_nb;
                ELSE -- language_str = 'en'
                    SELECT levenshtein(source_str, target_str) INTO guaranteeds_en_lev;
                    guaranteeds_en_lists_modif := target_nb - source_nb;
                END IF;
            END LOOP;

        -- Evaluate the sub_labels
            -- Fetch the sub_labels JSON
                SELECT "fertiscan_0.0.12".get_sub_labels_information_json(label_id) INTO dataset_json;
            -- Evaluate the sub_labels lists
                -- Loop for each language
                FOR language_str IN ARRAY['fr', 'en']
                LOOP
                -- Loop for each sub_label
                    FOR sub_label_key IN ARRAY['cautions', 'instructions']
                    LOOP
                        source_str := '';
                        target_str := '';
                        source_nb:= 0;
                        target_nb:= 0;
                        IF jsonb_array_length(original_dataset_json->sub_label_key->language_str) > 0 THEN
                            source_nb := jsonb_array_length(original_dataset_json->sub_label_key->language_str);
                            For i IN 0 .. source_nb - 1 LOOP
                                source_str := source_str || COALESCE(original_dataset_json->sub_label_key->language_str->>i, '') || ' ';
                            END LOOP;
                        END IF;

                        IF jsonb_array_length(dataset_json->sub_label_key->language_str) > 0 THEN
                            target_nb := jsonb_array_length(dataset_json->sub_label_key->language_str);
                            For i IN 0 .. target_nb - 1 LOOP
                                item_json := (dataset_json->sub_label_key->language_str->i);
                                target_str := target_str || COALESCE(dataset_json->sub_label_key->language_str->>i, '') || ' ';
                            END LOOP;
                        END IF;
                        
                        IF language_str = 'fr' THEN
                            IF sub_label_key = 'instructions' THEN
                                SELECT levenshtein(source_str, target_str) INTO instructions_lev;
                                instructions_fr_lists_modif := target_nb - source_nb;
                            ELSIF sub_label_key = 'cautions'
                                SELECT levenshtein(source_str, target_str) INTO cautions_lev;
                                cautions_fr_lists_modif := target_nb - source_nb;
                            END IF;
                        ELSE -- language_str = 'en'
                            IF sub_label_key = 'instructions' THEN
                                SELECT levenshtein(source_str, target_str) INTO instructions_lev;
                                instructions_en_lists_modif := target_nb - source_nb;
                            ELSIF sub_label_key = 'cautions'
                                SELECT levenshtein(source_str, target_str) INTO cautions_lev;
                                cautions_en_lists_modif := target_nb - source_nb;
                            END IF;
                        END IF;
                    END LOOP;

    -- Score the inspection

    -- Insert the evaluation into the inspection_evaluation table
    INSERT INTO "fertiscan_0.0.12".inspection_evaluation (
        inspection_id,
        score,
        label_info_lev_total,
        label_name_lev,
        label_reg_num_lev,
        label_lot_num_lev,
        metrics_lists_edited,
        metrics_lists_modif,
        metrics_lev,
        manufacturer_field_edited,
        manufacturer_lev_total,
        company_field_edited,
        company_lev_total,
        org_lev_total,
        instructions_lists_modif,
        instruction_lists_edit,
        instructions_lev,
        cautions_lists_modif,
        cautions_lists_edit,
        cautions_lev,
        guaranteeds_en_lists_modif,
        guaranteeds_fr_lists_modif,
        guaranteeds_en_lev,
        guaranteeds_fr_lev
    ) VALUES (
        id,
        score_value,
        label_info_lev_total,
        label_name_lev,
        label_reg_num_lev,
        label_lot_num_lev,
        metrics_lists_edited,
        metrics_lists_modif,
        metrics_lev,
        manufacturer_field_edited,
        manufacturer_lev_total,
        company_field_edited,
        company_lev_total,
        org_lev_total,
        instructions_lists_modif,
        instruction_lists_edit,
        instructions_lev,
        cautions_lists_modif,
        cautions_lists_edit,
        cautions_lev,
        guaranteeds_en_lists_modif,
        guaranteeds_fr_lists_modif,
        guaranteeds_en_lev,
        guaranteeds_fr_lev
    );
    RETURN;
END;
$function$;

