""" 
This module contains the function interacting with the database directly.
"""
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

# def connect_db():
#     """Connect to the postgresql database and return the connection."""
#     connection = psycopg.connect(
#         conninfo=NACHET_DB_URL,
#         autocommit=False,
#         options=f"-c search_path={NACHET_SCHEMA},public")
#     assert connection.info.encoding == 'utf-8', (
#         'Encoding is not UTF8: ' + connection.info.encoding)
#     # psycopg.extras.register_uuid()
#     return connection


def connect_db(conn_str : str = NACHET_DB_URL, schema :str  = NACHET_SCHEMA):
    """Connect to the postgresql database and return the connection."""
    connection = psycopg.connect(
        conninfo=conn_str,
        autocommit=False,
        options=f"-c search_path={schema},public",
    )
    assert connection.info.encoding == "utf-8", (
        "Encoding is not UTF8: " + connection.info.encoding
    )
    # psycopg.extras.register_uuid()
    return connection


def cursor(connection):
    """Return a cursor for the given connection."""
    return connection.cursor()


def end_query(connection, cursor):
    """Commit the transaction and close the cursor and connection."""
    connection.commit()
    cursor.close()
    connection.close()


def create_search_path(connection, cur,schema = NACHET_SCHEMA):
    cur.execute(f"""SET search_path TO "{schema}";""")
    connection.commit()

if __name__ == "__main__":
    connection = connect_db(FERTISCAN_DB_URL,FERTISCAN_SCHEMA)
    print(FERTISCAN_DB_URL)
    cur = cursor(connection)
    create_search_path(connection, cur,FERTISCAN_SCHEMA)
    end_query(connection, cur)
    print("Connection to the database successful")
