--Schema creation nachet_0.0.10
DO
$do$
BEGIN
IF (EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'nachet_0.0.10')) THEN

    CREATE TABLE "nachet_0.0.10"."user" (
        "id" uuid DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "email" VARCHAR(255) NOT NULL,
        "registration_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "nachet_0.0.10"."picture_set" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "picture_set" json NOT NULL,
        "owner_id" uuid NOT NULL REFERENCES "nachet_0.0.10".user(id),
        "upload_date" date NOT NULL DEFAULT current_timestamp
    );
    
    CREATE TABLE "nachet_0.0.10"."picture" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "picture" json NOT NULL,
        "picture_set_id" uuid NOT NULL REFERENCES "nachet_0.0.10".picture_set(id),
        "nb_obj" integer NOT NULL,
        "verified" boolean NOT NULL DEFAULT false
    );
    CREATE TABLE "nachet_0.0.10"."object_type" (
        "id" SERIAL PRIMARY KEY,
        "name" text NOT NULL
    );

    INSERT INTO "nachet_0.0.10"."object_type" ("name") VALUES ('seed');
      CREATE TABLE "nachet_0.0.10"."seed" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_.generate_v4() PRIMARY KEY,
        "name" text NOT NULL,
        "object_type_id" integer GENERATED ALWAYS AS (1) STORED
    );

    CREATE TABLE "nachet_0.0.10"."inference" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "inference" json NOT NULL,
        "picture_id" uuid NOT NULL REFERENCES "nachet_0.0.10".picture(id)
    );
 
    CREATE TABLE "nachet_0.0.10"."model" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "name" text NOT NULL
    );
    
    CREATE TABLE "nachet_0.0.10"."model_version" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "model_id" uuid NOT NULL REFERENCES "nachet_0.0.10".model(id),
        "data" json NOT NULL,
        "version" text NOT NULL
    );
    
    Alter table "nachet_0.0.10".model ADD "active_version" uuid NOT NULL REFERENCES "nachet_0.0.10".model_version(id);

    CREATE TABLE "nachet_0.0.10"."object" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "box_metadata" json NOT NULL,
        "inference_id" uuid NOT NULL REFERENCES "nachet_0.0.10".inference(id),
        "type_id" integer NOT NULL REFERENCES "nachet_0.0.10".object_type(id),
        "verified_id" uuid NOT NULL,
        "valid" boolean NOT NULL DEFAULT true,
        "top_inference_id" uuid NOT NULL
    );
    
    
    CREATE TABLE "nachet_0.0.10"."pipeline" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "name" text NOT NULL,
        "active" boolean NOT NULL DEFAULT false,
    );

    CREATE TABLE "nachet_0.0.10"."pipeline_default" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "pipeline_id" uuid NOT NULL REFERENCES "nachet_0.0.10".pipeline(id),
        "user_id" uuid NOT NULL REFERENCES "nachet_0.0.10".user(id)
    );

    CREATE UNIQUE INDEX "nachet_0.0.10_pipeline_default" ON "nachet_0.0.10".pipeline ("is_default") where is_default=true;
    
    CREATE TABLE "nachet_0.0.10"."pipeline_model" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "pipeline_id" uuid NOT NULL REFERENCES "nachet_0.0.10".pipeline(id),
        "model_id" uuid NOT NULL REFERENCES "nachet_0.0.10".model(id)
    );
    
    CREATE TABLE "nachet_0.0.10"."seed_obj" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "seed_id" uuid NOT NULL REFERENCES "nachet_0.0.10".seed(id),
        "object_id" uuid NOT NULL REFERENCES "nachet_0.0.10".object(id)
    );  

END IF;
END
$do$