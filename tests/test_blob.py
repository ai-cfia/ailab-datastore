import asyncio
import os
import unittest
import uuid

from azure.storage.blob import BlobServiceClient

import datastore.blob.__init__ as blob
from datastore.blob.__init__ import ConnectionStringError

BLOB_CONNECTION_STRING = os.environ["NACHET_STORAGE_URL_TESTING"]
if BLOB_CONNECTION_STRING is None or BLOB_CONNECTION_STRING == "":
    raise ValueError("NACHET_STORAGE_URL_TESTING is not set")


class TestGetBlobServiceClient(unittest.TestCase):
    def setUp(self):
        self.storage_url = BLOB_CONNECTION_STRING

    def test_create_BlobServiceClient(self):
        result = blob.create_BlobServiceClient(self.storage_url)

        self.assertGreater(len(result.api_version), 0)

    def test_get_blob_service_unsuccessful(self):
        with self.assertRaises(ConnectionStringError):
            asyncio.run(blob.create_BlobServiceClient("invalid_connection_string"))


class TestCreateContainerClient(unittest.TestCase):
    def setUp(self):
        self.storage_url = BLOB_CONNECTION_STRING
        self.container_name = "test-" + str(uuid.uuid4())
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.storage_url
        )

    def tearDown(self):
        self.blob_service_client.delete_container(self.container_name)

    def test_create_container_client(self):
        result = blob.create_container_client(
            self.blob_service_client, self.container_name
        )
        self.assertTrue(result.exists())
        self.assertGreater(len(result.container_name), 0)
