import psycopg
import os

print(os.getenv("NACHET_DB_URL"))
# Connect to your PostgreSQL database
conn = psycopg.connect(os.getenv("NACHET_DB_URL"))
# Create a cursor object
cur = conn.cursor()

# check if the table exists
cur.execute("""
    SELECT id,picture from "nachetdb_1.0.0".pictures
""")

## Commit the transaction
conn.commit()

for record in cur:
    print(record)
#print(cur.fetchone()[1])

# Close the cursor and connection
cur.close()
conn.close()
print("done")