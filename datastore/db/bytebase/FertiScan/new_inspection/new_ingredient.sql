CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".new_ingredient(
name TEXT,
value FLOAt,
read_unit FLOAT,
label_id UUID,
language "fertiscan_0.0.11".language,
organic BOOLEAN,
active BOOLEAN,
edited BOOLEAN = FALSE
)
RETURNS uuid 
LANGUAGE plpgsql
AS $function$
DECLARE
    ingredient_id uuid;
    record RECORD;
    _id uuid;
BEGIN
    INSERT INTO ingredient (
        organic, 
        active, 
        name,
        value, 
        unit, 
        edited, 
        label_id, 
        language)
    VALUES (
        organic, 
        active,  
        name,
        value,
        read_unit,
        edited, -- Assuming edited status
        label_id,  
        language
    )
    RETURNING id INTO ingredient_id;
    RETURN ingredient_id;
END;
$function$;