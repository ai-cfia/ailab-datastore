"""
This is a test script for the database packages. 
It tests the functions in the user, seed and picture modules.
"""

import unittest
from unittest.mock import MagicMock
import uuid
import json
from PIL import Image
import io
import base64
from time import sleep
from datastore.db.queries import user,seed,picture,inference
from datastore.db.metadata import picture_set as picture_set_data,picture as picture_data,validator
import datastore.db.__init__ as db


# --------------------  USER FUNCTIONS --------------------
class test_user_functions(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db()
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor)
        self.email = "test@email.gouv.ca"

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_is_user_registered(self):
        """
        This test checks if the is_user_registered function returns the correct value
        for a user that is not yet registered and one that is.
        """

        self.assertFalse(
            user.is_user_registered(self.cursor, self.email),
            "The user should not already be registered",
        )

        user_id = user.register_user(self.cursor, self.email)

        self.assertTrue(
            validator.is_valid_uuid(user_id), "The user_id is not a valid UUID"
        )

    def test_is_user_registered_error(self):
        """
        This test checks if the is_user_registered function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            user.is_user_registered(mock_cursor, self.email)

    def test_is_a_user_id(self):
        """
        This test checks if the is_a_user_id function returns the correct value
        for a user that is not yet registered and one that is.
        """
        user_id = user.register_user(self.cursor, self.email)

        self.assertTrue(
            user.is_a_user_id(self.cursor, user_id),
            "The user_id should be registered",
        )

        self.assertFalse(
            user.is_a_user_id(self.cursor, str(uuid.uuid4())),
            "The user_id should not be registered",
        )

    def test_is_a_user_id_error(self):
        """
        This test checks if the is_a_user_id function raises an exception when the connection fails
        """
        user_id = user.register_user(self.cursor, self.email)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            user.is_a_user_id(mock_cursor, user_id)

    def test_get_user_id(self):
        """
        This test checks if the get_user_id function returns the correct UUID
        """
        user_id = user.register_user(self.cursor, self.email)
        uuid = user.get_user_id(self.cursor, self.email)

        self.assertTrue(
            validator.is_valid_uuid(user_id),
            f"The user_id={user_id} is not a valid UUID",
        )
        self.assertTrue(
            validator.is_valid_uuid(uuid),
            f"The returned UUID={uuid} is not a valid UUID",
        )
        self.assertEqual(
            user_id, uuid, "The returned UUID is not the same as the registered UUID"
        )

    def test_get_user_id_not_registered(self):
        """
        This test checks if the get_user_id function raises an exception when the user is not registered
        """
        with self.assertRaises(user.UserNotFoundError):
            user.get_user_id(self.cursor, self.email)

    def test_get_user_id_error(self):
        """
        This test checks if the get_user_id function raises an exception when the connection fails
        """
        user.register_user(self.cursor, self.email)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            user.get_user_id(mock_cursor, self.email)

    def test_register_user(self):
        """
        This test checks if the register_user function returns a valid UUID
        """
        user_id = user.register_user(self.cursor, self.email)

        self.assertTrue(
            validator.is_valid_uuid(user_id), "The user_id is not a valid UUID"
        )

    def test_register_user_error(self):
        """
        This test checks if the register_user function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(user.UserCreationError):
            user.register_user(mock_cursor, self.email)

    # def test_link_container(self):
    #     """
    #     This test checks if the link_container function links the container to the user
    #     """
    #     user_id = user.register_user(self.cursor, self.email)
    #     container_url = "https://container.com"
    #     user.link_container(self.cursor, user_id, container_url)
    #     fetched_url = user.get_container_url(self.cursor, user_id)
    #     self.assertEqual(container_url, fetched_url)

    def test_link_container_not_registered(self):
        """
        This test checks if the link_container function raises an exception when the user is not registered
        """
        with self.assertRaises(user.UserNotFoundError):
            user.link_container(self.cursor, str(uuid.uuid4()), "https://container.com")

    def test_link_container_error(self):
        """
        This test checks if the link_container function raises an exception when the connection fails
        """
        user_id = user.register_user(self.cursor, self.email)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            user.link_container(mock_cursor, user_id, "https://container.com")

    # def test_get_container_url(self):
    #     """
    #     This test checks if the get_container_url function returns the correct container url
    #     """
    #     user_id = user.register_user(self.cursor, self.email)
    #     container_url = "https://container.com"
    #     user.link_container(self.cursor, user_id, container_url)

    #     fetched_url = user.get_container_url(self.cursor, user_id)

    #     self.assertEqual(container_url, fetched_url)

    def test_get_container_url_not_registered(self):
        """
        This test checks if the get_container_url function raises an exception when the user is not registered
        """
        with self.assertRaises(user.UserNotFoundError):
            user.get_container_url(self.cursor, str(uuid.uuid4()))

    # def test_get_container_url_not_linked(self):
    #     """
    #     This test checks if the get_container_url function raises an exception when the container is not linked
    #     """
    #     user_id = user.register_user(self.cursor, self.email)
    #     with self.assertRaises(user.ContainerNotSetError):
    #         user.get_container_url(self.cursor, user_id)

    def test_get_container_url_error(self):
        """
        This test checks if the get_container_url function raises an exception when the connection fails
        """
        user_id = user.register_user(self.cursor, self.email)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            user.get_container_url(mock_cursor, user_id)

# --------------------  SEED FUNCTIONS --------------------
class test_seed_functions(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db()
        self.cursor = db.cursor(self.con)
        self.seed_name = "test-name"

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_get_all_seeds_names(self):
        """
        This test checks if the get_all_seeds_names function returns a list of seeds
        with at least the one seed we added
        """
        seed.new_seed(self.cursor, self.seed_name)
        seeds = seed.get_all_seeds_names(self.cursor)

        self.assertNotEqual(len(seeds), 0)
        self.assertIn((self.seed_name,), seeds)

    def test_get_all_seeds_names_error(self):
        """
        This test checks if the get_all_seeds_names function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            seed.get_all_seeds_names(mock_cursor)

    def test_get_seed_id(self):
        """
        This test checks if the get_seed_id function returns the correct UUID
        """
        seed_uuid = seed.new_seed(self.cursor, self.seed_name)
        fetch_id = seed.get_seed_id(self.cursor, self.seed_name)

        self.assertTrue(validator.is_valid_uuid(fetch_id))
        self.assertEqual(seed_uuid, fetch_id)

    def test_get_nonexistant_seed_id(self):
        """
        This test checks if the get_seed_id function raises an exception when the seed does not exist
        """
        with self.assertRaises(seed.SeedNotFoundError):
            seed.get_seed_id(self.cursor, "nonexistant_seed")

    def test_get_seed_id_error(self):
        """
        This test checks if the get_seed_id function raises an exception when the connection fails
        """
        seed.new_seed(self.cursor, self.seed_name)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            seed.get_seed_id(mock_cursor, self.seed_name)

    def test_new_seed(self):
        """
        This test checks if the new_seed function returns a valid UUID
        """
        seed_id = seed.new_seed(self.cursor, self.seed_name)

        self.assertTrue(validator.is_valid_uuid(seed_id))

    def test_new_seed_error(self):
        """
        This test checks if the new_seed function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(seed.SeedCreationError):
            seed.new_seed(mock_cursor, self.seed_name)

    def test_is_seed_registered(self):
        """
        This test checks if the is_seed_registered function returns the correct value
        for a seed that is not yet registered and one that is.
        """
        self.assertFalse(
            seed.is_seed_registered(self.cursor, self.seed_name),
            "The seed should not already be registered",
        )

        seed.new_seed(self.cursor, self.seed_name)

        self.assertTrue(
            seed.is_seed_registered(self.cursor, self.seed_name),
            "The seed should be registered",
        )

    def test_is_seed_registered_error(self):
        """
        This test checks if the is_seed_registered function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            seed.is_seed_registered(mock_cursor, self.seed_name)

# --------------------  PICTURE FUNCTIONS --------------------
class test_pictures_functions(unittest.TestCase):
    def setUp(self):
        # prepare the connection and cursor
        self.con = db.connect_db()
        self.cursor = db.cursor(self.con)

        # prepare the seed
        self.seed_name = "test seed"
        self.seed_id = seed.new_seed(self.cursor, self.seed_name)

        # prepare the user
        self.user_id = user.register_user(self.cursor, "test@email")

        # prepare the picture_set and picture
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = base64.b64encode(self.image_byte_array.getvalue()).decode(
            "utf8"
        )
        self.nb_seed=1
        self.picture_set = picture_set_data.build_picture_set(self.user_id, 1)
        self.picture = picture_data.build_picture(
            self.pic_encoded, "www.link.com", self.nb_seed, 1.0, ""
        )

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_picture_set(self):
        """
        This test checks if the new_picture_set function returns a valid UUID
        """
        picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id
        )

        self.assertTrue(
            validator.is_valid_uuid(picture_set_id),
            "The picture_set_id is not a valid UUID",
        )

    def test_new_picture_set_error(self):
        """
        This test checks if the new_picture_set function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(picture.PictureSetCreationError):
            picture.new_picture_set(mock_cursor, self.picture_set, self.user_id)

    def test_new_picture(self):
        """
        This test checks if the new_picture function returns a valid UUID
        """
        # prepare the picture_set
        picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id
        )

        # create the new picture in the db
        picture_id = picture.new_picture(
            self.cursor, self.picture, picture_set_id, self.seed_id,self.nb_seed
        )

        self.assertTrue(
            validator.is_valid_uuid(picture_id), "The picture_id is not a valid UUID"
        )

    def test_new_picture_error(self):
        """
        This test checks if the new_picture function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(picture.PictureUploadError):
            picture.new_picture(
                mock_cursor, self.picture, str(uuid.uuid4()), self.seed_id,self.nb_seed
            )

    def test_get_inexisting_picture_set(self):
        """
        This test checks if the get_picture_set function raises an exception when the picture_set does not exist
        """
        with self.assertRaises(picture.PictureSetNotFoundError):
            picture.get_picture_set(self.cursor, str(uuid.uuid4()))

    def test_get_picture_set(self):
        """
        This test checks if the get_picture_set function returns an object
        """
        # prepare picture_set
        picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id
        )
        # test the function
        picture_set = picture.get_picture_set(self.cursor, picture_set_id)

        self.assertIsNotNone(picture_set, "The picture_set is None")
        self.assertNotEqual(len(picture_set), 0, "The picture_set is empty")

    def test_get_inexisting_picture(self):
        """
        This test checks if the get_picture function raises an exception when the picture does not exist
        """
        with self.assertRaises(picture.PictureNotFoundError):
            picture.get_picture(self.cursor, str(uuid.uuid4()))

    def test_get_picture(self):
        """
        This test checks if the get_picture function returns an object
        """
        # prepare picture_set
        picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id
        )

        # prepare picture
        picture_id = picture.new_picture(
            self.cursor, self.picture, picture_set_id, self.seed_id,self.nb_seed
        )

        # test the function
        picture_data = picture.get_picture(self.cursor, picture_id)

        self.assertIsNotNone(picture_data, "The picture_data is None")
        self.assertNotEqual(len(picture_data), 0, "The picture_data is empty")

    def test_update_picture_metadata(self):
        """
        This test checks if the update_picture_metadata function updates the metadata
        """
        # prepare picture_set
        picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id
        )

        # prepare picture
        picture_id = picture.new_picture(
            self.cursor, self.picture, picture_set_id, self.seed_id,self.nb_seed
        )
        new_picture = picture_data.build_picture(
            self.pic_encoded, "www.link.com", 6, 1.0, ""
        )
        picture_metadata = picture.get_picture(self.cursor, picture_id)
        # update the metadata
        picture.update_picture_metadata(self.cursor, picture_id, new_picture,6)
        new_picture = json.loads(new_picture)
        # get the updated metadata
        new_picture_metadata = picture.get_picture(self.cursor, picture_id)
        self.assertEqual(
            new_picture_metadata["user_data"],
            new_picture["user_data"],
            "The metadata was not updated correctly",
        )
        self.assertEqual(
            new_picture_metadata["metadata"],
            new_picture["metadata"],
            "The metadata was not updated correctly",
        )
        self.assertEqual(
            new_picture_metadata["image_data"],
            new_picture["image_data"],
            "The metadata was not updated correctly",
        )

        self.assertNotEqual(
            picture_metadata["user_data"],
            new_picture_metadata["user_data"],
            "The metadata was not updated correctly",
        )
        self.assertEqual(
            picture_metadata["metadata"],
            new_picture_metadata["metadata"],
            "The metadata was not updated correctly",
        )
        self.assertEqual(
            picture_metadata["image_data"],
            new_picture_metadata["image_data"],
            "The metadata was not updated correctly",
        )

    def test_update_picture_metadata_error(self):
        """
        This test checks if the update_picture_metadata function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Connection error")
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(picture.PictureUpdateError):
            picture.update_picture_metadata(mock_cursor, uuid.uuid4(), self.picture,self.nb_seed)

    def test_is_a_picture_set_id(self):
        """
        This test checks if the is_a_picture_set_id function returns the correct value
        for a picture_set that is not yet registered and one that is.
        """
        picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id
        )

        self.assertTrue(
            picture.is_a_picture_set_id(self.cursor, picture_set_id),
            "The picture_set_id should be registered",
        )

        self.assertFalse(
            picture.is_a_picture_set_id(self.cursor, str(uuid.uuid4())),
            "The picture_set_id should not be registered",
        )

    def test_is_a_picture_set_id_error(self):
        """
        This test checks if the is_a_picture_set_id function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            picture.is_a_picture_set_id(mock_cursor, uuid.uuid4())

# --------------------  INFERENCE FUNCTIONS --------------------
class test_inference_functions(unittest.TestCase):
    def setUp(self):
        # prepare the connection and cursor
        self.con = db.connect_db()
        self.cursor = db.cursor(self.con)

        # prepare the seed
        self.seed_name = "test seed"
        self.seed_id = seed.new_seed(self.cursor, self.seed_name)

        # prepare the user
        self.user_id = user.register_user(self.cursor, "test@email")

        # prepare the picture_set and picture
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = base64.b64encode(self.image_byte_array.getvalue()).decode(
            "utf8"
        )
        self.picture_set = picture_set_data.build_picture_set(self.user_id, 1)
        self.nb_seed=1
        self.picture = picture_data.build_picture(
            self.pic_encoded, "www.link.com", self.nb_seed, 1.0, ""
        )
        self.picture_set_id=picture.new_picture_set(self.cursor, self.picture_set, self.user_id)
        self.picture_id=picture.new_picture(self.cursor, self.picture, self.picture_set_id, self.seed_id,self.nb_seed)
        with open("tests/inference_example.json", "r") as f:
            self.inference= json.loads(f.read())
        self.inference_trim= '{"filename": "inference_example", "totalBoxes": 1, "totalBoxes": 1}'
        self.type=1

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_inference(self):
        """
        This test checks if the new_inference function returns a valid UUID
        """
        inference_id = inference.new_inference(self.cursor, self.inference_trim, self.user_id, self.picture_id, self.type)

        self.assertTrue(
            validator.is_valid_uuid(inference_id), "The inference_id is not a valid UUID"
        )
        
    def test_new_inference_error(self):
        """
        This test checks if the new_inference function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(inference.InferenceCreationError):
            inference.new_inference(mock_cursor, self.inference_trim, self.user_id, self.picture_id, self.type)

    def test_new_inference_obj(self):
        """
        This test checks if the new_inference_object function returns a valid UUID
        """
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        for box in self.inference["boxes"]:
            inference_obj_id=inference.new_inference_object(self.cursor,inference_id,json.dumps(box),self.type)
            self.assertTrue(
                validator.is_valid_uuid(inference_obj_id), "The inference_obj_id is not a valid UUID"
            )
    
    def test_new_inference_obj_error(self):
        """
        This test checks if the new_inference_object function raises an exception when the connection fails
        """
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
    
        with self.assertRaises(inference.InferenceCreationError):
            inference.new_inference_object(mock_cursor,inference_id,self.inference["boxes"][0],self.type)

    def test_new_seed_object(self):
        """
        This test checks if the new_seed_object function returns a valid UUID
        """
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        for box in self.inference["boxes"]:
            inference_obj_id=inference.new_inference_object(self.cursor,inference_id,json.dumps(box),self.type)
            seed_obj_id=inference.new_seed_object(self.cursor,self.seed_id,inference_obj_id,box["score"])
            self.assertTrue(
                validator.is_valid_uuid(seed_obj_id), "The seed_obj_id is not a valid UUID"
            )
      
    def test_new_seed_object_error(self):
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        inference_obj_id=inference.new_inference_object(self.cursor,inference_id,json.dumps(self.inference["boxes"][0]),self.type)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(inference.SeedObjectCreationError):
            inference.new_seed_object(mock_cursor,self.seed_id,inference_obj_id,32.1)
      
    def test_get_inference(self):
        """
        This test checks if the get_inference function returns a correctly build inference
        TODO : Add test for not existing inference
        """
        inference_trim=json.loads(self.inference_trim)
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        inference_data=inference.get_inference(self.cursor,str(inference_id))
        #inference_json=json.loads(inference_data)
        self.assertGreaterEqual(len(inference_trim),len(inference_data), "The inference is not correctly build and has more keys than expected")
        for key in inference_trim:
            self.assertTrue(key in inference_data, f"The key: {key} is not in the inference")
            self.assertEqual(inference_trim[key],inference_data[key],f"The value ({inference_data[key]}) of the key: {key} is not the same as the expected one: {inference_trim[key]}")
              
    def test_get_inference_object(self):
        """
        This test checks if the get_inference_object function returns a correctly build object
        """
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        inference_obj_id=inference.new_inference_object(self.cursor,inference_id,json.dumps(self.inference["boxes"][0]),self.type)
            
        inference_obj=inference.get_inference_object(self.cursor,str(inference_obj_id))
        
        self.assertEqual(len(inference_obj),10, "The inference object hasn't the number of keys expected")
        self.assertEqual(inference_obj[0],inference_obj_id, "The inference object id is not the same as the expected one")
                      
    def test_get_inference_object_error(self):
        """
        This test checks if the get_inference_object function raise an error if the inference oject does not exist
        """
        inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        inference_obj_id="00000000-0000-0000-0000-000000000000"
            
        with self.assertRaises(Exception):
            inference.get_inference_object(self.cursor,str(inference_obj_id))
        
    def test_get_objects_by_inference(self):
        """
        This test checks if the get_objects_by_inference function returns the corrects objects for an inference
        """
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        total_boxes = len(self.inference["boxes"])
        objects_id=[]
        for box in self.inference["boxes"]:
            inference_obj_id=inference.new_inference_object(self.cursor,inference_id,json.dumps(box),self.type)
            objects_id.append(inference_obj_id)
        
        objects = inference.get_objects_by_inference(self.cursor, inference_id)
        self.assertEqual(len(objects),total_boxes, "The number of objects is not the same as the expected one")
        for object in objects :
            self.assertEqual(object[2],inference_id, "The inference id is not the same as the expected one")
            self.assertTrue(object[0] in objects_id, "The object id is not in the list of expected objects")

    def test_get_inference_object_top_id(self):
        """
        This test checks if the get_inference_object_top_id function returns the correct top_id of an inference object
        """
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        inference_obj_id=inference.new_inference_object(self.cursor,inference_id,json.dumps(self.inference["boxes"][0]),self.type)
        seed_obj_id=inference.new_seed_object(self.cursor,self.seed_id,inference_obj_id,self.inference["boxes"][0]["score"])
        
        inference.set_inference_object_top_id(self.cursor,inference_obj_id,seed_obj_id)
        top_id=inference.get_inference_object_top_id(self.cursor,inference_obj_id)
        
        self.assertEqual(seed_obj_id,top_id,"The verified_id is not the same as the expected one")
        
    def test_set_inference_object_verified_id(self):
        """
        This test checks if the set_inference_object_verified_id function returns a correctly update inference object
        """
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        inference_obj_id=inference.new_inference_object(self.cursor,inference_id,json.dumps(self.inference["boxes"][0]),self.type)
        previous_inference_obj=inference.get_inference_object(self.cursor,inference_obj_id)
        seed_obj_id=inference.new_seed_object(self.cursor,self.seed_id,inference_obj_id,self.inference["boxes"][0]["score"])
        # Sleep to see a difference in the updated_at date of the object
        sleep(3)

        inference.set_inference_object_verified_id(self.cursor,inference_obj_id,seed_obj_id)
        inference_obj=inference.get_inference_object(self.cursor,inference_obj_id)
        self.assertEqual(str(inference_obj[4]),str(seed_obj_id),"The verified_id is not the same as the expected one")
        # this test is not working because the trigger to update the update_at field is missing
        self.assertNotEqual(inference_obj[8],previous_inference_obj[8],"The update_at field is not updated")
        
    def test_set_inference_object_valid(self):
        """
        This test checks if the set_inference_object_verified_id function returns a correctly update inference object
        """
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        inference_obj_id=inference.new_inference_object(self.cursor,inference_id,json.dumps(self.inference["boxes"][0]),self.type)
        previous_inference_obj=inference.get_inference_object(self.cursor,inference_obj_id)
        # Sleep to see a difference in the updated_at date of the object
        sleep(3)

        inference.set_inference_object_valid(self.cursor,inference_obj_id,True)
        inference_obj=inference.get_inference_object(self.cursor,inference_obj_id)
        self.assertTrue(str(inference_obj[5]),"The object validity is not the same as the expected one")
        self.assertNotEqual(inference_obj[8],previous_inference_obj[8],"The update_at field is not updated")
        
        inference.set_inference_object_valid(self.cursor,inference_obj_id,False)
        inference_obj=inference.get_inference_object(self.cursor,inference_obj_id)
        self.assertFalse(str(inference_obj[5]),"The object validity is not the same as the expected one")
        # this test is not working because the trigger to update the update_at field is missing
        self.assertNotEqual(inference_obj[8],previous_inference_obj[8],"The update_at field is not updated")
        
    def test_is_inference_verified(self):
        """
        Test if is_inference_verified function correctly returns the inference status
        """        
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        
        verified = inference.is_inference_verified(self.cursor, inference_id)
        self.assertFalse(verified, "The inference verified field should be False")
        
        inference.set_inference_verified(self.cursor, inference_id, True)
        
        verified = inference.is_inference_verified(self.cursor, inference_id)
        self.assertTrue(verified, "The inference should be fully verified")
        
    def test_verify_inference_status(self):
        """
        Test if verify_inference_status function correctly updates the inference status
        """
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        inference_obj_id=inference.new_inference_object(self.cursor,inference_id,json.dumps(self.inference["boxes"][0]),self.type)
        seed_obj_id=inference.new_seed_object(self.cursor,self.seed_id,inference_obj_id,self.inference["boxes"][0]["score"])

        inference.verify_inference_status(self.cursor, inference_id, self.user_id)
        
        verified = inference.is_inference_verified(self.cursor, inference_id)
        self.assertFalse(verified, "The inference verified field should be False")
        
        inference.set_inference_object_valid(self.cursor,inference_obj_id,True)
        inference.set_inference_object_verified_id(self.cursor,inference_obj_id,seed_obj_id)

        inference.verify_inference_status(self.cursor, inference_id, self.user_id)
        verified = inference.is_inference_verified(self.cursor, inference_id)
        self.assertTrue(verified, "The inference should be fully verified")
        
    def test_get_seed_object_id(self):
        """
        Test if get_seed_object_id function correctly returns the seed object id
        """
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        inference_obj_id=inference.new_inference_object(self.cursor,inference_id,json.dumps(self.inference["boxes"][0]),self.type)
        seed_obj_id=inference.new_seed_object(self.cursor,self.seed_id,inference_obj_id,self.inference["boxes"][0]["score"])
        
        fetched_seed_obj_id = inference.get_seed_object_id(self.cursor,self.seed_id, inference_obj_id)
        self.assertEqual(seed_obj_id, fetched_seed_obj_id, "The fetched seed object id is not the same as the expected one")
        
    def test_get_not_seed_object_id(self):
        """
        Test if get_seed_object_id function correctly returns the seed object id
        """
        inference_id=inference.new_inference(self.cursor,self.inference_trim,self.user_id,self.picture_id,self.type)
        inference_obj_id=inference.new_inference_object(self.cursor,inference_id,json.dumps(self.inference["boxes"][0]),self.type)
        seed_obj_id=inference.new_seed_object(self.cursor,self.seed_id,inference_obj_id,self.inference["boxes"][0]["score"])
        mock_seed_id = str(uuid.uuid4())
        fetched_seed_obj_id = inference.get_seed_object_id(self.cursor,mock_seed_id, inference_obj_id)
        self.assertTrue(fetched_seed_obj_id is None, "The fetched seed object id should be None")
        
if __name__ == "__main__":
    unittest.main()
