import psycopg
import os

NACHET_DB_URL = os.getenv("NACHET_DB_URL")

NACHET_SCHEMA = os.getenv("NACHET_SCHEMA")
print(NACHET_SCHEMA)
# Connect to your PostgreSQL database with the DB URL
conn = psycopg.connect(NACHET_DB_URL)
# Create a cursor object
cur = conn.cursor()

# # Create Schema
# cur.execute("""CREATE SCHEMA "%s";""",(NACHET_SCHEMA,)) 

# # Create Search Path
cur.execute(f"""SET search_path TO "{NACHET_SCHEMA}";""")



#Create Users table
cur.execute("""
    CREATE TABLE users (
        id uuid PRIMARY KEY,
        email VARCHAR(255),
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
# Create PictureSet table
cur.execute("""
    CREATE TABLE  picture_set (
        id uuid PRIMARY KEY,
        picture_set JSON,
        owner_id uuid REFERENCES users(id),
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
# Create Pictures table
cur.execute("""
    CREATE TABLE  pictures (
        id uuid PRIMARY KEY,
        picture JSON,
        picture_set_id uuid REFERENCES picture_set(id),
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
# Create seed DB
cur.execute("""
    CREATE TABLE seeds (
        id uuid PRIMARY KEY,
        metadata JSON,
        name VARCHAR(255)
    )
""" )
conn.commit()
# Create SeedPicture table
cur.execute("""
    CREATE TABLE picture_seed (
        id uuid PRIMARY KEY,
        seed_id uuid REFERENCES seeds(id),
        picture_id uuid REFERENCES pictures(id)
    )
""")

# # check if the search path exists
# cur.execute("Show search_path")

# check all the table under the schema
# cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'nachetdb_0.0.2'")

## Commit the transaction
conn.commit()

for record in cur:
    print(record)

# Close the cursor and connection
cur.close()
conn.close()
print("done")