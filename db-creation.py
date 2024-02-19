import psycopg2
import os

print(os.getenv("NACHET_DB_URL"))
# Connect to your PostgreSQL database
conn = psycopg2.connect(os.getenv("NACHET_DB_URL"))
#conn = psycopg2.connect(
#    host="",
#    dbname='',
#    port='',
#    user="",
#    password="")
# Create a cursor object
cur = conn.cursor()

# # Create Schema
# cur.execute("CREATE SCHEMA nachetdb_0.0.1")

# # Create Users table
# cur.execute("""
#     CREATE TABLE nachetdb_0.0.1.users (
#         id uuid  PRIMARY KEY,
#         email VARCHAR(255),
#     )
# """)

# # Create Indexes table
# cur.execute("""
#     CREATE TABLE nachetdb_0.0.1.indexes (
#         id SERIAL PRIMARY KEY,
#         index JSON,
#         ownerID INTEGER REFERENCES users(id)
#     )
# """)

# # Create Pictures table
# cur.execute("""
#     CREATE TABLE nachetdb_0.0.1.pictures (
#         id SERIAL PRIMARY KEY,
#         picture JSON,
#         indexID INTEGER REFERENCES indexes(id)
#     )
# """)

## Commit the transaction
#conn.commit()

# Check if the table exists
cur.execute("""
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'nachetdb_0.0.1'
        AND table_name = 'users'
    )
""")

exists = cur.fetchone()[0]

if exists:
    print("Table nachetdb_0.0.1.users exists.")
else:
    print("Table nachetdb_0.0.1.users does not exist.")

# Close the cursor and connection
cur.close()
conn.close()
print("done")