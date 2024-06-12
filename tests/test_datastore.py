"""
This is a test script for the highest level of the datastore packages. 
It tests the functions in the __init__.py files of the datastore packages.
"""
import io
import os
import unittest
from unittest.mock import MagicMock, patch
from PIL import Image
import json
import asyncio
import datastore.db.__init__ as db
import datastore.db.queries.inference as inference_queries
import datastore.__init__ as datastore
import datastore.db.metadata.validator as validator


class test_ml_structure(unittest.TestCase):
    def setUp(self):
        with open("tests/ml_structure_exemple.json") as file:
            self.ml_dict= json.load(file)
        self.conn = db.connect_db()
        self.cursor = db.cursor(self.conn)
        db.create_search_path(self.conn, self.cursor)
        
    def tearDown(self):
        self.conn.rollback()
        db.end_query(self.conn, self.cursor)
        
        
    def test_import_ml_structure_from_json(self):
        """
        Test the import function.
        """
        asyncio.run(datastore.import_ml_structure_from_json_version(self.cursor,self.ml_dict))
        self.cursor.execute("SELECT id FROM model WHERE name='that_model_name'")
        model_id=self.cursor.fetchone()[0]
        self.assertTrue(validator.is_valid_uuid(str(model_id)))
        self.cursor.execute("SELECT id FROM pipeline WHERE name='Second Pipeline'")
        pipeline_id=self.cursor.fetchone()[0]
        self.assertTrue(validator.is_valid_uuid(str(pipeline_id)))
        self.cursor.execute("SELECT id FROM pipeline_model WHERE pipeline_id=%s AND model_id=%s",(pipeline_id,model_id,))
        self.assertTrue(validator.is_valid_uuid(self.cursor.fetchone()[0]))
        
    def test_get_ml_structure(self):
        """
        Test the get function.
        """
        
        #asyncio.run(datastore.import_ml_structure_from_json_version(self.cursor,self.ml_dict))
        ml_structure= asyncio.run(datastore.get_ml_structure(self.cursor))
        #self.assertDictEqual(ml_structure,self.ml_dict)
        for pipeline in self.ml_dict["pipelines"]:
            for key in pipeline:
                if key!='Accuracy':
                    self.assertTrue((key in ml_structure["pipelines"][0].keys()),f"Key {key} was not found and expected in the returned dictionary")
        for model in self.ml_dict["models"]:
            for key in model:
                if key!='Accuracy' and key !='endpoint_name':
                    #print(key)
                    self.assertTrue((key in ml_structure["models"][0].keys()),f"Key {key} was not found and expected in the returned dictionary")
        
    def test_get_ml_structure_eeror(self):
        """
        Test the get version function.
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        with self.assertRaises(datastore.MLRetrievalError):
            asyncio.run(datastore.get_ml_structure(mock_cursor))
        
class test_user(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect_db()
        self.cursor = db.cursor(self.conn)
        db.create_search_path(self.conn, self.cursor)
        self.user_email="test@email"
        self.user_id=None
        self.connection_str=os.environ["NACHET_STORAGE_URL"]

        
    def tearDown(self):
        self.conn.rollback()
        if self.user_id is not None:
            self.container_client=asyncio.run(datastore.get_user_container_client(self.user_id,'test-user'))
            self.container_client.delete_container()
        self.user_id=None
        db.end_query(self.conn, self.cursor)

    def test_new_user(self):
        """
        Test the new user function.
        """
        user_obj=asyncio.run(datastore.new_user(self.cursor,self.user_email,self.connection_str,'test-user'))
        self.assertIsInstance(user_obj,datastore.User)
        #self.user_id=user_obj.id
        self.user_id=datastore.User.get_id(user_obj)
        self.assertTrue(validator.is_valid_uuid(self.user_id))
        self.assertEqual(datastore.User.get_email(user_obj),self.user_email)
        
    def test_already_existing_user(self):
        """
        Test the already existing user function.
        """
        user_obj=asyncio.run(datastore.new_user(self.cursor,self.user_email,self.connection_str,'test-user'))
        self.user_id=datastore.User.get_id(user_obj)
        self.assertTrue(validator.is_valid_uuid(self.user_id))
        with self.assertRaises(datastore.UserAlreadyExistsError):
            asyncio.run(datastore.new_user(self.cursor,self.user_email,self.connection_str,'test-user'))
        
    @patch("azure.storage.blob.ContainerClient.exists")
    def test_new_user_container_error(self,MockExists):
        """
        Test the new user container error function.
        """
        MockExists.return_value=False
        with self.assertRaises(datastore.ContainerCreationError):
            asyncio.run(datastore.new_user(self.cursor,self.user_email,self.connection_str,'test-user'))

    @patch("datastore.blob.azure_storage_api.create_folder")
    def test_new_user_folder_error(self,MockCreateFolder):
        """
        Test the new user folder error function.
        """
        MockCreateFolder.side_effect= datastore.azure_storage.CreateDirectoryError("Test error")
        with self.assertRaises(datastore.FolderCreationError):
            asyncio.run(datastore.new_user(self.cursor,self.user_email,self.connection_str,'test-user'))

    def test_get_User(self):
        """
        Test the get User object function.
        """
        user_obj=asyncio.run(datastore.new_user(self.cursor,self.user_email,self.connection_str,'test-user'))
        user_id= datastore.User.get_id(user_obj)
        user_get=asyncio.run(datastore.get_user(self.cursor,self.user_email))
        user_get_id=datastore.User.get_id(user_get)
        self.assertEqual(user_id,user_get_id)
        self.assertEqual(datastore.User.get_email(user_obj),datastore.User.get_email(user_get))

    def test_get_user_container_client(self):
        """
        Test the get user container client function.
        """
        user_obj=asyncio.run(datastore.new_user(self.cursor,self.user_email,self.connection_str,'test-user'))
        user_id= datastore.User.get_id(user_obj)
        container_client=asyncio.run(datastore.get_user_container_client(user_id,'test-user'))
        self.assertTrue(container_client.exists())

class test_picture(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db()
        self.cur = db.cursor(self.con)
        db.create_search_path(self.con, self.cur)
        self.connection_str=os.environ["NACHET_STORAGE_URL"]
        self.user_email="test@email"
        self.user_obj= asyncio.run(datastore.new_user(self.cur,self.user_email,self.connection_str,'test-user'))
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = self.image.tobytes()
        #self.picture_hash= asyncio.run(azure_storage.generate_hash(self.pic_encoded))
        self.container_name='test-container'
        self.user_id=datastore.User.get_id(self.user_obj)
        self.container_client = asyncio.run(datastore.get_user_container_client(self.user_id,'test-user'))
        with open("tests/inference_result.json") as file:
            self.inference= json.load(file)
    
    def tearDown(self):
        self.con.rollback()
        self.container_client.delete_container()
        db.end_query(self.con, self.cur)

    def test_upload_picture(self):
        """
        Test the upload picture function.
        """
        picture_id = asyncio.run(datastore.upload_picture(self.cur, self.user_id, self.pic_encoded,self.container_client))
        self.assertTrue(validator.is_valid_uuid(picture_id))

    def test_register_inference_result(self):
        """
        Test the register inference result function.
        """
        picture_id = asyncio.run(datastore.upload_picture(self.cur, self.user_id, self.pic_encoded,self.container_client))
        model_id = "test_model_id"
        
        result = asyncio.run(datastore.register_inference_result(self.cur,self.user_id,self.inference, picture_id, model_id))
        #self.cur.execute("SELECT result FROM inference WHERE picture_id=%s AND model_id=%s",(picture_id,model_id,))
        self.assertTrue(validator.is_valid_uuid(result["inference_id"]))

class test_feedback(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db()
        self.cur = db.cursor(self.con)
        db.create_search_path(self.con, self.cur)
        self.connection_str=os.environ["NACHET_STORAGE_URL"]
        self.user_email="test@email"
        self.user_obj= asyncio.run(datastore.new_user(self.cur,self.user_email,self.connection_str,'test-user'))
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = self.image.tobytes()
        self.container_name='test-container'
        self.user_id=datastore.User.get_id(self.user_obj)
        self.container_client = asyncio.run(datastore.get_user_container_client(self.user_id,'test-user'))  
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'inference_result.json')
        with open(file_path) as file:
            self.inference= json.load(file)
        picture_id = asyncio.run(datastore.upload_picture(self.cur, self.user_id, self.pic_encoded,self.container_client))
        model_id = "test_model_id"
        self.registered_inference = asyncio.run(datastore.register_inference_result(self.cur,self.user_id,self.inference, picture_id, model_id))
        self.inference_id = self.registered_inference.get("inference_id")
        self.boxes_id = []
        self.top_id = []
        for box in self.inference["boxes"]:
            self.boxes_id.append(box["box_id"])
            self.top_id.append(box["top_id"])
            
    def test_new_perfect_inference_feeback(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly updates the inference object after a perfect feedback is given
        """
        asyncio.run(datastore.new_perfect_inference_feeback(self.cur, self.inference_id, self.user_id, self.boxes_id))
        for i in range(len(self.boxes_id)) :
            object = inference_queries.get_inference_object(self.cur, self.boxes_id[i])
            # verified_id must be equal to top_id
            self.assertEqual(str(object[4]), self.top_id[i])
            # valid column must be true
            self.assertTrue(object[5])

if __name__ == "__main__":
    unittest.main()
