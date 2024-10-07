CREATE OR REPLACE FUNCTION "fertiscan_0.0.14".get_label_info_json(
label_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    record RECORD;
    verified_bool BOOLEAN = FALSE;
BEGIN
    SELECT 
        id,
        product_name,
        lot_number, 
        npk, 
        registration_number, 
        n, 
        p, 
        k,
        warranty, 
        company_info_id,
        manufacturer_info_id
    INTO 
        record
    FROM 
        label_information
    WHERE 
        id = label_id
    LIMIT 1; 
    IF record IS NULL THEN
        RAISE WARNING 'No record found for label_id: %', label_id;
        RETURN NULL;
    END IF;
    SELECT 
        verified
    INTO
        verified_bool
    FROM
        inspection
    WHERE
        label_info_id = label_id
    LIMIT 1; 
    RETURN jsonb_build_object(
        'label_id', record.id,
        'name', record.product_name,
        'k', record.k,
        'n', record.n,
        'p', record.p,
        'npk', record.npk,
        'warranty', record.warranty,  
        'lot_number', record.lot_number,
        'registration_number', record.registration_number,
        'verified', verified_bool
    );
END;
$function$
