import asyncio
import os
import sys
import datastore
import datastore.db as db


DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

BLOB_CONNECTION_STRING = os.environ["FERTISCAN_STORAGE_URL"]
if BLOB_CONNECTION_STRING is None or BLOB_CONNECTION_STRING == "":
    raise ValueError("NACHET_STORAGE_URL_TESTING is not set")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        raise Exception("Error: No file path provided as argument")
    connection = db.connect_db(DB_CONNECTION_STRING,DB_SCHEMA)
    cur = db.cursor(connection)
    db.create_search_path(connection, cur,DB_SCHEMA)
    user = asyncio.run(datastore.new_user(cur, email,BLOB_CONNECTION_STRING,'dev-user'))
    print(f"User created with the following uuid: {user.get_id()}")
    db.end_query(connection, cur)
