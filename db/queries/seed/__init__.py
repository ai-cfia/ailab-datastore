def get_all_seeds_names(cursor):
    """
    This function returns all the seed name from the database.
    
    Parameters:
    - cursor (cursor): The cursor of the database.
    
    Returns:
    - list of all the names.
    """
    query = """
        SELECT 
            name 
        FROM 
            seeds
            """
    cursor.execute(query)
    return cursor.fetchall()

def getSeedID(cursor,seed_name: str) -> str:
    """
    This function retrieve the UUUID of a seed.
    
    Parameters:
    - cursor (cursor): The cursor of the database.
    - seed_name (str): Name of the seed
    
    Returns:
    - The UUID of the seed.
    """
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

def newSeed(cursor, seed_name: str):
    """
    This function inserts a new seed into the database.
    
    Parameters:
    - cursor (cursor): The cursor of the database.
    - seed_name (str): Name of the seed
    
    """
    query = """
        INSERT INTO 
            seeds(name)
        VALUES
            (%s)
            """
    cursor.execute(query, (seed_name,))