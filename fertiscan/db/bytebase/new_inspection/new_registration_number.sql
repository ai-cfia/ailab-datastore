
DROP FUNCTION IF EXISTS "fertiscan_0.0.17".new_registration_number(TEXT, BOOLEAN, UUID, TEXT, BOOLEAN);
CREATE OR REPLACE FUNCTION "fertiscan_0.0.17".new_registration_number(
    identifier TEXT,
    label_info_id UUID,
    is_an_ingredient BOOLEAN DEFAULT NULL,
    read_name TEXT DEFAULT NULL,
    edited BOOLEAN DEFAULT FALSE
)
RETURNS uuid 
LANGUAGE plpgsql
AS $function$
DECLARE
    reg_num_id uuid;
BEGIN
    INSERT INTO "fertiscan_0.0.17".registration_number_information (
        identifier, 
        is_an_ingredient, 
        name,
        label_id,
        edited
    )
    VALUES (
        reg_num, 
        is_an_ingredient_val, 
        read_name,
        label_info_id,
        FALSE
    )
    RETURNING id INTO reg_num_id;
    RETURN reg_num_id;
END;
$function$;
