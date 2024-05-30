"""
This is a test script for the highest level of the datastore packages. 
It tests the functions in the __init__.py files of the datastore packages.
"""

import os
import unittest
from unittest.mock import MagicMock
from PIL import Image
import json
import asyncio
import datastore.blob.azure_storage_api
import datastore.db.__init__ as db
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
        for key in ml_structure.keys():
            print("key: "+key+" value: "+str(ml_structure[key])) 
            #self.assertEqual(ml_structure[key],self.ml_dict[key])
 
        
class test_user(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect_db()
        self.cursor = db.cursor(self.conn)
        db.create_search_path(self.conn, self.cursor)
        self.user_email="test@email"
        self.connection_str=os.environ["NACHET_STORAGE_URL"]

        
    def tearDown(self):
        self.conn.rollback()
        db.end_query(self.conn, self.cursor)

    def test_new_user(self):
        """
        Test the new user function.
        """
        user_id=datastore.new_user(self.cursor,self.user_email,self.connection_str)
        self.assertTrue(validator.is_valid_uuid(user_id))
    
    def test_already_existing_user(self):
        """
        Test the already existing user function.
        """
        user_id=datastore.new_user(self.cursor,self.user_email,self.connection_str)
        self.assertTrue(validator.is_valid_uuid(user_id))
        with self.assertRaises(datastore.UserAlreadyExistsError):
            datastore.new_user(self.cursor,self.user_email,self.connection_str)
        
    def test_new_user_container_error(self):
        """
        Test the new user container error function.
        """
        with self.assertRaises(datastore.ContainerCreationError):
            datastore.new_user(self.cursor,self.user_email,"wrong_connection_str")

    @patch("datastore.blob.azure_storage_api.create_folder")
    def test_new_user_folder_error(self,MockCreateFolder):
        """
        Test the new user folder error function.
        """
        MockCreateFolder.side_effect= datastore.azure_storage.CreateDirectoryError("Test error")
        with self.assertRaises(datastore.FolderCreationError):
            datastore.new_user(self.cursor,self.user_email,"wrong_connection_str")

    def test_get_user(self):
        """
        Test the get user function.
        """
        user_id=datastore.new_user(self.cursor,self.user_email,self.connection_str)
        user=datastore.get_user(self.cursor,user_id)
        self.assertEqual(user.get_id(),user_id)
        self.assertEqual(user.get_email(),self.connection_str)

class test_picture(unittest.TestCase):
    def setUp(self):
        self.con = datastore.db.connect_db()
        self.cur = datastore.db.cursor(con)
        datastore.db.create_search_path(con, cur)
        self.connection_str=os.environ["NACHET_STORAGE_URL"]
        self.user_email="test@email"
        self.user_id= datastore.new_user(self.cur,self.user_email,self.connection_str)
        self.image = Image.new('RGB', (100, 100), color = 'red')
        self.picture_hash= datastore.azure_storage.generate_hash(self.image)

    def tearDown(self):
        self.con.rollback()
        datastore.db.end_query(self.con, self.cur)

    def test_upload_picture(self):
        """
        Test the upload picture function.
        """
        picture_id = datastore.upload_picture(self.cur, self.user_id, self.picture_hash,self.connection_str)
        self.assertTrue(validator.is_valid_uuid(picture_id))

    def test_upload_picture_error(self):
        """
        Test the upload picture error function.
        """
        with self.assertRaises(datastore.PictureAlreadyExistsError):
            datastore.upload_picture(self.cur, self.user_id, self.picture_hash,self.connection_str)

    def test_register_inference_result(self):
        """
        Test the register inference result function.
        """
        picture_id = datastore.upload_picture(self.cur, self.user_id, self.picture_hash,self.connection_str)
        model_id = "test_model_id"
        result = "test_result"
        datastore.register_inference_result(self.cur, picture_id, model_id, result)
        self.cur.execute("SELECT result FROM inference WHERE picture_id=%s AND model_id=%s",(picture_id,model_id,))
        self.assertEqual(self.cur.fetchone()[0],result)
if __name__ == "__main__":
    unittest.main()
