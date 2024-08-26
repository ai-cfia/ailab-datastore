import os
import datastore.db as db
import datastore.db.queries as queries
import psycopg
from psycopg import sql

DB_URL = os.environ.get("FERTISCAN_DB_URL")
SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")

def create_db(DB_URL, SCHEMA : str):

    conn = db.connect_db(DB_URL, SCHEMA)
    cur = db.cursor(connection=conn)
    db.create_search_path(connection=conn, cur=cur, schema=SCHEMA)



    # Create the tables
    schema_number = SCHEMA.removeprefix("fertiscan_")
    try:
        path = "datastore/db/bytebase/FertiScan/schema_" + schema_number + ".sql"
        #execute_sql_file(cur, path)

        # Create the functions
        path = "datastore/db/bytebase/FertiScan/new_inspection"
        loop_for_sql_files(cur, path)

        path = "datastore/db/bytebase/FertiScan/new_inspection_function.sql"
        execute_sql_file(cur, path)

        path = "datastore/db/bytebase/FertiScan/get_inspection"
        loop_for_sql_files(cur, path)

        path = "datastore/db/bytebase/FertiScan/update_inspection_function.sql"
        execute_sql_file(cur, path)
    except Exception as e:
        conn.rollback()
        print(e)
    
    db.end_query(connection=conn, cursor=cur)

def loop_for_sql_files(cursor, folder_path):
    # Loop through all files in the specified folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.sql'):
                file_path = os.path.join(root, file)
                execute_sql_file(cursor, file_path)

def execute_sql_file(cursor,sql_file):
    with open(sql_file, 'r') as f:
        sql_content = f.read()
        try:
            cursor.execute(sql.SQL(sql_content))
            print(f"Executed {sql_file} successfully.")
        except Exception as e:
            raise Exception(f"Failed to execute {sql_file}: {e}")


if __name__ == "__main__":
    create_db(DB_URL=DB_URL, SCHEMA=SCHEMA)
