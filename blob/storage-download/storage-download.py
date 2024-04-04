"""
This script downloads all the files from a container in a storage account
to a specified local directory


Parameters:
- storage_url: the url of the storage account
- container_name: the name of the container
- local_dir: the local directory to download the files to

"""

import os
import sys
from azure.storage.blob import BlobServiceClient

def create_BlobServiceClient(storage_url):
    """
    This function creates a BlobServiceClient object

    Parameters:
    - storage_url: the url of the storage account

    Returns: BlobServiceClient object
    """
    # Create a blob service client
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=storage_url)
    return blob_service_client

def create_container_client(blob_service_client,container_name):
    """
    This function creates a container client object

    Parameters:
    - blob_service_client: the BlobServiceClient object
    - container_name: the name of the container

    Returns: ContainerClient object
    """
    # Get the container client
    container_client = blob_service_client.get_container_client(container_name)
    return container_client

def download_container(container_client,container_name,local_dir):
    """
    This function downloads all the files from a container in a storage account
    to the local directory "test"

    This serves as a way to locally download the container files for processing and importing within the db

    Parameters:
    - container_client: the Azure container client 
    - local_dir: the local directory to download the files to

    Returns: None
    """
    # List blobs in the container
    blob_list = container_client.list_blobs()
    # Iterate through each blob
    for i,blob in enumerate(blob_list):
        # Create a blob client
        blob_client = container_client.get_blob_client(
            container=container_name, blob=blob
        )
>>>>>>> c4eb497 (Fixes #2: Formatting):db/setup/storage-download.py
        # Download the blob
        local_file_path = f"{local_dir}/{blob.name}"
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        with open(local_file_path, "wb") as file:
            blob_data = container_client.download_blob(blob=blob.name)
            blob_data.readinto(file)
            nb_downloaded_files=i

    print("downloaded : " + str(nb_downloaded_files) + "/" + str(len(blob_list)))

if __name__ == "__main__":
    storage_url = sys.argv[1]
    container_name = sys.argv[2]
    local_dir = sys.argv[3]

    # Create a blob service client
    blob_service_client = create_BlobServiceClient(storage_url)
    # Create a container client
    container_client = create_container_client(blob_service_client,container_name)
    # Download the container
    download_container(container_client,container_name,local_dir)