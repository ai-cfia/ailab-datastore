
CREATE OR REPLACE FUNCTION "fertiscan_0.0.13".new_label_information(
    name TEXT,
    lot_number TEXT,
    npk TEXT,
    registration_number TEXT,
    n FLOAt,
    p FLOAT,
    k FLOAT,
    title_en TEXT,
    title_fr TEXT,
    is_minimal boolean,
    company_id UUID DEFAULT Null,
    manufacturer_id UUID DEFAULT Null
    )
RETURNS uuid 
LANGUAGE plpgsql
AS $function$
DECLARE
    label_id uuid;
    record RECORD;
BEGIN
    SET SEARCH_PATH TO "fertiscan_0.0.13";
	-- LABEL INFORMATION
    INSERT INTO label_information (
        product_name,lot_number, npk, registration_number, n, p, k, guaranteed_title_en, guaranteed_title_fr, title_is_minimal, company_info_id, manufacturer_info_id
    ) VALUES (
		name,
        lot_number,
        npk,
        registration_number,
        n,
        p,
        k,
        title_en,
        title_fr,
        is_minimal,
		company_id,
		manufacturer_id
    )
    RETURNING id INTO label_id;
    RETURN label_id;
END;
$function$;


CREATE OR REPLACE FUNCTION handle_null_titles()
RETURNS TRIGGER AS $$
BEGIN
    -- If guaranteed_title_en is NULL, set it to an empty string
    IF NEW.guaranteed_title_en IS NULL THEN
        NEW.guaranteed_title_en := '';
    END IF;
    
    -- If guaranteed_title_fr is NULL, set it to an empty string
    IF NEW.guaranteed_title_fr IS NULL THEN
        NEW.guaranteed_title_fr := '';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS handle_null_titles_trigger ON "fertiscan_0.0.13".label_information;
CREATE TRIGGER handle_null_titles_trigger
BEFORE INSERT OR UPDATE
ON "fertiscan_0.0.13".label_information
FOR EACH ROW
EXECUTE FUNCTION handle_null_titles();
