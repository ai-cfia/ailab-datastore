import datetime
import hashlib
import json
import os

from minio import Minio
from minio.error import S3Error
from urllib3.exceptions import MaxRetryError


class GenerateHashError(Exception):
    pass


class MountContainerError(Exception):
    pass


class GetBlobError(Exception):
    pass


class UploadImageError(Exception):
    pass


class UploadInferenceResultError(Exception):
    pass


class GetFolderUUIDError(Exception):
    pass


class FolderListError(Exception):
    pass


class CreateDirectoryError(Exception):
    pass


class ConnectionStringError(Exception):
    pass


"""
---- user-container based structure -----
- container name is user id (bucket in MinIO terms)
- whenever a new user is created, a new bucket is created with the user uuid
- inside the bucket, there are project folders (project name = project uuid)
- for each project folder, there is a json file with the project info and creation
date, in the bucket
- inside the project folder, there is an image file and a json file with
the image inference results
"""


async def generate_hash(image):
    """
    generates a hash value for the image to be used as the image name in the bucket
    """
    try:
        hash = hashlib.sha256(image).hexdigest()
        return hash

    except TypeError as error:
        print(error.__str__())
        raise GenerateHashError("The image is not in the correct format")
    except Exception as error:
        print(error.__str__())
        raise Exception("Unhandeled Datastore.blob.minio_api Error")


def build_container_name(name: str, tier: str = "user") -> str:
    """
    This function builds the bucket name based on the tier and the name.
    We include a tier to better structure the bucket names in the future. Other tiers could be 'dev' or 'test-user'

    Parameters:
    - name (str): the name of the bucket. Usually the user uuid
    - tier (str): the tier of the bucket; Default is 'user'
    """
    if not name or name.strip() == "":
        raise ValueError("Name is required")
    return "{}-{}".format(tier, name)


def build_blob_name(folder_path: str, blob_name: str, file_type: str = None) -> str:
    """
    This function builds the object name based on the folder name and the image uuid

    Parameters:
    - folder_path (str): The path to the folder
    - blob_name (str): Usually the uuid of the image
    - file_type (str): the type of the file (ex: png, jpg, json)
    """
    if not folder_path or folder_path.strip() == "":
        raise ValueError("Folder name is required")
    if not blob_name or blob_name.strip() == "":
        raise ValueError("Image uuid is required (parameter: blob_name)")
    if file_type is not None and file_type.strip() != "":
        return "{}/{}.{}".format(folder_path, blob_name, file_type)
    else:
        return "{}/{}".format(folder_path, blob_name)


async def mount_container(
    connection_string,
    container_uuid,
    create_container=True,
    tier="user",
    credentials="",
):
    """
    Creates a minio client connection to a bucket.

    Parameters:
    - connection_string: MinIO endpoint URL (e.g. "minio:9000")
    - container_uuid: the uuid of the bucket (usually the user uuid)
    - create_container: a boolean value to specify if the bucket should be created if it doesnt exist (default is True)
    - tier: the tier of the bucket (default is user)
    - credentials: tuple of (access_key, secret_key) for MinIO

    Returns:
    - container_client: the container client object (MinIO client and bucket name)
    """
    try:
        # Parse MinIO connection information from connection string
        # Format expected: "endpoint:port:access_key:secret_key"
        # Or handle credentials separately if provided
        parts = connection_string.split(':')
        
        if len(parts) < 2:
            raise ConnectionStringError("Invalid MinIO connection string format")
            
        endpoint = parts[0] + ":" + parts[1]
        
        # If credentials are provided as a separate parameter (expected format: "access_key:secret_key")
        if credentials and isinstance(credentials, str):
            cred_parts = credentials.split(':')
            if len(cred_parts) == 2:
                access_key, secret_key = cred_parts
            else:
                raise ConnectionStringError("Invalid credentials format")
        # Otherwise try to get from connection string if it has enough parts
        elif len(parts) >= 4:
            access_key, secret_key = parts[2], parts[3]
        else:
            raise ConnectionStringError("No valid credentials provided")
            
        # Create MinIO client
        minio_client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False  # Set to True for HTTPS
        )
        
        if minio_client:
            bucket_name = build_container_name(str(container_uuid), tier)
            
            # Check if bucket exists
            bucket_exists = minio_client.bucket_exists(bucket_name)
            
            if bucket_exists:
                # Return both the client and bucket name as our "container client"
                return {"client": minio_client, "bucket": bucket_name}
            elif create_container and not bucket_exists:
                # Create the bucket
                minio_client.make_bucket(bucket_name)
                
                # Create general directory for new user bucket
                # In S3/MinIO, "directories" are just prefixes in object names
                # We simulate directory creation by creating a marker object
                response = await create_folder({"client": minio_client, "bucket": bucket_name}, "General")
                if response:
                    return {"client": minio_client, "bucket": bucket_name}
                else:
                    raise MountContainerError("Error creating general directory")
            elif not create_container and not bucket_exists:
                raise MountContainerError("Container does not exist")
        else:
            raise ConnectionStringError("Failed to create MinIO client")
    except MaxRetryError:
        raise ConnectionStringError("Could not connect to MinIO server")
    except S3Error as error:
        raise ConnectionStringError(f"MinIO S3 error: {error}")
    except ValueError as error:
        raise ConnectionStringError(
            "The given connection information is invalid: " + error.__str__()
        )
    except MountContainerError as error:
        raise error
    except ConnectionStringError as error:
        raise error
    except Exception as error:
        raise Exception("Unhandeled error:" + error.__str__())


async def get_blob(container_client, blob_name):
    """
    gets the contents of a specified object in the user's bucket
    
    Parameters:
    - container_client: dict with MinIO client and bucket name
    - blob_name: the name of the object to retrieve
    """
    try:
        response = container_client["client"].get_object(
            container_client["bucket"], 
            str(blob_name)
        )
        blob_content = response.read()
        response.close()
        response.release_conn()
        return blob_content
    except Exception as error:
        raise GetBlobError(str(error) + "\nError getting object:" + blob_name)


async def upload_image(
    container_client, folder_name, folder_uuid, image: bytes, image_uuid
):
    """
    uploads the image to the specified folder within the user's bucket,
    if the specified folder doesnt exist, it creates it with a uuid

    Parameters:
    - container_client: dict with MinIO client and bucket name
    - folder_name: the name of the destination folder
    - folder_uuid : uuid of the picture_set
    - image: image data as bytes
    - image_uuid: unique identifier for the image
    """
    try:
        if not await is_a_folder(container_client, folder_name):
            raise CreateDirectoryError(f"Folder:{folder_name} does not exist")
        else:
            blob_name = build_blob_name(str(folder_name), str(image_uuid))
            metadata = {
                "picture_uuid": f"{str(image_uuid)}",
                "picture_set_uuid": f"{str(folder_uuid)}",
            }
            
            # Upload to MinIO
            container_client["client"].put_object(
                container_client["bucket"],
                blob_name,
                data=image,
                length=len(image),
                metadata=metadata
            )
            
            return blob_name
    except CreateDirectoryError or UploadImageError as e:
        raise e
    except Exception as error:
        print(error)
        raise Exception("Datastore.blob.minio_api unHandled Error")


async def is_a_folder(container_client, folder_name):
    """
    This function checks if a folder exists in the bucket

    Parameters:
    - container_client: dict with MinIO client and bucket name
    - folder_name: the name of the folder to check

    Returns: True if the folder exists, False otherwise
    """
    try:
        directories = await get_directories(container_client)
        if str(folder_name) in directories:
            return True
        else:
            return False
    except FolderListError as e:
        print(e)
        raise FolderListError(
            "Error getting folder list, could not check if its a folder"
        )
    except Exception:
        raise Exception("Datastore.blob.minio_api : Unhandled Error")


async def create_folder(container_client, folder_uuid=None, folder_name=None):
    """
    creates a folder in the user's bucket

    Parameters:
    - container_client: dict with MinIO client and bucket name
    - folder_uuid: the uuid of the folder to be created
    - folder_name: the name of the folder to be created (usually it's uuid)
    """
    try:
        # We want to enable 2 types of folder creation
        if folder_uuid is None and folder_name is None:
            raise CreateDirectoryError("Folder name and uuid not provided")
        elif folder_uuid is None:
            raise CreateDirectoryError("Folder uuid not provided")
            
        # Until we allow user to manually create folder and name them
        if folder_name is None:
            folder_name = folder_uuid
            
        if not await is_a_folder(container_client, folder_name):
            folder_data = {
                "folder_name": folder_name,
                "date_created": str(
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ),
            }
            
            # Usually we create a folder named General after creating a container.
            # Those folder do not have a UUID and are used to store general data
            if folder_uuid is not None:
                folder_data["folder_uuid"] = str(folder_uuid)
                
            # Create folder metadata file
            file_name = build_blob_name(str(folder_name), str(folder_name), "json")
            
            # Upload to MinIO
            container_client["client"].put_object(
                container_client["bucket"],
                file_name,
                data=json.dumps(folder_data),
                length=len(json.dumps(folder_data)),
                metadata={"picture_set_uuid": f"{str(folder_uuid)}"}
            )
            
            return True
        else:
            raise CreateDirectoryError("Folder already exists")

    except CreateDirectoryError as error:
        raise error
    except FolderListError as error:
        print(error)
        raise CreateDirectoryError("Error getting folder list, could not create folder")
    except Exception as error:
        print(error)
        raise Exception("Datastore unHandled Error")


async def create_dev_container_folder(
    dev_container_client, folder_uuid=None, folder_name=None, user_id=None
):
    """
    creates a folder in the dev user's bucket, this is used to archive data

    Parameters:
    - dev_container_client: dict with MinIO client and bucket name for dev user
    - folder_uuid: the uuid of the folder to be created
    - folder_name: the name of the folder to be created (usually it's uuid)
    - user_id : the user id of the user archiving a folder
    """
    try:
        # We want to enable 2 types of folder creation
        if folder_uuid is None and folder_name is None:
            raise CreateDirectoryError("Folder name and uuid not provided")
        elif folder_uuid is None:
            raise CreateDirectoryError("Folder uuid not provided")
        if user_id is None:
            raise CreateDirectoryError("User id not provided")
            
        # Until we allow user to manually create folder and name them
        if folder_name is None:
            folder_name = folder_uuid
            
        if not await is_a_folder(
            dev_container_client, "{}/{}".format(user_id, folder_name)
        ):
            folder_data = {
                "folder_name": "{}/{}".format(user_id, folder_name),
                "date_created": str(
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ),
            }
            
            # Usually we create a folder named General after creating a container.
            # Those folder do not have a UUID and are used to store general data
            if folder_uuid is not None:
                folder_data["folder_uuid"] = str(folder_uuid)
                
            file_name = build_blob_name(
                "{}/{}".format(str(user_id), str(folder_name)), str(folder_name), "json"
            )
            
            # Upload to MinIO
            dev_container_client["client"].put_object(
                dev_container_client["bucket"],
                file_name,
                data=json.dumps(folder_data),
                length=len(json.dumps(folder_data)),
                metadata={"picture_set_uuid": f"{str(folder_uuid)}"}
            )
            
            return True
        else:
            raise CreateDirectoryError("Folder already exists")

    except CreateDirectoryError as error:
        raise error
    except FolderListError as error:
        print(error)
        raise CreateDirectoryError("Error getting folder list, could not create folder")
    except Exception as error:
        print(error)
        raise Exception("Datastore unHandled Error")


async def upload_inference_result(container_client, folder_name, result, hash_value):
    """
    uploads the inference results json file to the specified folder
    in the users bucket
    
    Parameters:
    - container_client: dict with MinIO client and bucket name
    - folder_name: folder to upload to
    - result: JSON result to upload
    - hash_value: hash to use for the filename
    """
    try:
        folder_uuid = await get_folder_uuid(container_client, folder_name)
        if folder_uuid:
            json_name = build_blob_name(str(folder_name), hash_value, "json")
            
            # Upload to MinIO
            container_client["client"].put_object(
                container_client["bucket"],
                json_name,
                data=result,
                length=len(result)
            )
            
            return True

    except UploadInferenceResultError as error:
        print(error)
        return False


async def get_folder_uuid(container_client, folder_name):
    """
    gets the uuid of a folder in the user's bucket given the folder name by
    iterating through the folder json files and extracting the name
    to match given folder name
    
    Parameters:
    - container_client: dict with MinIO client and bucket name
    - folder_name: name of the folder to get UUID for
    """
    try:
        # List all objects in the bucket
        objects = container_client["client"].list_objects(
            container_client["bucket"],
            recursive=True
        )
        
        for obj in objects:
            # Check if it's a folder metadata JSON file
            if (
                obj.object_name.split(".")[-1] == "json"
                and obj.object_name.count("/") == 1
                and obj.object_name.split("/")[0] == obj.object_name.split("/")[1].split(".")[0]
            ):
                folder_json = await get_blob(container_client, obj.object_name)

                if folder_json:
                    folder_json = json.loads(folder_json)

                    if folder_json["folder_name"] == folder_name:
                        if "folder_uuid" not in folder_json:
                            raise GetFolderUUIDError(
                                "Folder UUID not found in folder metadata"
                            )
                        return folder_json["folder_uuid"]
                        
        raise GetFolderUUIDError(f"Folder '{folder_name}' not found")
    except GetFolderUUIDError as error:
        raise error
    except Exception as error:
        print(error)
        raise Exception("Datastore.blob.minio_api unHandled Error")


async def get_image_count(container_client, folder_name):
    """
    gets the number of images in a folder in the user's bucket
    
    Parameters:
    - container_client: dict with MinIO client and bucket name
    - folder_name: name of the folder to count images in
    """
    try:
        folder_uuid = await get_folder_uuid(container_client, folder_name)
        if folder_uuid:
            # List all objects with the folder prefix
            objects = container_client["client"].list_objects(
                container_client["bucket"],
                prefix=folder_name + "/",
                recursive=True
            )
            
            count = 0
            for obj in objects:
                # Count only non-JSON files as images
                if (obj.object_name.split("/")[0] == folder_name) and (
                    obj.object_name.split(".")[-1] != "json"
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
    returns a list of folder names in the user's bucket
    
    Parameters:
    - container_client: dict with MinIO client and bucket name
    """
    try:
        directories = {}
        
        # List all objects in the bucket
        objects = container_client["client"].list_objects(
            container_client["bucket"],
            recursive=True
        )
        
        # Extract folder information from JSON metadata files
        for obj in objects:
            if (
                obj.object_name.split(".")[-1] == "json"
                and obj.object_name.count("/") == 1
                and obj.object_name.split("/")[0] == obj.object_name.split("/")[1].split(".")[0]
            ):
                json_blob = await get_blob(container_client, obj.object_name)
                if json_blob:
                    folder_json = json.loads(json_blob)
                    image_count = await get_image_count(
                        container_client, folder_json["folder_name"]
                    )
                    directories[folder_json["folder_name"]] = image_count
                    
        return directories
    except FolderListError as error:
        raise error
    except Exception as error:
        print(error)
        raise FolderListError(f"Error getting directories: {str(error)}")


async def download_container(container_client, container_name, local_dir):
    """
    This function downloads all the files from a bucket to the local directory
    
    Parameters:
    - container_client: dict with MinIO client and bucket name
    - container_name: name of the bucket to download
    - local_dir: the local directory to download the files to
    """
    try:
        # List objects in the bucket
        objects = container_client["client"].list_objects(
            container_client["bucket"],
            recursive=True
        )
        
        # Iterate through each object
        for i, obj in enumerate(objects):
            # Create local file path
            local_file_path = build_blob_name(str(local_dir), str(obj.object_name))
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            
            # Download the object
            container_client["client"].fget_object(
                container_client["bucket"], 
                obj.object_name, 
                local_file_path
            )
    except Exception:
        raise Exception("Error downloading container")


async def get_blobs_from_tag(container_client, tag: str):
    """
    This function gets the names of objects in a picture set folder
    
    Parameters:
    - container_client: dict with MinIO client and bucket name
    - tag: the tag to search for in the objects (picture_set_uuid)
    
    Returns: the list of matching objects
    """
    try:
        # List all objects in the bucket
        objects = container_client["client"].list_objects(
            container_client["bucket"],
            recursive=True
        )
        
        result = []
        for obj in objects:
            # Get object metadata
            stat = container_client["client"].stat_object(
                container_client["bucket"], 
                obj.object_name
            )
            
            # Check if it has the requested tag
            if (
                stat.metadata
                and "X-Amz-Meta-Picture_set_uuid" in stat.metadata
                and stat.metadata["X-Amz-Meta-Picture_set_uuid"] == tag
            ):
                result.append(obj)
                
        if len(result) > 0:
            return result
        else:
            raise GetBlobError("No objects found with the given tag")
    except Exception as e:
        print(f"Exception during get_blobs_from_tag: {e}")
        raise GetBlobError(f"Error getting objects: {str(e)}")


async def delete_folder(container_client, picture_set_id):
    """
    This function deletes a folder in the user's bucket
    
    Parameters:
    - container_client: dict with MinIO client and bucket name
    - picture_set_id: id of the picture set related to the folder to delete
    
    Returns: True if the folder is deleted, False otherwise
    """
    try:
        # Get all objects with the specified tag
        blobs = await get_blobs_from_tag(container_client, picture_set_id)
        
        # Delete each object
        for blob in blobs:
            container_client["client"].remove_object(
                container_client["bucket"], 
                blob.object_name
            )
            
        return True

    except GetFolderUUIDError:
        return False
    except Exception:
        return False


async def move_blob(
    blob_name_source,
    blob_name_dest,
    folder_uuid,
    container_client_source,
    container_client_destination,
):
    """
    This function moves a blob from one bucket to another
    
    Parameters:
    - blob_name_source: the name of the object to move
    - blob_name_dest: the destination name of the object
    - folder_uuid: the folder UUID to tag the object with
    - container_client_source: source dict with MinIO client and bucket name
    - container_client_destination: destination dict with MinIO client and bucket name
    """
    try:
        # Get the object from source
        response = container_client_source["client"].get_object(
            container_client_source["bucket"], 
            blob_name_source
        )
        blob = response.read()
        response.close()
        response.release_conn()
        
        # Upload to destination
        container_client_destination["client"].put_object(
            container_client_destination["bucket"],
            blob_name_dest,
            data=blob,
            length=len(blob),
            metadata={"picture_set_uuid": f"{str(folder_uuid)}"}
        )
        
        # Delete from source
        container_client_source["client"].remove_object(
            container_client_source["bucket"], 
            blob_name_source
        )
        
        return True
    except Exception as e:
        raise Exception(f"Error moving blob: {e}") 