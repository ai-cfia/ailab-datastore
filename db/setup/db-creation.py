import db.queries.queries as queries

# Connect to your PostgreSQL database with the DB URL
conn = queries.createConnection()
# Create a cursor object
cur = queries.createCursor(conn)

# # Create Schema
# cur.execute("""CREATE SCHEMA "nachetdb_0.0.1";""") 

# # Create Search Path
# cur.execute("""SET search_path TO "nachetdb_0.0.1";""") 

# #Create Users table
# cur.execute("""
#     CREATE TABLE \"%s\".users (
#         id uuid  PRIMARY KEY,
#         email VARCHAR(255)
#     )
# """ % ("nachetdb_0.0.1"))

# # Create Indexes table
# cur.execute("""
#     CREATE TABLE  \"%s\".indexes (
#         id uuid  PRIMARY KEY,
#         index JSON,
#         ownerID uuid REFERENCES "nachetdb_0.0.1".users(id)
#     )
# """ % ("nachetdb_0.0.1"))

# # Create Pictures table
# cur.execute("""
#     CREATE TABLE  \"%s\".pictures (
#         id uuid  PRIMARY KEY,
#         picture JSON,
#         indexID uuid REFERENCES "nachetdb_0.0.1".indexes(id)
#     )
# """ % ("nachetdb_0.0.1"))

# Create seed DB
cur.execute("""
    CREATE TABLE  \"%s\".seeds (
        id uuid  PRIMARY KEY,
        info JSON,
        name VARCHAR(255)
    )
""" % ("nachetdb_0.0.1"))

# # check if the schema exists
cur.execute("""
    SELECT EXISTS (
        SELECT *
        FROM information_schema.schemata
        WHERE schema_name = 'nachetdb_0.0.1'
    )
""")

# # check if the search path exists
# cur.execute("Show search_path")


## Commit the transaction
conn.commit()

print(cur.fetchone()[0])

# Close the cursor and connection
cur.close()
conn.close()
print("done")