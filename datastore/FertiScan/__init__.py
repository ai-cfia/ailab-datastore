import uuid

from azure.storage.blob.aio import ContainerClient
from dotenv import load_dotenv
from psycopg import Cursor

import datastore
import datastore.db.metadata.inspection as data_inspection
import datastore.db.queries.inspection as inspection
import datastore.db.queries.picture as picture
from datastore.db.metadata.validator import AnalysisForm

load_dotenv()


async def register_inspection(
    cursor: Cursor,
    container_client: ContainerClient,
    user_id: str,
    hashed_pictures: list[str],
    analysis_form: AnalysisForm | dict,
):
    """
    Register an analysis in the database

    Parameters:
    - cursor: The cursor object to interact with the database.
    - container_client: The user's container client used for picture uploads.
    - user_id (str): The UUID of the user.
    - hashed_pictures (list[str]): The list of hashed pictures to upload.
    - analysis_form (Union[AnalysisForm, dict]): The form containing analysis data or a dictionary.

    Returns:
    - str: The UUID of the created inspection.
    """
    try:
        if isinstance(analysis_form, dict):
            analysis_form = AnalysisForm(**analysis_form)

        # Create picture set for this analysis
        picture_set_id = picture.new_picture_set(cursor, user_id)
        picture_set_id = uuid.uuid4()

        # Upload pictures to storage
        await datastore.upload_pictures(
            cursor=cursor,
            user_id=user_id,
            hashed_pictures=hashed_pictures,
            container_client=container_client,
            picture_set_id=picture_set_id,
        )

        # Register analysis in the database
        inspection_import = data_inspection.build_inspection_import(analysis_form)
        return inspection.new_inspection(
            cursor, user_id, picture_set_id, inspection_import
        )
    except Exception as e:
        print(e.__str__())
        raise Exception("Datastore Unhandled Error")
