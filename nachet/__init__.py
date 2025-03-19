from enum import Enum
import json
import os
from uuid import UUID

from dotenv import load_dotenv

import datastore.blob.azure_storage_api as azure_storage
import nachet.db.metadata.inference as inference_metadata
import nachet.db.metadata.machine_learning as ml_metadata
import datastore.db.metadata.picture_set as data_picture_set
import datastore.db.metadata.validator as validator
import nachet.db.queries.inference as inference
import nachet.db.queries.machine_learning as machine_learning
from datastore.db.queries import picture, container
import nachet.db.queries.seed as seed
import datastore.db.queries.user as user
from datastore import (
    ContainerController,
    BlobUploadError,
    FolderCreationError,
    UserNotOwnerError,
    ContainerCreationError,
    verify_user_can_write,
    get_user,
    get_container_controller,
)

load_dotenv()

NACHET_BLOB_ACCOUNT = os.environ.get("NACHET_BLOB_ACCOUNT")
if NACHET_BLOB_ACCOUNT is None or NACHET_BLOB_ACCOUNT == "":
    raise ValueError("NACHET_BLOB_ACCOUNT is not set")

NACHET_BLOB_KEY = os.environ.get("NACHET_BLOB_KEY")
if NACHET_BLOB_KEY is None or NACHET_BLOB_KEY == "":
    raise ValueError("NACHET_BLOB_KEY is not set")

NACHET_STORAGE_URL = os.environ.get("NACHET_STORAGE_URL")
if NACHET_STORAGE_URL is None or NACHET_STORAGE_URL == "":
    raise ValueError("NACHET_STORAGE_URL is not set")
DEV_USER_EMAIL = os.environ.get("DEV_USER_EMAIL")
if DEV_USER_EMAIL is None or DEV_USER_EMAIL == "":
    # raise ValueError("DEV_USER_EMAIL is not set")
    print("Warning: DEV_USER_EMAIL not set")

NACHET_DB_URL = os.environ.get("NACHET_DB_URL")
if NACHET_DB_URL is None or NACHET_DB_URL == "":
    raise ValueError("NACHET_DB_URL is not set")

NACHET_SCHEMA = os.environ.get("NACHET_SCHEMA")
if NACHET_SCHEMA is None or NACHET_SCHEMA == "":
    raise ValueError("NACHET_SCHEMA is not set")


class InferenceCreationError(Exception):
    pass


class InferenceFeedbackError(Exception):
    pass


class MLRetrievalError(Exception):
    pass


class ObjectType(Enum):
    SEED: int = 1


async def upload_pictures_known(
    cursor,
    user_id: UUID,
    picture_set_id: UUID,
    container_controller: ContainerController,
    pictures,
    seed_name: str = None,
    seed_id: UUID = None,
    zoom_level: float = None,
    nb_seeds: int = 0,
):
    """
    Upload an array of pictures that the seed is known to the user container

    Parameters:
    - cursor: The cursor object to interact with the database.
    - user_id (str): The UUID of the user.
    - picture (str): The image to upload.
    - container_client: The container client of the user.
    - pictures array: array of images to upload
    - seed_name: The name of the seed on the images.
    - seed_id: The id of the seed on the images.
    - picture_set_id: The UUID of the picture set where to add the pictures.
    - nb_seeds: The number of seeds on the picture.
    - zoom_level: The zoom level of the picture.

    Returns:
        array of the new pictures UUID
    """
    try:
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )
        if nb_seeds is None:
            raise ValueError(
                "Missing argument 'nb_seeds' was expected to have a integer value but received None"
            )
        if not seed_id and not seed_name:
            raise seed.SeedNotFoundError(
                "Error: seed_name and seed_id not found in the new box. We don't know what to do with it and this should not happen."
            )
        if not seed_id and seed_name:
            if seed.is_seed_registered(cursor=cursor, seed_name=seed_name):
                # mistake from the front end, this seed is known in the db
                seed_id = str(seed.get_seed_id(cursor=cursor, seed_name=seed_name))
            else:
                # create the seed
                seed_id = str(seed.new_seed(cursor=cursor, seed_name=seed_name))

        pictures_id = await container_controller.upload_pictures(
            cursor=cursor,
            user_id=user_id,
            hashed_pictures=pictures,
            folder_id=picture_set_id,
            nb_objects=nb_seeds,
        )

        for picture_id in pictures_id:
            picture.new_picture_seed(
                cursor=cursor, picture_id=picture_id, seed_id=seed_id
            )

        return pictures_id
    except seed.SeedNotFoundError as e:
        raise e
    except user.UserNotFoundError as e:
        raise e
    except Exception:
        raise BlobUploadError("An error occured during the upload of the pictures")


async def register_inference_result(
    cursor,
    user_id: UUID,
    inference_dict: dict,
    picture_id: UUID,
    pipeline_id: UUID = None,
    type: int = ObjectType.SEED.value,
) -> dict:
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

        if pipeline_id is None:
            model_name = inference_dict["models"][0]["name"]
            pipeline_id = machine_learning.get_pipeline_id_from_model_name(
                cursor, model_name
            )
        inference_dict["pipeline_id"] = str(pipeline_id)

        inference_id = inference.new_inference(
            cursor, trimmed_inference, user_id, picture_id, type, pipeline_id
        )
        nb_object = int(inference_dict["totalBoxes"])
        inference_dict["totalBoxes"] = int(nb_object)
        inference_dict["inference_id"] = inference_id

        # loop through the boxes
        for box_index in range(nb_object):
            # TODO: adapt for multiple types of objects
            if type == ObjectType.SEED.value:
                # TODO : adapt for the seed_id in the inference_dict
                top_id = seed.get_seed_id(
                    cursor, inference_dict["boxes"][box_index]["label"]
                )
                inference_dict["boxes"][box_index]["object_type_id"] = 1
            else:
                raise inference.InferenceCreationError("Error: type not recognized")
            # Formatting the box
            box = inference_metadata.build_object_import(
                inference_dict["boxes"][box_index]
            )
            inference_dict["boxes"][box_index]["is_verified"] = False

            object_inference_id = inference.new_inference_object(
                cursor, inference_id, box, type, manual_detection=False
            )
            inference_dict["boxes"][box_index]["box_id"] = object_inference_id
            # loop through the topN Prediction
            top_score = -1
            if "topN" in inference_dict["boxes"][box_index]:
                for topN in inference_dict["boxes"][box_index]["topN"]:

                    # Retrieve the right seed_id
                    seed_id = seed.get_seed_id(cursor=cursor, seed_name=topN["label"])
                    id = inference.new_seed_object(
                        cursor, seed_id, object_inference_id, topN["score"]
                    )
                    topN["object_id"] = id
                    if topN["score"] > top_score:
                        top_score = topN["score"]
                        top_id = id
            else:
                seed_id = seed.get_seed_id(
                    cursor, inference_dict["boxes"][box_index]["label"]
                )
                top_id = inference.new_seed_object(
                    cursor,
                    seed_id,
                    object_inference_id,
                    inference_dict["boxes"][box_index]["score"],
                )
            inference.set_inference_object_top_id(cursor, object_inference_id, top_id)
            inference_dict["boxes"][box_index]["top_id"] = top_id
        return inference_metadata.Inference.model_validate(inference_dict).model_dump()
    except ValueError as e:
        raise ValueError(
            f"The value of 'totalBoxes' {inference_dict["totalBoxes"]} is not an integer.\n"
            + e.__str__()
        )


async def new_correction_inference_feedback(
    cursor, inference_dict: dict, type: int = ObjectType.SEED.value
):
    """
    This function is for saving a user correction on an Inference.

    Parameters:
    - cursor: Database cursor for executing SQL queries.
    - inference_dict: Dictionary containing inference data, including:
        - inferenceId: ID of the inference.
        - userId: ID of the user providing the feedback.
        - boxes: List of boxes with metadata and seed information.
    - type: Integer indicating the type of object (default is 1 for the seeds).
    """
    try:
        # FE uses different namming scheme
        inference_id = inference_dict.get("inference_id") or inference_dict.get(
            "inferenceId"
        )
        if not inference_id:
            raise InferenceFeedbackError(
                "Error: neither 'inferenceId' nor 'inference_id' found in the given inference_dict"
            )
        # FE uses different namming scheme
        user_id = inference_dict.get("user_id") or inference_dict.get("userId")
        if not user_id:
            raise InferenceFeedbackError(
                "Error: neither 'user_id' nor 'userId' found in the given inference_dict"
            )
        if not (user.is_a_user_id(cursor, user_id)):
            raise InferenceFeedbackError(
                f"Error: The user ID: {user_id} not found in the database"
            )
        # Removing this in case of creating Boxes or deleting boxes; The FE doesnt need to manage the TotalBoxes value
        # if infence_dict["totalBoxes"] != len(inference_dict["boxes"] & infence_dict["totalBoxes"] > 0 ):
        #     if len(inference_dict["boxes"]) == 0:
        #         raise InferenceFeedbackError("Error: No boxes found in the given inference_dict")
        #     else if len(inference_dict["boxes"]) > infence_dict["totalBoxes"]:
        #         raise InferenceFeedbackError("Error: There are more boxes than the totalBoxes")
        #     else if len(inference_dict["boxes"]) < infence_dict["totalBoxes"]:
        #         raise InferenceFeedbackError("Error: There are less boxes than the totalBoxes")

        # Uppon User request, they want to be able to edit in case of mistake
        # if inference.is_inference_verified(cursor, inference_id):
        #     raise InferenceFeedbackError(
        #         f"Error: Inference {inference_id} is already verified"
        #     )
        for object in inference_dict["boxes"]:
            box_id = object["boxId"]
            seed_name = object["label"]
            seed_id = object["classId"]
            # flag_seed = False
            # flag_box_metadata = False
            valid = False
            box_metadata = object["box"]

            if box_id == "":
                # This is a new box created by the user

                # Check if the seed is known
                if seed_id == "" and seed_name == "":
                    raise InferenceFeedbackError(
                        "Error: seed_name and seed_id not found in the new box. We don't know what to do with it and this should not happen."
                    )
                if seed_id == "":
                    if seed.is_seed_registered(cursor, seed_name):
                        # Mistake from the FE, the seed is known in the database
                        seed_id = seed.get_seed_id(cursor, seed_name)
                    else:
                        # unknown seed
                        seed_id = seed.new_seed(cursor, seed_name)
                # Create the new object
                object_id = inference.new_inference_object(
                    cursor, inference_id, box_metadata, 1, manual_detection=True
                )
                seed_object_id = inference.new_seed_object(
                    cursor, seed_id, object_id, 0
                )
                # Set the verified_id to the seed_object_id
                inference.set_inference_object_verified_id(
                    cursor, object_id, seed_object_id
                )
                valid = True
            else:  # This is a box that was created by the pipeline so it should be within the database

                # Removing this check based on a user request of
                # being able to edit a verified box in case of mistake
                # if inference.is_object_verified(cursor, box_id):
                #     raise InferenceFeedbackError(
                #         f"Error: Object {box_id} is already verified"
                #     )

                # This is a box that was created by the pipeline so it should be within the database
                object_db = inference.get_inference_object(
                    cursor, box_id
                )  # Raises an error when there is nothing returned
                object_metadata = object_db[1]
                object_id = object_db[0]

                # Check if there are difference between the metadata in the DB and the dict received
                if not (
                    inference_metadata.compare_object_metadata(
                        box_metadata, object_metadata["box"]
                    )
                ):
                    # Update the object metadata
                    # flag_box_metadata = True
                    inference.set_object_box_metadata(
                        cursor, box_id, json.dumps(box_metadata)
                    )

                # Check if the seed is known
                if seed_id == "":
                    if seed_name == "":
                        # box has been deleted by the user
                        valid = False
                    else:
                        valid = True
                        if seed.is_seed_registered(cursor, seed_name):
                            # The seed is known in the database and it was a mistake from the FE
                            seed_id = seed.get_seed_id(cursor, seed_name)
                        else:  # The seed is not known in the database
                            seed_id = seed.new_seed(cursor, seed_name)
                            seed_object_id = inference.new_seed_object(
                                cursor, seed_id, object_id, 0
                            )
                            inference.set_inference_object_verified_id(
                                cursor, object_id, seed_object_id
                            )

                # If a seed is selected by the user or if it is a known seed that the FE has not recognized
                if seed_id != "":
                    # Box is still valid
                    valid = True
                    # Check if a new seed has been selected
                    previous_top_inference_id = inference.get_inference_object_top_id(
                        cursor=cursor, inference_object_id=box_id
                    )

                    # Retrieve the seed_object inference made by the pipeline associated with this box if there was any
                    new_top_id = inference.get_seed_object_id(cursor, seed_id, box_id)
                    if new_top_id is None:
                        # Seed selected was not an inference guess, we need to create a new seed_object
                        new_top_id = inference.new_seed_object(
                            cursor, seed_id, box_id, 0
                        )
                        inference.set_inference_object_verified_id(
                            cursor, box_id, new_top_id
                        )
                        # flag_seed = True

                    # Check if we edit the
                    if previous_top_inference_id != new_top_id:
                        # Seed was not correctly identified, set the verified_id to the correct seed_object.id
                        # flag_seed = True
                        inference.set_inference_object_verified_id(
                            cursor, box_id, new_top_id
                        )
                    else:
                        # Seed was correctly identified, set the verified_id to the top_id
                        # flag_seed = False
                        inference.set_inference_object_verified_id(
                            cursor, box_id, previous_top_inference_id
                        )

            # Update the object validity

            # Should be always valid=True unless it was deleted by the user meaning the box has an id
            # but not a pipeline classification attributed to it (seed_id & seed_name are empty),
            inference.set_inference_object_valid(cursor, box_id, valid)
        # Check if all the valid objects have a verified_id and set the inference status
        inference.verify_inference_status(cursor, inference_id, user_id)
    except InferenceFeedbackError:
        raise
    except Exception as e:
        raise Exception(f"Datastore Unhandled Error: {e}")


async def new_perfect_inference_feeback(
    cursor, inference_id: UUID, user_id: UUID, boxes_id: list[UUID]
):
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
        for box_id in boxes_id:
            if not inference.check_inference_object_exist(cursor, box_id):
                raise inference.InferenceObjectNotFoundError(
                    f"Error: could not get inference object for id {str(box_id)}"
                )
        # Check if inference exists
        if not inference.check_inference_exist(cursor, inference_id):
            raise inference.InferenceNotFoundError(
                f"Inference not found based on the given id: {str(inference_id)}"
            )

        # There is a user request to allow to edit a miss-clic when verifying a seed.
        # if inference.is_inference_verified(cursor, inference_id):
        #     raise inference.InferenceAlreadyVerifiedError(
        #         f"Can't add feedback to a verified inference, id: {str(inference_id)}"
        #     )

        # Since this is a perfect inference for all the given object detected from the pipeline,
        # This means the best guest is the actual seed
        for object_id in boxes_id:
            top_inference_id = inference.get_inference_object_top_id(cursor, object_id)
            inference.set_inference_object_verified_id(
                cursor, object_id, top_inference_id
            )
            inference.set_inference_object_valid(cursor, object_id, True)

        # We check if all the boxes of the inference have been verified
        # (some might not be a perfect guess therefore will require a different approach)
        inference.verify_inference_status(cursor, inference_id, user_id)

    except (
        user.UserNotFoundError,
        inference.InferenceObjectNotFoundError,
        inference.InferenceNotFoundError,
        inference.InferenceAlreadyVerifiedError,
    ) as e:
        raise e
    except Exception as e:
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
        model_id = machine_learning.new_model(
            cursor, model_name, endpoint_name, task_id
        )
        # set active_version if not the test model
        if model_name != "test_model1":
            version = "0.0.1"
            model_version_id = machine_learning.new_model_version(
                cursor, model_id, version, model_db
            )
            machine_learning.set_active_model(
                cursor, str(model_id), str(model_version_id)
            )
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
        pipeline_id = machine_learning.new_pipeline(
            cursor, pipeline_db, pipeline_name, model_ids
        )
        # set the pipeline active if not the test pipeline
        if pipeline_name != "test_pipeline":
            machine_learning.set_active_pipeline(cursor, str(pipeline_id))


async def get_ml_structure(cursor):
    """
    This function retrieves the machine learning structure from the database.

    Returns a usable json object with the machine learning structure for the FE and BE
    """
    ml_structure = {"pipelines": [], "models": []}
    pipelines = machine_learning.get_active_pipeline(cursor)
    if len(pipelines) == 0:
        raise MLRetrievalError("No Active pipelines found in the database.")
    model_list = []
    for pipeline in pipelines:
        # (id, name, active:bool, is_default: bool, data, model_ids: array)

        pipeline_name = pipeline[1]
        pipeline_id = pipeline[0]
        default = pipeline[3]
        if pipeline[4] is not None:
            pipeline_data = pipeline[4]
        else:
            pipeline_data = None
        model_ids = pipeline[5]

        pipeline_dict = ml_metadata.build_pipeline_export(
            data=pipeline_data,
            name=pipeline_name,
            id=pipeline_id,
            default=default,
            model_ids=model_ids,
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


async def get_picture_sets_info(cursor, user_id: UUID):
    """This function retrieves the picture sets names and number of pictures from the database.
    This also retrieve for each picture in the picture set their name, if an inference exist and if the picture is validated.

    **Note**: This can be achieved through the container_controller.model.folders (dict[UUID,Folder]) which contains all the folders and their information

    Args:
        user_id (str): id of the user
    """
    try:
        # Check if user exists
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )

        result = []
        picture_sets = picture.get_user_picture_sets(cursor, user_id)
        for picture_set in picture_sets:
            picture_set_info = {}
            picture_set_id = picture_set[0]
            picture_set_name = picture_set[1]

            picture_set_info["picture_set_id"] = str(picture_set_id)
            picture_set_info["folder_name"] = picture_set_name

            pictures = picture.get_picture_set_pictures(cursor, picture_set_id)
            picture_set_info["nb_pictures"] = len(pictures)

            picture_set_info["pictures"] = []
            for pic in pictures:
                picture_info = {}
                picture_id = pic[0]
                picture_info["picture_id"] = str(picture_id)

                is_validated = picture.is_picture_validated(cursor, picture_id)
                inference_exist = picture.check_picture_inference_exist(
                    cursor, picture_id
                )
                picture_info["is_validated"] = is_validated
                picture_info["inference_exist"] = inference_exist

                picture_set_info["pictures"].append(picture_info)
            result.append(picture_set_info)
        return result
    except (
        user.UserNotFoundError,
        picture.GetPictureSetError,
        picture.GetPictureError,
    ) as e:
        raise e
    except Exception as e:
        raise picture.GetPictureSetError(
            f"An error occured while retrieving the picture sets : {e}"
        )


async def get_picture_inference(
    cursor, user_id: UUID, picture_id: UUID = None, inference_id: UUID = None
) -> dict:
    """
    Retrieves inference (if exist) of the given picture

    Args:
        cursor: The cursor object to interact with the database.
        user_id (str): id of the user
        picture_id (str): id of the picture
        inference_id (str): id of the inference
    """
    try:
        # Si aucun id (ni picture_id ni inference_id) n'est fourni, lève une exception.
        if picture_id is None and inference_id is None:
            raise ValueError("Error: picture_id or inference_id must be provided")

        # Check if user exists
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )

        # Si picture_id n'est pas fourni, mais inference_id l'est, récupère le picture_id en utilisant inference_id.
        if picture_id is None and inference_id is not None:
            picture_id = inference.get_inference_picture_id(cursor, inference_id)

        # Check if picture set exists
        if not picture.is_a_picture_id(cursor, picture_id):
            raise picture.PictureNotFoundError(
                f"Picture not found based on the given id: {picture_id}"
            )
        # Check user is owner of the picture set where the picture is
        picture_set_id = picture.get_picture_picture_set_id(cursor, picture_id)
        container_id = picture.get_picture_set_container_id(cursor, picture_set_id)

        if not verify_user_can_write(cursor, container_id, user_id):
            raise UserNotOwnerError(
                f"User can't access this picture, user uuid :{user_id}, picture : {picture_id}"
            )

        if picture.check_picture_inference_exist(cursor, picture_id):
            inf = inference.get_inference_by_picture_id(cursor, picture_id)
            inf = inference_metadata.rebuild_inference(cursor, inf)
            return inf.model_dump()
        else:
            return None

    except (
        user.UserNotFoundError,
        picture.PictureNotFoundError,
        UserNotOwnerError,
        ValueError,
    ) as e:
        raise e


async def delete_picture_set_with_archive(
    cursor,
    user_id: UUID,
    picture_set_id: UUID,
    container_controller: ContainerController,
) -> UUID:
    """
    Delete a picture set from the database and the blob storage but archives inferences and pictures in dev container

    Args:
        cursor: The cursor object to interact with the database.
        user_id (str): id of the user
        picture_set_id (str): id of the picture set to delete
        container_client: The container client of the user.

    Return:
    - UUID of the newly created archive folder
    """
    try:
        # Check if user exists
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )
        # Check if picture set exists
        if not picture.is_a_picture_set_id(cursor, picture_set_id):
            raise picture.PictureSetNotFoundError(
                f"Picture set not found based on the given id: {picture_set_id}"
            )
        # Check user is owner of the picture set
        if picture.get_picture_set_owner_id(cursor, picture_set_id) != user_id:
            raise UserNotOwnerError(
                f"User can't delete this folder, user uuid :{user_id}, folder name : {picture_set_id}"
            )
        # making sure there is an actual container attached to the container controller
        if not container_controller.container_client.exists():
            container_controller.get_container_client(
                connection_str=NACHET_STORAGE_URL, credentials=None
            )
            if not container_controller.container_client.exists():
                raise ContainerCreationError(
                    "You are trying to delete picture from a Container that has not been created or cant be found. Make sure to create the storage space using container_controller.create_storage() so we can access it. \nIn the current case, there should be no pictures associated with this container, therefore no picture to delete meaning there is a flaw in the logic"
                )

        # Check if the picture set is the default picture set (deprecated, we can delete any folder and create new ones if needed.)
        # general_folder_id = str(user.get_default_picture_set(cursor, user_id))
        # if general_folder_id == picture_set_id:
        #     raise picture.PictureSetDeleteError(
        #         f"User can't delete the default picture set, user uuid :{user_id}"
        #     )

        folder_name = picture.get_picture_set_name(cursor, picture_set_id)
        if folder_name is None:
            folder_name = str(
                picture_set_id
            )  # based on convention. The name should be automatically set as the id in the DB if not specified. This is a safety case
        validated_pictures = picture.get_validated_pictures(cursor, picture_set_id)

        # Fetching Dev
        dev_user_obj = await get_user(cursor=cursor, email=DEV_USER_EMAIL)
        dev_user_id = dev_user_obj.model.id

        dev_container_id = list(dev_user_obj.model.containers.keys())[0]
        dev_container_controller = await get_container_controller(
            cursor=cursor,
            container_id=dev_container_id,
            connection_str=NACHET_STORAGE_URL,
            credentials=None,
        )

        if not dev_container_controller.container_client.exists():
            raise BlobUploadError(
                f"Error while connecting to the dev container: {dev_user_id}"
            )
        # Checking if the user already has archived inferences
        already_archived = False
        archive_user_folder_model = None
        for folder in dev_container_controller.model.folders.values():
            if folder.name == str(user_id):
                already_archived = True
                archive_user_folder_model = folder.model_copy()
                break
        if not already_archived:
            # Archive user folder
            archive_user_folder_model = await dev_container_controller.create_folder(
                cursor=cursor,
                performed_by=dev_user_id,
                folder_name=str(user_id),
                nb_pictures=0,
                parent_folder_id=None,  # creating the folder at the root
            )

        archive_user_folder_id = archive_user_folder_model.id

        # Archiving the data
        nb_picture = len(validated_pictures)
        archived_folder_model = await dev_container_controller.create_folder(
            cursor=cursor,
            performed_by=dev_user_id,
            folder_name=folder_name,  # the id of the previously uploaded folder
            nb_pictures=nb_picture,
            parent_folder_id=archive_user_folder_id,  # new folder created within the user's archive folder
        )
        for picture_id in picture.get_validated_pictures(cursor, picture_set_id):
            picture_metadata = picture.get_picture(cursor, picture_id)
            # change the link in the metadata
            blob_name = azure_storage.build_blob_name(folder_name, str(picture_id))

            # special case for the dev container pictures
            dev_blob_name = azure_storage.build_blob_name(
                folder_path=archived_folder_model.path, blob_name=str(picture_id)
            )
            picture_metadata["link"] = dev_blob_name

            picture.update_picture_metadata(
                cursor, picture_id, json.dumps(picture_metadata), 0
            )
            # set picture set to dev one
            picture.update_picture_picture_set_id(
                cursor, picture_id, archived_folder_model.id
            )
            # move the picture to the dev container returns true if successfully moved
            if not (
                await azure_storage.move_blob(
                    blob_name_source=blob_name,
                    blob_name_dest=dev_blob_name,
                    folder_uuid=archived_folder_model.id,
                    container_client_source=container_controller.container_client,
                    container_client_destination=dev_container_controller.container_client,
                )
            ):
                raise BlobUploadError(
                    f"Error while moving the picture : {picture_id} to the dev container"
                )

        if len(picture.get_validated_pictures(cursor, picture_set_id)) > 0:
            # This should not happen, All validated pictures should of been moved already by this function.
            # We are just making sure there are no traces left in the DB.
            raise picture.PictureSetDeleteError(
                f"Can't delete the folder, there are still validated pictures in it, folder name : {picture_set_id}"
            )

        # Delete the folder in the blob storage
        await container_controller.delete_folder_permanently(
            cursor=cursor, user_id=user_id, folder_id=picture_set_id
        )

        return archived_folder_model.id
    except (
        user.UserNotFoundError,
        picture.PictureSetNotFoundError,
        picture.PictureSetDeleteError,
        UserNotOwnerError,
    ) as e:
        raise e
    except Exception as e:
        raise Exception(f"Datastore Unhandled Error: {e}")


async def find_validated_pictures(cursor, user_id: UUID, picture_set_id: UUID):
    """
    Find pictures that have been validated by the user in the given picture set

    Args:
        cursor: The cursor object to interact with the database.
        user_id (str): id of the user that should be the owner of the picture set
        picture_set_id (str): id of the picture set

    Returns:
        list of picture_id
    """
    try:
        # Check if user exists
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )
        # Check if picture set exists
        if not picture.is_a_picture_set_id(cursor, picture_set_id):
            raise picture.PictureSetNotFoundError(
                f"Picture set not found based on the given id: {picture_set_id}"
            )
        # Check user is owner of the picture set
        container_id = picture.get_picture_set_container_id(
            cursor=cursor, picture_set_id=picture_set_id
        )
        if not verify_user_can_write(
            cursor=cursor, container_id=container_id, user_id=user_id
        ):
            raise UserNotOwnerError(
                f"User isn't owner of this folder, user uuid :{user_id}, folder uuid : {picture_set_id}"
            )

        validated_pictures_id = picture.get_validated_pictures(cursor, picture_set_id)
        return validated_pictures_id
    except (
        user.UserNotFoundError,
        picture.PictureSetNotFoundError,
        UserNotOwnerError,
    ) as e:
        raise e
    except Exception as e:
        raise Exception(f"Datastore Unhandled Error: {e}")
