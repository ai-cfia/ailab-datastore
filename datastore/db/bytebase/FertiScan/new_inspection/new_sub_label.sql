CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".new_sub_label(
content_fr TEXT,
content_en TEXT,
label_id UUID,
sub_type_id UUID
)
RETURNS uuid 
LANGUAGE plpgsql
AS $function$
DECLARE
    sub_label_id uuid;
    record RECORD
    _id uuid;
BEGIN
    INSERT INTO sub_label (text_content_fr,text_content_en, label_id, edited, sub_type_id)
	VALUES (
	    content_fr,
		content_en,
		label_id,
		FALSE,
		sub_type_id
	)
    RETURNING id INTO sub_label_id;
    RETURN sub_label_id;
END;
$function$;