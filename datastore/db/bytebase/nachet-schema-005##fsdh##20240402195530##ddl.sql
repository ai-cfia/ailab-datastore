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

SET search_path TO "nachet_0.0.5";

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