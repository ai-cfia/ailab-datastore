""" 
This module contains the function interacting with the database directly.
"""
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

NACHET_DB_URL = os.environ.get("NACHET_DB_URL")
if NACHET_DB_URL is None or NACHET_DB_URL == "":
    raise ValueError("NACHET_DB_URL is not set")

NACHET_SCHEMA = os.environ.get("NACHET_SCHEMA")
if NACHET_SCHEMA is None or NACHET_SCHEMA == "":
    raise ValueError("NACHET_SCHEMA is not set")

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


def connect_db():
    """Connect to the postgresql database and return the connection."""
    connection = psycopg.connect(
        conninfo=NACHET_DB_URL,
        autocommit=False,
        options=f"-c search_path={NACHET_SCHEMA},public",
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


def create_search_path(connection, cur):
    cur.execute(f"""SET search_path TO "{NACHET_SCHEMA}";""")
    connection.commit()

if __name__ == "__main__":
    connection = connect_db()
    cur = cursor(connection)
    create_search_path(connection, cur)
    end_query(connection, cur)
    print("Connection to the database successful")
