"""
This module is responsible for handling the user data in the database 
and the user container in the blob storage.
"""
import datastore.db.queries.user as user
import datastore.db.queries.inference as inference
import datastore.db.queries.machine_learning as machine_learning
import datastore.db.metadata.machine_learning as ml_metadata
import datastore.db.metadata.inference as inference_metadata
import datastore.db.metadata.validator as validator
import datastore.db.queries.seed as seed
import datastore.blob as blob
import datastore.blob.azure_storage_api as azure_storage
import json
from azure.storage.blob import BlobServiceClient
import os

NACHET_BLOB_ACCOUNT = os.environ.get('NACHET_BLOB_ACCOUNT')
if NACHET_BLOB_ACCOUNT is None or NACHET_BLOB_ACCOUNT == "":
    raise ValueError('NACHET_BLOB_ACCOUNT is not set')

NACHET_BLOB_KEY = os.environ.get('NACHET_BLOB_KEY')
if NACHET_BLOB_KEY is None or NACHET_BLOB_KEY == "":
    raise ValueError('NACHET_BLOB_KEY is not set')

NACHET_STORAGE_URL = os.environ.get('NACHET_STORAGE_URL')
if NACHET_STORAGE_URL is None or NACHET_STORAGE_URL == "":
    raise ValueError('NACHET_STORAGE_URL is not set')

class UserAlreadyExistsError(Exception):
    pass
class ContainerCreationError(Exception):
    pass
class FolderCreationError(Exception):
    pass
class InferenceCreationError(Exception):
    pass

class User():
    def __init__(self, email: str ,id:str=None):
        self.id = id
        self.email = email
        
def get_User(email, cursor):
    """
    Get a user from the database

    Parameters:
    - email (str): The email of the user.
    - cursor: The cursor object to interact with the database.
    """
    user_id = user.get_user_id(email, cursor)
    return User(email, user_id)

async def new_user(email, cursor,connection_string):
    """
    Create a new user in the database and blob storage.

    Parameters:
    - email (str): The email of the user.
    - cursor: The cursor object to interact with the database.
    - connection_string: The connection string to connect with the Azure storage account
    """
    try:        
        # Register the user in the database
        if user.is_user_registered(email, cursor):
            raise UserAlreadyExistsError("User already exists")
        user_uuid = user.register_user(email, cursor)
        
        # Create the user container in the blob storage
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        container_client =blob_service_client.create_container(f"user-{user_uuid}")
        
        if not container_client.exists():
            raise ContainerCreationError("Error creating the user container")

        # Link the container to the user in the database
        user.link_container(cursor=cursor,user_id=user_uuid,container_url=container_client.url)
        
        # Basic user container structure
        response = await azure_storage.create_folder(container_client, "General")
        if not response:
            raise FolderCreationError("Error creating the user folder")
        return User(email, user_uuid)
        
    except Exception:
        raise Exception("Unhandled Error")
    
async def get_user_container_client(user_id,tier="user"):
    """
    Get the container client of a user

    Parameters:
    - user_id (int): The id of the user.

    Returns: ContainerClient object
    """
    sas = blob.get_account_sas(NACHET_BLOB_ACCOUNT,NACHET_BLOB_KEY)
    # Get the container client
    container_client = await azure_storage.mount_container(NACHET_STORAGE_URL,user_id,True,tier,sas)
    return container_client

async def register_inference_result(cursor,user_id:str,inference_dict,picture_id:str,pipeline_id:str,type:int=1):
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
        trimmed_inference = inference_metadata.build_inference_import(inference)
        inference_id=inference.new_inference(cursor,trimmed_inference,user_id,picture_id,type)
        nb_object = int(inference_dict["totalBoxes"])
        inference_dict["inference_id"]=str(inference_id)
        # loop through the boxes
        for box_index in range(nb_object):
            #TODO: adapt for multiple types of objects
            if type==1:
                top_id = seed.get_seed_id(cursor,inference_dict["boxes"][box_index]["label"])
                inference["boxes"][box_index]["object_type_id"]=1
            else:
                raise inference.InferenceCreationError("Error: type not recognized")
            box = inference_metadata.build_object_import(inference_dict["boxes"][box_index])
            object_inference_id = inference.new_inference_object(cursor,inference_id,box,type)
            inference_dict["boxes"][box_index]["box_id"]=str(object_inference_id)
            # loop through the topN Prediction
            top_score=-1
            for topN in inference_dict["boxes"][box_index]["topN"]:
                
                # Retrieve the right seed_id
                seed_id=seed.get_seed_id(cursor,topN["label"])
                id=inference.new_seed_object(cursor,seed_id,object_inference_id,topN["score"])
                topN["object_id"]=str(id)
                if topN["score"]>top_score:
                    top_score=topN["score"]
                    top_id=id
            inference.set_inference_object_top_id(cursor,object_inference_id,top_id)
            inference_dict["boxes"][box_index]["top_id"]=str(top_id)
        
        return inference_dict
    except ValueError:
        raise ValueError("The value of 'totalBoxes' is not an integer.")
    except Exception:
        raise Exception("Unhandled Error")

async def import_ml_structure_from_json_version(cursor,ml_version:dict):
    """
    TODO: build tests
    """
    pipelines = ml_version["pipelines"]
    models = ml_version["models"]
    # Create the models
    for model in models:
        model_db = ml_metadata.build_model_import(model)
        task_id = machine_learning.get_task_id(cursor,model["task"])
        model_name=model["model_name"]
        endpoint_name=model["endpoint_name"]
        machine_learning.new_model(cursor,model_db,model_name,endpoint_name,task_id)
    # Create the pipelines
    for pipeline in pipelines:
        pipeline_db = ml_metadata.build_pipeline_import(pipeline)
        pipeline_name=pipeline["pipeline_name"]
        model_ids=[]
        # Establish the relationship between the pipelines and its models
        for name_model in pipeline["models"]:
            model_id=0
            model_id = machine_learning.get_model_id_from_name(cursor,name_model)
            if validator.is_valid_uuid(model_id):
                model_ids.append(model_id)
            else:
                raise ValueError(f"Model {name_model} not found")
        machine_learning.new_pipeline(cursor,pipeline_db,pipeline_name,model_ids)
    
async def get_ml_structure(cursor):
    """
    This function retrieves the machine learning structure from the database.
    
    Returns a usable json object with the machine learning structure for the FE and BE
    """
    ml_structure = {"pipelines":[],"models":[]}
    pipelines = machine_learning.get_active_pipeline(cursor)
    model_list=[]
    for pipeline in pipelines:
        # (id, name, active:bool, is_default: bool, data, model_ids: array)
        pipeline_name = pipeline[1]
        pipeline_id = pipeline[0]
        default = pipeline[3]
        model_ids = pipeline[5]
        pipeline_dict=ml_metadata.build_pipeline_export(pipeline[4],pipeline_name,pipeline_id,default,model_ids)
        ml_structure["pipelines"].append(pipeline_dict)
        for model_id in model_ids:
            if model_id not in model_list:
                model_list.append(model_id)
            model_db = machine_learning.get_model(cursor,model_id)
            #(id, name, endpoint_name, task_name, data,version: str)
            model_name = model_db[1]
            model_endpoint = model_db[2]
            model_task = model_db[3]
            model_version = model_db[5]
            model_dict = ml_metadata.build_model_export(model_db[4],model_id,model_name,model_endpoint,model_task,model_version)
            ml_structure["models"].append(model_dict)
    return ml_structure

async def get_seed_info(cursor):
    """
    This function retrieves the seed information from the database.
    
    Returns a usable json object with the seed information for the FE and BE
    """
    seeds = seed.get_all_seeds(cursor)
    seed_dict = {"seeds":[]}
    for seed_db in seeds:
        seed_id = seed_db[0]
        seed_name = seed_db[1]
        seed_dict["seeds"].append({"seed_id":seed_id,"seed_name":seed_name})
    return seed_dict
