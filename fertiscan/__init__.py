import os
from uuid import UUID

from azure.storage.blob import ContainerClient
from dotenv import load_dotenv
from psycopg import Cursor

import datastore
import datastore.db.queries.picture as picture
import datastore.db.queries.user as user
import fertiscan.db.metadata.inspection as data_inspection
from fertiscan.db.queries import ingredient,inspection,label,metric,nutrients,organization,registration_number,specification,sub_label

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
    # ----------
    # Label info
    label_info_id = label.new_label_information(
        cursor=cursor,
        name=formatted_analysis.product.name,
        lot_number=formatted_analysis.product.lot_number,
        npk=formatted_analysis.product.npk,
        n=formatted_analysis.product.n,
        p=formatted_analysis.product.p,
        k=formatted_analysis.product.k,
        title_en=formatted_analysis.guaranteed_analysis.title.en,
        title_fr=formatted_analysis.guaranteed_analysis.title.fr,
        is_minimal=formatted_analysis.guaranteed_analysis.is_minimal,
        record_keeping=formatted_analysis.product.record_keeping
    )
    formatted_analysis.product.label_id = label_info_id 
    # Metrics
    # Weight
    for record in formatted_analysis.product.metrics.weight:
        metric.new_metric(
            cursor=cursor,
            value= record.value,
            read_unit=record.unit,
            label_id=label_info_id,
            metric_type='weight',
            edited=False
        )
    # Density
    metric.new_metric(
        cursor=cursor,
        value= formatted_analysis.product.metrics.density.value,
        read_unit=formatted_analysis.product.metrics.density.unit,
        label_id=label_info_id,
        metric_type='density',
        edited=False
    )
    # Volume
    metric.new_metric(
        cursor=cursor,
        value= formatted_analysis.product.metrics.volume.value,
        read_unit=formatted_analysis.product.metrics.volume.unit,
        label_id=label_info_id,
        metric_type='volume',
        edited=False
    )
    
    #Ingredients
    for ingredient_en in formatted_analysis.ingredients.en:
        ingredient.new_ingredient(
            cursor=cursor,
            name = ingredient_en.name,
            value= ingredient_en.value,
            read_unit= ingredient_en.unit,
            label_id=label_info_id,
            language="en",
            organic=None,
            active=None,
            edited=False,
        )
    for ingredient_fr in formatted_analysis.ingredients.fr:
        ingredient.new_ingredient(
            cursor=cursor,
            name = ingredient_fr.name,
            value= ingredient_fr.value,
            read_unit= ingredient_fr.unit,
            label_id=label_info_id,
            language="fr",
            organic=None,
            active=None,
            edited=False,
        )
        
    # Sub Label
    instruction_id = sub_label.get_sub_type_id(cursor,"instructions")
    caution_id = sub_label.get_sub_type_id(cursor,"cautions")
    max_instruction = max(len(formatted_analysis.instructions.en),len(formatted_analysis.instructions.fr))
    max_caution = max(len(formatted_analysis.cautions.en),len(formatted_analysis.cautions.fr))
    for i in range(0,max_instruction):
        if i >= len(formatted_analysis.instructions.fr):
            fr = None
            en = formatted_analysis.instructions.en[i]
        elif i >= len(formatted_analysis.instructions.en):
            fr = formatted_analysis.instructions.fr[i]
            en = None
        else:
            fr = formatted_analysis.instructions.fr[i]
            en = formatted_analysis.instructions.en[i]
        sub_label.new_sub_label(
            cursor=cursor,
            text_fr=fr,
            text_en=en,
            label_id=label_info_id,
            sub_type_id=str(instruction_id),
            edited=False,
        )
        
    for i in range(0,max_caution):
        if i >= len(formatted_analysis.cautions.fr):
            fr = None
            en = formatted_analysis.cautions.en[i]
        elif i >= len(formatted_analysis.cautions.en):
            fr = formatted_analysis.cautions.fr[i]
            en = None
        else:
            fr = formatted_analysis.cautions.fr[i]
            en = formatted_analysis.cautions.en[i]
        sub_label.new_sub_label(
            cursor=cursor,
            text_fr=formatted_analysis.cautions.fr[i],
            text_en=formatted_analysis.cautions.en[i],
            label_id=label_info_id,
            sub_type_id=str(caution_id),
            edited=False,
        )
    
    # Guaranteed Analysis
    for record in formatted_analysis.guaranteed_analysis.en:
       nutrients.new_guaranteed_analysis(
           cursor=cursor,
           read_name=record.name,
           value=record.value,
           unit = record.unit,
           label_id=label_info_id,
           language="en",
           element_id=None,
           edited= False
       ) 
    for record in formatted_analysis.guaranteed_analysis.fr:
       nutrients.new_guaranteed_analysis(
           cursor=cursor,
           read_name=record.name,
           value=record.value,
           unit = record.unit,
           label_id=label_info_id,
           language="fr",
           element_id=None,
           edited= False
       ) 
       
    # Reg numbers
    for record in formatted_analysis.product.registration_numbers:
        registration_number.new_registration_number(
            cursor=cursor,
            registration_number=record.registration_number,
            label_id=label_info_id,
            is_an_ingredient=record.is_an_ingredient,
            read_name=None,
            edited=False
        )
        
    # Organization
    flag = True
    for record in formatted_analysis.organizations:
        record.id=organization.new_organization_information(
            cursor=cursor,
            address=record.address,
            name=record.name,
            website=record.website,
            phone_number=record.phone_number,
            label_id=label_info_id,
            edited=False,
            is_main_contact=flag,
        )
        if flag==True:
            # We do this since we have no way of knowing who is the main contact
            flag=False
    
    # Inspection
    formatted_analysis.inspection_id = inspection.new_inspection(
        cursor=cursor,
        user_id=user_id,
        picture_set_id=folder_id,
        verified=False,
        label_id=label_info_id,
        container_id=container_id
    )
    analysis_db = data_inspection.Inspection.model_validate(formatted_analysis)
    inspection.save_inspection_original_dataset(
        cursor=cursor,
        inspection_id=formatted_analysis.inspection_id,
        og_data=analysis_db.model_dump_json(),
    )
    
    # ------------
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

