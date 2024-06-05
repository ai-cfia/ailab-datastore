"""
This module contains the queries related to the inference related tables.

"""
import json
import datastore.db.queries.seed as seed
import datastore.db.metadata.inference as metadata

class InferenceCreationError(Exception):
    pass

class SeedObjectCreationError(Exception):  
    pass

class InferenceNotFoundError(Exception):
    pass


def new_inference(cursor, inference, user_id: str, picture_id:str,type):
    """
    This function uploads a new inference to the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inference (str): The inference to upload. Must be formatted as a json
    - user_id (str): The UUID of the user uploading.
    - picture_id (str): The UUID of the picture the inference is related to.

    Returns:
    - The inference dict with the UUIDs of the inference, boxes and topN.
    """
    try:
        query = """
            INSERT INTO 
                inference(
                    inference,
                    picture_id,
                    user_id
                    )
            VALUES
                (%s,%s,%s)
            RETURNING id    
            """
        cursor.execute(
            query,
            (
                inference,
                picture_id,
                user_id,
            ),
        )
        inference_id=cursor.fetchone()[0]
        return inference_id
    except Exception:
        raise InferenceCreationError("Error: inference not uploaded")

def new_inference_object(cursor, inference_id: str,box_metadata:str,type_id:int):
    """
    This function uploads a new inference object to the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inference_id (str): The UUID of the inference.
    - type_id (int): The UUID of the type.

    Returns:
    - The UUID of the inference object.
    """
    try:
        query = """
            INSERT INTO 
                object(
                    inference_id,
                    box_metadata,
                    type_id
                    )
            VALUES
                (%s,%s,%s)
            RETURNING id    
            """
        cursor.execute(
            query,
            (
                inference_id,
                box_metadata,
                type_id,
            ),
        )
        return cursor.fetchone()[0]
    except Exception:
        raise InferenceCreationError("Error: inference object not uploaded")
    
def set_inference_object_top_id(cursor, inference_object_id: str, top_id:str):
    """
    This function sets the top_id of an inference.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inference_id (str): The UUID of the inference.
    - top_id (str): The UUID of the top.
    """
    try:
        query = """
            UPDATE 
                object
            SET
                top_inference_id = %s
            WHERE 
                id = %s
            """
        cursor.execute(query, (top_id,inference_object_id))
    except Exception:
        raise Exception(f"Error: could not set top_inference_id {top_id} for inference {inference_object_id}")
    
def get_inference_object_top_id(cursor, inference_object_id: str):
    """
    This function gets the top_id of an inference.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inference_id (str): The UUID of the inference.

    Returns:
    - The UUID of the top.
    """
    try:
        query = """
            SELECT 
                top_inference_id
            FROM 
                object
            WHERE 
                id = %s
            """
        cursor.execute(query, (inference_object_id,))
        res = cursor.fetchone()[0]
        return res
    except Exception:
        raise Exception(f"Error: could not get top_inference_id for inference {inference_object_id}")
def new_seed_object(cursor, seed_id: str, object_id:str,score:float):
    """
    This function uploads a new seed object (seed prediction) to the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - seed_id (str): The UUID of the seed.
    - object_id (str): The UUID of the object.
    - score (float): The score of the prediction.

    Returns:
    - The UUID of the seed object.
    """
    try:
        query = """
            INSERT INTO 
                seed_obj(
                    seed_id,
                    object_id,
                    score
                    )
            VALUES
                (%s,%s,%s)
            RETURNING id    
            """
        cursor.execute(
            query,
            (
                seed_id,
                object_id,
                score,
            ),
        )
        return cursor.fetchone()[0]
    except Exception:
        raise SeedObjectCreationError("Error: seed object not uploaded")
def get_inference(cursor, inference_id: str):
    """
    This function gets an inference from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inference_id (str): The UUID of the inference.

    Returns:
    - The inference.
    """
    try:
        query = """
            SELECT 
                inference
            FROM 
                inference
            WHERE 
                id = %s
            """
        cursor.execute(query, (inference_id,))
        res = cursor.fetchone()[0]
        return res
    except Exception:
        raise InferenceNotFoundError(f"Error: could not get inference {inference_id}")


def set_inference_object_verified_id(cursor, inference_object_id: str, verified_id:str):
    """
    This function sets the verified_id of an object.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inference_object_id (str): The UUID of the object.
    - verified_id (str): The UUID of the verified.
    """
    try:
        query = """
            UPDATE 
                object
            SET
                verified_id = %s
            WHERE 
                id = %s
            """
        cursor.execute(query, (verified_id,inference_object_id))
    except Exception:
        raise Exception(f"Error: could not update verified_id for object {inference_object_id}")
    
def set_inference_object_valid(cursor, inference_object_id: str, is_valid:bool):
    """
    This function sets the is_valid of an object.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inference_object_id (str): The UUID of the object.
    - is_valid (bool): if the inference object is valid
    """
    try:
        query = """
            UPDATE 
                object
            SET
                valid = %s
            WHERE 
                id = %s
            """
        cursor.execute(query, (is_valid,inference_object_id))
    except Exception:
        raise Exception(f"Error: could not update valid for object {inference_object_id}")