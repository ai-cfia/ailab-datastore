"""
This module contains the function to generate the metadata necessary to interact with the database and the other layers of Nachet for all the inference related objects. 
The metadata is generated in a json format and is used to store the metadata in the database.

"""


import json

def build_inference_import(model_inference:dict)->str:
    """
    This funtion build an inference json object from the model inference.
    This serves as the metadata for the inference object in the database.
    
    Parameters:
    - model_inference: (dict) The model inference object.
    
    Returns:
    - The inference db object in a string format.
    """
    
    inference = {
        "filename": model_inference.filename,
        "overlapping": model_inference.overlapping,
        "overlappingIndices": model_inference.overlappingIndices,
        "totalBoxes": model_inference.totalBoxes,
    }
    return json.dumps(inference)

def build_object_import(object:dict)->str:
    """
    This function build the object from the model inference object.
    This serves as the metadata for the object in the database.
    
    Parameters:
    - object: (dict) The object from the model inference object.
    
    Returns:
    - The object db object in a string format.
    """
    data={
        "box":object.box,
        "color":object.color,
    }
    return json.dumps(data)