BEGIN;

--- SEED_OBJECT ---
-- delete actual constraint
ALTER TABLE "nachet_0.0.11"."seed_obj" DROP CONSTRAINT IF EXISTS seed_obj_object_id_fkey;
-- new constraint
ALTER TABLE "nachet_0.0.11"."seed_obj"
ADD CONSTRAINT seed_obj_object_id_fkey FOREIGN KEY (object_id)
REFERENCES "nachet_0.0.11"."object"(id) ON DELETE CASCADE;

--- OBJECT ---
-- delete actual constraint
ALTER TABLE "nachet_0.0.11"."object" DROP CONSTRAINT IF EXISTS object_inference_id_fkey;
-- new constraint
ALTER TABLE "nachet_0.0.11"."object"
ADD CONSTRAINT object_inference_id_fkey FOREIGN KEY (inference_id)
REFERENCES "nachet_0.0.11"."inference"(id) ON DELETE CASCADE;

--- INFERENCE ---
-- delete actual constraint
ALTER TABLE "nachet_0.0.11"."inference" DROP CONSTRAINT IF EXISTS inference_picture_id_fkey;
-- new constraint
ALTER TABLE "nachet_0.0.11"."inference"
ADD CONSTRAINT inference_picture_id_fkey FOREIGN KEY (picture_id)
REFERENCES "nachet_0.0.11"."picture"(id) ON DELETE CASCADE;

--- PICTURE_SEED ---
-- delete actual constraint
ALTER TABLE "nachet_0.0.11"."picture_seed" DROP CONSTRAINT IF EXISTS picture_seed_picture_id_fkey;
-- new constraint
ALTER TABLE "nachet_0.0.11"."picture_seed"
ADD CONSTRAINT picture_seed_picture_id_fkey FOREIGN KEY (picture_id)
REFERENCES "nachet_0.0.11"."picture"(id) ON DELETE CASCADE;

--- PICTURE ---
-- delete actual constraint
ALTER TABLE "nachet_0.0.11"."picture" DROP CONSTRAINT IF EXISTS picture_picture_set_id_fkey;
-- new constraint
ALTER TABLE "nachet_0.0.11"."picture"
ADD CONSTRAINT picture_picture_set_id_fkey FOREIGN KEY (picture_set_id)
REFERENCES "nachet_0.0.11"."picture_set"(id) ON DELETE CASCADE;

COMMIT;