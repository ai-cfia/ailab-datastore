"""
This module contains the function to generate the metadata necessary to interact with the database and the other layers of Nachet for all the inference related objects. 
The metadata is generated in a json format and is used to store the metadata in the database.

"""

import json


class MissingKeyError(Exception):
    pass


def build_inference_import(model_inference: dict) -> str:
    """
    This funtion build an inference json object from the model inference.
    This serves as the metadata for the inference object in the database.

    Parameters:
    - model_inference: (dict) The model inference object.

    Returns:
    - The inference db object in a string format.
    """
    try:
        if "filename" not in model_inference:
            raise MissingKeyError("filename")
        if "labelOccurrence" not in model_inference:
            raise MissingKeyError("labelOccurrence")
        if "totalBoxes" not in model_inference:
            raise MissingKeyError("totalBoxes")
        inference = {
            "filename": model_inference["filename"],
            "labelOccurrence": model_inference["labelOccurrence"],
            "totalBoxes": model_inference["totalBoxes"],
        }
        return json.dumps(inference)
    except MissingKeyError as e:
        raise MissingKeyError(f"Missing key: {e}")


def build_object_import(object: dict) -> str:
    """
    This function build the object from the model inference object.
    This serves as the metadata for the object in the database.

    Parameters:
    - object: (dict) The object from the model inference object.

    Returns:
    - The object db object in a string format.
    """
    data = {
        "box": object["box"],
        "color": object["color"],
        "overlapping": object["overlapping"],
        "overlappingIndices": object["overlappingIndices"],
    }
    return json.dumps(data)
