"""
This file contains the queries for the seed table.
"""

class SeedNotFoundError(Exception):
    pass

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
        result=cursor.fetchone()[0]
        return result
    except(TypeError):
        raise SeedNotFoundError("Error: seed not found")
    except:
        raise Exception("unhandled error")


def new_seed(cursor, seed_name: str):
    """
    This function inserts a new seed into the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - seed_name (str): Name of the seed

    """
    try:
        query = """
            INSERT INTO 
                seeds(name)
            VALUES
                (%s)
            RETURNING id
            """
        cursor.execute(
            query,
            (
                seed_name,
            ),
        )
        return cursor.fetchone()[0]
    except:
        raise Exception("Error: picture_set not uploaded")
