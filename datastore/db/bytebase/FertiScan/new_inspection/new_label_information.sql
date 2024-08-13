CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".new_label_information(
    name TEXT,
    lot_number TEXT,
    npk TEXT,
    registration_number TEXT,
    n FLOAt,
    p FLOAT,
    k FLOAT,
    warranty TEXT,
    company_id UUID,
    manufacturer_id UUID
    )
RETURNS uuid 
LANGUAGE plpgsql
AS $function$
DECLARE
    label_id uuid;
    record RECORD
BEGIN
	-- LABEL INFORMATION
    INSERT INTO label_information (
        product_name,lot_number, npk, registration_number, n, p, k, company_info_id, manufacturer_info_id
    ) VALUES (
		name,
        lot_number,
        npk,
        registration_number,
        n,
        p,
        k,
        warranty,
		company_id,
		manufacturer_id
    )
    RETURNING id INTO label_id;
    RETURN label_id;
END;
$function$;