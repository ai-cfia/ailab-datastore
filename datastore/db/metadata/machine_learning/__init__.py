"""
This module contains all the functions and classes that are used to store and retrieve metadata for machine learning models.
"""
import json

def build_pipeline_import(pipeline:dict)->str:
    """
    This function builds the model metadata for the database.

    Parameters:
    - model (dict): The model object.

    Returns:
    - The model db object in a string format.
    """
    pipeline_db = {
        "models": pipeline["models"],
        "created_by": pipeline["created_by"],
        "creation_date": pipeline["creation_date"],
        "description": pipeline["description"],
        "job_name": pipeline["job_name"],
        "architecture_version": pipeline[""],
        "dataset": pipeline["dataset"],
        "metrics": pipeline["metrics"],
        "identifiable": pipeline["identifiable"]
    }
    return json.dumps(pipeline_db)

def build_pipeline_export(data:dict,name:str,id:str,default:bool,model_ids)->dict:
    """
    This function builds the model metadata for the database.

    Parameters:
    - model (dict): The model object.

    Returns:
    - The model db object in a string format.
    """
    pipeline_db = {
        "models": model_ids,
        "pipeline_id": str(id),
        "pipeline_name": name,
        "default": default,
    }
    for key in data:
        pipeline_db[key] = data[key]
    return pipeline_db

def build_model_import(model:dict)->str:
    """
    This function builds the model metadata for the database.

    Parameters:
    - model (dict): The model object.

    Returns:
    - The model db object in a string format.
    """
    model_db = {
        "api_call_function":model["api_call_function"],
        "endpoint":model["endpoint"],
        "api_key": model["api_key"],
        "inference_function": model["inference_function"],
        "content_type": model["content_type"],
        "deployment_platform": model["deployment_platform"],
        "created_by": model["created_by"],
        "creation_date":model["creation_date"],
        "description": model["description"],
        "job_name": model["job_name"],
        "dataset": model["dataset"],
        "metrics": model["metrics"],
        "identifiable": model["identifiable"]
    }
    return json.dumps(model_db)

def build_model_export(data:dict,id,name:str,endpoint:str,task_name:str,version:str)->dict:
    """
    This function builds the model metadata for the database.

    Parameters:
    - model (dict): The model object.

    Returns:
    - The model db object in a string format.
    """
    model_db = {
        "model_id": str(id),
        "model_name": name,
        "endpoint_name": endpoint,
        "task": task_name,
        "version": version
    }
    for key in data:
        model_db[key] = data[key]
    return model_db