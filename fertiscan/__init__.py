import os
from uuid import UUID

from azure.storage.blob import ContainerClient
from dotenv import load_dotenv
from psycopg import Cursor

import datastore
import datastore.db.metadata.picture_set as data_picture_set
import datastore.db.queries.picture as picture
import datastore.db.queries.user as user
import fertiscan.db.metadata.inspection as data_inspection
import fertiscan.db.queries.inspection as inspection
from fertiscan.db.models import DBInspection, Inspection

load_dotenv()

FERTISCAN_DB_URL = os.environ.get("FERTISCAN_DB_URL")
if FERTISCAN_DB_URL is None or FERTISCAN_DB_URL == "":
    print("Warning: FERTISCAN_DB_URL not set")

FERTISCAN_SCHEMA = os.environ.get("FERTISCAN_SCHEMA")
if FERTISCAN_SCHEMA is None or FERTISCAN_SCHEMA == "":
    print("Warning: FERTISCAN_SCHEMA not set")

FERTISCAN_STORAGE_URL = os.environ.get("FERTISCAN_STORAGE_URL")
if FERTISCAN_STORAGE_URL is None or FERTISCAN_STORAGE_URL == "":
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
    - analysis_dict (dict): The analysis to register in a dict string.
    - picture: The picture encoded to upload.

    Returns:
    - The analysis_dict with the analysis_id added.
    """
    try:
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )
        if not container_client.exists():
            raise datastore.ContainerCreationError(
                f"Container not found based on the given user_id: {user_id}"
            )

        # Create picture set for this analysis
        picture_set_metadata = data_picture_set.build_picture_set(
            user_id, len(hashed_pictures)
        )
        picture_set_id = picture.new_picture_set(cursor, picture_set_metadata, user_id)

        await datastore.create_picture_set(
            cursor, container_client, len(hashed_pictures), user_id, str(picture_set_id)
        )

        # Upload pictures to storage
        await datastore.upload_pictures(
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
    except data_inspection.MissingKeyError:
        raise


async def update_inspection(
    cursor: Cursor,
    inspection_id: str | UUID,
    user_id: str | UUID,
    updated_data: dict | Inspection,
):
    """
    Update an existing inspection record in the database.

    Parameters:
    - cursor (Cursor): Database cursor for executing queries.
    - inspection_id (str | UUID): UUID of the inspection to update.
    - user_id (str | UUID): UUID of the user performing the update.
    - updated_data (dict | Inspection): Dictionary or Inspection model containing updated inspection data.

    Returns:
    - Inspection: Updated inspection data from the database.

    Raises:
    - InspectionUpdateError: If an error occurs during the update.
    """
    if isinstance(inspection_id, str):
        inspection_id = UUID(inspection_id)
    if isinstance(user_id, str):
        user_id = UUID(user_id)
    if not user.is_a_user_id(cursor, str(user_id)):
        raise user.UserNotFoundError(f"User not found based on the given id: {user_id}")

    if not isinstance(updated_data, Inspection):
        updated_data = Inspection.model_validate(updated_data)

    # The inspection record must exist before updating it
    if not inspection.is_a_inspection_id(cursor, str(inspection_id)):
        raise inspection.InspectionNotFoundError(
            f"Inspection not found based on the given id: {inspection_id}"
        )

    updated_result = inspection.update_inspection(
        cursor, inspection_id, user_id, updated_data.model_dump()
    )
    return Inspection.model_validate(updated_result)


async def get_full_inspection_json(
    cursor,
    inspection_id,
    user_id=None,
    picture_set_id=None,
    label_info_id=None,
    company_info_id=None,
    manufacturer_info_id=None,
):
    """
    Get the full inspection json from the database

    Parameters:
    - cursor: The cursor object to interact with the database.
    - inspection_id: The inspection id of the inspection.

    Returns:
    - The inspection json.
    """
    try:
        if not inspection.is_a_inspection_id(
            cursor=cursor, inspection_id=inspection_id
        ):
            raise inspection.InspectionNotFoundError(
                f"Inspection not found based on the given id: {inspection_id}"
            )

        # Check Ids
        if (
            (
                picture_set_id is None
                or picture_set_id == ""
                or not picture.is_a_picture_set_id(
                    cursor=cursor, picture_set_id=picture_set_id
                )
            )
            or (
                user_id is None
                or user_id == ""
                or not user.is_a_user_id(cursor=cursor, user_id=user_id)
            )
            or (label_info_id is None or label_info_id == "")
            or (company_info_id is None or company_info_id == "")
            or (manufacturer_info_id is None or manufacturer_info_id == "")
        ):
            ids = inspection.get_inspection_fk(cursor, inspection_id)
            picture_set_id = ids[2]
            label_info_id = ids[0]
            company_info_id = ids[3]
            manufacturer_info_id = ids[4]
            user_id = ids[1]
        else:
            if not picture.is_a_picture_set_id(
                cursor=cursor, picture_set_id=picture_set_id
            ):
                raise picture.PictureSetNotFoundError(
                    f"Picture set not found based on the given id: {picture_set_id}"
                )
            if not user.is_a_user_id(cursor=cursor, user_id=user_id):
                raise user.UserNotFoundError(
                    f"User not found based on the given id: {user_id}"
                )
            ids = inspection.get_inspection_fk(cursor, inspection_id)
            if not picture_set_id == ids[2]:
                raise Warning(
                    "Picture set id does not match the picture_set_id in the inspection for the given inspection_id"
                )
            if not label_info_id == ids[0]:
                raise Warning(
                    "Label info id does not match the label_info_id in the inspection for the given inspection_id"
                )
            if not company_info_id == ids[3]:
                raise Warning(
                    "Company info id does not match the company_info_id in the inspection for the given inspection_id"
                )
            if not manufacturer_info_id == ids[4]:
                raise Warning(
                    "Manufacturer info id does not match the manufacturer_info_id in the inspection for the given inspection_id"
                )
            if not user_id == ids[1]:
                raise Warning(
                    "User id does not match the user_id in the inspection for the given inspection_id"
                )

        # Retrieve pictures
        # pictures_ids = picture.get_picture_in_picture_set(cursor, picture_set_id)

        # Retrieve label_info
        inspection_metadata = data_inspection.build_inspection_export(
            cursor, inspection_id, label_info_id
        )

        return inspection_metadata
    except inspection.InspectionNotFoundError:
        raise


async def get_user_analysis_by_verified(cursor, user_id, verified: bool):
    """
    This function fetch all the inspection of a user

    Parameters:
    - cursor: The cursor object to interact with the database.
    - user_id: The user id of the user.

    Returns:
    - List of unverified analysis.
    [
        inspection.id,
        inspection.upload_date,
        inspection.updated_at,
        inspection.sample_id,  -- Not used at the moment
        inspection.picture_set_id,
        label_info.id as label_info_id,
        label_info.product_name,
        label_info.company_info_id,
        label_info.manufacturer_info_id
        company_info.id as company_info_id,
        company_info.company_name
    ]
    """

    try:
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )
        return inspection.get_all_user_inspection_filter_verified(
            cursor, user_id, verified
        )
    except user.UserNotFoundError:
        raise


async def delete_inspection(
    cursor: Cursor,
    inspection_id: str | UUID,
    user_id: str | UUID,
    container_client: ContainerClient,
) -> DBInspection:
    """
    Delete an existing inspection record and its associated picture set from the database.

    Parameters:
    - cursor (Cursor): Database cursor for executing queries.
    - inspection_id (str | UUID): UUID of the inspection to delete.
    - user_id (str | UUID): UUID of the user performing the deletion.

    Returns:
    - DBInspection: The deleted inspection data from the database.

    """
    if isinstance(inspection_id, str):
        inspection_id = UUID(inspection_id)
    if isinstance(user_id, str):
        user_id = UUID(user_id)

    # Delete the inspection and get the returned data
    deleted_inspection = inspection.delete_inspection(cursor, inspection_id, user_id)
    deleted_inspection = DBInspection.model_validate(deleted_inspection)

    await datastore.delete_picture_set_permanently(
        cursor, str(user_id), str(deleted_inspection.picture_set_id), container_client
    )

    return deleted_inspection
