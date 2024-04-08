"""
This module contains the queries related to the user table.
"""
class UserCreationError(Exception):
    pass
class UserNotFoundError(Exception):
    pass


def is_user_registered(cursor, email: str) -> bool:
    """
    This function checks if a user is registered in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - email (str): The email of the user.

    Returns:
    - True if the user is registered, False otherwise.
    """
    try:
        query = """
            SELECT EXISTS(
                SELECT 
                    1 
                FROM 
                    users
                WHERE 
                    email = %s
            )
                """
        cursor.execute(query, (email,))
        res = cursor.fetchone()[0]
        return res
    except:
        raise Exception("Error: could not check if user is registered")


def get_user_id(cursor, email: str) -> str:
    """
    This function retrieves the UUID of a user.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - email (str): Email of the user

    Returns:
    - The UUID of the user.
    """
    try:
        query = """
            SELECT 
                id 
            FROM 
                users
            WHERE 
                email = %s
                """
        cursor.execute(query, (email,))
        res = cursor.fetchone()[0]
        return res
    except(TypeError) :
        raise UserNotFoundError("Error: user could not be retrieved")
    except:
        raise Exception("Unhandled Error")


def register_user(cursor, email: str) -> None:
    """
    This function registers a user in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - email (str): Email of the user

    Returns:
    - The UUID of the user.
    """
    try:
        query = """
            INSERT INTO 
                users(email)
            VALUES
                (%s)
            RETURNING id
            """
        cursor.execute(
            query,
            (email,),
        )
        return cursor.fetchone()[0]
    except:
        raise UserCreationError("Error: user not registered")
