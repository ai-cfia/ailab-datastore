"""
This module is responsible for handling the user data in the database 
and the user container in the blob storage.
"""

import datastore.db.queries.user as user
import datastore.db.queries.inference as inference
import datastore.db.queries.machine_learning as machine_learning
import datastore.db.queries.picture as picture
import datastore.db.metadata.machine_learning as ml_metadata
import datastore.db.metadata.inference as inference_metadata
import datastore.db.metadata.validator as validator
import datastore.db.queries.seed as seed
import datastore.db.metadata.picture_set as data_picture_set
import datastore.blob as blob
import datastore.blob.azure_storage_api as azure_storage
import json
from azure.storage.blob import BlobServiceClient,ContainerClient
import os

NACHET_BLOB_ACCOUNT = os.environ.get("NACHET_BLOB_ACCOUNT")
if NACHET_BLOB_ACCOUNT is None or NACHET_BLOB_ACCOUNT == "":
    raise ValueError("NACHET_BLOB_ACCOUNT is not set")

NACHET_BLOB_KEY = os.environ.get("NACHET_BLOB_KEY")
if NACHET_BLOB_KEY is None or NACHET_BLOB_KEY == "":
    raise ValueError("NACHET_BLOB_KEY is not set")

NACHET_STORAGE_URL = os.environ.get("NACHET_STORAGE_URL")
if NACHET_STORAGE_URL is None or NACHET_STORAGE_URL == "":
    raise ValueError("NACHET_STORAGE_URL is not set")


class UserAlreadyExistsError(Exception):
    pass

class MLRetrievalError(Exception):
    pass

class BlobUploadError(Exception):
    pass

class ContainerCreationError(Exception):
    pass

class FolderCreationError(Exception):
    pass

class InferenceCreationError(Exception):
    pass

class InferenceFeedbackError(Exception):
    pass


class User:
    def __init__(self, email: str, id: str = None,tier:str='user'):
        self.id = id
        self.email = email
        self.tier = tier
    def get_email(self):
        return self.email
    def get_id(self):
        return self.id
    def get_container_client(self):
        return get_user_container_client(self.id,self.tier)


async def get_user(cursor, email)->User:
    """
    Get a user from the database

    Parameters:
    - email (str): The email of the user.
    - cursor: The cursor object to interact with the database.
    """
    user_id = user.get_user_id(cursor, email)
    return User(email, user_id)


async def new_user(cursor,email, connection_string,tier='user')->User:
    """
    Create a new user in the database and blob storage.

    Parameters:
    - email (str): The email of the user.
    - cursor: The cursor object to interact with the database.
    - connection_string: The connection string to connect with the Azure storage account
    """
    try:
        # Register the user in the database
        if user.is_user_registered(cursor, email):
            raise UserAlreadyExistsError("User already exists")
        user_uuid = user.register_user(cursor, email)

        # Create the user container in the blob storage
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        container_client = blob_service_client.create_container(f"{tier}-{user_uuid}")

        if not container_client.exists():
            raise ContainerCreationError("Error creating the user container")

        # Link the container to the user in the database
        pic_set_metadata = data_picture_set.build_picture_set(
            user_id=user_uuid, nb_picture=0
        )
        pic_set_id = picture.new_picture_set(cursor, pic_set_metadata, user_uuid)
        user.set_default_picture_set(cursor, user_uuid, pic_set_id)
        # Basic user container structure
        response = await azure_storage.create_folder(
            container_client, str(pic_set_id), "General"
        )
        if not response:
            raise FolderCreationError("Error creating the user folder")
        return User(email, user_uuid)
    except azure_storage.CreateDirectoryError:
        raise FolderCreationError("Error creating the user folder")
    except UserAlreadyExistsError:
        raise
    except ContainerCreationError:
        raise 
    except Exception as e:
        print(e)
        raise Exception("Datastore Unhandled Error")


async def get_user_container_client(user_id, tier="user"):
    """
    Get the container client of a user

    Parameters:
    - user_id (int): The id of the user.

    Returns: ContainerClient object
    """
    sas = blob.get_account_sas(NACHET_BLOB_ACCOUNT, NACHET_BLOB_KEY)
    # Get the container client
    container_client = await azure_storage.mount_container(
        NACHET_STORAGE_URL, user_id, True, tier,sas
    )
    if isinstance(container_client,ContainerClient):
        return container_client


async def upload_picture(cursor, user_id, picture_hash, container_client):
    """
    Upload a picture to the user container

    Parameters:
    - cursor: The cursor object to interact with the database.
    - user_id (str): The UUID of the user.
    - picture (str): The image to upload.
    - container_client: The container client of the user.
    """
    try:
        # Create picture instance in DB
        empty_picture = json.dumps([])
        picture_set_id = user.get_default_picture_set(cursor, user_id)
        picture_id = picture.new_picture_unknown(
            cursor=cursor,
            picture=empty_picture,
            picture_set_id=picture_set_id,
        )
        # Upload the picture to the Blob Storage
        response = await azure_storage.upload_image(
            container_client, "General", picture_hash, picture_id
        )
        if not response:
            raise BlobUploadError("Error uploading the picture")
        # Update the picture metadata in the DB
        data = {
            "link": "General/" + str(picture_id),
            "description": "Uploaded through the API",
        }
        picture.update_picture_metadata(cursor, picture_id, json.dumps(data),0)

        return picture_id
    except BlobUploadError or azure_storage.UploadImageError:
        raise BlobUploadError("Error uploading the picture")
    except Exception as e:
        print(e)
        raise Exception("Datastore Unhandled Error")

async def register_inference_result(
    cursor,
    user_id: str,
    inference_dict,
    picture_id: str,
    pipeline_id: str,
    type: int = 1,
):
    """
    Register an inference result in the database

    Parameters:
    - cursor: The cursor object to interact with the database.
    - user_id (str): The UUID of the user.
    - inference (str): The inference to register in a dict string (soon to be json loaded).
    - picture_id (str): The UUID of the picture.
    - pipeline_id (str): The UUID of the pipeline.
    """
    try:
        trimmed_inference = inference_metadata.build_inference_import(inference_dict)
        inference_id = inference.new_inference(
            cursor, trimmed_inference, user_id, picture_id, type
        )
        nb_object = int(inference_dict["totalBoxes"])
        inference_dict["inference_id"] = str(inference_id)
        # loop through the boxes
        for box_index in range(nb_object):
            # TODO: adapt for multiple types of objects
            if type == 1:
                top_id = seed.get_seed_id(
                    cursor, inference_dict["boxes"][box_index]["label"]
                )
                inference_dict["boxes"][box_index]["object_type_id"] = 1
            else:
                raise inference.InferenceCreationError("Error: type not recognized")
            box = inference_metadata.build_object_import(
                inference_dict["boxes"][box_index]
            )
            object_inference_id = inference.new_inference_object(
                cursor, inference_id, box, type
            )
            inference_dict["boxes"][box_index]["box_id"] = str(object_inference_id)
            # loop through the topN Prediction
            top_score = -1
            if "topN" in inference_dict["boxes"][box_index]:
                for topN in inference_dict["boxes"][box_index]["topN"]:

                    # Retrieve the right seed_id
                    seed_id = seed.get_seed_id(cursor, topN["label"])
                    id = inference.new_seed_object(
                        cursor, seed_id, object_inference_id, topN["score"]
                    )
                    topN["object_id"] = str(id)
                    if topN["score"] > top_score:
                        top_score = topN["score"]
                        top_id = id
            else:
                seed_id = seed.get_seed_id(cursor, inference_dict["boxes"][box_index]["label"])
                top_id = inference.new_seed_object(cursor, seed_id, object_inference_id, inference_dict["boxes"][box_index]["score"])
            inference.set_inference_object_top_id(cursor, object_inference_id, top_id)
            inference_dict["boxes"][box_index]["top_id"] = str(top_id)

        return inference_dict
    except ValueError:
        raise ValueError("The value of 'totalBoxes' is not an integer.")
    except Exception as e:
        print(e.__str__())
        raise Exception("Unhandled Error")

async def new_correction_inference_feedback(cursor,inference_dict, type: int = 1):
    """
    TODO: doc
    """
    try:
        if "inference_id" in inference_dict.keys():
            inference_id = inference_dict["inference_id"]
        else:
            raise InferenceFeedbackError("Error: inference_id not found in the given infence_dict")
        for object in inference_dict["boxes"]:
            box_id = object["box_id"]
            box_metadata = json.loads(build_object_import(object))

            # DB box metadata
            object_db = inference.get_inference_object(cursor, box_id)
            object_metadata = json.loads(object_db[2])

            # Check if there are difference between the metadata
            flag_box_metadata = false
            if (inference_metadata.compare_object_metadata(box_metadata, object_metadata)):
                # Update the object metadata
                flag_box_metadata = true
                inference.set_object_box_metadata(cursor, box_id, json.dumps(box_metadata))

            # Check for the correct seed
            seed_name = object["label"]
            flag_seed = false
            valid = false
            if seed_name == "":
                # box has been deleted
                valid = false
            else: 
                valid = true
                # Check if a new seed has been selected
                top_inference_id = inference.get_inference_object_top_id(cursor, object_id)
                new_top_id = inference.get_seed_object_from_feedback(cursor, seed_name, box_id )
                if top_inference_id != new_top_id:
                    # Seed was not correctly identified, set the verified_id to the right seed_object.id
                    flag_seed = true
                    inference.set_inference_object_verified_id(cursor, box_id, new_top_id)
                else:
                    # Seed was correctly identified, set the verified_id to the top_id
                    flag_seed = false
                    inference.set_inference_object_verified_id(cursor, box_id, top_inference_id)
            # Update the object validity
            inference.set_inference_object_valid(cursor, box_id, valid)
            
    except InferenceFeedbackError:
        raise
    except Exception as e:
        print(e.__str__())
        raise Exception("Datastore Unhandled Error")


async def new_perfect_inference_feeback(cursor, inference_id, user_id, boxes_id) :
    """
    Update objects when a perfect feedback is sent by a user and update the inference if all the objects in it are verified.
    
    Args:
        cursor: The cursor object to interact with the database.
        inference_id (str): id of the inference on which feedback is given
        user_id (str): id of the user giving a feedback
        boxes_id (str array): array of id of the objects that are correctly identified
    """
    try:
        # Check if user exists
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )
        # Check if boxes_id exists
        for box_id in boxes_id :
            if not inference.check_inference_object_exist(cursor, box_id):
                raise inference.InferenceObjectNotFoundError(
                    f"Error: could not get inference object for id {box_id}"
                )
        # Check if inference exists
        if not inference.check_inference_exist(cursor, inference_id):
            raise inference.InferenceNotFoundError(
                f"Inference not found based on the given id: {inference_id}"
            )
        
        if inference.is_inference_verified(cursor, inference_id):
            raise inference.InferenceAlreadyVerifiedError(
                f"Can't add feedback to a verified inference, id: {inference_id}"
            )
        
        for object_id in boxes_id:
            top_inference_id = inference.get_inference_object_top_id(cursor, object_id)
            inference.set_inference_object_verified_id(cursor, object_id, top_inference_id )
            inference.set_inference_object_valid(cursor, object_id, True)
            
        inference.verify_inference_status(cursor, inference_id, user_id)
        
    except (user.UserNotFoundError, inference.InferenceObjectNotFoundError, inference.InferenceNotFoundError, inference.InferenceAlreadyVerifiedError) as e:
        raise e
    except Exception as e:
        print(e)
        raise Exception(f"Datastore Unhandled Error : {e}")
    
async def import_ml_structure_from_json_version(cursor, ml_version: dict):
    """
    TODO: build tests
    """
    pipelines = ml_version["pipelines"]
    models = ml_version["models"]
    # Create the models
    for model in models:
        model_db = ml_metadata.build_model_import(model)
        task_id = machine_learning.get_task_id(cursor, model["task"])
        model_name = model["model_name"]
        endpoint_name = model["endpoint_name"]
        machine_learning.new_model(cursor, model_db, model_name, endpoint_name, task_id)
    # Create the pipelines
    for pipeline in pipelines:
        pipeline_db = ml_metadata.build_pipeline_import(pipeline)
        pipeline_name = pipeline["pipeline_name"]
        model_ids = []
        # Establish the relationship between the pipelines and its models
        for name_model in pipeline["models"]:
            model_id = 0
            model_id = machine_learning.get_model_id_from_name(cursor, name_model)
            if validator.is_valid_uuid(model_id):
                model_ids.append(model_id)
            else:
                raise ValueError(f"Model {name_model} not found")
        machine_learning.new_pipeline(cursor, pipeline_db, pipeline_name, model_ids)


async def get_ml_structure(cursor):
    """
    This function retrieves the machine learning structure from the database.

    Returns a usable json object with the machine learning structure for the FE and BE
    """
    try:
        ml_structure = {"pipelines": [], "models": []}
        pipelines = machine_learning.get_active_pipeline(cursor)
        if len(pipelines)==0:
            raise MLRetrievalError("No Active pipelines found in the database.")
        model_list = []
        for pipeline in pipelines:
            # (id, name, active:bool, is_default: bool, data, model_ids: array)
            pipeline_name = pipeline[1]
            pipeline_id = pipeline[0]
            default = pipeline[3]
            model_ids = pipeline[5]
            pipeline_dict = ml_metadata.build_pipeline_export(
                pipeline[4], pipeline_name, pipeline_id, default, model_ids
            )
            ml_structure["pipelines"].append(pipeline_dict)
            for model_id in model_ids:
                if model_id not in model_list:
                    model_list.append(model_id)
                model_db = machine_learning.get_model(cursor, model_id)
                # (id, name, endpoint_name, task_name, data,version: str)
                model_name = model_db[1]
                model_endpoint = model_db[2]
                model_task = model_db[3]
                model_version = model_db[5]
                model_dict = ml_metadata.build_model_export(
                    model_db[4],
                    model_id,
                    model_name,
                    model_endpoint,
                    model_task,
                    model_version,
                )
                ml_structure["models"].append(model_dict)
        return ml_structure
    except MLRetrievalError:
        raise
    except Exception as e:
        print(e)
        raise Exception("Datastore Unhandled Error")


async def get_seed_info(cursor):
    """
    This function retrieves the seed information from the database.

    Returns a usable json object with the seed information for the FE and BE
    """
    seeds = seed.get_all_seeds(cursor)
    seed_dict = {"seeds": []}
    for seed_db in seeds:
        seed_id = seed_db[0]
        seed_name = seed_db[1]
        seed_dict["seeds"].append({"seed_id": seed_id, "seed_name": seed_name})
    return seed_dict
