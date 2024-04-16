"""
This module is responsible for handling the user data in the database 
and the user container in the blob storage.
"""
import datastore.db.queries.user as user
import datastore.blob.azure_storage_api as azure_storage_api
import datastore.blob.__init__ as blob
from azure.storage.blob import BlobServiceClient
import os

NACHET_BLOB_ACCOUNT = os.environ.get('NACHET_BLOB_ACCOUNT')
if NACHET_BLOB_ACCOUNT is None or NACHET_BLOB_ACCOUNT == "":
    raise ValueError('NACHET_BLOB_ACCOUNT is not set')

NACHET_BLOB_KEY = os.environ.get('NACHET_BLOB_KEY')
if NACHET_BLOB_KEY is None or NACHET_BLOB_KEY == "":
    raise ValueError('NACHET_BLOB_KEY is not set')

NACHET_STORAGE_URL = os.environ.get('NACHET_STORAGE_URL')
if NACHET_STORAGE_URL is None or NACHET_STORAGE_URL == "":
    raise ValueError('NACHET_STORAGE_URL is not set')

class UserAlreadyExistsError(Exception):
    pass
class ContainerCreationError(Exception):
    pass
class FolderCreationError(Exception):
    pass

class User():
    def __init__(self, email: str ,id:str=None):
        self.id = id
        self.email = email
        
def get_User(email, cursor):
    """
    Get a user from the database

    Parameters:
    - email (str): The email of the user.
    - cursor: The cursor object to interact with the database.
    """
    user_id = user.get_user_id(email, cursor)
    return User(email, user_id)

async def new_user(email, cursor,connection_string):
    """
    Create a new user in the database and blob storage.

    Parameters:
    - email (str): The email of the user.
    - cursor: The cursor object to interact with the database.
    - connection_string: The connection string to connect with the Azure storage account
    """
    try:        
        # Register the user in the database
        if user.is_user_registered(email, cursor):
            raise UserAlreadyExistsError("User already exists")
        user_uuid = user.register_user(email, cursor)
        
        # Create the user container in the blob storage
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        container_client =blob_service_client.create_container(f"user-{user_uuid}")
        
        if not container_client.exists():
            raise ContainerCreationError("Error creating the user container")

        # Link the container to the user in the database
        user.link_container(cursor=cursor,user_id=user_uuid,container_url=container_client.url)
        
        # Basic user container structure
        response = await azure_storage_api.create_folder(container_client, "General")
        if not response:
            raise FolderCreationError("Error creating the user folder")
        return User(email, user_uuid)
        
    except:
        raise Exception("Unhandled Error")
    
async def get_user_container_client(user_id,tier="user"):
    """
    Get the container client of a user

    Parameters:
    - user_id (int): The id of the user.

    Returns: ContainerClient object
    """
    sas = blob.get_account_sas(NACHET_BLOB_ACCOUNT,NACHET_BLOB_KEY)
    # Get the container client
    container_client = await azure_storage_api.mount_container(NACHET_STORAGE_URL,user_id,True,tier,sas)
    return container_client
