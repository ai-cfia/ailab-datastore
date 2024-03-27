import json
import uuid
def new_picture_set(cursor,picture_set,user_id:str):
    """
    This function uploads a new PictureSet to the database.
    
    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture_set (str): The PictureSet to upload. Must be formatted as a json
    - user_id (str): The UUID of the user uploading.
    
    Returns:
    - The UUID of the picture_set.
    """
    try:
        query = """
            INSERT INTO 
                picture_set(
                    id,
                    picture_set,
                    owner_id
                    )
            VALUES
                (%s,%s,%s)
            RETURNING id    
            """
        cursor.execute(query, (uuid.uuid4(),picture_set,user_id,))
        return cursor.fetchone()[0]
    except:
        raise Exception("Error: picture_set not uploaded")
    

def new_picture(cursor,picture,picture_set_id:str,seed_id:str):
    """
    This function uploads a NEW PICTURE to the database.
    
    Parameters:
    - cursor (cursor): The cursor of the database.
    - picture (str): The Picture to upload. Must be formatted as a json
    - picture_set_id (str): The UUID of the Picture_set the picture is in.
    - seedID (str): The UUID of the seed the picture is linked to.
    
    Returns:
    - The UUID of the picture.
    """
    try:
        query = """
            INSERT INTO 
                pictures(
                    id,
                    picture,
                    picture_set_id
                    )
            VALUES
                (%s,%s,%s)
            RETURNING id
                """
        cursor.execute(query, (uuid.uuid4(),picture,picture_set_id,))
        id=cursor.fetchone()[0]
        query = """
            INSERT INTO 
                picture_seed(
                    id,
                    seed_id,
                    picture_id
                    )
            VALUES
                (%s,%s,%s)
                """
        cursor.execute(query, (uuid.uuid4(),seed_id,id,))
        return id
    except:
        raise Exception("Error: Picture not uploaded")


def get_picture_set(cursor,picture_set_id:str):
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
    except:
        raise Exception("Error: PictureSet not found")

def get_user_latest_picture_set(cursor,user_id:str):
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
        cursor.execute(query,(user_id,))
        return cursor.fetchone()[0]
    except:
        raise Exception("Error: picture_set not found")