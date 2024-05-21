"""
This module contains the queries related to the user table.
"""


class UserCreationError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class ContainerNotSetError(Exception):
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
    except Exception:
        raise Exception(f"Error: could not check if the email {email} is a registered user")


def is_a_user_id(cursor, user_id: str) -> bool:
    """
    This function checks if a user is registered in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - user_id (str): The UUID of the user.

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
                    id = %s
            )
                """
        cursor.execute(query, (user_id,))
        res = cursor.fetchone()[0]
        return res
    except Exception:
        raise Exception(f"Error: could not check if {user_id} given is a user id")


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
    except TypeError:
        raise UserNotFoundError(f"Error: user {email} could not be retrieved")
    except Exception:
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
                users (email)
            VALUES
                (%s)
            RETURNING id
            """
        cursor.execute(
            query,
            (email,),
        )
        return cursor.fetchone()[0]
    except Exception:
        raise UserCreationError(f"Error: user {email} not registered")


def link_container(cursor, user_id: str, container_url: str):
    """
    This function links a container to a user in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - container_url (str): The url of the container

    Returns:
    - None
    """
    try:
        if not is_a_user_id(cursor=cursor, user_id=user_id):
            raise UserNotFoundError(f"User not found for the given id: {user_id}")
        query = """
            UPDATE 
                users
            SET 
                container_url = %s
            WHERE 
                id = %s
            """
        cursor.execute(
            query,
            (
                user_id,
                container_url,
            ),
        )
    except UserNotFoundError:
        raise
    except Exception:
        raise Exception("Error: could not link container to user")


def get_container_url(cursor, user_id: str):
    """
    This function retrieves the container url of a user.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - user_id (str): The UUID of the user

    Returns:
    - The container url of the user.
    """
    try:
        if not is_a_user_id(cursor=cursor, user_id=user_id):
            raise UserNotFoundError(f"User not found for the given id: {user_id}")
        query = """
            SELECT 
                container_url
            FROM 
                users
            WHERE 
                id = %s
            """
        cursor.execute(query, (user_id,))
        res = cursor.fetchone()[0]
        return res
    except TypeError:
        raise ContainerNotSetError(
            "Error: user does not have a container URL under its name"
        )
    except UserNotFoundError as e:
        raise e
    except Exception:
        raise Exception("Error: could not retrieve container url")
