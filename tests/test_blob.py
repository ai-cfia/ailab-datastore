import os
import unittest
import asyncio
from unittest.mock import patch, Mock, MagicMock
from azure.storage.blob import BlobServiceClient
import datastore.blob.__init__ as blob
from azure.core.exceptions import ResourceNotFoundError

class TestGetBlobServiceClient(unittest.TestCase):
    def setUp(self):
        self.storage_url = os.environ.get("NACHET_STORAGE_URL")
        
    def test_create_BlobServiceClient(self, MockFromConnectionString):

        result = asyncio.run(
            blob.create_BlobServiceClient(self.storage_url)
        )
  
        self.assertGreater(len(result.api_version), 0)

    @patch("azure.storage.blob.BlobServiceClient.from_connection_string")
    def test_get_blob_service_unsuccessful(self, MockFromConnectionString):
        MockFromConnectionString.return_value = None

        with self.assertRaises(ConnectionStringError) as context:
            asyncio.run(get_blob_client("invalid_connection_string"))

        print(context.exception == "the given connection string is invalid: invalid_connection_string")
