# import datastore.FertiScan as FertiScan
# import datastore
# import datastore.db.__init__ as db
# import os
# import json

# if __name__ == "__main__":
#     analysis_json = json.loads('tests/analyse.json')

#     con = db.connect_db(FertiScan.FERTISCAN_DB_URL)
#     cursor = con.cursor()
#     db.create_search_path(con, cursor, FertiScan.FERTISCAN_SCHEMA)

#     user_email = 'test@email'
#     datastore.new_user(cursor, user_email)

#     user_id = datastore.get_user_id(cursor, user_email)
#     container_client = datastore.get_user_container_client(user_id, 'test-user')

#     analysis = FertiScan.register_analysis(cursor, container_client, user_id, analysis_json)

#     print(analysis)


import asyncio
import json
import os
import traceback

from azure.storage.blob import ContainerClient
from dotenv import load_dotenv
from psycopg import connect

from datastore import get_user, new_user
from datastore.FertiScan import register_analysis, update_inspection
from datastore.db.metadata.inspection import Inspection

load_dotenv()

# Constants for configuration
DB_CONNECTION_STRING = os.getenv("FERTISCAN_DB_URL")
if not DB_CONNECTION_STRING:
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.getenv("FERTISCAN_SCHEMA", "fertiscan_0.0.9")
STORAGE_CONNECTION_STRING = os.getenv("FERTISCAN_AZURE_STORAGE_CONNECTION_STRING")
if not STORAGE_CONNECTION_STRING:
    raise ValueError("FERTISCAN_AZURE_STORAGE_CONNECTION_STRING is not set")

# Load JSON data from file
def load_json_from_file(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Load a single image from file and return its binary data
def load_image(image_path):
    with open(image_path, "rb") as image_file:
        return image_file.read()

# Define the main testing function
async def main():
    try:
        # Create a real database connection
        conn = connect(DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public")
        conn.autocommit = False
        cursor = conn.cursor()

        # Load images one by one (assuming paths are provided)
        image_paths = ["img.jpg"]  # Replace with actual paths
        hashed_pictures = [load_image(path) for path in image_paths]

        # Create a sample analysis form from JSON
        analysis_dict = load_json_from_file("tests/FertiScan/analyse.json")

        # Sample user ID and hashed pictures
        email = "example1@mail.com"
        await new_user(cursor=cursor, email=email, connection_string=STORAGE_CONNECTION_STRING)
        user = await get_user(cursor, email)
        user_id = user.id

        container_client = ContainerClient.from_connection_string(
            STORAGE_CONNECTION_STRING, container_name=f"user-{user_id}"
        )

        # Register analysis and obtain inspection data
        returned_data = await register_analysis(
            cursor=cursor,
            container_client=container_client,
            user_id=user_id,
            hashed_pictures=hashed_pictures,
            analysis_dict=analysis_dict,
        )
        
        print(f"Returned Data: {returned_data}")

        inspection_id = returned_data['inspection_id']  # Extract inspection ID
        print(f"Inspection ID: {inspection_id}")
        print(f"User ID: {user_id}")

        # Modify the returned data to simulate an update
        updated_data = returned_data.copy()
        updated_data['company']['name'] = "Updated Company Name"
        updated_data['product']['metrics']['weight'][0]['value'] = 26.0
        updated_data['verified'] = True

        # Convert to Inspection object if needed
        updated_data_model = Inspection(**updated_data)

        # Update the inspection
        updated_result = await update_inspection(
            cursor=cursor,
            inspection_id=inspection_id,
            user_id=user_id,
            updated_data=updated_data_model,
        )
        print(f"Updated Inspection Result: {updated_result}")

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        conn.rollback()
        cursor.close()
        conn.close()

# Run the testing function
asyncio.run(main())
