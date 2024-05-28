import json
import unittest
import asyncio
from unittest.mock import patch, Mock, MagicMock
from azure.storage.blob import BlobServiceClient
from PIL import Image
import datastore.blob.__init__ as blob
import os
from datastore.blob.azure_storage_api import (
    MountContainerError,
    ConnectionStringError,
    GetBlobError,
    CreateDirectoryError,
    generate_hash,
    get_blob,
    upload_image,
    mount_container,
    is_a_folder,
    create_folder,
    get_folder_uuid
)
from azure.core.exceptions import ResourceNotFoundError

class TestMountContainerFunction(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid="uuid"

    def tearDown(self):
        self.container_client.delete_container()
    
    def test_mount_existing_container(self):

        result = asyncio.run(
            mount_container(self.storage_url, self.container_uuid,False,self.tier)
        )

        self.assertTrue(result.exists())

    def test_mount_nonexisting_container_create(self):
        """
        tests when a container does not exists and create_container flag is set to True,
        should create a new container and return the container client
        """
        not_uuid="not_uuid"
        result = asyncio.run(
            mount_container(self.storage_url, not_uuid,True,self.tier)
        )

        self.assertTrue(result.exists())

    def test_mount_nonexisting_container_no_create(self):
        not_uuid="not_uuid"
        with self.assertRaises(MountContainerError):
            asyncio.run(
                mount_container(self.storage_url, not_uuid,False,self.tier)
            )
        
    def test_mount_container_connection_string_error(self):
        with self.assertRaises(ConnectionStringError):
            asyncio.run(
                mount_container("invalid_url", self.container_uuid,True,self.tier)
            )
    


class TestGetBlob(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid="uuid"
        self.container_name=f"{self.tier}-{self.container_uuid}"
        self.container_client = blob.create_container_client(self.blob_service_client, self.container_name)
        self.blob_service_client = blob.create_BlobServiceClient(self.storage_url)
        self.blob_name = "test_blob"
        self.blob= "test_blob_content"
        self.container_client.upload_blob(name=self.blob_name, data=self.blob)
    
    def tearDown(self):
        self.container_client.delete_container()
    
    def test_get_blob(self):

        result = asyncio.run(
            get_blob(self.container_client, self.blob_name)
        )

        self.assertEqual(result, self.blob)

    def test_get_blob_error(self):
        blob = "nonexisting_blob"
        mock_blob_client = Mock()
        mock_blob_client.download_blob.side_effect = ResourceNotFoundError("Resource not found")

        mock_container_client = Mock()
        mock_container_client.get_blob_client.return_value = mock_blob_client

        with self.assertRaises(GetBlobError) as context:
            asyncio.run(get_blob(mock_container_client, blob))
        print(str(context.exception) == f"the specified blob: {blob} cannot be found")


class TestUploadImage(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid="uuid"
        self.container_name=f"{self.tier}-{self.container_uuid}"
        self.container_client = blob.create_container_client(self.blob_service_client, self.container_name)
        self.blob_service_client = blob.create_BlobServiceClient(self.storage_url)
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_uuid="image_uuid"
        self.image_hash=generate_hash(self.image)
        self.container_client.upload_blob(name=self.blob_name, data=self.blob)
        self.folder_name="test_folder"
        create_folder(self.container_client, self.folder_name)
    
    def tearDown(self):
        self.container_client.delete_container()
    
    def test_upload_image(self):
        expected_result = "{}/{}.png".format(self.folder_name, self.image_uuid)
        result = asyncio.run(
            upload_image(self.container_client, self.folder_name,self.image_hash,self.image_uuid)
        )

        self.assertEqual(result, expected_result)

    def test_upload_image_wrong_folder(self):
        """
        This test checkes if the function raises an error when the folder does not exist
        """
        not_folder_name="not_folder"
        with self.assertRaises(GetBlobError):
            asyncio.run(
                upload_image(self.container_client, not_folder_name,self.image_hash,self.image_uuid)
            )

class TestIsAFolder(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid="uuid"
        self.container_name=f"{self.tier}-{self.container_uuid}"
        self.container_client = blob.create_container_client(self.blob_service_client, self.container_name)
        self.blob_service_client = blob.create_BlobServiceClient(self.storage_url)
        self.folder_name="test_folder"
        create_folder(self.container_client, self.folder_name)
    
    def tearDown(self):
        self.container_client.delete_container()
    
    def test_is_a_folder(self):
        result = is_a_folder(self.container_client, self.folder_name)
        self.assertTrue(result)

    def test_is_not_a_folder(self):
        not_folder_name="not_folder"
        result = is_a_folder(self.container_client, not_folder_name)
        self.assertFalse(result)
        
class TestCreateFolder(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid="uuid"
        self.container_name=f"{self.tier}-{self.container_uuid}"
        self.container_client = blob.create_container_client(self.blob_service_client, self.container_name)
        self.blob_service_client = blob.create_BlobServiceClient(self.storage_url)
    
    def tearDown(self):
        self.container_client.delete_container()
    
    def test_create_folder(self):
        folder_name="test_folder"
        result = create_folder(self.container_client, folder_name)
        self.assertTrue(result)

    def test_create_existing_folder(self):
        folder_name="test_folder"
        create_folder(self.container_client, folder_name)
        with self.assertRaises(CreateDirectoryError):
            result = create_folder(self.container_client, folder_name)
        

    def test_create_folder_error(self):
        folder_name="test_folder"
        mock_container_client = Mock()
        mock_container_client.get_blob_client.side_effect = ResourceNotFoundError("Resource not found")
        with self.assertRaises(GetBlobError):
            create_folder(mock_container_client, folder_name)
            
class TestGenerateHash(unittest.TestCase):
    def setUp(self):
        self.image = Image.new("RGB", (1980, 1080), "blue")
    
    def test_generate_hash(self):
        result = generate_hash(self.image)
        self.assertEqual(len(result), 64)

    def test_generate_hash_error(self):
        with self.assertRaises(TypeError):
            generate_hash("not an image")
            
class TestGetFolderUUID(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid="uuid"
        self.container_name=f"{self.tier}-{self.container_uuid}"
        self.container_client = blob.create_container_client(self.blob_service_client, self.container_name)
        self.blob_service_client = blob.create_BlobServiceClient(self.storage_url)
        self.folder_name="test_folder"
        create_folder(self.container_client, self.folder_name)
    
    def tearDown(self):
        self.container_client.delete_container()
    
    def test_get_folder_uuid(self):
        result = get_folder_uuid(self.folder_name)
        self.assertEqual(result, self.folder_name)

    def test_get_folder_uuid_error(self):
        not_folder_name="not_folder"
        with self.assertRaises(ValueError):
            get_folder_uuid(not_folder_name)

if __name__ == "__main__":
    unittest.main()