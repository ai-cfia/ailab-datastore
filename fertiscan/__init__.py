import os
from uuid import UUID

from azure.storage.blob import ContainerClient
from dotenv import load_dotenv
from psycopg import Cursor

import datastore
import datastore.db.queries.picture as picture
import datastore.db.queries.user as user
import fertiscan.db.metadata.inspection as data_inspection
import fertiscan.db.queries.inspection as inspection

from datastore import ContainerController, ClientController, User

from pydantic import BaseModel
from typing import Optional

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
    
class InspectionController:
    def __init__(self,inspection_model:data_inspection.Inspection):
        self.model:data_inspection.Inspection = inspection_model
        self.id:UUID = inspection_model.inspection_id
        return
    
    def get_inspection_image_location_data(
        self,
        cursor: Cursor
    )->tuple[UUID,UUID]:
        """
        Retrieve the relevant information regarding where the Inspection Images are stored
        This is usefull to perform Container_Controller.get_folder_pictures()

        Parameters:
        - cursor (Cursor): Database cursor for executing queries.
        
        Returns:
        - tuple (container_id: UUID, folder: UUID): The id necessary to locate the images 
        """
        if not inspection.is_a_inspection_id(cursor=cursor, inspection_id=self.id):
            raise inspection.InspectionNotFoundError(
                f"Inspection not found based on the given id: {self.id}"
            )
        picture_set_id = inspection.get_inspection_fk(cursor,self.id)[2]

        container_id = picture.get_picture_set_container_id(
            cursor=cursor,
            picture_set_id=picture_set_id
            )
        return (container_id,picture_set_id)
    
    def update_inspection(
        self,
        cursor: Cursor,
        user_id: UUID,
        updated_data: dict | data_inspection.Inspection,
    )->data_inspection.Inspection:
        """
            Update an existing inspection record in the database.

            Parameters:
            - cursor (Cursor): Database cursor for executing queries.
            - inspection_id (str | UUID): UUID of the inspection to update.
            - user_id (str | UUID): UUID of the user performing the update.
            - updated_data (dict | data_inspection.Inspection): Dictionary or Inspection model containing updated inspection data.

            Returns:
            - data_inspection.Inspection: Updated inspection data from the database.

            Raises:
            - InspectionUpdateError: If an error occurs during the update.
            """
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
                raise user.UserNotFoundError(f"User not found based on the given id: {user_id}")
        if not isinstance(updated_data, data_inspection.Inspection):
                updated_data = data_inspection.Inspection.model_validate(updated_data)        
        # The inspection record must exist before updating it
        if not inspection.is_a_inspection_id(cursor, str(self.model.inspection_id)):
                raise inspection.InspectionNotFoundError(
                    f"Inspection not found based on the given id: {self.model.inspection_id}"
                ) 
        if self.model.container_id != updated_data.container_id or self.model.folder_id != updated_data.folder_id:
            raise Warning("You should not update an Inspection picture location. This does not cause issues in the DB but could result in errors when attempting to fetch the pictures")
        if not datastore.container_db.is_a_container(cursor=cursor,container_id=updated_data.container_id):
            raise datastore.ContainerCreationError(f"Container not found based on the given id: {updated_data.container_id}") 
        # Make sure the user can verify this inspection
        if not datastore.verify_user_can_write(cursor=cursor,container_id=updated_data.container_id,user_id=user_id):
            raise datastore.PermissionNotHighEnough(f"The user {user_id} does not have the write permission or higher which mean he cannot upload an inspection in the container {self.id}")
        updated_result = inspection.update_inspection(
            cursor, self.model.inspection_id, user_id, updated_data.model_dump_json()
        )
        return data_inspection.Inspection.model_validate(updated_result)
    
    async def delete_inspection(
        self,
        cursor:Cursor,
        user_id: UUID,
    )-> data_inspection.DBInspection:
        """
            Delete an existing inspection record and its associated picture set from the database.

            Parameters:
            - cursor (Cursor): Database cursor for executing queries.
            - inspection_id (str | UUID): UUID of the inspection to delete.
            - user_id (str | UUID): UUID of the user performing the deletion.

            Returns:
            - data_inspection.Inspection: The deleted inspection data from the database.

            """
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(f"User not found based on the given id: {user_id}")
        if not datastore.container_db.is_a_container(cursor=cursor,container_id=self.model.container_id):
            raise datastore.ContainerCreationError(f"Container not found based on the given id: {self.model.container_id}") 
        if not datastore.verify_user_can_write(cursor=cursor,container_id=self.model.container_id,user_id=user_id):
            raise datastore.PermissionNotHighEnough(f"The user {user_id} does not have the write permission or higher which mean he cannot upload an inspection in the container {self.id}")
    
        # Delete the inspection and get the returned data
        deleted_inspection = inspection.delete_inspection(cursor, self.id, user_id)
        deleted_inspection = data_inspection.DBInspection.model_validate(deleted_inspection)
        
        container_controller:ContainerController = await datastore.get_container_controller(cursor,self.model.container_id,FERTISCAN_STORAGE_URL,None)
        
        await container_controller.delete_folder_permanently(cursor,user_id,self.model.folder_id)
        return deleted_inspection
      
def new_inspection(cursor:Cursor, user_id:UUID, analysis_dict, container_id:UUID, folder_id:UUID)->InspectionController:
    """
    Register an analysis in the database
    
    Parameters:
    - cursor: The cursor object to interact with the database.
    - container_client: The container client of the user.
    - analysis_dict (dict): The analysis to register in a dict string
    
    Returns:
    - The analysis_dict with the analysis_id added.
    """
    if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(f"User not found based on the given id: {user_id}")
    if not datastore.container_db.is_a_container(cursor=cursor,container_id=container_id):
        raise datastore.ContainerCreationError(f"Container not found based on the given id: {container_id}") 
    if not datastore.verify_user_can_write(cursor=cursor,container_id=container_id,user_id=user_id):
        raise datastore.PermissionNotHighEnough(f"The user {user_id} does not have the write permission or higher which mean he cannot upload an inspection in the container {container_id}")
    
    formatted_analysis = data_inspection.build_inspection_import(
        analysis_form=analysis_dict,
        user_id=user_id,
        folder_id=folder_id,
        container_id=container_id)
    
    analysis_db = inspection.new_inspection_with_label_info(
            cursor, user_id, folder_id, formatted_analysis.model_dump_json()
        )
    analysis_db = data_inspection.Inspection.model_validate(analysis_db)
    inspection_controller = InspectionController(analysis_db)
        
    return inspection_controller

def get_inspection(
    cursor:Cursor,
    inspection_id:UUID,
)->InspectionController:
    """
        Get the full inspection json from the database and return a controller for it

        Parameters:
        - cursor: The cursor object to interact with the database.

        Returns:
        - The inspection json.
        """
    if not inspection.is_a_inspection_id(cursor=cursor, inspection_id=inspection_id):
        raise inspection.InspectionNotFoundError(
                f"Inspection not found based on the given id: {inspection_id}"
            )
    
    # Retrieve label_info
    inspection_metadata = data_inspection.build_inspection_export(
        cursor, inspection_id
    )
    inspection_controller = InspectionController(inspection_model=inspection_metadata)
    return inspection_controller

def get_user_analysis_by_verified(
    cursor:Cursor,
    user_id:UUID,
    verified : bool 
):
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
    if not user.is_a_user_id(cursor=cursor, user_id=user_id):
        raise user.UserNotFoundError(f"User not found based on the given id: {user_id}")
    return inspection.get_all_user_inspection_filter_verified(cursor, user_id, verified)

