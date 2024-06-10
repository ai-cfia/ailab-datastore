import os
import unittest
import asyncio
import uuid
from azure.storage.blob import BlobServiceClient
import datastore.blob.__init__ as blob
from azure.core.exceptions import ResourceNotFoundError
from datastore.blob.__init__ import ConnectionStringError

class TestGetBlobServiceClient(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        
    def test_create_BlobServiceClient(self):

        result = blob.create_BlobServiceClient(self.storage_url)
  
        self.assertGreater(len(result.api_version), 0)

    def test_get_blob_service_unsuccessful(self):

        with self.assertRaises(ConnectionStringError):
            asyncio.run(blob.create_BlobServiceClient("invalid_connection_string"))


class TestCreateContainerClient(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        self.container_name = str(uuid.uuid4())
        self.blob_service_client = BlobServiceClient.from_connection_string(self.storage_url)
        
    def test_create_container_client(self):

        result = blob.create_container_client(self.blob_service_client, self.container_name)
        self.assertTrue(result.exists())
        self.assertGreater(len(result.container_name), 0)