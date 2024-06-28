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
import uuid
import asyncio
import datastore.db.__init__ as db
import datastore.__init__ as datastore
import datastore.db.metadata.validator as validator
import datastore.db.queries.seed as seed_query



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
        self.seed_name = "test-name"
        self.seed_id = seed_query.new_seed(self.cur, self.seed_name)
        with open("tests/inference_result.json") as file:
            self.inference= json.load(file)
        self.folder_name = "test_folder"
    
    def tearDown(self):
        self.con.rollback()
        self.container_client.delete_container()
        db.end_query(self.con, self.cur)

    def test_upload_picture_unknown(self):
        """
        Test the upload picture function.
        """
        picture_id = asyncio.run(datastore.upload_picture_unknown(self.cur, self.user_id, self.pic_encoded,self.container_client))
        self.assertTrue(validator.is_valid_uuid(picture_id))

    def test_register_inference_result(self):
        """
        Test the register inference result function.
        """
        picture_id = asyncio.run(datastore.upload_picture_unknown(self.cur, self.user_id, self.pic_encoded,self.container_client))
        model_id = "test_model_id"
        
        result = asyncio.run(datastore.register_inference_result(self.cur,self.user_id,self.inference, picture_id, model_id))
        #self.cur.execute("SELECT result FROM inference WHERE picture_id=%s AND model_id=%s",(picture_id,model_id,))
        self.assertTrue(validator.is_valid_uuid(result["inference_id"]))

    def test_create_picture_set(self):
        """
        Test the creation of a picture set
        """
        picture_set_id = asyncio.run(datastore.create_picture_set(self.cur, self.container_client, 0, self.user_id))
        self.assertTrue(validator.is_valid_uuid(picture_set_id))
    
    def test_create_picture_set_connection_error(self):
        """
        This test checks if the create_picture_set function correctly raise an exception if the connection to the db fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            asyncio.run(datastore.create_picture_set(mock_cursor, self.container_client, 0, self.user_id))
            
    def test_create_picture_set_error_user_not_found(self):
        """
        This test checks if the create_picture_set function correctly raise an exception if the user given doesn't exist in db
        """
        with self.assertRaises(datastore.user.UserNotFoundError):
            asyncio.run(datastore.create_picture_set(self.cur, self.container_client, 0, uuid.uuid4()))
    
    def test_upload_picture_known(self):
        """
        Test the upload picture function with a known seed
        """
        picture_set_id = asyncio.run(datastore.create_picture_set(self.cur, self.container_client, 0, self.user_id))
        picture_id = asyncio.run(datastore.upload_picture_known(self.cur, self.user_id, self.pic_encoded,self.container_client, self.seed_id, picture_set_id))
        self.assertTrue(validator.is_valid_uuid(picture_id))
     
    def test_upload_picture_known_error_user_not_found(self):
        """
        This test checks if the upload_picture_known function correctly raise an exception if the user given doesn't exist in db
        """
        picture_set_id = asyncio.run(datastore.create_picture_set(self.cur, self.container_client, 0, self.user_id))
        with self.assertRaises(datastore.user.UserNotFoundError):
            asyncio.run(datastore.upload_picture_known(self.cur, uuid.uuid4(), self.pic_encoded,self.container_client, self.seed_id, picture_set_id))
    
    def test_upload_picture_known_connection_error(self):
        """
        This test checks if the upload_picture_known function correctly raise an exception if the connection to the db fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        picture_set_id = asyncio.run(datastore.create_picture_set(self.cur, self.container_client, 0, self.user_id))
        with self.assertRaises(Exception):
            asyncio.run(datastore.upload_picture_known(mock_cursor, self.user_id, self.pic_encoded,self.container_client, self.seed_id, picture_set_id))
        
    def test_upload_pictures(self):
        """
        Test the upload pictures function
        """
        pictures = [self.pic_encoded,self.pic_encoded,self.pic_encoded]
        picture_set_id = asyncio.run(datastore.create_picture_set(self.cur, self.container_client, 0, self.user_id))
        picture_ids = asyncio.run(datastore.upload_pictures(self.cur, self.user_id, picture_set_id, self.container_client, pictures, self.seed_name))
        self.assertTrue(all([validator.is_valid_uuid(picture_id) for picture_id in picture_ids]))
        self.assertEqual(len(pictures), asyncio.run(datastore.azure_storage.get_image_count(self.container_client, str(picture_set_id))))
        
    def test_upload_pictures_error_user_not_found(self):
        """
        This test checks if the upload_picture_known function correctly raise an exception if the user given doesn't exist in db
        """
        picture_set_id = asyncio.run(datastore.create_picture_set(self.cur, self.container_client, 0, self.user_id))
        with self.assertRaises(datastore.user.UserNotFoundError):
            asyncio.run(datastore.upload_pictures(self.cur, uuid.uuid4(), picture_set_id, self.container_client,[self.pic_encoded,self.pic_encoded,self.pic_encoded], self.seed_name))
    
    def test_upload_pictures_connection_error(self):
        """
        This test checks if the upload_picture_known function correctly raise an exception if the connection to the db fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        picture_set_id = asyncio.run(datastore.create_picture_set(self.cur, self.container_client, 0, self.user_id))
        with self.assertRaises(Exception):
            asyncio.run(datastore.upload_pictures(mock_cursor, self.user_id, picture_set_id, self.container_client,[self.pic_encoded,self.pic_encoded,self.pic_encoded], self.seed_name))
            
    def test_upload_pictures_error_seed_not_found(self):
        """
        This test checks if the upload_picture_known function correctly raise an exception if the seed given doesn't exist in db
        """
        picture_set_id = asyncio.run(datastore.create_picture_set(self.cur, self.container_client, 0, self.user_id))
        with self.assertRaises(datastore.seed.SeedNotFoundError):
            asyncio.run(datastore.upload_pictures(self.cur, self.user_id, picture_set_id, self.container_client,[self.pic_encoded,self.pic_encoded,self.pic_encoded], "unknown_seed"))
    
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
        picture_id = asyncio.run(datastore.upload_picture_unknown(self.cur, self.user_id, self.pic_encoded,self.container_client))
        model_id = "test_model_id"
        self.registered_inference = asyncio.run(datastore.register_inference_result(self.cur,self.user_id,self.inference, picture_id, model_id))
        self.registered_inference["user_id"] = self.user_id
        self.mock_box = {
                "topX": 123,
                "topY": 456,
                "bottomX": 789,
                "bottomY": 123
            }
        self.inference_id = self.registered_inference.get("inference_id")
        self.boxes_id = []
        self.top_id = []
        self.unreal_seed_id= datastore.seed.new_seed(self.cur, "unreal_seed")
        for box in self.registered_inference["boxes"]:
            self.boxes_id.append(box["box_id"])
            self.top_id.append(box["top_id"])
            box["classId"] = datastore.seed.get_seed_id(self.cur, box["label"])

    def tearDown(self):
        self.con.rollback()
        self.container_client.delete_container()
        db.end_query(self.con, self.cur)
            
    def test_new_perfect_inference_feedback(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly updates the inference object after a perfect feedback is given
        """
        asyncio.run(datastore.new_perfect_inference_feeback(self.cur, self.inference_id, self.user_id, self.boxes_id))
        for i in range(len(self.boxes_id)) :
            object = datastore.inference.get_inference_object(self.cur, self.boxes_id[i])
            # verified_id must be equal to top_id
            self.assertEqual(str(object[4]), self.top_id[i])
            # valid column must be true
            self.assertTrue(object[5])
          
    def test_new_perfect_inference_feedback_error_verified_inference(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly raise an exception if the inference given is already verified
        """
        asyncio.run(datastore.new_perfect_inference_feeback(self.cur, self.inference_id, self.user_id, self.boxes_id))
        self.assertTrue(datastore.inference.is_inference_verified(self.cur, self.inference_id))
        with self.assertRaises(datastore.inference.InferenceAlreadyVerifiedError):
            asyncio.run(datastore.new_perfect_inference_feeback(self.cur, self.inference_id, self.user_id, self.boxes_id))
          
            
    def test_new_perfect_inference_feedback_error_inference_not_found(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly raise an exception if the inference given doesn't exist in db
        """
        with self.assertRaises(datastore.inference.InferenceNotFoundError):
            asyncio.run(datastore.new_perfect_inference_feeback(self.cur, str(uuid.uuid4()), self.user_id, self.boxes_id))
            
    def test_new_perfect_inference_feedback_error_inference_object_not_found(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly raise an exception if one of the inference object given doesn't exist in db
        """
        with self.assertRaises(datastore.inference.InferenceObjectNotFoundError):
            asyncio.run(datastore.new_perfect_inference_feeback(self.cur, self.inference_id, self.user_id, [self.boxes_id[0], str(uuid.uuid4())]))
            
    def test_new_perfect_inference_feedback_error_user_not_found(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly raise an exception if the user given doesn't exist in db
        """
        with self.assertRaises(datastore.user.UserNotFoundError):
            asyncio.run(datastore.new_perfect_inference_feeback(self.cur, self.inference_id, str(uuid.uuid4()), self.boxes_id))
    
    def test_new_perfect_inference_feedback_connection_error(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly raise an exception if the connection to the db fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            asyncio.run(datastore.new_perfect_inference_feeback(mock_cursor, self.inference_id, self.user_id, self.boxes_id))

    def test_new_correction_inference_feedback(self):
        """
        This test checks if the new_correction_inference_feeback function correctly
        """
        self.assertTrue(validator.is_valid_uuid(self.inference_id))
        
        asyncio.run(datastore.new_correction_inference_feedback(self.cur, self.registered_inference, 1))
        for i in range(len(self.boxes_id)) :
            object = datastore.inference.get_inference_object(self.cur, self.boxes_id[i])
            # verified_id must be equal to top_id
            self.assertEqual(str(object[4]), self.top_id[i])
            # valid column must be true
            self.assertTrue(object[6])
            
    def test_new_correction_inference_feedback_new_guess(self):
        """
        This test checks if the new_correction_inference_feeback function correctly when another guess is verified
        """
        self.assertTrue(validator.is_valid_uuid(self.inference_id))
        new_top_ids =[]
        for box in self.registered_inference["boxes"]:
            box["label"] = box["topN"][1]["label"]
            box["classId"] = datastore.seed.get_seed_id(self.cur, box["label"])
            new_top_ids.append(box["topN"][1]["object_id"])
        asyncio.run(datastore.new_correction_inference_feedback(self.cur, self.registered_inference, 1))
        for i in range(len(self.boxes_id)) :
            object_db = datastore.inference.get_inference_object(self.cur, self.boxes_id[i])
            # verified_id must be equal to top_id
            self.assertTrue(str(object_db[4]) == new_top_ids[i])
            # valid column must be true
            self.assertTrue(object_db[6])
            
    def test_new_correction_inference_feedback_box_edited(self):
        """
        This test checks if the new_correction_inference_feeback function correctly when the box metadata is updated
        """
        self.assertTrue(validator.is_valid_uuid(self.inference_id))
        for box in self.registered_inference["boxes"]:
            box["box"]= self.mock_box
        asyncio.run(datastore.new_correction_inference_feedback(self.cur, self.registered_inference, 1))
        for box in self.registered_inference["boxes"] :
            object_db = datastore.inference.get_inference_object(self.cur, box["box_id"])
            # The new box metadata must be updated
            self.assertDictEqual(object_db[1]["box"], self.mock_box)
            # The top_id must be equal to the previous top_id
            self.assertEqual(str(object_db[4]), box["top_id"])
            # valid column must be true
            self.assertTrue(object_db[6])
            
    def test_new_correction_inference_feedback_not_guess(self):
        """
        This test checks if the new_correction_inference_feeback function correctly when the box is not a guess
        """
        self.assertTrue(validator.is_valid_uuid(self.inference_id))
        for box in self.registered_inference["boxes"]:
            box["label"] = "unreal_seed"
            box["classId"] = self.unreal_seed_id
        asyncio.run(datastore.new_correction_inference_feedback(self.cur, self.registered_inference, 1))
        for i in range(len(self.boxes_id)) :
            object_db = datastore.inference.get_inference_object(self.cur, self.boxes_id[i])
            # verified_id must be equal to the new_top_id
            new_top_id = datastore.inference.get_seed_object_id(self.cur,self.unreal_seed_id,object_db[0])
            self.assertTrue(validator.is_valid_uuid(new_top_id))
            self.assertEqual(str(object_db[4]),str(new_top_id))
            # valid column must be true
            self.assertTrue(object_db[6])
            
    def test_new_correction_inference_feedback_not_valid(self):
        """
        This test checks if the new_correction_inference_feeback function correctly when the box is not a guess
        """
        self.assertTrue(validator.is_valid_uuid(self.inference_id))
        for box in self.registered_inference["boxes"]:
            box["label"] = ""
            box["classId"] = ""
        asyncio.run(datastore.new_correction_inference_feedback(self.cur, self.registered_inference, 1))
        for i in range(len(self.boxes_id)) :
            object_db = datastore.inference.get_inference_object(self.cur, self.boxes_id[i])
            # verified_id must not be an id
            self.assertEqual(object_db[4], None)
            # valid column must be false
            self.assertFalse(object_db[6])
            
    def test_new_correction_inference_feedback_unknown_seed(self):
        """
        This test checks if the new_correction_inference_feeback function correctly when the box is not a guess
        """
        self.assertTrue(validator.is_valid_uuid(self.inference_id))
        for box in self.registered_inference["boxes"]:
            box["label"] = "unknown_seed"
            box["classId"] = ""
        asyncio.run(datastore.new_correction_inference_feedback(self.cur, self.registered_inference, 1))
        for i in range(len(self.boxes_id)) :
            object_db = datastore.inference.get_inference_object(self.cur, self.boxes_id[i])
            # verified_id must be equal to an id
            self.assertTrue(validator.is_valid_uuid(str(object_db[4])))
            # valid column must be true
            self.assertTrue(object_db[6])

class test_picture_set(unittest.TestCase):
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
        self.seed_name = "test-name"
        self.seed_id = seed_query.new_seed(self.cur, self.seed_name)
        self.folder_name = "test_folder"
        self.picture_set_id = asyncio.run(datastore.create_picture_set(self.cur, self.container_client, 0, self.user_id, self.folder_name))
    
    def tearDown(self):
        self.con.rollback()
        self.container_client.delete_container()
        db.end_query(self.con, self.cur)

    def test_get_picture_sets_info(self) :
        """
        Test the get_picture_sets_info function
        """
        
        picture_sets_info = asyncio.run(datastore.get_picture_sets_info(self.cur, self.user_id))
        self.assertEqual(len(picture_sets_info), 2)
        self.assertEqual(picture_sets_info.get(self.picture_set_id)[1], 0)
        self.assertEqual(picture_sets_info.get(self.picture_set_id)[0], self.folder_name)
        
        self.pictures = [self.pic_encoded,self.pic_encoded,self.pic_encoded]
        self.picture_set_id = asyncio.run(datastore.create_picture_set(self.cur, self.container_client, 0, self.user_id, self.folder_name + "2"))
        asyncio.run(datastore.upload_pictures(self.cur, self.user_id, self.picture_set_id, self.container_client, self.pictures, self.seed_name))
        
        picture_sets_info = asyncio.run(datastore.get_picture_sets_info(self.cur, self.user_id))
        self.assertEqual(len(picture_sets_info), 3)
        self.assertEqual(picture_sets_info.get(self.picture_set_id)[1], 3)
        self.assertEqual(picture_sets_info.get(self.picture_set_id)[0], self.folder_name + "2")
        
    def test_get_picture_sets_info_error_user_not_found(self):
        """
        This test checks if the get_picture_sets_info function correctly raise an exception if the user given doesn't exist in db
        """
        with self.assertRaises(datastore.user.UserNotFoundError):
            asyncio.run(datastore.get_picture_sets_info(self.cur, uuid.uuid4()))

    def test_get_picture_sets_info_error_connection_error(self):
        """
        This test checks if the get_picture_sets_info function correctly raise an exception if the connection to the db fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            asyncio.run(datastore.get_picture_sets_info(mock_cursor, self.user_id))
    
    def test_delete_picture_set(self):
        """
        This test checks the delete_picture_set function 
        """
        picture_sets_info = asyncio.run(datastore.get_picture_sets_info(self.cur, self.user_id))
        self.assertEqual(len(picture_sets_info), 2)
        asyncio.run(datastore.delete_picture_set(self.cur, self.user_id, self.picture_set_id, self.container_client))
        
        picture_sets_info = asyncio.run(datastore.get_picture_sets_info(self.cur, self.user_id))
        self.assertEqual(len(picture_sets_info), 1)
    
    def test_delete_picture_set_error_user_not_found(self):
        """
        This test checks if the delete_picture_set function correctly raise an exception if the user given doesn't exist in db
        """
        with self.assertRaises(datastore.user.UserNotFoundError):
            asyncio.run(datastore.delete_picture_set(self.cur, uuid.uuid4(), self.picture_set_id, self.container_client))
    
    def test_delete_picture_set_error_connection_error(self):
        """
        This test checks if the delete_picture_set function correctly raise an exception if the connection to the db fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            asyncio.run(datastore.delete_picture_set(mock_cursor, self.user_id, self.picture_set_id, self.container_client))
        
    def test_delete_picture_set_error_picture_set_not_found(self):
        """
        This test checks if the delete_picture_set function correctly raise an exception if the picture set given doesn't exist in db
        """
        with self.assertRaises(datastore.picture.PictureSetNotFoundError):
            asyncio.run(datastore.delete_picture_set(self.cur, self.user_id, uuid.uuid4(), self.container_client))
    
    def test_delete_picture_set_error_not_owner(self):
        """
        This test checks if the delete_picture_set function correctly raise an exception if the user is not the owner of the picture set
        """
        not_owner_user_obj= asyncio.run(datastore.new_user(self.cur,"notowner@email",self.connection_str,'test-user'))
        not_owner_user_id=datastore.User.get_id(not_owner_user_obj)
        
        with self.assertRaises(datastore.picture.PictureSetDeleteError):
            asyncio.run(datastore.delete_picture_set(self.cur, not_owner_user_id, self.picture_set_id, self.container_client))
            
        container_client = asyncio.run(datastore.get_user_container_client(not_owner_user_id,'test-user'))
        container_client.delete_container()
    
    def test_delete_picture_set_error_default_folder(self):
        """
        This test checks if the delete_picture_st function correctly raise an exception if the user want to delete the folder "General"
        """
        general_folder_id = datastore.user.get_default_picture_set(self.cur, self.user_id)
        with self.assertRaises(datastore.picture.PictureSetDeleteError):
            asyncio.run(datastore.delete_picture_set(self.cur, self.user_id, general_folder_id, self.container_client))
               
class test_analysis(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(db.FERTISCAN_DB_URL, db.FERTISCAN_SCHEMA)
        self.cur = db.cursor(self.con)
        db.create_search_path(self.con, self.cur,db.FERTISCAN_SCHEMA)
        self.connection_str=os.environ["FERTISCAN_STORAGE_URL"]
        
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = self.image.tobytes()

        self.container_name='dev'
        # self.credentials = datastore.blob.get_account_sas(os.environ["FERTISCAN_BLOB_ACCOUNT"], os.environ["FERTISCAN_BLOB_KEY"])
        # self.container_client = asyncio.run(datastore.azure_storage.mount_container(self.connection_str,self.container_name,True,'test',self.credentials))
        self.container_client = 'on hold'
        self.analysis_dict = {
            "company_name": "GreenGrow Fertilizers Inc.",
            "company_address": "123 Greenway Blvd Springfield IL 62701 USA",
            "company_website": "www.greengrowfertilizers.com",
        }      

    def tearDown(self):
        self.con.rollback()
        # self.container_client.delete_container()
        db.end_query(self.con, self.cur)

    def test_registere_analysis(self):
        """
        Test the register analysis function
        """
        # self.assertTrue(self.container_client.exists())
        analysis = asyncio.run(datastore.register_analysis(self.cur, self.container_client,self.analysis_dict,self.pic_encoded,"","General"))
        self.assertTrue(validator.is_valid_uuid(analysis["analysis_id"]))

if __name__ == "__main__":
    unittest.main()
