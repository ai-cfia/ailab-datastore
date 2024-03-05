import psycopg
import os
import uuid

# Connect to your PostgreSQL database with the DB URL
conn = psycopg.connect(os.getenv("NACHET_DB_URL"))
# Create a cursor object
cur = conn.cursor()

id = uuid.uuid4()

#Query to insert a seed
query="INSERT INTO \"nachetdb_1.0.0\".seeds (name) VALUES ('Solanum nigrum')"

#query = "Select id,name from \"nachetdb_1.0.0\".seeds"

print(query)

cur.execute(query)

## Commit the transaction
conn.commit()

for row in cur.fetchall():
    print(row)


# Close the cursor and connection
cur.close()
conn.close()
print("done")
