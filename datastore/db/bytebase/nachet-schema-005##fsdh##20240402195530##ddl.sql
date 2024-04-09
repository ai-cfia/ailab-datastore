SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE SCHEMA "nachet_0.0.5";

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "nachet_0.0.5";

CREATE TABLE "nachet_0.0.5".users (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "nachet_0.0.5".picture_set (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    picture_set JSON,
    owner_id uuid REFERENCES users(id),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "nachet_0.0.5".pictures (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    picture_set_id uuid REFERENCES picture_set(id),
    picture JSON,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "nachet_0.0.5".seeds (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    metadata JSON,
    name VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "nachet_0.0.5".picture_seed (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    picture_id uuid REFERENCES picture(id),
    seed_id uuid REFERENCES seeds(id),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE SCHEMA "finesse_1.0.0";

CREATE SCHEMA "nachet_0.0.3";

CREATE SCHEMA "nachet_0.0.4";

CREATE SCHEMA "nachetdb_0.0.1";

CREATE SCHEMA "nachetdb_0.0.2";

CREATE SCHEMA "nachetdb_1.0.0";

CREATE SCHEMA test_schema_two;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "nachet_0.0.4";

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';

SET default_tablespace = '';

SET default_table_access_method = heap;

CREATE TABLE "nachet_0.0.3".picture_seed (
    id uuid NOT NULL,
    seed_id uuid,
    picture_id uuid
);

CREATE TABLE "nachet_0.0.3".picture_set (
    id uuid NOT NULL,
    picture_set json,
    owner_id uuid,
    upload_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "nachet_0.0.3".pictures (
    id uuid NOT NULL,
    picture json,
    picture_set_id uuid,
    upload_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "nachet_0.0.3".seeds (
    id uuid NOT NULL,
    metadata json,
    name character varying(255)
);

CREATE TABLE "nachet_0.0.3".users (
    id uuid NOT NULL,
    email character varying(255),
    registration_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "nachet_0.0.4".picture_seed (
    id uuid DEFAULT "nachet_0.0.4".uuid_generate_v4() NOT NULL,
    seed_id uuid,
    picture_id uuid NOT NULL
);

CREATE TABLE "nachet_0.0.4".picture_set (
    id uuid DEFAULT "nachet_0.0.4".uuid_generate_v4() NOT NULL,
    picture_set json NOT NULL,
    owner_id uuid NOT NULL,
    upload_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE "nachet_0.0.4".pictures (
    id uuid DEFAULT "nachet_0.0.4".uuid_generate_v4() NOT NULL,
    picture json NOT NULL,
    picture_set_id uuid NOT NULL,
    upload_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE "nachet_0.0.4".seeds (
    id uuid DEFAULT "nachet_0.0.4".uuid_generate_v4() NOT NULL,
    metadata json,
    name character varying(255) NOT NULL,
    upload_date date DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE "nachet_0.0.4".users (
    id uuid DEFAULT "nachet_0.0.4".uuid_generate_v4() NOT NULL,
    email character varying(255) NOT NULL,
    registration_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "nachetdb_0.0.1".indexes (
    id uuid NOT NULL,
    index json,
    ownerid uuid
);

CREATE TABLE "nachetdb_0.0.1".pictures (
    id uuid NOT NULL,
    picture json,
    indexid uuid
);

CREATE TABLE "nachetdb_0.0.1".seeds (
    id uuid NOT NULL,
    info json,
    name character varying(255)
);

CREATE TABLE "nachetdb_0.0.1".users (
    id uuid NOT NULL,
    email character varying(255)
);

CREATE TABLE "nachetdb_0.0.2".pictures (
    id uuid NOT NULL,
    picture json,
    indexid uuid
);

CREATE TABLE "nachetdb_0.0.2".seedpicture (
    id uuid NOT NULL,
    seedid uuid,
    pictureid uuid
);

CREATE TABLE "nachetdb_0.0.2".seeds (
    id uuid NOT NULL,
    info json,
    name character varying(255)
);

CREATE TABLE "nachetdb_0.0.2".sessions (
    id uuid NOT NULL,
    session json,
    ownerid uuid
);

CREATE TABLE "nachetdb_0.0.2".users (
    id uuid NOT NULL,
    email character varying(255)
);

CREATE TABLE "nachetdb_1.0.0".indexes (
    id uuid NOT NULL,
    index json,
    ownerid uuid
);

CREATE TABLE "nachetdb_1.0.0".pictures (
    id uuid NOT NULL,
    picture json,
    indexid uuid
);

CREATE TABLE "nachetdb_1.0.0".seeds (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    family character varying(255),
    genus character varying(255),
    species character varying(255)
);

CREATE SEQUENCE "nachetdb_1.0.0".seeds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE "nachetdb_1.0.0".seeds_id_seq OWNED BY "nachetdb_1.0.0".seeds.id;

CREATE TABLE "nachetdb_1.0.0".users (
    id uuid NOT NULL,
    email character varying(255)
);

ALTER TABLE ONLY "nachetdb_1.0.0".seeds ALTER COLUMN id SET DEFAULT nextval('"nachetdb_1.0.0".seeds_id_seq'::regclass);

ALTER TABLE ONLY "nachet_0.0.3".picture_seed
    ADD CONSTRAINT picture_seed_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachet_0.0.3".picture_set
    ADD CONSTRAINT picture_set_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachet_0.0.3".pictures
    ADD CONSTRAINT pictures_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachet_0.0.3".seeds
    ADD CONSTRAINT seeds_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachet_0.0.3".users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachet_0.0.4".picture_seed
    ADD CONSTRAINT picture_seed_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachet_0.0.4".picture_set
    ADD CONSTRAINT picture_set_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachet_0.0.4".pictures
    ADD CONSTRAINT pictures_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachet_0.0.4".seeds
    ADD CONSTRAINT seeds_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachet_0.0.4".users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_0.0.1".indexes
    ADD CONSTRAINT indexes_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_0.0.1".pictures
    ADD CONSTRAINT pictures_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_0.0.1".seeds
    ADD CONSTRAINT seeds_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_0.0.1".users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_0.0.2".pictures
    ADD CONSTRAINT pictures_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_0.0.2".seedpicture
    ADD CONSTRAINT seedpicture_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_0.0.2".seeds
    ADD CONSTRAINT seeds_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_0.0.2".sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_0.0.2".users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_1.0.0".indexes
    ADD CONSTRAINT indexes_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_1.0.0".pictures
    ADD CONSTRAINT pictures_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_1.0.0".seeds
    ADD CONSTRAINT seeds_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachetdb_1.0.0".users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

ALTER TABLE ONLY "nachet_0.0.3".picture_seed
    ADD CONSTRAINT picture_seed_picture_id_fkey FOREIGN KEY (picture_id) REFERENCES "nachet_0.0.3".pictures(id);

ALTER TABLE ONLY "nachet_0.0.3".picture_seed
    ADD CONSTRAINT picture_seed_seed_id_fkey FOREIGN KEY (seed_id) REFERENCES "nachet_0.0.3".seeds(id);

ALTER TABLE ONLY "nachet_0.0.3".picture_set
    ADD CONSTRAINT picture_set_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES "nachet_0.0.3".users(id);

ALTER TABLE ONLY "nachet_0.0.3".pictures
    ADD CONSTRAINT pictures_picture_set_id_fkey FOREIGN KEY (picture_set_id) REFERENCES "nachet_0.0.3".picture_set(id);

ALTER TABLE ONLY "nachet_0.0.4".picture_seed
    ADD CONSTRAINT "picture_seed-fk-f4xoixfb" FOREIGN KEY (picture_id) REFERENCES "nachet_0.0.4".pictures(id);

ALTER TABLE ONLY "nachet_0.0.4".picture_seed
    ADD CONSTRAINT "picture_seed-fk-t1o008x5" FOREIGN KEY (seed_id) REFERENCES "nachet_0.0.4".seeds(id);

ALTER TABLE ONLY "nachet_0.0.4".picture_seed
    ADD CONSTRAINT picture_seed_picture_id_fkey FOREIGN KEY (picture_id) REFERENCES "nachet_0.0.4".pictures(id);

ALTER TABLE ONLY "nachet_0.0.4".picture_seed
    ADD CONSTRAINT picture_seed_seed_id_fkey FOREIGN KEY (seed_id) REFERENCES "nachet_0.0.4".seeds(id);

ALTER TABLE ONLY "nachet_0.0.4".picture_set
    ADD CONSTRAINT "picture_set-fk-vz4mpzh9" FOREIGN KEY (owner_id) REFERENCES "nachet_0.0.4".users(id);

ALTER TABLE ONLY "nachet_0.0.4".picture_set
    ADD CONSTRAINT picture_set_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES "nachet_0.0.4".users(id);

ALTER TABLE ONLY "nachet_0.0.4".pictures
    ADD CONSTRAINT "pictures-fk-g47uaci9" FOREIGN KEY (picture_set_id) REFERENCES "nachet_0.0.4".picture_set(id);

ALTER TABLE ONLY "nachet_0.0.4".pictures
    ADD CONSTRAINT pictures_picture_set_id_fkey FOREIGN KEY (picture_set_id) REFERENCES "nachet_0.0.4".picture_set(id);

ALTER TABLE ONLY "nachetdb_0.0.1".indexes
    ADD CONSTRAINT indexes_ownerid_fkey FOREIGN KEY (ownerid) REFERENCES "nachetdb_0.0.1".users(id);

ALTER TABLE ONLY "nachetdb_0.0.1".pictures
    ADD CONSTRAINT pictures_indexid_fkey FOREIGN KEY (indexid) REFERENCES "nachetdb_0.0.1".indexes(id);

ALTER TABLE ONLY "nachetdb_0.0.2".pictures
    ADD CONSTRAINT pictures_indexid_fkey FOREIGN KEY (indexid) REFERENCES "nachetdb_0.0.2".sessions(id);

ALTER TABLE ONLY "nachetdb_0.0.2".seedpicture
    ADD CONSTRAINT seedpicture_pictureid_fkey FOREIGN KEY (pictureid) REFERENCES "nachetdb_0.0.2".pictures(id);

ALTER TABLE ONLY "nachetdb_0.0.2".seedpicture
    ADD CONSTRAINT seedpicture_seedid_fkey FOREIGN KEY (seedid) REFERENCES "nachetdb_0.0.2".seeds(id);

ALTER TABLE ONLY "nachetdb_0.0.2".sessions
    ADD CONSTRAINT sessions_ownerid_fkey FOREIGN KEY (ownerid) REFERENCES "nachetdb_0.0.2".users(id);

ALTER TABLE ONLY "nachetdb_1.0.0".indexes
    ADD CONSTRAINT indexes_ownerid_fkey FOREIGN KEY (ownerid) REFERENCES "nachetdb_1.0.0".users(id);

ALTER TABLE ONLY "nachetdb_1.0.0".pictures
    ADD CONSTRAINT pictures_indexid_fkey FOREIGN KEY (indexid) REFERENCES "nachetdb_1.0.0".indexes(id);