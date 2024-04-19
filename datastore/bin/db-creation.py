import os
import datastore.db as db
import datastore.db.queries as queries

NACHET_SCHEMA = os.getenv("NACHET_SCHEMA")


def create_db():

    # Connect to your PostgreSQL database with the DB URL
    conn = db.connect_db()
    # Create a cursor object
    cur = db.cursor(connection=conn)

    # Create Schema
    cur.execute("""CREATE SCHEMA "%s";""", (NACHET_SCHEMA,))

    # # Create Search Path
    cur.execute(f"""SET search_path TO "{NACHET_SCHEMA}";""")

    # Create Users table
    query = """
        CREATE TABLE users (
            id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
            email VARCHAR(255),
            container_url VARCHAR(255),
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    queries.query_db(conn, cur, query)

    # Create PictureSet table

    query = """
        CREATE TABLE  picture_set (
            id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
            picture_set JSON,
            owner_id uuid REFERENCES users(id),
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    queries.query_db(conn, cur, query)

    # Create Pictures table

    query = """
        CREATE TABLE  pictures (
            id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
            picture JSON,
            picture_set_id uuid REFERENCES picture_set(id),
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """

    # Create seed DB
    query = """
        CREATE TABLE seeds (
            id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
            metadata JSON,
            name VARCHAR(255)
        )
    """
    queries.query_db(conn, cur, query)

    # Create SeedPicture table
    query = """
        CREATE TABLE picture_seed (
            id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
            seed_id uuid REFERENCES seeds(id),
            picture_id uuid REFERENCES pictures(id)
        )
    """
    queries.query_db(conn, cur, query)

    # # check if the search path exists
    # cur.execute("Show search_path")

    # check all the table under the schema
    # cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'nachetdb_0.0.2'")

    db.end_query(connection=conn, cursor=cur)
    print("done")


if __name__ == "__main__":
    create_db()
