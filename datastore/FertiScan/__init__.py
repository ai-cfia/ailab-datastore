import asyncio
import json
import os

from dotenv import load_dotenv

import datastore
import datastore.blob as blob
import datastore.blob.azure_storage_api as azure_storage
import datastore.db.metadata.inspection as data_inspection
import datastore.db.metadata.picture_set as data_picture_set
import datastore.db.queries.inspection as inspection
import datastore.db.queries.picture as picture

load_dotenv()

FERTISCAN_DB_URL = os.environ.get("FERTISCAN_DB_URL")
if FERTISCAN_DB_URL is None or FERTISCAN_DB_URL == "":
    # raise ValueError("FERTISCAN_DB_URL is not set")
    print("Warning: FERTISCAN_DB_URL not set")

FERTISCAN_SCHEMA = os.environ.get("FERTISCAN_SCHEMA")
if FERTISCAN_SCHEMA is None or FERTISCAN_SCHEMA == "":
    # raise ValueError("FERTISCAN_SCHEMA is not set")
    print("Warning: FERTISCAN_SCHEMA not set")

FERTISCAN_STORAGE_URL = os.environ.get("FERTISCAN_STORAGE_URL")
if FERTISCAN_STORAGE_URL is None or FERTISCAN_STORAGE_URL == "":
    # raise ValueError("FERTISCAN_STORAGE_URL is not set")
    print("Warning: FERTISCAN_STORAGE_URL not set")


async def register_analysis(
    cursor,
    container_client,
    user_id,
    hashed_pictures,
    analysis_dict,
):
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
        # Create picture set for this analysis
        picture_set_metadata = data_picture_set.build_picture_set(
            user_id, len(hashed_pictures)
        )
        picture_set_id = picture.new_picture_set(
            cursor, picture_set_metadata, user_id, "General"
        )

        # Upload pictures to storage
        picture_ids = await datastore.upload_pictures(
            cursor=cursor,
            user_id=user_id,
            container_client=container_client,
            picture_set_id=picture_set_id,
            hashed_pictures=hashed_pictures,
        )

        # Register analysis in the database
        formatted_analysis = data_inspection.build_inspection_import(analysis_dict)

        analysis_db = inspection.new_inspection_with_label_info(
            cursor, user_id, picture_set_id, formatted_analysis
        )
        return analysis_db
    except Exception as e:
        print(e.__str__())
        raise Exception("Datastore Unhandled Error")
