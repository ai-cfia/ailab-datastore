--Schema creation nachet_0.0.11
DO
$do$
BEGIN
IF (EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'nachet_0.0.11')) THEN

    CREATE TABLE "nachet_0.0.11"."users" (
        "id" uuid DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "email" VARCHAR(255) NOT NULL,
        "registration_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE SET CURRENT_TIMESTAMP
    );

    CREATE TABLE "nachet_0.0.11"."picture_set" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "picture_set" json NOT NULL,
        "owner_id" uuid NOT NULL REFERENCES "nachet_0.0.11".users(id),
        "upload_date" date NOT NULL DEFAULT current_timestamp
    );

    ALTER TABLE "nachet_0.0.11"."users" ADD "default_set_id" uuid REFERENCES "nachet_0.0.11".picture_set(id) ON DELETE SET NULL;
    
    CREATE TABLE "nachet_0.0.11"."picture" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "picture" json NOT NULL,
        "picture_set_id" uuid NOT NULL REFERENCES "nachet_0.0.11".picture_set(id),
        "nb_obj" integer NOT NULL,
        "verified" boolean NOT NULL DEFAULT false,
        "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "nachet_0.0.11"."object_type" (
        "id" SERIAL PRIMARY KEY,
        "name" text NOT NULL
    );

    CREATE TABLE "nachet_0.0.11"."seed" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "name" text NOT NULL,
        "object_type_id" integer GENERATED ALWAYS AS (1) STORED
    );

    CREATE TABLE "nachet_0.0.11"."picture_seed" (
        "id" uuid DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "picture_id" uuid NOT NULL REFERENCES picture(id) ON DELETE CASCADE,
        "seed_id" uuid NOT NULL REFERENCES seeds(id) ON DELETE CASCADE,
        "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "nachet_0.0.11"."inference" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "inference" json NOT NULL,
        "picture_id" uuid NOT NULL REFERENCES "nachet_0.0.11".picture(id) ON DELETE CASCADE,
        "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "users_id" uuid NOT NULL REFERENCES "nachet_0.0.11".users(id) ON DELETE SET NULL
    );

    CREATE TABLE "nachet_0.0.11"."task" (
        "id" SERIAL PRIMARY KEY,
        "name" text NOT NULL
    );
 
    CREATE TABLE "nachet_0.0.11"."model" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "name" text NOT NULL,
        "endpoint_name" text NOT NULL,
        "task_id" integer NOT NULL REFERENCES "nachet_0.0.11".task(id),
        "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE "nachet_0.0.11"."model_version" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "model_id" uuid NOT NULL REFERENCES "nachet_0.0.11".model(id) ON DELETE CASCADE,
        "data" json NOT NULL,
        "version" text NOT NULL,
        "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    Alter table "nachet_0.0.11".model ADD "active_version" uuid REFERENCES "nachet_0.0.11".model_version(id);

    CREATE TABLE "nachet_0.0.11"."object" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "box_metadata" json NOT NULL,
        "inference_id" uuid NOT NULL REFERENCES "nachet_0.0.11".inference(id) ON DELETE CASCADE,
        "type_id" integer NOT NULL REFERENCES "nachet_0.0.11".object_type(id) ON DELETE CASCADE,
        "verified" boolean NOT NULL DEFAULT true,
        "top_id" uuid,
        "upload_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE SET CURRENT_TIMESTAMP
    );
    
    
    CREATE TABLE "nachet_0.0.11"."pipeline" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "name" text NOT NULL,
        "active" boolean NOT NULL DEFAULT false,
        "is_default" boolean not null default false,
        data json NOT NULL,
    );
   
    CREATE TRIGGER "pipeline_default_trigger" BEFORE insert OR UPDATE ON "nachet_0.0.11"."pipeline"
    FOR EACH ROW EXECUTE FUNCTION "nachet_0.0.11".pipeline_default_trigger();

    CREATE FUNCTION "nachet_0.0.11".pipeline_default_trigger() RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.is_default THEN
            UPDATE "nachet_0.0.11".pipeline SET is_default=false WHERE is_default=true;
        END IF;
        RETURN NEW;
    END;
   $$language plpgsql;

    CREATE TABLE "nachet_0.0.11"."pipeline_default" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "pipeline_id" uuid NOT NULL REFERENCES "nachet_0.0.11".pipeline(id) ON DELETE CASCADE,
        "users_id" uuid NOT NULL REFERENCES "nachet_0.0.11".users(id) ON DELETE CASCADE
    );

    CREATE UNIQUE INDEX "nachet_0.0.11_pipeline_default" ON "nachet_0.0.11".pipeline ("is_default") where is_default=true;
    
    CREATE TABLE "nachet_0.0.11"."pipeline_model" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "pipeline_id" uuid NOT NULL REFERENCES "nachet_0.0.11".pipeline(id) ON DELETE CASCADE,
        "model_id" uuid NOT NULL REFERENCES "nachet_0.0.11".model(id) ON DELETE CASCADE
    );
    
    CREATE TABLE "nachet_0.0.11"."seed_obj" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "seed_id" uuid NOT NULL REFERENCES "nachet_0.0.11".seed(id) ON DELETE CASCADE,
        "object_id" uuid NOT NULL REFERENCES "nachet_0.0.11".object(id) ON DELETE CASCADE,
        "score" float NOT NULL
    );  

    INSERT INTO "nachet_0.0.10".seed(name) VALUES
    ('Brassica napus'),
    ('Brassica juncea'),
    ('Cirsium arvense'),
    ('Cirsium vulgare'),
    ('Carduus nutans'),
    ('Bromus secalinus'),
    ('Bromus hordeaceus'),
    ('Bromus japonicus'),
    ('Lolium temulentum'),
    ('Solanum carolinense'),
    ('Solanum nigrum'),
    ('Solanum rostratum'),
    ('Ambrosia artemisiifolia'),
    ('Ambrosia trifida'),
    ('Ambrosia psilostachya');

    INSERT INTO "nachet_0.0.10".task(name) VALUES
    ('Object Detection'),
    ('Classification'),
    ('Segmentation');

    
END
$do$
