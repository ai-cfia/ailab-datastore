from azure.storage.blob import (
    BlobServiceClient,
    generate_account_sas,
    ResourceTypes,
    AccountSasPermissions,
)
from datetime import timedelta, datetime
import os


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


def create_container_client(blob_service_client, container_name):
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


def get_account_sas(account_name: str, key: str):
    """
    This function returns the account sas token

    Parameters:
    - name: the name of the storage account
    - key: the key of the storage account

    Returns: str
    """
    # Get the account sas token
    account_sas = generate_account_sas(
        account_name=account_name,
        account_key=key,
        resource_types=ResourceTypes(service=True, container=True, object=True),
        permission=AccountSasPermissions(
            read=True,
            write=True,
            delete=True,
            list=True,
            add=True,
            create=True,
            update=True,
            tag=True,
            filter_by_tag=True,
        ),
        expiry=datetime.now() + timedelta(minutes=5),
    )
    return account_sas
