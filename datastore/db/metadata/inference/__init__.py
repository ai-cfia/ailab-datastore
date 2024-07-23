"""
This module contains the function to generate the metadata necessary to interact with the database and the other layers of Nachet for all the inference related objects. 
The metadata is generated in a json format and is used to store the metadata in the database.

"""

import json
import datastore.db.queries.seed as seed
import datastore.db.queries.inference as inference

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

def compare_object_metadata(object1:dict , object2:dict) -> bool:
    """
    This function compares two object metadata to check if they are the same.

    Parameters:
    - object1: (dict) The first object to compare.
    - object2: (dict) The second object to compare.

    Returns:
    - True if the objects are the same, False otherwise.
    """
    keys = ["topX", "topY", "bottomX", "bottomY"]
    for key in keys:
        if object1[key] != object2[key]:
            return False
    return True

def rebuild_inference(cursor, inf) :
    """
    This function rebuilds the inference object from the database.

    Parameters:
    - inference: The inference from the database to convert into inference result.

    Returns:
    - The inference object as a dict.
    """
    inference_id = str(inf[0])
    inference_data = json.loads(json.dumps(inf[1]))
    
    objects = inference.get_objects_by_inference(cursor, inference_id)
    boxes = rebuild_boxes_export(cursor, objects)
    
    inf = {
        "boxes": boxes,
        "filename": inference_data.get("filename"),
        "inference_id": inference_id,
        "labelOccurrence" : inference_data.get("labelOccurrence"),
        "totalBoxes" : inference_data.get("totalBoxes"),
    }
    return inf


def rebuild_boxes_export(cursor, objects) :
    """
    This function rebuilds the boxes object from the database.

    Parameters:
    - objects: The objects of an inference from the database to convert into boxes.

    Returns:
    - The boxes object as an array of dict.
    """
    boxes = []
    for object in objects:
        box_id = str(object[0])
        
        box_metadata = object[1]
        box_metadata = json.loads(json.dumps(box_metadata))
        
        box = box_metadata.get("box")
        color = box_metadata.get("color")
        overlapping = box_metadata.get("overlapping")
        overlappingIndices = box_metadata.get("overlappingIndices")
        
        top_id = str(inference.get_inference_object_top_id(cursor, box_id))
        top_seed_id = str(seed.get_seed_object_seed_id(cursor, top_id))
        
        seed_objects = inference.get_seed_object_by_object_id(cursor, box_id)
        topN = rebuild_topN_export(cursor, seed_objects)
        
        top_score = 0
        if inference.is_object_verified(cursor, box_id):
            top_score = 1
        else :
            for seed_object in seed_objects:
                score = seed_object[2]
                seed_id = str(seed_object[1])
                if seed_id == top_seed_id:
                    top_score = score
        top_label = seed.get_seed_name(cursor, top_seed_id)

        object = {"box" : box, 
                    "box_id": box_id, 
                    "color" : color, 
                    "label" : top_label, 
                    "object_type_id" : 1, 
                    "overlapping" : overlapping, 
                    "overlappingIndices" : overlappingIndices, 
                    "score" : top_score, 
                    "topN": topN, 
                    "top_id" : top_id}

        boxes.append(object)
    return boxes


def rebuild_topN_export(cursor, seed_objects) :
    """
    This function rebuilds the topN object from the database.

    Parameters:
    - seed_objects: The seed_objects from the database to convert into topN.

    Returns:
    - The topN object as an array of dict.
    """
    topN = []
    for seed_obj in seed_objects :
        seed_obj = {
            "label": seed.get_seed_name(cursor, str(seed_obj[1])), 
            "object_id": str(seed_obj[0]), 
            "score": seed_obj[2]}
        topN.append(seed_obj)
    return topN
