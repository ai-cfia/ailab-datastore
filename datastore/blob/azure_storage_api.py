import json
import uuid
import hashlib
import os
import datetime
from azure.storage.blob import BlobServiceClient

from custom_exceptions import (
    ConnectionStringError,
    MountContainerError,
    GetBlobError,
    UploadImageError,
    UploadInferenceResultError,
    GetFolderUUIDError,
    FolderListError,
    GenerateHashError,
    CreateDirectoryError,
)

"""
---- user-container based structure -----
- container name is user id
- whenever a new user is created, a new container is created with the user uuid
- inside the container, there are project folders (project name = project uuid)
- for each project folder, there is a json file with the project info and creation
date, in the container
- inside the project folder, there is an image file and a json file with
the image inference results
"""


async def generate_hash(image):
    """
    generates a hash value for the image to be used as the image name in the container
    """
    try:
        hash = hashlib.sha256(image).hexdigest()
        return hash

    except GenerateHashError as error:
        print(error)


async def mount_container(connection_string, container_uuid, create_container=True,tier="user"):
    """
    Creates a container_client as an object that can be used in other functions.
    
    Parameters:
    - connection_string: the connection string to the azure storage account
    - container_uuid: the uuid of the container (usually the user uuid)
    - create_container: a boolean value to specify if the container should be created if it doesnt exist (default is True)
    - tier: the tier of the container (default is user, should be changed if the structure changes to accomodate other type of containers)
    
    Returns:
    - container_client: the container client object
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        if blob_service_client:
            container_name = "{}-{}".format(tier,container_uuid)
            container_client = blob_service_client.get_container_client(container_name)
            if container_client.exists():
                return container_client
            elif create_container and not container_client.exists():
                container_client = blob_service_client.create_container(container_name)
                # create general directory for new user container
                response = await create_folder(container_client, "General")
                if response:
                    return container_client
                else:
                    return False
        else:
            raise ConnectionStringError("Invalid connection string")

    except MountContainerError as error:
        print(error)
        return False


async def get_blob(container_client, blob_name):
    """
    gets the contents of a specified blob in the user's container
    """
    try:
        blob_client = container_client.get_blob_client(blob_name)
        blob = blob_client.download_blob()
        blob_content = blob.readall()
        return blob_content

    except GetBlobError as error:
        print(error)
        return False


async def upload_image(container_client, folder_uuid, image, image_uuid):
    """
    uploads the image to the specified folder within the user's container,
    if the specified folder doesnt exist, it creates it with a uuid
    """
    try:
        directories = await get_directories(container_client)
        if folder_uuid not in directories:
            raise CreateDirectoryError("Folder does not exist")
        else:
            blob_name = "{}/{}.png".format(folder_uuid, image_uuid)
            container_client.upload_blob(blob_name, image, overwrite=True)
            return blob_name

    except UploadImageError as error:
        print(error)
        return False


async def create_folder(container_client, folder_name):
    """
    creates a folder in the user's container
    
    Parameters:
    - container_client: the container client object to interact with the Azure storage account
    - folder_name: the name of the folder to be created (usually it's uuid)
    """
    try:
        directories = await get_directories(container_client)
        if folder_name not in directories:
            folder_data = {
                "folder_name": folder_name,
                "date_created": str(
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ),
            }
            file_name = "{}/{}.json".format(folder_name, folder_name)
            container_client.upload_blob(
                file_name, json.dumps(folder_data), overwrite=True
            )
            return True
        else:
            return False

    except CreateDirectoryError as error:
        print(error)
        return False


async def upload_inference_result(container_client, folder_name, result, hash_value):
    """
    uploads the inference results json file to the specified folder
    in the users container
    """
    try:
        folder_uuid = await get_folder_uuid(container_client, folder_name)
        if folder_uuid:
            json_name = "{}/{}.json".format(folder_uuid, hash_value)
            container_client.upload_blob(json_name, result, overwrite=True)
            return True

    except UploadInferenceResultError as error:
        print(error)
        return False


async def get_folder_uuid(container_client, folder_name):
    """
    gets the uuid of a folder in the user's container given the folder name by
    iterating through the folder json files and extracting the name
    to match given folder name
    """
    try:
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            if (
                blob.name.split(".")[-1] == "json"
                and blob.name.count("/") == 1
                and blob.name.split("/")[0] == blob.name.split("/")[1].split(".")[0]
            ):
                folder_json = await get_blob(container_client, blob.name)
                if folder_json:
                    folder_json = json.loads(folder_json)
                    if folder_json["folder_name"] == folder_name:
                        return blob.name.split(".")[0].split("/")[-1]
        return False
    except GetFolderUUIDError as error:
        print(error)
        return False


async def get_image_count(container_client, folder_name):
    """
    gets the number of images in a folder in the user's container
    """
    try:
        folder_uuid = await get_folder_uuid(container_client, folder_name)
        if folder_uuid:
            blob_list = container_client.list_blobs()
            count = 0
            for blob in blob_list:
                if (blob.name.split("/")[0] == folder_uuid) and (
                    blob.name.split(".")[-1] == "png"
                ):
                    count += 1
            return count
        else:
            return False
    except GetFolderUUIDError as error:
        print(error)
        return False


async def get_directories(container_client):
    """
    returns a list of folder names in the user's container
    """
    try:
        directories = {}
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            if (
                blob.name.split(".")[-1] == "json"
                and blob.name.count("/") == 1
                and blob.name.split("/")[0] == blob.name.split("/")[1].split(".")[0]
            ):
                json_blob = await get_blob(container_client, blob.name)
                if json_blob:
                    folder_json = json.loads(json_blob)
                    image_count = await get_image_count(
                        container_client, folder_json["folder_name"]
                    )
                    directories[folder_json["folder_name"]] = image_count
        return directories
    except FolderListError as error:
        print(error)
        return []

async def download_container(container_client,container_name,local_dir):
    """
    This function downloads all the files from a container in a storage account
    to the local directory "test"

    This serves as a way to locally download the container files for processing and importing within the db

    Parameters:
    - container_client: the Azure container client 
    - local_dir: the local directory to download the files to

    Returns: None
    """
    try:
        # List blobs in the container
        blob_list = container_client.list_blobs()
        # Iterate through each blob
        for i,blob in enumerate(blob_list):
            # Create a blob client
            blob_client = container_client.get_blob_client(
                container=container_name, blob=blob
            )
            # Download the blob
            local_file_path = f"{local_dir}/{blob.name}"
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            with open(local_file_path, "wb") as file:
                blob_data = blob_client.download_blob(blob=blob.name)
                blob_data.readinto(file)
                nb_downloaded_files=i
    except:
        raise Exception("Error downloading container")