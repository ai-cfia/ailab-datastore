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