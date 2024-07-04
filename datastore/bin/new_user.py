import asyncio
import sys
import datastore
import datastore.db as db


if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        raise Exception("Error: No file path provided as argument")
    connection = db.connect_db()
    cur = db.cursor(connection)
    db.create_search_path(connection, cur)
    user = asyncio.run(datastore.new_user(cur, email,datastore.NACHET_STORAGE_URL,'user'))
    print(f"User created with the following uuid: {user.get_id()}")
    db.end_query(connection, cur)