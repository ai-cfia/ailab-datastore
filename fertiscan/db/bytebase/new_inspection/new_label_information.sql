drOp FUNCTION IF EXISTS "fertiscan_0.0.17".new_label_information(TEXT, TEXT, TEXT,  FLOAT, FLOAT, FLOAT, TEXT, TEXT, BOOLEAN, UUID, UUID);
CREATE OR REPLACE FUNCTION "fertiscan_0.0.17".new_label_information(
    name TEXT,
    lot_number TEXT,
    npk TEXT,
    n FLOAt,
    p FLOAT,
    k FLOAT,
    guaranteed_title_en TEXT,
    guaranteed_title_fr TEXT,
    is_minimal boolean,
    company_id UUID DEFAULT Null,
    manufacturer_id UUID DEFAULT Null,
    record_keeping BOOLEAN DEFAULT NULL
    )
RETURNS uuid 
LANGUAGE plpgsql
AS $function$
DECLARE
    label_id uuid;
    record RECORD;
BEGIN
    SET SEARCH_PATH TO "fertiscan_0.0.17";
	-- LABEL INFORMATION
    INSERT INTO label_information (
        product_name,lot_number, npk, registration_number, n, p, k, guaranteed_title_en, guaranteed_title_fr, title_is_minimal, company_info_id, manufacturer_info_id, record_keeping
    ) VALUES (
		name,
        lot_number,
        npk,
        n,
        p,
        k,
        guaranteed_title_en,
        guaranteed_title_fr,
        is_minimal,
		company_id,
		manufacturer_id,
        record_keeping
    )
    RETURNING id INTO label_id;
    RETURN label_id;
END;
$function$;
