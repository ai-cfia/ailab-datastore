import unittest
from unittest.mock import patch, MagicMock
import datastore.bin.upload_picture_set as upload_picture_set
import datastore.db as db
import datastore.db.queries.user as user
import datastore.db.queries.seed as seed
import datastore.db.queries.picture as picture_query
from datastore.blob import azure_storage_api
import asyncio
import json
from PIL import Image
import base64
import uuid
import io

class test_upload_picture_set(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db()
        self.cursor = db.cursor(self.con)
        db.create_search_path(self.con,self.cursor)
        
        self.email = "test@email"
        self.user_id = user.register_user(self.cursor, self.email)
    
        self.seed_name = "test_seed"
        self.seed_id = seed.new_seed(self.cursor, self.seed_name)

        self.image = Image.new('RGB', (1980, 1080),'blue')
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format='TIFF')
        self.pic_encoded = base64.b64encode(self.image_byte_array.getvalue()).decode("utf8")
        
        self.pictures=[self.pic_encoded, self.pic_encoded]
        
        self.connection_string = "www.test.com"
        
        self.blob_list=""
        # user.link_container(self.cursor, self.user_id, self.connection_string)
        
        # mock the client container and blob service client
        self.mock_container_client = MagicMock()
        self.mock_container_client.exists.return_value = True
        self.mock_container_client.url = self.connection_string
    
        
        
    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)
        
    @patch("azure.storage.blob.ContainerClient.upload_blob")
    @patch("datastore.bin.upload_picture_set.blob.create_folder")
    @patch("datastore.bin.upload_picture_set.blob.upload_image")
    def test_upload_picture_set(self,MockUploadBlob,MockCreateFolder,MockUploadImage):
        """
        This test checks if the upload_picture_set function runs without issue
        """
        #TODO: check if the pictures are uploaded in the blob storage
        MockCreateFolder.retun_value = True
        zoom_level = 1.0
        nb_seeds = 1
        picture_set_id = upload_picture_set.upload_picture_set(self.cursor, self.mock_container_client, self.pictures, self.user_id, self.seed_name, zoom_level, nb_seeds)
        self.assertTrue(True)
        self.assertTrue(picture_query.is_a_picture_set_id(self.cursor, picture_set_id))
        
        
    def test_non_existing_seed(self):
        """
        This test checks if the upload_picture_set function raises an exception when the seed does not exist
        """
        with self.assertRaises(seed.SeedNotFoundError):
            asyncio.run(upload_picture_set.upload_picture_set(self.cursor, self.mock_container_client, self.pictures, self.user_id, "non_existing_seed", 1.0, 1))

    def test_non_existing_user(self):
        """
        This test checks if the upload_picture_set function raises an exception when the user does not exist
        """
        with self.assertRaises(user.UserNotFoundError):
            asyncio.run(upload_picture_set.upload_picture_set(self.cursor, self.mock_container_client, self.pictures, uuid.uuid4(), self.seed_name, 1.0, 1))

    @patch("datastore.bin.upload_picture_set.blob.create_folder")
    @patch("azure.storage.blob.ContainerClient.upload_blob")
    def test_already_existing_folder(self,MockCreateFolder,MockUploadBlob):
        """
        This test checks if the upload_picture_set function raises an exception when the folder already exists
        """
        with self.assertRaises(upload_picture_set.AlreadyExistingFolderError):
            MockCreateFolder.retun_value = False
            zoom_level = 1.0
            nb_seeds = 1
            asyncio.run(upload_picture_set.upload_picture_set(self.cursor, self.mock_container_client, self.pictures, self.user_id, self.seed_name, zoom_level, nb_seeds))

    @patch("datastore.bin.upload_picture_set.picture_query.new_picture")
    @patch("azure.storage.blob.ContainerClient.upload_blob")
    def test_upload_picture_set_exception(self,MockNewPicture,MockUploadBlob):
        """
        This test checks if the upload_picture_set function raises an exception when an error occurs
        """
        MockNewPicture.side_effect = Exception("Connection Error")
        with self.assertRaises(upload_picture_set.UploadError):
            upload_picture_set.upload_picture_set(self.cursor, self.mock_container_client, self.pictures, self.user_id, self.seed_name, 1.0, 1)
if __name__ == "__main__":
    unittest.main()