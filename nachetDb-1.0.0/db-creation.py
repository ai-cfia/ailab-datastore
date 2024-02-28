import psycopg
import os

print(os.getenv("NACHET_DB_URL"))
# Connect to your PostgreSQL database
conn = psycopg.connect(os.getenv("NACHET_DB_URL"))
# Create a cursor object
cur = conn.cursor()

# # Create Schema
# cur.execute("CREATE SCHEMA \"%s\"" % ("nachetdb_1.0.0"))

# #Create Users table
# cur.execute("""
#     CREATE TABLE \"%s\".users (
#         id uuid  PRIMARY KEY,
#         email VARCHAR(255)
#     )
# """ % ("nachetdb_1.0.0"))

# # Create Indexes table
# cur.execute("""
#     CREATE TABLE  \"%s\".indexes (
#         id SERIAL PRIMARY KEY,
#         index JSON,
#         ownerID uuid REFERENCES "nachetdb_1.0.0".users(id)
#     )
# """ % ("nachetdb_1.0.0"))

# # Create Pictures table
# cur.execute("""
#     CREATE TABLE  \"%s\".pictures (
#         id SERIAL PRIMARY KEY,
#         picture JSON,
#         indexID INTEGER REFERENCES "nachetdb_1.0.0".indexes(id)
#     )
# """ % ("nachetdb_1.0.0"))

# check if the table exists
cur.execute("""
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'nachetdb_1.0.0'
        AND table_name = 'users'
    )
""")

## Commit the transaction
conn.commit()

print(cur.fetchone()[0])

# Close the cursor and connection
cur.close()
conn.close()
print("done")