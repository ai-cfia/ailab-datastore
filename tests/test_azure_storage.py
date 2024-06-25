import io
import uuid
import unittest
import asyncio
from unittest.mock import Mock
from PIL import Image
import datastore.blob.__init__ as blob
import os
from datastore.blob.azure_storage_api import (
    MountContainerError,
    ConnectionStringError,
    GetBlobError,
    CreateDirectoryError,
    FolderListError,
    GenerateHashError,
    GetFolderUUIDError,
    generate_hash,
    get_blob,
    upload_image,
    mount_container,
    is_a_folder,
    create_folder,
    get_folder_uuid,
    get_blobs_from_tag,
    get_directories
)

class TestMountContainerFunction(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.account_name = os.environ.get("NACHET_BLOB_ACCOUNT")
        self.account_key = os.environ.get("NACHET_BLOB_KEY")
        self.credential= blob.get_account_sas(self.account_name, self.account_key)
        self.tier="testuser"
        self.container_uuid=str(uuid.uuid4())
    
    def test_mount_existing_container(self):

        container_client = asyncio.run(
            mount_container(self.storage_url, self.container_uuid,True,self.tier)
        )

        self.assertTrue(container_client.exists())
        container_client.delete_container()

    def test_mount_nonexisting_container_create(self):
        """
        tests when a container does not exists and create_container flag is set to True,
        should create a new container and return the container client
        """
        not_uuid="notuuid"
        container_client = asyncio.run(
            mount_container(self.storage_url, not_uuid,True,self.tier,self.credential)
        )

        self.assertTrue(container_client.exists())
        container_client.delete_container()

    def test_mount_nonexisting_container_no_create(self):
        not_uuid="alsonotuuid"
        with self.assertRaises(MountContainerError):
            asyncio.run(
                mount_container(self.storage_url, not_uuid,False,self.tier,self.credential)
            )
        
    def test_mount_container_connection_string_error(self):
        with self.assertRaises(ConnectionStringError):
            asyncio.run(
                mount_container("invalid-url", self.container_uuid,True,self.tier)
            )
    


class TestGetBlob(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid=str(uuid.uuid4())
        self.container_name=f"{self.tier}-{self.container_uuid}"
        self.blob_service_client = blob.create_BlobServiceClient(self.storage_url)
        self.container_client = self.blob_service_client.create_container(self.container_name)
        self.blob_name = "test_blob"
        self.blob= "test_blob_content"
        self.container_client.upload_blob(name=self.blob_name, data=self.blob)
    
    def tearDown(self):
        self.container_client.delete_container()
    
    def test_get_blob(self):
        self.assertTrue(self.container_client.exists())
        result = asyncio.run(
            get_blob(self.container_client, self.blob_name)
        )

        self.assertEqual(str(result.decode()), self.blob)

    def test_get_blob_error(self):
        blob = "nonexisting_blob"
        mock_blob_client = Mock()
        mock_blob_client.download_blob.side_effect = GetBlobError("Resource not found")

        mock_container_client = Mock()
        mock_container_client.get_blob_client.return_value = mock_blob_client

        with self.assertRaises(GetBlobError):
            asyncio.run(get_blob(mock_container_client, blob))


class TestUploadImage(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid=str(uuid.uuid4())
        self.container_name=f"{self.tier}-{self.container_uuid}"
        self.blob_service_client = blob.create_BlobServiceClient(self.storage_url)
        self.container_client = self.blob_service_client.create_container(self.container_name)
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.image_byte = self.image.tobytes()
        self.image_hash = asyncio.run(generate_hash(self.image_byte))
        self.image_uuid = str(uuid.uuid4())
        #self.container_client.upload_blob(name=self.blob_name, data=self.blob)
        self.folder_name="test_folder"
        asyncio.run(create_folder(self.container_client, self.folder_name))
    
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
        with self.assertRaises(CreateDirectoryError):
            asyncio.run(
                upload_image(self.container_client, not_folder_name,self.image_hash,self.image_uuid)
            )

class TestIsAFolder(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid=str(uuid.uuid4())
        self.container_name=f"{self.tier}-{self.container_uuid}"
        self.blob_service_client = blob.create_BlobServiceClient(self.storage_url)
        self.container_client = self.blob_service_client.create_container(self.container_name)
        self.folder_name="test_folder"
        asyncio.run(create_folder(self.container_client, self.folder_name))
    
    def tearDown(self):
        self.container_client.delete_container()
    
    def test_is_a_folder(self):
        self.assertTrue(self.container_client.exists())
        result = asyncio.run(is_a_folder(self.container_client, self.folder_name))
        self.assertTrue(result)

    def test_is_not_a_folder(self):
        self.assertTrue(self.container_client.exists())
        not_folder_name="not_folder"
        result = asyncio.run(is_a_folder(self.container_client, not_folder_name))
        self.assertFalse(result)
        
class TestCreateFolder(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid=str(uuid.uuid4())
        self.container_name=f"{self.tier}-{self.container_uuid}"
        self.blob_service_client = blob.create_BlobServiceClient(self.storage_url)
        self.container_client = self.blob_service_client.create_container(self.container_name)
    
    def tearDown(self):
        self.container_client.delete_container()
    
    def test_create_folder(self):
        folder_name="test_folder"
        result =  asyncio.run(create_folder(self.container_client, folder_name))
        self.assertTrue(result)

    def test_create_existing_folder(self):
        folder_name="test_folder"
        asyncio.run(create_folder(self.container_client, folder_name))
        with self.assertRaises(CreateDirectoryError):
            asyncio.run(create_folder(self.container_client, folder_name))
        

    def test_create_folder_error(self):
        folder_name="tessst_folder"
        mock_container_client = Mock()
        mock_container_client.list_blobs.side_effect = FolderListError("Resource not found")
        with self.assertRaises(CreateDirectoryError):
            asyncio.run(create_folder(mock_container_client, folder_name))
            
class TestGenerateHash(unittest.TestCase):
    def setUp(self):
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.image_byte = self.image.tobytes()

    def test_generate_hash(self):
        result = asyncio.run(generate_hash(self.image_byte))
        self.assertEqual(len(result), 64)

    def test_generate_hash_error(self):
        with self.assertRaises(GenerateHashError):
            asyncio.run(generate_hash("not an image"))
            
class TestGetFolderUUID(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid=str(uuid.uuid4())
        self.container_name=f"{self.tier}-{self.container_uuid}"
        self.blob_service_client = blob.create_BlobServiceClient(self.storage_url)
        self.container_client = self.blob_service_client.create_container(self.container_name)
        self.folder_name="test_folder"
        self.folder_uuid= str(uuid.uuid4())
        asyncio.run(create_folder(self.container_client,self.folder_uuid, self.folder_name))
    
    def tearDown(self):
        self.container_client.delete_container()
    0
    def test_get_folder_uuid(self):
        result = asyncio.run(get_folder_uuid(self.container_client,self.folder_name))
        self.assertEqual(result, self.folder_uuid)

    def test_get_folder_uuid_error(self):
        not_folder_name="not_folder"
        with self.assertRaises(GetFolderUUIDError):
            asyncio.run(get_folder_uuid(self.container_client,not_folder_name))

class TestGetBlobsFromTag(unittest.TestCase) :
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid=str(uuid.uuid4())
        self.container_name=f"{self.tier}-{self.container_uuid}"
        self.blob_service_client = blob.create_BlobServiceClient(self.storage_url)
        self.container_client = self.blob_service_client.create_container(self.container_name)
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.image_byte = self.image.tobytes()
        self.image_hash = asyncio.run(generate_hash(self.image_byte))
        self.image_uuid = str(uuid.uuid4())
        self.folder_name="test_folder"
        self.folder_uuid= str(uuid.uuid4())
        asyncio.run(create_folder(self.container_client,self.folder_uuid, self.folder_name))
        asyncio.run(upload_image(self.container_client, self.folder_name,self.image_hash,self.image_uuid))
        
    def tearDown(self):
        self.container_client.delete_container()

    def test_get_blobs_from_tag(self):
        tag = 'test_folder'
        try:
            result = asyncio.run(get_blobs_from_tag(self.container_client, tag))
            self.assertGreater(len(result), 0)
        except Exception as e:
            print(f"Test failed with exception: {e}")

    def test_get_blobs_from_tag_error(self):
        tag = "wrong_tag"
        with self.assertRaises(Exception):
            asyncio.run(get_blobs_from_tag(self.container_client, tag))
            
    

class TestGetDirectories(unittest.TestCase) :
    def setUp(self) :
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.tier="testuser"
        self.container_uuid=str(uuid.uuid4())
        self.container_name=f"{self.tier}-{self.container_uuid}"
        self.blob_service_client = blob.create_BlobServiceClient(self.storage_url)
        self.container_client = self.blob_service_client.create_container(self.container_name)
        self.folder_name="test_folder"
        self.folder_uuid= str(uuid.uuid4())
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.image_byte = self.image.tobytes()
        self.image_hash = asyncio.run(generate_hash(self.image_byte))
        self.image_uuid = str(uuid.uuid4())
        asyncio.run(create_folder(self.container_client,self.folder_uuid, self.folder_name))
        
    def tearDown(self):
        self.container_client.delete_container()
    
    def test_get_directories(self) :
        try:
            result = asyncio.run(get_directories(self.container_client))
            self.assertEqual(len(result), 1)
            self.assertEqual(result.get(self.folder_name), 0)
            
            asyncio.run(upload_image(self.container_client, self.folder_name,self.image_hash,self.image_uuid))
            
            result = asyncio.run(get_directories(self.container_client))
            self.assertEqual(len(result), 1)
            self.assertEqual(result.get(self.folder_name), 1)
        except Exception as e:
            print(f"Test failed with exception: {e}")
            
    def test_get_directories_error(self):
        mock_container_client = Mock()
        mock_container_client.list_blobs.side_effect = FolderListError("Resource not found")
        with self.assertRaises(FolderListError):
            asyncio.run(get_directories(mock_container_client))
        
    
if __name__ == "__main__":
    unittest.main()
