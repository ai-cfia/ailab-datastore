import os
from azure.storage.blob import BlobServiceClient


def folderProcessing(storage_url, container_name):
    """
    This function downloads all the files from a container in a storage account
    to the local directory "test"

    This serves as a way to locally download the container files for processing and importing within the db

    Parameters:
    - storage_url: the url of the storage account
    - container_name: the name of the container

    Returns: None
    """

    # Create a blob service client
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=storage_url)

    # # Get the container client
    container_client = blob_service_client.get_container_client(container_name)
    if container_client.exists():
        print("Container exists")
    else:
        print("Container does not exist")
    # print("===============================================")
    # print(container_name)
    # Specify the local directory
    local_dir = "test"

    # List blobs in the container
    blob_list = container_client.list_blobs()
    i = 0
    # Iterate through each blob
    for blob in blob_list:
        # Create a blob client
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob.name
        )
        # Download the blob
        local_file_path = f"{local_dir}/{blob.name}"
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        with open(local_file_path, "wb") as file:
            blob_data = blob_client.download_blob()
            # blob_data = container_client.download_blob(blob=blob.name)
            blob_data.readinto(file)
            i = i + 1

    print("downloaded : " + str(i) + "/" + str(len(blob_list)))
