--Schema creation nachet_0.0.8
DO
$do$
BEGIN
IF (EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'nachet_0.0.8')) THEN

    CREATE TABLE "nachet_0.0.8"."user" (
        "id" uuid DEFAULT "uuid_".uuid_generate_v4() PRIMARY KEY,
        "email" VARCHAR(255) NOT NULL,
        "registration_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE "nachet_0.0.8"."picture_set" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "picture_set" json NOT NULL,
        "owner_id" uuid NOT NULL REFERENCES "nachet_0.0.8".user(id),
        "upload_date" date NOT NULL DEFAULT current_timestamp
    );
    
    CREATE TABLE "nachet_0.0.8"."picture" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "picture" json NOT NULL,
        "picture_set_id" uuid NOT NULL REFERENCES "nachet_0.0.8".picture_set(id),
        "nb_obj" integer NOT NULL,
        "verified" boolean NOT NULL DEFAULT false
    );
    CREATE TABLE "nachet_0.0.8"."object_type" (
        "id" SERIAL PRIMARY KEY,
        "name" text NOT NULL
    );

    INSERT INTO "nachet_0.0.8"."object_type" ("name") VALUES ('seed');
    
    CREATE TABLE "nachet_0.0.8"."seed" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "name" text NOT NULL,
        "object_type_id" integer GENERATED ALWAYS AS (1) STORED
    );

    CREATE TABLE "nachet_0.0.8"."inference" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "inference" json NOT NULL,
        "picture_id" uuid NOT NULL REFERENCES "nachet_0.0.8".picture(id)
    );
 
    CREATE TABLE "nachet_0.0.8"."model" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "name" text NOT NULL,
        "active_version" uuid NOT NULL REFERENCES "nachet_0.0.8".model_version(id)
    );
    
    CREATE TABLE "nachet_0.0.8"."model_version" (
        "id" integer NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "model_id" uuid NOT NULL REFERENCES "nachet_0.0.8".model(id),
        "data" json NOT NULL,
        "version" text NOT NULL DEFAULT '0.0.0'
    );
    
    CREATE TABLE "nachet_0.0.8"."object" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "box_metadata" json NOT NULL,
        "inference_id" uuid NOT NULL REFERENCES "nachet_0.0.8".inference(id),
        "type_id" uuid NOT NULL REFERENCES "nachet_0.0.8".obj_type(id),
        "verified_id" uuid NOT NULL,
        "valid" boolean NOT NULL DEFAULT true,
        "top_inference_id" uuid NOT NULL
    );
    
    
    CREATE TABLE "nachet_0.0.8"."pipeline" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "name" text NOT NULL,
        "active" boolean NOT NULL DEFAULT false,
        "is_default" boolean NOT NULL DEFAULT false
    );

    CREATE UNIQUE INDEX "nachet_0.0.8"."pipeline_default" ON "nachet_0.0.8".pipeline("is_default") where is_default=true;
    
    CREATE TABLE "nachet_0.0.8"."pipeline_model" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "pipeline_id" uuid NOT NULL REFERENCES "nachet_0.0.8".pipeline(id),
        "model_id" uuid NOT NULL REFERENCES "nachet_0.0.8".model(id)
    );
    
    CREATE TABLE "nachet_0.0.8"."seed_obj" (
        "id" uuid NOT NULL DEFAULT uuid_.uuid_generate_v4() PRIMARY KEY,
        "seed_id" uuid NOT NULL REFERENCES "nachet_0.0.8".seed(id),
        "object_id" uuid NOT NULL REFERENCES "nachet_0.0.8".object(id)
    );
END IF;
END
$do$
