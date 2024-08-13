CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".get_sub_label_json(
label_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    record RECORD
    sub_type_record RECORD
    fr text[];
    en text[];
    result_json jsonb;
BEGIN
-- Get all sub_labels for a given label_id
    SELECT 
        sl.id,
        sl.text_content_fr,
        sl.text_content_en,
        sl.edited
        st.type_en
    INTO 
        record
    FROM 
        sub_label AS sl
    LEFT JOIN 
        sub_type AS st 
    ON 
        sub_label.sub_type_id = sub_type.id
    WHERE 
        sl.label_id = label_id
    ORDER BY 
        sub_type_id
-- Get all sub_types 
    SELECT 
        type_en
    INTO
        sub_type_record
    FROM
        sub_type
    GROUP BY
        st.type_en
-- Loop through all sub types
    FOR i IN 1..array_length(sub_type_record, 1) LOOP
    -- Create sub_type json object
    result_json = jsonb_build_object(
        sub_type_record[i], jsonb_build_object(
            'fr', [],
            'en', []
        )
        For j in 1..array_length(record, 1) LOOP
            IF sub_type_record[i] = record[j].type_en THEN
                fr[i] = record[j].text_content_fr
                en[i] = record[j].text_content_en
            END IF
        END LOOP
        fr[i] = record.text_content_fr
        en[i] = record.text_content_en
    END LOOP

    RETURN jsonb_build_object(
        'id', record.id,
        
    );
END;
$function$;