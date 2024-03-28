import uuid


def get_all_seeds_names(cursor):
    """
    This function returns all the seed name from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.

    Returns:
    - list of all the names.
    """
    try:
        query = """
            SELECT 
                name 
            FROM 
                seeds
            """
        cursor.execute(query)
        return cursor.fetchall()
    except:
        raise Exception("Error: seeds could not be retrieved")


def get_seed_id(cursor, seed_name: str) -> str:
    """
    This function retrieve the UUUID of a seed.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - seed_name (str): Name of the seed

    Returns:
    - The UUID of the seed.
    """
    try:
        query = """
            SELECT 
                id 
            FROM 
                seeds
            WHERE 
                name = %s
                """
        cursor.execute(query, (seed_name,))
        return cursor.fetchone()[0]
    except:
        raise Exception("Error: seed not found")


def new_seed(cursor, seed_name: str):
    # TODO: remove id from the table
    """
    This function inserts a new seed into the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - seed_name (str): Name of the seed

    """
    seed_id = uuid.uuid4()
    try:
        query = """
            INSERT INTO 
                seeds(id,name)
            VALUES
                (%s,%s)
            RETURNING id
            """
        cursor.execute(
            query,
            (
                seed_id,
                seed_name,
            ),
        )
        return cursor.fetchone()[0]
    except:
        raise Exception("Error: picture_set not uploaded")
