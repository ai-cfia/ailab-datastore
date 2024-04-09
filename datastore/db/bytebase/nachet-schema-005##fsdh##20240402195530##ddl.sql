CREATE SCHEMA "nachet_0.0.5";

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "nachet_0.0.5";

SET search_path TO "nachet_0.0.5";

CREATE TABLE user (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE picture_set (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    picture_set JSON,
    owner_id uuid REFERENCES users(id),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE picture (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    picture_set_id uuid REFERENCES picture_set(id),
    picture JSON,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE seeds (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    metadata JSON,
    name VARCHAR(255),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE picture_seed (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    picture_id uuid REFERENCES picture(id),
    seed_id uuid REFERENCES seeds(id),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);