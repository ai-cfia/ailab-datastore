"""
This module is responsible for handling the user data in the database 
and the user container in the blob storage.
"""

import datastore.db.queries.user as user
import datastore.db.queries.inference as inference
import datastore.db.queries.machine_learning as machine_learning
import datastore.db.queries.picture as picture
import datastore.db.queries.analysis as analysis
import datastore.db.metadata.machine_learning as ml_metadata
import datastore.db.metadata.inference as inference_metadata
import datastore.db.metadata.validator as validator
import datastore.db.queries.seed as seed
import datastore.db.metadata.picture_set as data_picture_set
import datastore.blob as blob
import datastore.blob.azure_storage_api as azure_storage
import uuid
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

FERTISCAN_STORAGE_URL =  os.environ.get("FERTISCAN_STORAGE_URL")
if FERTISCAN_STORAGE_URL is None or FERTISCAN_STORAGE_URL == "":
    raise ValueError("FERTISCAN_STORAGE_URL is not set")


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
        pic_set_id = picture.new_picture_set(cursor, pic_set_metadata, user_uuid,  "General")
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


async def get_user_container_client(user_id, tier="user",storage_url = NACHET_STORAGE_URL):
    """
    Get the container client of a user

    Parameters:
    - user_id (int): The id of the user.

    Returns: ContainerClient object
    """
    sas = blob.get_account_sas(NACHET_BLOB_ACCOUNT, NACHET_BLOB_KEY)
    # Get the container client
    container_client = await azure_storage.mount_container(
        storage_url, user_id, True, tier,sas
    )
    if isinstance(container_client,ContainerClient):
        return container_client

async def create_picture_set(cursor, container_client, nb_pictures:int, user_id: str, folder_name = None):
    """
    Create a picture_set in the database and a related folder in the blob storage

    Args:
        cursor: The cursor object to interact with the database.
        container_client: The container client of the user.
        nb_pictures (int): number of picture that the picture set should be related to
        user_id (str): id of the user creating this picture set
        folder_name : name of the folder/picture set

    Returns:
        _type_: _description_
    """
    try:

        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )

        picture_set = data_picture_set.build_picture_set(user_id, nb_pictures)
        picture_set_id = picture.new_picture_set(
            cursor=cursor, picture_set=picture_set, user_id=user_id, folder_name=folder_name
        )

        folder_created = await azure_storage.create_folder(container_client, str(picture_set_id), folder_name)
        if not folder_created:
            raise FolderCreationError(f"Error while creating this folder : {picture_set_id}")
        
        return picture_set_id
    except (user.UserNotFoundError, FolderCreationError, data_picture_set.PictureSetCreationError, picture.PictureSetCreationError, azure_storage.CreateDirectoryError) as e:
        raise e
    except Exception:
        raise BlobUploadError("An error occured during the upload of the picture set")


async def upload_picture_unknown(cursor, user_id, picture_hash, container_client, picture_set_id=None):
    """
    Upload a picture that we don't know the seed to the user container

    Parameters:
    - cursor: The cursor object to interact with the database.
    - user_id (str): The UUID of the user.
    - picture (str): The image to upload.
    - container_client: The container client of the user.
    """
    try:
        
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )
        
        empty_picture = json.dumps([])
        # Create picture instance in DB
        if picture_set_id is None :
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
        # Update the picture metadata in the DB
        data = {
            "link": "General/" + str(picture_id),
            "description": "Uploaded through the API",
        }
        
        if not response:
            raise BlobUploadError("Error uploading the picture")
        
        picture.update_picture_metadata(cursor, picture_id, json.dumps(data),0)

        return picture_id
    except BlobUploadError or azure_storage.UploadImageError:
        raise BlobUploadError("Error uploading the picture")
    except Exception as e:
        print(e)
        raise Exception("Datastore Unhandled Error")

async def upload_picture_known(cursor, user_id, picture_hash, container_client, seed_id, picture_set_id=None, nb_seeds=None, zoom_level=None):
    """
    Upload a picture that the seed is known to the user container

    Parameters:
    - cursor: The cursor object to interact with the database.
    - user_id (str): The UUID of the user.
    - picture (str): The image to upload.
    - container_client: The container client of the user.
    - seed_id: The UUID of the seed on the image.
    - picture_set_id: The UUID of the picture set where to add the picture.
    - nb_seeds: The number of seeds on the picture.
    - zoom_level: The zoom level of the picture.
    """
    try:
        
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )
        
        empty_picture = json.dumps([])
        # Create picture instance in DB
        if picture_set_id is None :
            picture_set_id = user.get_default_picture_set(cursor, user_id)
        picture_id = picture.new_picture(
            cursor=cursor,
            picture=empty_picture,
            picture_set_id=picture_set_id,
            seed_id=seed_id,
        )
        # Upload the picture to the Blob Storage
        folder_name = picture.get_picture_set_name(cursor, picture_set_id)
        if folder_name is None:
            folder_name = picture_set_id
        
        response = await azure_storage.upload_image(
            container_client, folder_name, picture_hash, picture_id
        )
        picture_link = container_client.url + "/" + str(folder_name) + "/" + str(picture_id)
        # Create picture metadata and update DB instance (with link to Azure blob)
        """
        data = picture_metadata.build_picture(
            pic_encoded=picture_hash,
            link=picture_link,
            nb_seeds=nb_seeds,
            zoom=zoom_level,
            description="upload_picture_set script",
        )
        """
        data = {
            "link": picture_link,
            "nb_seeds":nb_seeds,
            "zoom":zoom_level,
            "description": "Uploaded through the API",
        }
        if not response:
            raise BlobUploadError("Error uploading the picture")
        
        picture.update_picture_metadata(cursor, picture_id, json.dumps(data),0)

        return picture_id
    except BlobUploadError or azure_storage.UploadImageError:
        raise BlobUploadError("Error uploading the picture")
    except (user.UserNotFoundError) as e:
        raise e
    except Exception as e:
        print(e)
        raise Exception("Datastore Unhandled Error")

async def upload_pictures(cursor, user_id, picture_set_id, container_client, pictures, seed_name: str, zoom_level: float = None, nb_seeds: int = None) :
    """
    Upload an array of pictures that the seed is known to the user container

    Parameters:
    - cursor: The cursor object to interact with the database.
    - user_id (str): The UUID of the user.
    - picture (str): The image to upload.
    - container_client: The container client of the user.
    - pictures array: array of images to upload
    - seed_name: The name of the seed on the images.
    - picture_set_id: The UUID of the picture set where to add the pictures.
    - nb_seeds: The number of seeds on the picture.
    - zoom_level: The zoom level of the picture.

    Returns:
        array of the new pictures UUID
    """
    try:
        
        if not seed.is_seed_registered(cursor=cursor, seed_name=seed_name):
            raise seed.SeedNotFoundError(
                f"Seed not found based on the given name: {seed_name}"
            )
        seed_id = seed.get_seed_id(cursor=cursor, seed_name=seed_name)
        
        pictures_id = []
        for picture_encoded in pictures:
            id = await upload_picture_known(cursor, user_id, picture_encoded, container_client, seed_id, picture_set_id, nb_seeds, zoom_level)
            pictures_id.append(id)

        return pictures_id
    except (seed.SeedNotFoundError) as e:
        raise e
    except user.UserNotFoundError as e:
        raise e
    except Exception:
        raise BlobUploadError("An error occured during the upload of the pictures")
    

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
    
    Returns:
    - The inference_dict with the inference_id, box_id and top_id added.
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
                # TODO : adapt for the seed_id in the inference_dict
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
                cursor, inference_id, box, type, False
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
        if "inferenceId" in inference_dict.keys():
            inference_id = inference_dict["inferenceId"]
        else:
            raise InferenceFeedbackError("Error: inference_id not found in the given infence_dict")
        if "userId" in inference_dict.keys():
            user_id = inference_dict["userId"]
            if not (user.is_a_user_id(cursor, user_id)):
                raise InferenceFeedbackError(f"Error: user_id {user_id} not found in the database")
        else:
            raise InferenceFeedbackError("Error: user_id not found in the given infence_dict")
        # if infence_dict["totalBoxes"] != len(inference_dict["boxes"] & infence_dict["totalBoxes"] > 0 ):
        #     if len(inference_dict["boxes"]) == 0:
        #         raise InferenceFeedbackError("Error: No boxes found in the given inference_dict")
        #     else if len(inference_dict["boxes"]) > infence_dict["totalBoxes"]:
        #         raise InferenceFeedbackError("Error: There are more boxes than the totalBoxes")
        #     else if len(inference_dict["boxes"]) < infence_dict["totalBoxes"]:
        #         raise InferenceFeedbackError("Error: There are less boxes than the totalBoxes")
        if inference.is_inference_verified(cursor, inference_id):
            raise InferenceFeedbackError(f"Error: Inference {inference_id} is already verified")
        for object in inference_dict["boxes"]:
            box_id = object["boxId"]
            seed_name = object["label"]
            seed_id = object["classId"]
            # flag_seed = False
            # flag_box_metadata = False
            valid = False
            box_metadata = object["box"]
            
            if box_id =="":
                # This is a new box created by the user
                
                # Check if the seed is known
                if seed_id == "" and seed_name == "":
                    raise InferenceFeedbackError("Error: seed_name and seed_id not found in the new box. We don't know what to do with it and this should not happen.")
                if seed_id == "":
                    if seed.is_seed_registered(cursor, seed_name):
                        # Mistake from the FE, the seed is known in the database
                        seed_id = seed.get_seed_id(cursor, seed_name)
                    else:
                        #unknown seed
                        seed_id = seed.new_seed(cursor, seed_name)
                # Create the new object
                object_id = inference.new_inference_object(cursor, inference_id, box_metadata, 1,True)
                seed_object_id = inference.new_seed_object(cursor, seed_id, object_id, 0)
                # Set the verified_id to the seed_object_id
                inference.set_inference_object_verified_id(cursor, object_id, seed_object_id)
                valid = True
            else: 
                if (inference.is_object_verified(cursor, box_id)):
                    raise InferenceFeedbackError(f"Error: Object {box_id} is already verified")
                # This is a box that was created by the pipeline so it should be within the database
                object_db = inference.get_inference_object(cursor, box_id)
                object_metadata = object_db[1]
                object_id = object_db[0]

                # Check if there are difference between the metadata
                if not (inference_metadata.compare_object_metadata(box_metadata, object_metadata["box"])):
                    # Update the object metadata
                    # flag_box_metadata = True
                    inference.set_object_box_metadata(cursor, box_id, json.dumps(box_metadata))
                
                # Check if the seed is known
                if seed_id == "":
                    if seed_name == "": 
                        # box has been deleted by the user
                        valid = False
                    else:
                        valid = True
                        if(seed.is_seed_registered(cursor, seed_name)):
                            # The seed is known in the database and it was a mistake from the FE
                            seed_id = seed.get_seed_id(cursor, seed_name)
                        else: # The seed is not known in the database
                            seed_id = seed.new_seed(cursor, seed_name)
                            seed_object_id = inference.new_seed_object(cursor, seed_id, object_id, 0)
                            inference.set_inference_object_verified_id(cursor, object_id, seed_object_id)
                else: 
                    #Box is still valid
                    valid = True
                    # Check if a new seed has been selected
                    top_inference_id = inference.get_inference_object_top_id(cursor, object_db[0])
                    new_top_id = inference.get_seed_object_id(cursor, seed_id, box_id )
                    
                    if new_top_id is None:
                        # Seed selected was not an inference guess, we need to create a new seed_object
                        new_top_id=inference.new_seed_object(cursor, seed_id, box_id, 0)
                        inference.set_inference_object_verified_id(cursor, box_id, new_top_id)
                        # flag_seed = True
                    if top_inference_id != new_top_id:
                        # Seed was not correctly identified, set the verified_id to the correct seed_object.id
                        # flag_seed = True
                        inference.set_inference_object_verified_id(cursor, box_id, new_top_id)
                    else:
                        # Seed was correctly identified, set the verified_id to the top_id
                        # flag_seed = False
                        inference.set_inference_object_verified_id(cursor, box_id, top_inference_id)
            
            # Update the object validity
            inference.set_inference_object_valid(cursor, box_id, valid)
        inference.verify_inference_status(cursor, inference_id, user_id)
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

async def get_picture_sets_info(cursor, user_id: str):
    """This function retrieves the picture sets names and number of pictures from the database.

    Args:
        user_id (str): id of the user
    """
    # Check if user exists
    if not user.is_a_user_id(cursor=cursor, user_id=user_id):
        raise user.UserNotFoundError(
            f"User not found based on the given id: {user_id}"
        )
    
    result = {}
    picture_sets = picture.get_user_picture_sets(cursor, user_id)
    for picture_set in picture_sets:
        picture_set_id = picture_set[0]
        nb_picture = picture.count_pictures(cursor, picture_set_id)
        result[picture_set[1]] = nb_picture
    return result
    
    
async def register_analysis(cursor,container_client, analysis_dict,picture_id :str,picture,folder = "General"):
    """
    Register an analysis in the database

    Parameters:
    - cursor: The cursor object to interact with the database.
    - container_client: The container client of the user.
    - analysis_dict (dict): The analysis to register in a dict string (soon to be json loaded).
    - picture: The picture encoded to upload.

    Returns:
    - The analysis_dict with the analysis_id added.
    """
    try:
        if picture_id is None or picture_id == "":
            picture_id = str(uuid.uuid4())
        # if not azure_storage.is_a_folder(container_client, folder):
        #     azure_storage.create_folder(container_client, folder)
        # azure_storage.upload_image(container_client, folder, picture, picture_id)
        analysis_id = analysis.new_analysis(cursor, json.dumps(analysis_dict))
        analysis_dict["analysis_id"] = str(analysis_id)
        return analysis_dict
    except Exception as e:
        print(e.__str__())
        raise Exception("Datastore Unhandled Error")
