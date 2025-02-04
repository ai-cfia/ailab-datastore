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
    
class Inspection(BaseModel):
    id: UUID
    user_id: UUID
    folder_id : UUID
    label_id: Optional[UUID] = None
    verified: Optional[bool] = None
    
class InspectionController:
    def __init__(self,inspection_model: Inspection):
        self.model:Inspection = inspection_model
        

    def register_analysis(
        self,
        cursor: Cursor,
        analysis_dict,
    ):
        """
        Register an analysis in the database

        Parameters:
        - cursor: The cursor object to interact with the database.
        - container_client: The container client of the user.
        - analysis_dict (dict): The analysis to register in a dict string

        Returns:
        - The analysis_dict with the analysis_id added.
        """
        if not user.is_a_user_id(cursor=cursor, user_id=self.model.user_id):
            raise user.UserNotFoundError(f"User not found based on the given id: {self.model.user_id}")
        # Register analysis in the database
        formatted_analysis = data_inspection.build_inspection_import(analysis_dict,user_id)

        analysis_db = inspection.new_inspection_with_label_info(
            cursor, self.model.user_id, self.model.folder_id, formatted_analysis
        )
        self.model.id = analysis_db["inspection_id"]
        return analysis_db
    
    def update_inspection(
        self,
        cursor: Cursor,
        updated_data: dict | data_inspection.Inspection,
    ):
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
        if not user.is_a_user_id(cursor=cursor, user_id=self.model.user_id):
            raise user.UserNotFoundError(f"User not found based on the given id: {self.model.user_id}")
        
        if not isinstance(updated_data, data_inspection.Inspection):
            updated_data = data_inspection.Inspection.model_validate(updated_data)

        # The inspection record must exist before updating it
        if not inspection.is_a_inspection_id(cursor, str(self.model.id)):
            raise inspection.InspectionNotFoundError(
                f"Inspection not found based on the given id: {self.model.id}"
            ) 

        updated_result = inspection.update_inspection(
            cursor, self.model.id, self.model.user_id, updated_data.model_dump()
        )
        return data_inspection.Inspection.model_validate(updated_result)

    def get_full_inspection_analysis(
        self,
        cursor:Cursor,
    ):
        """
        Get the full inspection json from the database

        Parameters:
        - cursor: The cursor object to interact with the database.

        Returns:
        - The inspection json.
        """
        if not inspection.is_a_inspection_id(cursor=cursor, inspection_id=self.model.id):
            raise inspection.InspectionNotFoundError(
                f"Inspection not found based on the given id: {self.model.id}"
            )
        
        # Retrieve label_info
        inspection_metadata = data_inspection.build_inspection_export(
            cursor, self.model.id
        )
        return inspection_metadata

    def get_user_analysis_by_verified(
        self,
        cursor:Cursor,
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
        if not user.is_a_user_id(cursor=cursor, user_id=self.model.user_id):
            raise user.UserNotFoundError(f"User not found based on the given id: {self.model.user_id}")
        return inspection.get_all_user_inspection_filter_verified(cursor, self.model.user_id, verified)
        
    def delete_inspection(
        self,
        cursor:Cursor,
        container_id: UUID,
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

        # Delete the inspection and get the returned data
        deleted_inspection = inspection.delete_inspection(cursor, self.model.id, self.model.user_id)
        deleted_inspection = data_inspection.DBInspection.model_validate(deleted_inspection)
        container_controller:ContainerController = datastore.get_container_controller(cursor,container_id)
        
        container_controller.delete_folder_permanently(cursor,self.model.user_id,self.model.folder_id)

        return deleted_inspection

    def get_inspection_image_location_data(
        self,
        cursor: Cursor,
        )->tuple[UUID,UUID]:
        """
        Retrieve the relevant information regarding where the Inspection Images are stored
        This is usefull to perform Container_Controller.get_folder_pictures()

        Parameters:
        - cursor (Cursor): Database cursor for executing queries.
        
        Returns:
        - tuple (container_id: UUID, folder: UUID): The id necessary to locate the images 
        """
        if not inspection.is_a_inspection_id(cursor=cursor, inspection_id=self.model.id):
            raise inspection.InspectionNotFoundError(
                f"Inspection not found based on the given id: {self.model.id}"
            )
        picture_set_id = inspection.get_inspection_fk(cursor,self.model.id)[2]

        container_id = picture.get_picture_set_container_id(
            cursor=cursor,
            picture_set_id=picture_set_id
            )
        return (container_id,picture_set_id)
