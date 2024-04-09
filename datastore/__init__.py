import datastore.db.queries.user as user
import datastore.blob.azure_storage_api as blob
from azure.storage.blob import BlobServiceClient

class UserAlreadyExistsError(Exception):
    pass
class ContainerCreationError(Exception):
    pass
class FolderCreationError(Exception):
    pass

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
        response = await blob.create_folder(container_client, "General")
        if not response:
            raise FolderCreationError("Error creating the user folder")
        
        
    except:
        raise Exception("Unhandled Error")