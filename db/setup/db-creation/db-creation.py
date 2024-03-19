import psycopg
import os

NACHET_DB_URL = os.getenv("NACHET_DB_URL")

NACHET_SCHEMA = os.getenv("NACHET_SCHEMA")
# Connect to your PostgreSQL database with the DB URL
conn = psycopg.connect(NACHET_DB_URL)
# Create a cursor object
cur = conn.cursor()

# # Create Schema
# cur.execute("""CREATE SCHEMA "nachetdb_0.0.2";""") 

# # Create Search Path
# cur.execute("""SET search_path TO "nachetdb_0.0.2";""") 

# #Create Users table
# cur.execute("""
#     CREATE TABLE \"%s\".users (
#         id uuid  PRIMARY KEY,
#         email VARCHAR(255)
#     )
# """ % ("nachetdb_0.0.2"))

# # Create Sessions table
# cur.execute("""
#     CREATE TABLE  \"%s\".sessions (
#         id uuid  PRIMARY KEY,
#         session JSON,
#         ownerID uuid REFERENCES "nachetdb_0.0.2".users(id)
#     )
# """ % ("nachetdb_0.0.2"))

# # Create Pictures table
# cur.execute("""
#     CREATE TABLE  \"%s\".pictures (
#         id uuid  PRIMARY KEY,
#         picture JSON,
#         indexID uuid REFERENCES "nachetdb_0.0.2".sessions(id)
#     )
# """ % ("nachetdb_0.0.2"))

# # Create seed DB
# cur.execute("""
#     CREATE TABLE  \"%s\".seeds (
#         id uuid  PRIMARY KEY,
#         info JSON,
#         name VARCHAR(255)
#     )
# """ % ("nachetdb_0.0.2"))

# # Create SeedPicture table
# cur.execute("""
#     CREATE TABLE  \"%s\".seedpicture (
#         id uuid  PRIMARY KEY,
#         seedID uuid REFERENCES "nachetdb_0.0.2".seeds(id),
#         pictureID uuid REFERENCES "nachetdb_0.0.2".pictures(id)
#     )
# """ % ("nachetdb_0.0.2"))

# # check if the search path exists
# cur.execute("Show search_path")

# check all the table under the schema
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'nachetdb_0.0.2'")

## Commit the transaction
conn.commit()

for record in cur:
    print(record)

# Close the cursor and connection
cur.close()
conn.close()
print("done")