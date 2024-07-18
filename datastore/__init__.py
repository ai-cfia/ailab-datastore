"""
This module is responsible for handling the user data in the database 
and the user container in the blob storage.
"""

import datastore.db.queries.user as user
import datastore.db.queries.picture as picture
import datastore.db.metadata.picture_set as data_picture_set
import datastore.blob as blob
import datastore.blob.azure_storage_api as azure_storage
from azure.storage.blob import BlobServiceClient, ContainerClient
from dotenv import load_dotenv

load_dotenv()

class UserAlreadyExistsError(Exception):
    pass


class UserNotOwnerError(Exception):
    pass


class BlobUploadError(Exception):
    pass


class ContainerCreationError(Exception):
    pass


class FolderCreationError(Exception):
    pass



class User:
    def __init__(self, email: str, id: str = None, tier: str = "user"):
        self.id = id
        self.email = email
        self.tier = tier

    def get_email(self):
        return self.email

    def get_id(self):
        return self.id

    def get_container_client(self):
        return get_user_container_client(self.id, self.tier)


async def get_user(cursor, email) -> User:
    """
    Get a user from the database

    Parameters:
    - email (str): The email of the user.
    - cursor: The cursor object to interact with the database.
    """
    user_id = user.get_user_id(cursor, email)
    return User(email, user_id)


async def new_user(cursor, email, connection_string, tier="user") -> User:
    """
    Create a new user in the database and blob storage.

    Parameters:
    - email (str): The email of the user.
    - cursor: The cursor object to interact with the database.
    - connection_string: The connection string to connect with the Azure storage account
    """
    try:
        # Register the user in the database
        if user.is_user_registered(cursor, email):
            raise UserAlreadyExistsError("User already exists")
        user_uuid = user.register_user(cursor, email)

        # Create the user container in the blob storage
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        container_client = blob_service_client.create_container(f"{tier}-{user_uuid}")

        if not container_client.exists():
            raise ContainerCreationError("Error creating the user container")

        # Link the container to the user in the database
        pic_set_metadata = data_picture_set.build_picture_set(
            user_id=user_uuid, nb_picture=0
        )
        pic_set_id = picture.new_picture_set(
            cursor, pic_set_metadata, user_uuid, "General"
        )
        user.set_default_picture_set(cursor, user_uuid, pic_set_id)
        # Basic user container structure
        response = await azure_storage.create_folder(
            container_client, str(pic_set_id), "General"
        )
        if not response:
            raise FolderCreationError("Error creating the user folder")
        return User(email, user_uuid)
    except azure_storage.CreateDirectoryError:
        raise FolderCreationError("Error creating the user folder")
    except UserAlreadyExistsError:
        raise
    except ContainerCreationError:
        raise
    except Exception as e:
        print(e)
        raise Exception("Datastore Unhandled Error")


async def get_user_container_client(
    user_id, storage_url, account, key, tier="user"
):
    """
    Get the container client of a user

    Parameters:
    - user_id (int): The id of the user.

    Returns: ContainerClient object
    """
    sas = blob.get_account_sas(account, key)
    # Get the container client
    container_client = await azure_storage.mount_container(
        storage_url, user_id, True, tier, sas
    )
    if isinstance(container_client, ContainerClient):
        return container_client


async def create_picture_set(
    cursor, container_client, nb_pictures: int, user_id: str, folder_name=None
):
    """
    Create a picture_set in the database and a related folder in the blob storage

    Args:
        cursor: The cursor object to interact with the database.
        container_client: The container client of the user.
        nb_pictures (int): number of picture that the picture set should be related to
        user_id (str): id of the user creating this picture set
        folder_name : name of the folder/picture set
        blob_name: customize blob name to create the folder in blob storage. Should look like path for a json file, example : {...}/{...}/{...}.json

    Returns:
        picture_set_id : uuid of the new picture set
    """
    try:

        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )

        picture_set = data_picture_set.build_picture_set(user_id, nb_pictures)
        picture_set_id = picture.new_picture_set(
            cursor=cursor,
            picture_set=picture_set,
            user_id=user_id,
            folder_name=folder_name,
        )

        folder_created = await azure_storage.create_folder(
            container_client, str(picture_set_id), folder_name
        )
        if not folder_created:
            raise FolderCreationError(
                f"Error while creating this folder : {picture_set_id}"
            )

        return picture_set_id
    except (
        user.UserNotFoundError,
        FolderCreationError,
        data_picture_set.PictureSetCreationError,
        picture.PictureSetCreationError,
        azure_storage.CreateDirectoryError,
    ) as e:
        raise e
    except Exception:
        raise BlobUploadError("An error occured during the upload of the picture set")


async def get_picture_sets_info(cursor, user_id: str):
    """This function retrieves the picture sets names and number of pictures from the database.
    This also retrieve for each picture in the picture set their name, if an inference exist and if the picture is validated.

    Args:
        user_id (str): id of the user
    """
    # Check if user exists
    if not user.is_a_user_id(cursor=cursor, user_id=user_id):
        raise user.UserNotFoundError(f"User not found based on the given id: {user_id}")

    result = []
    picture_sets = picture.get_user_picture_sets(cursor, user_id)
    for picture_set in picture_sets:
        picture_set_info = {}
        picture_set_id = picture_set[0]
        picture_set_name = picture_set[1]
        
        picture_set_info["picture_set_id"] = picture_set_id
        picture_set_info["folder_name"] = picture_set_name
        
        pictures = picture.get_picture_set_pictures(cursor, picture_set_id)
        picture_set_info["nb_pictures"] = len(pictures)
        
        picture_set_info["pictures"] = []
        for pic in pictures :
            picture_info = {}
            picture_id = pic[0]
            picture_info["picture_id"] = picture_id

            is_validated = picture.is_picture_validated(cursor, picture_id)
            inference_exist = picture.check_picture_inference_exist(cursor, picture_id)
            picture_info["is_validated"] = is_validated
            picture_info["inference_exist"] = inference_exist
            
            picture_set_info["pictures"].append(picture_info)
        result.append(picture_set_info)
    print(result)
    return result


async def delete_picture_set_permanently(
    cursor, user_id, picture_set_id, container_client
):
    """
    Delete a picture set from the database and the blob storage

    Args:
        cursor: The cursor object to interact with the database.
        user_id (str): id of the user
        picture_set_id (str): id of the picture set to delete
        container_client: The container client of the user.
    """
    try:
        # Check if user exists
        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )
        # Check if picture set exists
        if not picture.is_a_picture_set_id(cursor, picture_set_id):
            raise picture.PictureSetNotFoundError(
                f"Picture set not found based on the given id: {picture_set_id}"
            )
        # Check user is owner of the picture set
        if picture.get_picture_set_owner_id(cursor, picture_set_id) != user_id:
            raise UserNotOwnerError(
                f"User can't delete this folder, user uuid :{user_id}, folder name : {picture_set_id}"
            )
        # Check if the picture set is the default picture set
        general_folder_id = user.get_default_picture_set(cursor, user_id)
        if general_folder_id == picture_set_id:
            raise picture.PictureSetDeleteError(
                f"User can't delete the default picture set, user uuid :{user_id}"
            )

        # Delete the folder in the blob storage
        await azure_storage.delete_folder(container_client, picture_set_id)
        # Delete the picture set
        picture.delete_picture_set(cursor, picture_set_id)

        return True
    except (
        user.UserNotFoundError,
        picture.PictureSetNotFoundError,
        picture.PictureSetDeleteError,
        UserNotOwnerError,
    ) as e:
        raise e
    except Exception as e:
        print(e)
        raise Exception("Datastore Unhandled Error")
