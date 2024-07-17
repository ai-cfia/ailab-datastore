import os
from dotenv import load_dotenv


load_dotenv()

FERTISCAN_DB_URL = os.environ.get("FERTISCAN_DB_URL")
if FERTISCAN_DB_URL is None or FERTISCAN_DB_URL == "":
    # raise ValueError("FERTISCAN_DB_URL is not set")
    print("Warning: FERTISCAN_DB_URL not set")

FERTISCAN_SCHEMA = os.environ.get("FERTISCAN_SCHEMA")
if FERTISCAN_SCHEMA is None or FERTISCAN_SCHEMA == "":
    # raise ValueError("FERTISCAN_SCHEMA is not set")
    print("Warning: FERTISCAN_SCHEMA not set")

FERTISCAN_STORAGE_URL =  os.environ.get("FERTISCAN_STORAGE_URL")
if FERTISCAN_STORAGE_URL is None or FERTISCAN_STORAGE_URL == "":
    # raise ValueError("FERTISCAN_STORAGE_URL is not set")
    print("Warning: FERTISCAN_STORAGE_URL not set")

async def register_analysis(
    cursor, container_client, analysis_dict, picture_id: str, picture, folder="General"
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
        if picture_id is None or picture_id == "":
            picture_id = str(uuid.uuid4())
        # if not azure_storage.is_a_folder(container_client, folder):
        #     azure_storage.create_folder(container_client, folder)
        # azure_storage.upload_image(container_client, folder, picture, picture_id)
        # analysis_id = analysis.new_analysis(cursor, json.dumps(analysis_dict))
        #analysis_dict["analysis_id"] = str(analysis_id)
        return None
    except Exception as e:
        print(e.__str__())
        raise Exception("Datastore Unhandled Error")
