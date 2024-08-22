class PictureUploadError(Exception):
    pass


class PictureNotFoundError(Exception):
    pass


class PictureSetCreationError(Exception):
    pass


class PictureSetNotFoundError(Exception):
    pass


class PictureUpdateError(Exception):
    pass

class GetPictureSetError(Exception):
    pass

class GetPictureError(Exception):
    pass

class PictureSetDeleteError(Exception):
    pass

"""
This module contains all the queries related to the Picture and PictureSet tables.
"""

def new_picture_set(cursor, picture_set, user_id: str, folder_name: str = None):
    """
    This function uploads a new PictureSet to the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_set (str): The PictureSet to upload. Must be formatted as a json
    - user_id (str): The UUID of the user uploading.
    - folder_name (str, optional): The name of the folder. Defaults to None.

    Returns:
    - The UUID of the picture_set.
    """
    try:
        query = """
            INSERT INTO 
                picture_set(
                    picture_set,
                    owner_id,
                    name
                    )
            VALUES
                (%s, %s, %s)
            RETURNING id
            """
        cursor.execute(
            query,
            (
                picture_set,
                user_id,
                folder_name,
            ),
        )
        return cursor.fetchone()[0]
    except Exception:
        raise PictureSetCreationError("Error: picture_set not uploaded")


def new_picture(cursor, picture, picture_set_id: str, seed_id: str, nb_objects=0 ):
    """
    This function uploads a NEW PICTURE to the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture (str): The Picture METADATA to upload. Must be formatted as a json
    - picture_set_id (str): The UUID of the Picture_set the picture is in.
    - seedID (str): The UUID of the seed the picture is linked to.
    - nb_objects (int): The number of objects in the picture.

    Returns:
    - The UUID of the picture.
    """
    try:
        query = """
            INSERT INTO 
                picture(
                    picture,
                    picture_set_id,
                    nb_obj
                    )
            VALUES
                (%s,%s,%s)
            RETURNING id
                """
        cursor.execute(
            query,
            (
                picture,
                picture_set_id,
                nb_objects,
            ),
        )
        picture_id = cursor.fetchone()[0]
        query = """
            INSERT INTO 
                picture_seed(
                    seed_id,
                    picture_id
                    )
            VALUES
                (%s,%s)
                """
        cursor.execute(
            query,
            (
                seed_id,
                picture_id,
            ),
        )
        return picture_id
    except Exception:
        raise PictureUploadError("Error: Picture not uploaded")

def new_picture_unknown(cursor, picture, picture_set_id:str, nb_objects=0):
    """
    This function uploads a NEW PICTURE to the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture (str): The Picture METADATA to upload. Must be formatted as a json
    - picture_set_id (str): The UUID of the Picture_set the picture is in.
    - nb_objects (int): The number of objects in the picture.

    Returns:
    - The UUID of the picture.
    """
    try:
        query = """
            INSERT INTO 
                picture(
                    picture,
                    picture_set_id,
                    nb_obj
                    )
            VALUES
                (%s,%s,%s)
            RETURNING id
                """
        cursor.execute(
            query,
            (
                picture,
                picture_set_id,
                nb_objects,
            ),
        )
        return cursor.fetchone()[0]
    except Exception:
        raise PictureUploadError("Error: Picture not uploaded")


def get_picture_set(cursor, picture_set_id: str):
    """
    This function retrieves a PictureSet from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_set_id (str): The UUID of the PictureSet to retrieve.

    Returns:
    - The PictureSet in json format.
    """
    try:
        query = """
            SELECT
                picture_set
            FROM
                picture_set
            WHERE
                id = %s
                """
        cursor.execute(query, (picture_set_id,))
        return cursor.fetchone()[0]
    except Exception:
        raise PictureSetNotFoundError(f"Error: PictureSet not found:{picture_set_id}")
    
def get_picture_set_name(cursor, picture_set_id: str):
    """
    This function retrieves the name of a PictureSet from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - user_id (str): The UUID of the user to retrieve the picture_set from (the owner).
    - picture_set_id (str): The UUID of the PictureSet to retrieve.

    Returns:
    - The name of the PictureSet.
    """
    try:
        query = """
            SELECT
                name
            FROM
                picture_set
            WHERE
                id = %s
                """
        cursor.execute(query, (picture_set_id, ))
        name = cursor.fetchone()[0]
        return name if name is not None else picture_set_id
    except Exception:
        raise PictureSetNotFoundError(f"Error: PictureSet not found:{picture_set_id}")

def get_user_picture_sets(cursor, user_id: str):
    """
    This function retrieves all the PictureSets of a specific user from the database.

    Args:
    - cursor (cursor): The cursor of the database.
    - user_id (str): uuid of the user
    """
    try :
        query = """
            SELECT
                id,
                name
            FROM
                picture_set
            WHERE
                owner_id = %s
            """
        cursor.execute(query, (user_id,))
        if cursor.rowcount == 0:
            raise GetPictureSetError(f"Error: PictureSet not found for user:{user_id}")
        return cursor.fetchall()
    except Exception:
        raise GetPictureSetError(f"Error: Error retrieving picture_sets for user:{user_id}")

def get_picture(cursor, picture_id: str):
    """
    This function retrieves a Picture from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_id (str): The UUID of the Picture to retrieve.

    Returns:
    - The Picture in json format.
    """
    try:
        query = """
            SELECT
                picture
            FROM
                picture
            WHERE
                id = %s
                """
        cursor.execute(query, (picture_id,))
        return cursor.fetchone()[0]
    except Exception:
        raise PictureNotFoundError(f"Error: Picture not found: {picture_id}")

def count_pictures(cursor, picture_set_id: str):
    """This function retrieves the number of pictures in a picture_set.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_set_id (str): id of the picture_set to count the pictures from.
    """
    try :
        query = """
            SELECT
                COUNT(*)
            FROM
                picture
            WHERE
                picture_set_id = %s
            """
        cursor.execute(query, (picture_set_id,))
        return cursor.fetchone()[0]
    except Exception:
        raise PictureSetNotFoundError(f"Error getting pictures count in picture set : {picture_set_id}")

def get_picture_set_pictures(cursor, picture_set_id: str):
    """
    This function retrieves all the pictures of a specific picture_set from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_set_id (str): The UUID of the PictureSet to retrieve the pictures from.

    Returns:
    - The pictures in json format.
    """
    try:
        query = """
            SELECT
                *
            FROM
                picture
            WHERE
                picture_set_id = %s
            """
        cursor.execute(query, (picture_set_id,))
        return cursor.fetchall()
    except Exception:
        raise GetPictureError(f"Error: Error while getting pictures for picture_set:{picture_set_id}")

def get_validated_pictures(cursor, picture_set_id: str):
    """
    This functions select pictures from a picture set that have been validated. Therefore, there should exists picture_seed entity for this picture.  

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_set_id (str): The UUID of the PictureSet to retrieve the pictures from.
    """
    try :
        query = """
            SELECT
                p.id
            FROM
                picture_seed ps
            JOIN picture p on ps.picture_id = p.id 
            WHERE
                p.picture_set_id = %s
            """
        cursor.execute(query, (picture_set_id,))
        result = [row[0] for row in cursor.fetchall()]
        return result
    except Exception:
        raise GetPictureError(f"Error: Error while getting validated pictures for picture_set:{picture_set_id}")
    
def is_picture_validated(cursor, picture_id: str):
    """
    This functions check if a picture is validated. Therefore, there should exists picture_seed entity for this picture.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_id (str): The UUID of the picture to check.
    """
    try :
        query = """
            SELECT EXISTS(
                SELECT 
                    1 
                FROM 
                    picture_seed
                WHERE 
                    picture_id = %s
            )
            """
        cursor.execute(query, (picture_id,))
        result = cursor.fetchone()[0]
        return result
    except Exception:
        raise GetPictureError(
            f"Error: could not check if the picture {picture_id} is validated")

def check_picture_inference_exist(cursor, picture_id: str):
    """
    This functions check whether a picture is associated with an inference.
    
    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_id (str): The UUID of the picture to check.
    """
    try :
        query = """
            SELECT EXISTS(
                SELECT
                    1 
                FROM 
                    inference
                WHERE 
                    picture_id = %s
            )
            """
        cursor.execute(query, (picture_id,))
        result = cursor.fetchone()[0]
        return result
    except Exception:
        raise GetPictureError(
            f"Error: could not check if the picture {picture_id} has an existing inference")

def change_picture_set_id(cursor, user_id, old_picture_set_id, new_picture_set_id):
    """
    This function change picture_set_id of all pictures in a picture_set to a new one.
    
    Parameters:
    - cursor (cursor): The cursor of the database.
    - user_id (str): The UUID of the user who want to change the picture_set of pictures (the owner).
    - picture_set_id (str): The UUID of the PictureSet to retrieve the pictures from.
    """
    try :
        if get_picture_set_owner_id(cursor, old_picture_set_id) != user_id :
            raise PictureUpdateError(f"Error: old picture set not own by user :{user_id}")
        if get_picture_set_owner_id(cursor, new_picture_set_id) != user_id :
            raise PictureUpdateError(f"Error: new picture set not own by user :{user_id}")
        
        query = """
            UPDATE picture
            SET picture_set_id = %s
            WHERE picture_set_id = %s
        """
        cursor.execute(query, (new_picture_set_id, old_picture_set_id,))
    except PictureUpdateError as e:
        raise e
    except Exception:
        raise PictureUpdateError(f"Error: Error while updating pictures for picture_set:{old_picture_set_id}, for user:{user_id}")

def get_user_latest_picture_set(cursor, user_id: str):
    """
    This function retrieves the latest picture_set of a specific user from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - user_id (str): The UUID of the user to retrieve the picture_set from (the owner).

    Returns:
    - The picture_set in json format.
    """
    try:
        query = """
            SELECT
                picture_set
            FROM
                picture_set
            WHERE
                owner_id = %s
            ORDER BY
                upload_date
            DESC
            LIMIT 1
                """
        cursor.execute(query, (user_id,))
        return cursor.fetchone()[0]
    except Exception:
        raise PictureSetNotFoundError(
            f"Error: picture_set not found for user:{user_id} "
        )


def update_picture_metadata(cursor, picture_id: str, metadata: dict, nb_objects: int):
    """
    This function updates the metadata of a picture in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_id (str): The UUID of the picture to update.
    - metadata (dict): The metadata to update. Must be formatted as a json.

    Returns:
    - None
    """
    try:
        query = """
            UPDATE
                picture
            SET
                picture = %s,
                nb_obj = %s
            WHERE
                id = %s
            """
        cursor.execute(query, (metadata,nb_objects, picture_id))
    except Exception:
        raise PictureUpdateError(f"Error: Picture metadata not updated:{picture_id}")


def is_a_picture_set_id(cursor, picture_set_id):
    """
    This function checks if a picture_set_id exists in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_set_id (str): The UUID of the picture_set to check.
    """
    try:
        query = """
            SELECT EXISTS(
                SELECT 
                    1 
                FROM 
                    picture_set
                WHERE 
                    id = %s
            )
                """
        cursor.execute(query, (picture_set_id,))
        res = cursor.fetchone()[0]
        return res
    except Exception:
        raise Exception("unhandled error")

def is_a_picture_id(cursor, picture_id):
    """
    This function checks if a picture_id exists in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_id (str): The UUID of the picture to check.
    """
    try:
        query = """
            SELECT EXISTS(
                SELECT 
                    1 
                FROM 
                    picture
                WHERE 
                    id = %s
            )
                """
        cursor.execute(query, (picture_id,))
        res = cursor.fetchone()[0]
        return res
    except Exception:
        raise Exception("unhandled error")

def get_picture_picture_set_id(cursor, picture_id):
    """
    This function retrieves the picture_set_id of a picture in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_id (str): The UUID of the picture to retrieve the picture_set_id from.
    """
    try:
        query = """
            SELECT
                picture_set_id
            FROM
                picture
            WHERE
                id = %s
            """
        cursor.execute(query, (picture_id,))
        return str(cursor.fetchone()[0])
    except Exception:
        raise PictureNotFoundError(f"Error: Picture not found:{picture_id}")
    
def get_picture_set_owner_id(cursor, picture_set_id):
    """
    This function retrieves the owner_id of a picture_set.
    
    parameters:
    - cursor (cursor) : The cursor of the database.
    - picture_set_id (str) : The UUID of the picture_set to retrieve the owner_id from.
    """
    try:
        query = """
            SELECT
                owner_id
            FROM
                picture_set
            WHERE
                id = %s
            """
        cursor.execute(query, (picture_set_id,))
        return str(cursor.fetchone()[0])
    except Exception:
        raise PictureSetNotFoundError(f"Error: PictureSet not found:{picture_set_id}")
    
def update_picture_picture_set_id(cursor, picture_id, new_picture_set_id):
    """
    This function updates the picture_set_id of a picture in the database.

    parameters:
    - cursor (cursor) : The cursor of the database.
    - picture_id (str) : Picture to update.
    - new_picture_set_id (str) : New picture_set_id.
    """
    try:
        query = """
            UPDATE
                picture
            SET
                picture_set_id = %s
            WHERE
                id = %s
            """
        cursor.execute(query, (new_picture_set_id, picture_id))
    except Exception:
        raise PictureUpdateError(f"Error: Picture picture_set_id not updated:{picture_id}")
    
def delete_picture_set(cursor, picture_set_id):
    """
    This function deletes a picture_set from the database.
    
    parameters:
    - cursor (cursor) : The cursor of the database.
    - picture_set_id (str) : The UUID of the picture_set to delete.
    """
    try:
        query = """
            DELETE FROM
                picture_set
            WHERE
                id = %s
            """
        cursor.execute(query, (picture_set_id,))
    except Exception:
        raise PictureSetDeleteError(f"Error: PictureSet not deleted:{picture_set_id}")

def get_picture_in_picture_set(cursor, picture_set_id):
    """
    This function retrieves all the pictures of a specific picture_set from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_set_id (str): The UUID of the PictureSet to retrieve the pictures from.

    Returns:
    - The pictures in json format.
    """
    try:
        query = """
            SELECT
                picture
            FROM
                picture
            WHERE
                picture_set_id = %s
            """
        cursor.execute(query, (picture_set_id,))
        return cursor.fetchall()
    except Exception:
        raise GetPictureError(f"Error: Error while getting pictures for picture_set:{picture_set_id}")