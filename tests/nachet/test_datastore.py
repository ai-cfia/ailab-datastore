"""
This is a test script for the highest level of the datastore packages.
It tests the functions in the __init__.py files of the datastore packages.
"""

import io
import os
import unittest
from unittest.mock import MagicMock
from PIL import Image, ImageChops
import json
import uuid
import asyncio
import datastore.db.__init__ as db
import datastore.__init__ as datastore
import nachet.__init__ as nachet
import datastore.db.metadata.validator as validator
from nachet.db.metadata.inference import Inference
import nachet.db.queries.seed as seed_query
from copy import deepcopy


DB_CONNECTION_STRING = os.environ.get("NACHET_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("NACHET_DB_URL is not set")

DB_SCHEMA = os.environ.get("NACHET_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("NACHET_SCHEMA_TESTING is not set")

BLOB_CONNECTION_STRING = os.environ["NACHET_STORAGE_URL"]
if BLOB_CONNECTION_STRING is None or BLOB_CONNECTION_STRING == "":
    raise ValueError("NACHET_STORAGE_URL_TESTING is not set")

BLOB_ACCOUNT = os.environ["NACHET_BLOB_ACCOUNT"]
if BLOB_ACCOUNT is None or BLOB_ACCOUNT == "":
    raise ValueError("NACHET_BLOB_ACCOUNT is not set")

BLOB_KEY = os.environ["NACHET_BLOB_KEY"]
if BLOB_KEY is None or BLOB_KEY == "":
    raise ValueError("NACHET_BLOB_KEY is not set")

DEV_USER_EMAIL = os.environ.get("DEV_USER_EMAIL")
if DEV_USER_EMAIL is None or DEV_USER_EMAIL == "":
    # raise ValueError("DEV_USER_EMAIL is not set")
    print("Warning: DEV_USER_EMAIL not set")


class test_ml_structure(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "ml_structure_exemple.json")
        with open(file_path) as file:
            self.ml_dict = json.load(file)
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_import_ml_structure_from_json(self):
        """
        Test the import function.
        """
        asyncio.run(
            nachet.import_ml_structure_from_json_version(self.cursor, self.ml_dict)
        )
        self.cursor.execute("SELECT id FROM model WHERE name='that_model_name'")
        model_id = self.cursor.fetchone()[0]
        self.assertTrue(validator.is_valid_uuid(str(model_id)))
        self.cursor.execute("SELECT id FROM pipeline WHERE name='Second Pipeline'")
        pipeline_id = self.cursor.fetchone()[0]
        self.assertTrue(validator.is_valid_uuid(str(pipeline_id)))
        self.cursor.execute(
            "SELECT id FROM pipeline_model WHERE pipeline_id=%s AND model_id=%s",
            (
                pipeline_id,
                model_id,
            ),
        )
        self.assertTrue(validator.is_valid_uuid(self.cursor.fetchone()[0]))

    def test_get_ml_structure(self):
        """
        Test the get function.
        """
        asyncio.run(
            nachet.import_ml_structure_from_json_version(self.cursor, self.ml_dict)
        )
        ml_structure = asyncio.run(nachet.get_ml_structure(self.cursor))

        # self.assertDictEqual(ml_structure,self.ml_dict)
        for pipeline in self.ml_dict["pipelines"]:
            for key in pipeline.keys():
                # These are keys not necessarly found in the DB but will be saved on imports if present
                # The Getter we are testing fetches all pipelines (some that might not been initialized from an import)
                # Therefore, We are skipping theses keys for now
                if key not in ["Accuracy"]:
                    # print(ml_structure["pipelines"][0].keys())
                    self.assertTrue(
                        (key in ml_structure["pipelines"][0].keys()),
                        f"Key {key} was not found and expected in the returned dictionary",
                    )
        for model in self.ml_dict["models"]:
            if (
                model.get("created_by") == "Avery GoodDataScientist"
            ):  # testing only for the imported pipelines
                for key in model.keys():
                    if key not in ["Accuracy", "endpoint_name"]:
                        # print(key)
                        self.assertTrue(
                            (key in ml_structure["models"][0].keys()),
                            f"Key {key} was not found and expected in the returned dictionary",
                        )

    def test_get_ml_structure_eeror(self):
        """
        Test the get version function.
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        with self.assertRaises(nachet.MLRetrievalError):
            asyncio.run(nachet.get_ml_structure(mock_cursor))


class test_picture(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        self.connection_str = BLOB_CONNECTION_STRING
        self.user_email = "testing-nachet-picture@email"
        self.user_obj = asyncio.run(
            datastore.new_user(
                cursor=self.cursor,
                email=self.user_email,
                connection_string=self.connection_str,
                tier="test-user-nachet",
                role=datastore.Role.INSPECTOR,
            )
        )
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = self.image.tobytes()
        self.pictures = [self.pic_encoded, self.pic_encoded, self.pic_encoded]
        # self.picture_hash= asyncio.run(azure_storage.generate_hash(self.pic_encoded))
        self.container_name = "test-nachet-datastore-container"
        self.user_id = datastore.User.get_id(self.user_obj)
        self.assertEqual(self.user_obj.model.id, self.user_id)
        # Get Container controller
        self.container_id = list(self.user_obj.model.containers.keys())[0]
        self.container_ctrl = asyncio.run(
            datastore.get_container_controller(
                cursor=self.cursor,
                container_id=self.container_id,
                connection_str=self.connection_str,
                credentials=None,
            )
        )
        # Containter should exists for picture to be uploaded into it
        self.assertTrue(self.container_ctrl.container_client.exists())

        self.folder_name = "test-nachet-datastore-folder"
        self.folder = asyncio.run(
            self.container_ctrl.create_folder(
                self.cursor,
                performed_by=self.user_id,
                folder_name=self.folder_name,
                nb_pictures=1,
                parent_folder_id=None,
            )
        )
        self.folder_id = self.folder.id

        self.seed_name = "test-name"
        self.seed_id = seed_query.new_seed(self.cursor, self.seed_name)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "inference_result.json")
        with open(file_path) as file:
            self.inference = json.load(file)
        self.folder_name = "test_folder"

        self.nb_seeds = int(self.inference["totalBoxes"])

    def tearDown(self):
        self.con.rollback()
        self.container_ctrl.container_client.delete_container()
        db.end_query(self.con, self.cursor)

    def test_upload_picture_unknown(self):
        """
        Test the upload picture function.
        """
        # This is done through the Global Datastore (it shouldnt be tested here but here's how it look like)
        picture_ids = asyncio.run(
            self.container_ctrl.upload_pictures(
                self.cursor,
                user_id=self.user_id,
                hashed_pictures=[self.pic_encoded],
                folder_id=None,
            )
        )
        self.assertEqual(len(picture_ids), 1)
        self.assertIsInstance(picture_ids[0], uuid.UUID)

    def test_register_inference_result(self):
        """
        Test the register inference result function.
        """
        picture_ids = asyncio.run(
            self.container_ctrl.upload_pictures(
                self.cursor,
                user_id=self.user_id,
                hashed_pictures=[self.pic_encoded],
                folder_id=None,
            )
        )
        picture_id = picture_ids[0]

        result = asyncio.run(
            nachet.register_inference_result(
                self.cursor, self.user_id, self.inference, picture_id, None
            )
        )
        # self.cursor.execute("SELECT result FROM inference WHERE picture_id=%s AND model_id=%s",(picture_id,model_id,))
        self.assertTrue(validator.is_valid_uuid(result["inference_id"]))
        Inference.model_validate(result)

    def test_upload_pictures_known(self):
        """
        Test the upload picture function with a known seed
        """
        # Creating the folder beforehand
        folder_model = asyncio.run(
            self.container_ctrl.create_folder(
                cursor=self.cursor,
                performed_by=self.user_id,
                folder_name=self.folder_name,
                nb_pictures=1,
                parent_folder_id=None,
            )
        )
        folder_id = folder_model.id
        # Check if the folder is in the container model
        self.assertTrue(self.container_ctrl.model.folders.__contains__(folder_id))

        picture_ids = asyncio.run(
            nachet.upload_pictures_known(
                cursor=self.cursor,
                user_id=self.user_id,
                pictures=[self.pic_encoded],
                container_controller=self.container_ctrl,
                picture_set_id=folder_id,
                seed_id=self.seed_id,
                zoom_level=None,
                nb_seeds=self.nb_seeds,
            )
        )
        self.assertEqual(len(picture_ids), 1)
        self.assertTrue(validator.is_valid_uuid(picture_ids[0]))

        # Verify if the picture is in the container
        picture_blob = asyncio.run(
            self.container_ctrl.get_picture_blob(
                cursor=self.cursor,
                picture_id=picture_ids[0],
                user_id=self.user_id,
            )
        )
        self.assertIsNotNone(picture_blob)
        # Verify if the picture is in the container model
        folder_model = self.container_ctrl.model.folders.get(folder_id)
        self.assertEqual(folder_model.pictures, picture_ids)

        # Without specifying the folder beforehand (it will create a new folder)
        picture_ids = asyncio.run(
            nachet.upload_pictures_known(
                cursor=self.cursor,
                user_id=self.user_id,
                pictures=[self.pic_encoded],
                container_controller=self.container_ctrl,
                picture_set_id=None,
                seed_id=self.seed_id,
                seed_name=None,
                zoom_level=None,
                nb_seeds=self.nb_seeds,
            )
        )
        self.assertEqual(len(picture_ids), 1)
        self.assertTrue(validator.is_valid_uuid(picture_ids[0]))

        # uploading multiple pictures
        picture_ids = asyncio.run(
            nachet.upload_pictures_known(
                cursor=self.cursor,
                user_id=self.user_id,
                pictures=[self.pic_encoded, self.pic_encoded],
                container_controller=self.container_ctrl,
                picture_set_id=None,
                seed_id=self.seed_id,
                zoom_level=None,
                nb_seeds=self.nb_seeds,
            )
        )
        self.assertEqual(len(picture_ids), 2)
        self.assertTrue(validator.is_valid_uuid(picture_ids[0]))
        self.assertTrue(validator.is_valid_uuid(picture_ids[1]))

    def test_upload_picture_known_error_user_not_found(self):
        """
        This test checks if the upload_picture_known function correctly raise an exception if the user given doesn't exist in db
        """

        with self.assertRaises(nachet.user.UserNotFoundError):
            asyncio.run(
                nachet.upload_pictures_known(
                    cursor=self.cursor,
                    user_id=uuid.uuid4(),
                    pictures=[self.pic_encoded, self.pic_encoded],
                    container_controller=self.container_ctrl,
                    picture_set_id=None,
                    seed_id=self.seed_id,
                    zoom_level=None,
                    nb_seeds=self.nb_seeds,
                )
            )

    def test_upload_picture_known_connection_error(self):
        """
        This test checks if the upload_picture_known function correctly raise an exception if the connection to the db fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")

        with self.assertRaises(Exception):
            asyncio.run(
                nachet.upload_pictures_known(
                    mock_cursor,
                    self.user_id,
                    pictures=[self.pic_encoded, self.pic_encoded],
                    container_controller=self.container_ctrl,
                    picture_set_id=None,
                    seed_id=self.seed_id,
                    zoom_level=None,
                    nb_seeds=self.nb_seeds,
                )
            )

    def test_get_picture_inference(self):
        """
        This test checks if the get_picture_inference function correctly returns the inference of a picture
        """
        picture_ids = asyncio.run(
            nachet.upload_pictures_known(
                cursor=self.cursor,
                user_id=self.user_id,
                pictures=[self.pic_encoded, self.pic_encoded],
                container_controller=self.container_ctrl,
                picture_set_id=self.folder_id,
                seed_id=self.seed_id,
                zoom_level=None,
                nb_seeds=self.nb_seeds,
            )
        )
        picture_id = picture_ids[0]
        inference = asyncio.run(
            nachet.register_inference_result(
                cursor=self.cursor,
                user_id=self.user_id,
                inference_dict=self.inference,
                picture_id=picture_id,
                pipeline_id=None,
                type=1,  # seeds = 1
            )
        )

        picture_inference = asyncio.run(
            nachet.get_picture_inference(
                cursor=self.cursor,
                user_id=self.user_id,
                picture_id=picture_id,
                inference_id=None,  # We are testing to see if we can fetch an image inference
            )
        )
        self.maxDiff = None
        self.assertDictEqual(picture_inference, inference)

        empty_picture_inference = asyncio.run(
            nachet.get_picture_inference(
                cursor=self.cursor,
                user_id=self.user_id,
                inference_id=None,
                picture_id=picture_ids[1],  # using the picture without an inference
            )
        )

        self.assertIsNone(empty_picture_inference)

    def test_get_picture_inference_by_inference_id(self):
        """
        This test checks if the get_picture_inference function correctly returns the inference of a picture
        """
        picture_ids = asyncio.run(
            nachet.upload_pictures_known(
                cursor=self.cursor,
                user_id=self.user_id,
                pictures=[self.pic_encoded],
                container_controller=self.container_ctrl,
                picture_set_id=self.folder_id,
                seed_id=self.seed_id,
                zoom_level=None,
                nb_seeds=self.nb_seeds,
            )
        )
        picture_id = picture_ids[0]
        inference = asyncio.run(
            nachet.register_inference_result(
                cursor=self.cursor,
                user_id=self.user_id,
                inference_dict=self.inference,
                picture_id=picture_id,
                pipeline_id=None,
                type=1,  # seeds = 1
            )
        )
        inference_id = inference["inference_id"]

        picture_inference = asyncio.run(
            nachet.get_picture_inference(
                cursor=self.cursor,
                user_id=self.user_id,
                inference_id=inference_id,
                picture_id=None,  # We are testing fetching by inference
            )
        )
        self.maxDiff = None
        self.assertDictEqual(picture_inference, inference)

    def test_get_picture_inference_error_missing_arguments(self):
        """
        This test checks if the get_pictures_inferences function correctly raise an exception if picture_id and inference_id are not provided
        """
        with self.assertRaises(ValueError):
            asyncio.run(nachet.get_picture_inference(self.cursor, uuid.uuid4()))

    def test_get_picture_inference_error_user_not_found(self):
        """
        This test checks if the get_pictures_inferences function correctly raise an exception if the user given doesn't exist in db
        """
        picture_ids = asyncio.run(
            nachet.upload_pictures_known(
                cursor=self.cursor,
                user_id=self.user_id,
                pictures=[self.pic_encoded],
                container_controller=self.container_ctrl,
                picture_set_id=self.folder_id,
                seed_id=self.seed_id,
                zoom_level=None,
                nb_seeds=self.nb_seeds,
            )
        )
        picture_id = picture_ids[0]
        with self.assertRaises(datastore.user.UserNotFoundError):
            asyncio.run(
                nachet.get_picture_inference(self.cursor, uuid.uuid4(), picture_id)
            )

    def test_get_picture_inference_error_connection_error(self):
        """
        This test checks if the get_pictures_inferences function correctly raise an exception if the connection to the db fails
        """
        picture_ids = asyncio.run(
            nachet.upload_pictures_known(
                cursor=self.cursor,
                user_id=self.user_id,
                pictures=[self.pic_encoded],
                container_controller=self.container_ctrl,
                picture_set_id=self.folder_id,
                seed_id=self.seed_id,
                zoom_level=None,
                nb_seeds=self.nb_seeds,
            )
        )
        picture_id = picture_ids[0]
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            asyncio.run(
                nachet.get_picture_inference(mock_cursor, self.user_id, picture_id)
            )

    def test_get_picture_inference_error_picture_not_found(self):
        """
        This test checks if the get_pictures_inferences function correctly raise an exception if the picture given doesn't exist in db
        """
        with self.assertRaises(datastore.picture.PictureNotFoundError):
            asyncio.run(
                nachet.get_picture_inference(self.cursor, self.user_id, uuid.uuid4())
            )

    def test_get_picture_inference_error_not_owner(self):
        """
        This test checks if the get_pictures_inferences function correctly raise an exception if the user is not the owner of the picture set
        """
        picture_ids = asyncio.run(
            nachet.upload_pictures_known(
                cursor=self.cursor,
                user_id=self.user_id,
                pictures=[self.pic_encoded],
                container_controller=self.container_ctrl,
                picture_set_id=self.folder_id,
                seed_id=self.seed_id,
                zoom_level=None,
                nb_seeds=self.nb_seeds,
            )
        )
        picture_id = picture_ids[0]

        not_owner_user_obj = asyncio.run(
            datastore.new_user(
                self.cursor, "notowner@email", self.connection_str, "test-user-nachet"
            )
        )
        not_owner_user_id = not_owner_user_obj.model.id

        with self.assertRaises(nachet.UserNotOwnerError):
            asyncio.run(
                nachet.get_picture_inference(self.cursor, not_owner_user_id, picture_id)
            )

        to_delete_container_id = list(not_owner_user_obj.model.containers.keys())[0]
        to_delete_container_controller = asyncio.run(
            datastore.get_container_controller(
                cursor=self.cursor,
                container_id=to_delete_container_id,
                connection_str=self.connection_str,
                credentials=None,
            )
        )
        to_delete_container_controller.container_client.delete_container()

    def test_get_picture_blob(self):
        """
        This test checks if the get_picture_blob function correctly returns the blob of a picture
        """
        # This test is not centered around Nachet needs; however we are leaving it here to showcase this behavior is handled
        picture_ids = asyncio.run(
            nachet.upload_pictures_known(
                cursor=self.cursor,
                user_id=self.user_id,
                pictures=[self.pic_encoded],
                container_controller=self.container_ctrl,
                picture_set_id=self.folder_id,
                seed_id=self.seed_id,
                zoom_level=None,
                nb_seeds=self.nb_seeds,
            )
        )
        picture_id = picture_ids[0]
        blob = asyncio.run(
            self.container_ctrl.get_picture_blob(
                cursor=self.cursor,
                picture_id=picture_id,
                user_id=self.user_id,
            )
        )
        blob_image = Image.frombytes("RGB", (1980, 1080), blob)

        difference = ImageChops.difference(blob_image, self.image)
        self.assertTrue(difference.getbbox() is None)

    def test_get_picture_blob_error_user_not_found(self):
        """
        This test checks if the get_pictures_inferences function correctly raise an exception if the user given doesn't exist in db
        """
        with self.assertRaises(datastore.picture.PictureNotFoundError):
            asyncio.run(
                self.container_ctrl.get_picture_blob(
                    cursor=self.cursor,
                    picture_id=uuid.uuid4(),
                    user_id=self.user_id,
                )
            )

    def test_get_picture_blob_error_not_owner(self):
        """
        This test checks if the get_pictures_inferences function correctly raise an exception if the user is not the owner of the picture set
        """
        picture_ids = asyncio.run(
            nachet.upload_pictures_known(
                cursor=self.cursor,
                user_id=self.user_id,
                pictures=[self.pic_encoded],
                container_controller=self.container_ctrl,
                picture_set_id=self.folder_id,
                seed_id=self.seed_id,
                zoom_level=None,
                nb_seeds=self.nb_seeds,
            )
        )
        picture_id = picture_ids[0]

        not_owner_user_obj = asyncio.run(
            datastore.new_user(
                self.cursor, "notowner@email", self.connection_str, "test-user-nachet"
            )
        )
        not_owner_user_id = not_owner_user_obj.model.id

        with self.assertRaises(datastore.UserNotOwnerError):
            asyncio.run(
                self.container_ctrl.get_picture_blob(
                    cursor=self.cursor,
                    picture_id=picture_id,
                    user_id=not_owner_user_id,
                )
            )

        to_delete_container_id = list(not_owner_user_obj.model.containers.keys())[0]
        to_delete_container_controller = asyncio.run(
            datastore.get_container_controller(
                cursor=self.cursor,
                container_id=to_delete_container_id,
                connection_str=self.connection_str,
                credentials=None,
            )
        )
        to_delete_container_controller.container_client.delete_container()


class test_picture_set(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        self.connection_str = BLOB_CONNECTION_STRING
        self.user_email = "testingss@email"
        self.user_obj = asyncio.run(
            datastore.new_user(
                self.cursor, self.user_email, self.connection_str, "test-user-nachet"
            )
        )
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = self.image.tobytes()
        # self.picture_hash= asyncio.run(azure_storage.generate_hash(self.pic_encoded))
        self.container_name = "test-container"
        self.user_id = datastore.User.get_id(self.user_obj)
        self.assertEqual(self.user_obj.model.id, self.user_id)
        # Get Container controller
        self.container_id = list(self.user_obj.model.containers.keys())[0]
        self.container_ctrl = asyncio.run(
            datastore.get_container_controller(
                cursor=self.cursor,
                container_id=self.container_id,
                connection_str=self.connection_str,
                credentials=None,
            )
        )
        # Containter should exists for picture to be uploaded into it
        self.assertTrue(self.container_ctrl.container_client.exists())

        self.seed_name = "test-name"
        self.seed_id = seed_query.new_seed(self.cursor, self.seed_name)

        self.folder_name = "test-nachet-datastore-folder"
        self.folder = asyncio.run(
            self.container_ctrl.create_folder(
                self.cursor,
                performed_by=self.user_id,
                folder_name=self.folder_name,
                nb_pictures=3,
                parent_folder_id=None,
            )
        )
        self.folder_id = self.folder.id

        self.nb_pictures = 3  # we uploaded 3 pictures
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "inference_result.json")
        with open(file_path) as file:
            self.inference = json.load(file)
            self.nb_seeds = self.inference["totalBoxes"]

        self.pictures_ids = asyncio.run(
            self.container_ctrl.upload_pictures(
                cursor=self.cursor,
                user_id=self.user_id,
                hashed_pictures=[self.pic_encoded, self.pic_encoded, self.pic_encoded],
                folder_id=self.folder_id,
                nb_objects=self.nb_seeds,
            )
        )

        self.dev_user_obj = asyncio.run(
            datastore.get_user(cursor=self.cursor, email=os.environ["DEV_USER_EMAIL"])
        )
        self.dev_user_id = self.dev_user_obj.model.id

        self.dev_container_id = list(self.dev_user_obj.model.containers.keys())[0]
        self.dev_container_controller = asyncio.run(
            datastore.get_container_controller(
                cursor=self.cursor,
                container_id=self.dev_container_id,
                connection_str=self.connection_str,
                credentials=None,
            )
        )

    def tearDown(self):
        self.con.rollback()
        self.container_ctrl.container_client.delete_container()
        db.end_query(self.con, self.cursor)

    def test_get_picture_sets_info(self):
        """
        Test the get_picture_sets_info function
        """
        picture_sets_info = asyncio.run(
            nachet.get_picture_sets_info(self.cursor, self.user_id)
        )

        self.assertEqual(
            len(picture_sets_info), 2, "there is a default folder and one we created"
        )

        for picture_set in picture_sets_info:
            if picture_set["picture_set_id"] == self.folder_id:
                pictures = picture_set["pictures"]
                self.assertEqual(len(pictures), self.nb_pictures)
                for pic in pictures:
                    self.assertIn(uuid.UUID(pic["picture_id"]), self.pictures_ids)
                    # We only uploaded the pictures without specifying the seed, nor giving an Inference
                    self.assertFalse(pic["is_validated"])
                    self.assertFalse(pic["inference_exist"])

        # Updating a picture with an Inference
        inference = asyncio.run(
            nachet.register_inference_result(
                self.cursor, self.user_id, self.inference, self.pictures_ids[0], None
            )
        )  # Updating a picture with an Inference
        asyncio.run(
            nachet.register_inference_result(
                self.cursor, self.user_id, self.inference, self.pictures_ids[1], None
            )
        )
        # Validating only the first one
        asyncio.run(
            nachet.new_perfect_inference_feeback(
                self.cursor,
                inference["inference_id"],
                self.user_id,
                [box["box_id"] for box in inference["boxes"]],
            )
        )

        picture_sets_info = asyncio.run(
            nachet.get_picture_sets_info(self.cursor, self.user_id)
        )

        self.assertEqual(
            len(picture_sets_info), 2, "there is a default folder and one we created"
        )

        for picture_set in picture_sets_info:
            if picture_set["picture_set_id"] == str(self.folder_id):
                pictures = picture_set["pictures"]
                self.assertEqual(len(pictures), self.nb_pictures)
                for pic in pictures:
                    self.assertIn(uuid.UUID(pic["picture_id"]), self.pictures_ids)
                    if str(pic["picture_id"]) == str(self.pictures_ids[0]):
                        self.assertTrue(pic["inference_exist"])
                        self.assertTrue(pic["is_validated"])
                    elif str(pic["picture_id"]) == str(self.pictures_ids[1]):
                        # We did not validate the second inference
                        self.assertTrue(pic["inference_exist"])
                        self.assertFalse(pic["is_validated"])
                    else:
                        self.assertFalse(pic["inference_exist"])
                        self.assertFalse(pic["is_validated"])

    def test_get_picture_sets_info_error_user_not_found(self):
        """
        This test checks if the get_picture_sets_info function correctly raise an exception if the user given doesn't exist in db
        """
        with self.assertRaises(datastore.user.UserNotFoundError):
            asyncio.run(nachet.get_picture_sets_info(self.cursor, uuid.uuid4()))

    def test_get_picture_sets_info_error_connection_error(self):
        """
        This test checks if the get_picture_sets_info function correctly raise an exception if the connection to the db fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            asyncio.run(nachet.get_picture_sets_info(mock_cursor, self.user_id))

    def test_find_validated_pictures(self):
        """
        This test checks if the find_validated_pictures function correctly returns the validated pictures of a picture_set
        """

        self.assertEqual(
            len(
                asyncio.run(
                    nachet.find_validated_pictures(
                        cursor=self.cursor,
                        user_id=self.user_id,
                        picture_set_id=self.folder_id,
                    )
                )
            ),
            0,
            "No validated pictures should be found",
        )

        inferences = []
        for picture_id in self.pictures_ids:
            # Using deepcopy to ensure each inference is a unique object without shared references
            inference_copy = deepcopy(self.inference)
            inference = asyncio.run(
                nachet.register_inference_result(
                    self.cursor,
                    self.user_id,
                    inference_copy,
                    picture_id,
                    None,
                )
            )
            inferences.append(inference)
        # Validating only one inference
        asyncio.run(
            nachet.new_perfect_inference_feeback(
                self.cursor,
                inferences[0]["inference_id"],
                self.user_id,
                [box["box_id"] for box in inferences[0]["boxes"]],
            )
        )
        nb_validated = 1

        self.assertEqual(
            len(
                asyncio.run(
                    nachet.find_validated_pictures(
                        cursor=self.cursor,
                        user_id=self.user_id,
                        picture_set_id=self.folder_id,
                    )
                )
            ),
            nb_validated,
            "One validated pictures should be found",
        )
        # Validating all the inferences
        asyncio.run(
            nachet.new_perfect_inference_feeback(
                self.cursor,
                inferences[1]["inference_id"],
                self.user_id,
                [box["box_id"] for box in inferences[1]["boxes"]],
            )
        )
        nb_validated += 1
        asyncio.run(
            nachet.new_perfect_inference_feeback(
                self.cursor,
                inferences[2]["inference_id"],
                self.user_id,
                [box["box_id"] for box in inferences[2]["boxes"]],
            )
        )
        nb_validated += 1

        self.assertEqual(
            len(
                asyncio.run(
                    nachet.find_validated_pictures(
                        cursor=self.cursor,
                        user_id=self.user_id,
                        picture_set_id=self.folder_id,
                    )
                )
            ),
            nb_validated,
            "3 validated pictures should be found",
        )

    def test_find_validated_pictures_error_user_not_found(self):
        """
        This test checks if the find_validated_pictures function correctly raise an exception if the user given doesn't exist in db
        """
        with self.assertRaises(nachet.user.UserNotFoundError):
            asyncio.run(
                nachet.find_validated_pictures(
                    self.cursor, uuid.uuid4(), self.folder_id
                )
            )

    def test_find_validated_pictures_error_connection_error(self):
        """
        This test checks if the find_validated_pictures function correctly raise an exception if the connection to the db fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            asyncio.run(
                nachet.find_validated_pictures(
                    mock_cursor, self.user_id, self.folder_id
                )
            )

    def test_find_validated_pictures_error_picture_set_not_found(self):
        """
        This test checks if the find_validated_pictures function correctly raise an exception if the picture set given doesn't exist in db
        """
        with self.assertRaises(nachet.picture.PictureSetNotFoundError):
            asyncio.run(
                nachet.find_validated_pictures(self.cursor, self.user_id, uuid.uuid4())
            )

    def test_find_validated_pictures_error_not_owner(self):
        """
        This test checks if the find_validated_pictures function correctly raise an exception if the user is not the owner of the picture set
        """
        not_owner_user_obj = asyncio.run(
            datastore.new_user(
                self.cursor, "notowner@email", self.connection_str, "test-user-nachet"
            )
        )
        not_owner_user_id = datastore.User.get_id(not_owner_user_obj)

        with self.assertRaises(nachet.UserNotOwnerError):
            asyncio.run(
                nachet.find_validated_pictures(
                    self.cursor, not_owner_user_id, self.folder_id
                )
            )

        to_delete_container_id = list(not_owner_user_obj.model.containers.keys())[0]
        to_delete_container_controller = asyncio.run(
            datastore.get_container_controller(
                cursor=self.cursor,
                container_id=to_delete_container_id,
                connection_str=self.connection_str,
                credentials=None,
            )
        )
        to_delete_container_controller.container_client.delete_container()

    def test_delete_picture_set_with_archive(self):
        """
        This test checks if the delete_picture_set_with_archive function correctly archive the picture set in dev container and delete it from user container
        """
        # Create inferences for pictures in the picture set
        inferences = []
        for picture_id in self.pictures_ids:
            # Using deepcopy to ensure each inference is a unique object without shared references
            inference_copy = deepcopy(self.inference)
            inference = asyncio.run(
                nachet.register_inference_result(
                    cursor=self.cursor,
                    user_id=self.user_id,
                    inference_dict=inference_copy,
                    picture_id=picture_id,
                    pipeline_id=None,
                    type=1,
                )
            )
            inferences.append(inference)
        # Validate 2 of 3 pictures in the picture set
        self.assertTrue(len(self.pictures_ids) == 3)
        asyncio.run(
            nachet.new_perfect_inference_feeback(
                self.cursor,
                inferences[1]["inference_id"],
                self.user_id,
                [box["box_id"] for box in inferences[1]["boxes"]],
            )
        )
        asyncio.run(
            nachet.new_perfect_inference_feeback(
                self.cursor,
                inferences[2]["inference_id"],
                self.user_id,
                [box["box_id"] for box in inferences[2]["boxes"]],
            )
        )
        validated_pictures = asyncio.run(
            nachet.find_validated_pictures(self.cursor, self.user_id, self.folder_id)
        )

        dev_nb_folders = len(
            asyncio.run(nachet.get_picture_sets_info(self.cursor, self.dev_user_id))
        )
        # Check there is the right number of picture sets in db user
        self.assertEqual(
            len(asyncio.run(nachet.get_picture_sets_info(self.cursor, self.user_id))),
            2,
            "There should be 2 folders for the user; one being folder created by default, one being the one created for the test",
        )

        dev_picture_set_id = asyncio.run(
            nachet.delete_picture_set_with_archive(
                cursor=self.cursor,
                user_id=self.user_id,
                picture_set_id=self.folder_id,
                container_controller=self.container_ctrl,
            )
        )
        # This is the root folder created for all the user's archive (it contains the folder archived)
        self.dev_container_controller.fetch_all_data(cursor=self.cursor)
        dev_archive_user_folder_model = self.dev_container_controller.model.folders.get(
            dev_picture_set_id
        )
        dev_archive_user_folder_id = dev_archive_user_folder_model.parent_id

        # Check there is the right number of picture sets in db for each user after moving
        self.assertEqual(
            len(asyncio.run(nachet.get_picture_sets_info(self.cursor, self.user_id))),
            1,
        )
        self.assertEqual(
            len(
                asyncio.run(nachet.get_picture_sets_info(self.cursor, self.dev_user_id))
            ),
            dev_nb_folders + 2,
            "We moved the folder of picture from a new user container to the dev container. This means the dev container contains 2 new folder; one for the user (since he never archived stuff before) and one for the deleted folder",
        )

        # Check blobs have also moved in blob storage
        for picture_id in validated_pictures:
            with self.assertRaises(datastore.picture.PictureSetNotFoundError):
                asyncio.run(
                    self.container_ctrl.get_picture_blob(
                        cursor=self.cursor, picture_id=picture_id, user_id=self.user_id
                    )
                )
            blob = asyncio.run(
                self.dev_container_controller.get_picture_blob(
                    cursor=self.cursor, picture_id=picture_id, user_id=self.dev_user_id
                )
            )
            self.assertEqual(blob, self.pic_encoded)

        # TEAR DOWN
        # Delete the user folder in the blob storage
        asyncio.run(
            self.dev_container_controller.delete_folder_permanently(
                cursor=self.cursor,
                user_id=self.dev_user_id,
                folder_id=dev_archive_user_folder_id,  # This should delete all the created folders in the dev archive container
            )
        )

    def test_delete_picture_set_with_archive_error_user_not_found(self):
        """
        This test checks if the delete_picture_set_with_archive function correctly raise an exception if the user given doesn't exist in db
        """
        with self.assertRaises(nachet.user.UserNotFoundError):
            asyncio.run(
                nachet.delete_picture_set_with_archive(
                    cursor=self.cursor,
                    user_id=uuid.uuid4(),
                    picture_set_id=self.folder_id,
                    container_controller=self.container_ctrl,
                )
            )

    def test_delete_picture_set_with_archive_error_connection_error(self):
        """
        This test checks if the delete_picture_set_with_archive function correctly raise an exception if the connection to the db fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            asyncio.run(
                nachet.delete_picture_set_with_archive(
                    cursor=mock_cursor,
                    user_id=self.user_id,
                    picture_set_id=self.folder_id,
                    container_controller=self.container_ctrl,
                )
            )

    def test_delete_picture_set_with_archive_error_picture_set_not_found(self):
        """
        This test checks if the delete_picture_set_with_archive function correctly raise an exception if the picture set given doesn't exist in db
        """
        with self.assertRaises(nachet.picture.PictureSetNotFoundError):
            asyncio.run(
                nachet.delete_picture_set_with_archive(
                    cursor=self.cursor,
                    user_id=self.user_id,
                    picture_set_id=uuid.uuid4(),
                    container_controller=self.container_ctrl,
                )
            )

    def test_delete_picture_set_with_archive_error_not_owner(self):
        """
        This test checks if the delete_picture_set_with_archive function correctly raise an exception if the user is not the owner of the picture set
        """
        not_owner_user_obj = asyncio.run(
            datastore.new_user(
                self.cursor, "notowner@email", self.connection_str, "test-user-nachet"
            )
        )
        not_owner_user_id = datastore.User.get_id(not_owner_user_obj)

        with self.assertRaises(nachet.UserNotOwnerError):
            asyncio.run(
                nachet.delete_picture_set_with_archive(
                    cursor=self.cursor,
                    user_id=not_owner_user_id,
                    picture_set_id=self.folder_id,
                    container_controller=self.container_ctrl,
                )
            )

        to_delete_container_id = list(not_owner_user_obj.model.containers.keys())[0]
        to_delete_container_controller = asyncio.run(
            datastore.get_container_controller(
                cursor=self.cursor,
                container_id=to_delete_container_id,
                connection_str=self.connection_str,
                credentials=None,
            )
        )
        to_delete_container_controller.container_client.delete_container()

    def test_delete_picture_set_with_archive_error_default_folder(self):
        """
        This test checks if the delete_picture_set_with_archive function correctly raise an exception if the user want to delete the folder "General"
        """
        # Deprecated

        # general_folder_id = datastore.user.get_default_picture_set(
        #     self.cursor, self.user_id
        # )
        # with self.assertRaises(nachet.picture.PictureSetDeleteError):
        #     asyncio.run(
        #         nachet.delete_picture_set_with_archive(
        #             self.cursor,
        #             str(self.user_id),
        #             str(general_folder_id),
        #             self.container_client,
        #         )
        #     )


class test_feedback(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        self.connection_str = BLOB_CONNECTION_STRING
        self.user_email = "testingss@email"
        self.user_obj = asyncio.run(
            datastore.new_user(
                self.cursor, self.user_email, self.connection_str, "test-user-nachet"
            )
        )
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = self.image.tobytes()
        #
        self.container_name = "test-container"
        self.user_id = datastore.User.get_id(self.user_obj)
        self.assertEqual(self.user_obj.model.id, self.user_id)
        # Get Container controller
        self.container_id = list(self.user_obj.model.containers.keys())[0]
        self.container_ctrl = asyncio.run(
            datastore.get_container_controller(
                cursor=self.cursor,
                container_id=self.container_id,
                connection_str=self.connection_str,
                credentials=None,
            )
        )
        # Containter should exists for picture to be uploaded into it
        self.assertTrue(self.container_ctrl.container_client.exists())

        self.seed_name = "test-name"
        self.seed_id = seed_query.new_seed(self.cursor, self.seed_name)
        self.number_seed_detected = 6

        self.folder_name = "test-nachet-datastore-folder"
        self.folder = asyncio.run(
            self.container_ctrl.create_folder(
                self.cursor,
                performed_by=self.user_id,
                folder_name=self.folder_name,
                nb_pictures=1,
                parent_folder_id=None,
            )
        )
        self.folder_id = self.folder.id
        self.pictures_ids = asyncio.run(
            self.container_ctrl.upload_pictures(
                cursor=self.cursor,
                user_id=self.user_id,
                hashed_pictures=[self.pic_encoded, self.pic_encoded, self.pic_encoded],
                folder_id=self.folder_id,
                nb_objects=self.number_seed_detected,
            )
        )
        self.nb_pictures = 3  # we uploaded 3 pictures

        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "inference_result.json")
        with open(file_path) as file:
            self.inference = json.load(file)

        self.registered_inference = asyncio.run(
            nachet.register_inference_result(
                cursor=self.cursor,
                user_id=self.user_id,
                inference_dict=self.inference,
                picture_id=self.pictures_ids[0],
                pipeline_id=None,
                type=nachet.ObjectType.SEED.value,
            )
        )
        self.registered_inference["user_id"] = self.user_id
        self.mock_box = {"topX": 123, "topY": 456, "bottomX": 789, "bottomY": 123}
        self.inference_id = self.registered_inference.get("inference_id")
        self.boxes_id: list[uuid.UUID] = []
        self.top_id = []
        for box in self.registered_inference["boxes"]:
            self.boxes_id.append(box["box_id"])
            self.top_id.append(box["top_id"])
        self.unreal_seed_name = "unreal_seed"
        self.unreal_seed_id = nachet.seed.new_seed(self.cursor, self.unreal_seed_name)

    def tearDown(self):
        self.con.rollback()
        self.container_ctrl.container_client.delete_container()
        db.end_query(self.con, self.cursor)

    def test_new_perfect_inference_feedback(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly updates the inference object after a perfect feedback is given
        """
        asyncio.run(
            nachet.new_perfect_inference_feeback(
                cursor=self.cursor,
                inference_id=self.inference_id,
                user_id=self.user_id,
                boxes_id=self.boxes_id,
            )
        )
        for i in range(len(self.boxes_id)):
            object = nachet.inference.get_inference_object(
                self.cursor, self.boxes_id[i]
            )
            verified_id = object[4]
            top_id = object[5]
            # verified_id must be equal to top_id
            self.assertEqual(verified_id, self.top_id[i])
            self.assertEqual(verified_id, top_id)
            # valid column must be true
            self.assertTrue(object[5])

    def test_new_perfect_inference_feedback_verified_inference(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly if the inference given is already verified
        """
        asyncio.run(
            nachet.new_perfect_inference_feeback(
                self.cursor, self.inference_id, self.user_id, self.boxes_id
            )
        )
        self.assertTrue(
            nachet.inference.is_inference_verified(self.cursor, self.inference_id)
        )

        # There should not be an error raise based on user's request
        # with self.assertRaises(nachet.inference.InferenceAlreadyVerifiedError):
        #     asyncio.run(
        #         nachet.new_perfect_inference_feeback(
        #             self.cursor, self.inference_id, self.user_id, self.boxes_id
        #         )
        #     )
        asyncio.run(
            nachet.new_perfect_inference_feeback(
                self.cursor, self.inference_id, self.user_id, self.boxes_id
            )
        )
        # There should not be an error raise based on user's request
        self.assertTrue(
            nachet.inference.is_inference_verified(self.cursor, self.inference_id)
        )

    def test_new_perfect_inference_feedback_error_inference_not_found(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly raise an exception if the inference given doesn't exist in db
        """
        with self.assertRaises(nachet.inference.InferenceNotFoundError):
            asyncio.run(
                nachet.new_perfect_inference_feeback(
                    cursor=self.cursor,
                    inference_id=uuid.uuid4(),
                    user_id=self.user_id,
                    boxes_id=self.boxes_id,
                )
            )

    def test_new_perfect_inference_feedback_error_inference_object_not_found(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly raise an exception if one of the inference object given doesn't exist in db
        """
        with self.assertRaises(nachet.inference.InferenceObjectNotFoundError):
            asyncio.run(
                nachet.new_perfect_inference_feeback(
                    cursor=self.cursor,
                    inference_id=self.inference_id,
                    user_id=self.user_id,
                    boxes_id=[self.boxes_id[0], uuid.uuid4()],
                )
            )

    def test_new_perfect_inference_feedback_error_user_not_found(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly raise an exception if the user given doesn't exist in db
        """
        with self.assertRaises(nachet.user.UserNotFoundError):
            asyncio.run(
                nachet.new_perfect_inference_feeback(
                    cursor=self.cursor,
                    inference_id=self.inference_id,
                    user_id=uuid.uuid4(),
                    boxes_id=self.boxes_id,
                )
            )

    def test_new_perfect_inference_feedback_connection_error(self):
        """
        This test checks if the new_perfect_inference_feeback function correctly raise an exception if the connection to the db fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            asyncio.run(
                nachet.new_perfect_inference_feeback(
                    cursor=mock_cursor,
                    inference_id=self.inference_id,
                    user_id=self.user_id,
                    boxes_id=self.boxes_id,
                )
            )

    def test_new_correction_inference_feedback(self):
        """
        This test checks if the new_correction_inference_feeback function correctly
        """
        self.assertTrue(validator.is_valid_uuid(self.inference_id))
        # temporary fix until we fix FE
        self.registered_inference["inferenceId"] = self.inference_id
        self.registered_inference["userId"] = self.user_id

        for box in self.registered_inference["boxes"]:
            self.boxes_id.append(box["box_id"])
            self.top_id.append(box["top_id"])
            # Making top guess the right seed
            box["classId"] = nachet.seed.get_seed_id(self.cursor, box["label"])
            box["boxId"] = box["box_id"]
        asyncio.run(
            nachet.new_correction_inference_feedback(
                cursor=self.cursor,
                inference_dict=self.registered_inference,
                type=nachet.ObjectType.SEED.value,
            )
        )
        for i in range(len(self.boxes_id)):
            object = nachet.inference.get_inference_object(
                cursor=self.cursor, inference_object_id=self.boxes_id[i]
            )
            # verified_id must be equal to top_id
            self.assertEqual(object[4], self.top_id[i])
            # valid column must be true
            self.assertTrue(object[6])

    def test_new_correction_inference_feedback_new_guess(self):
        """
        This test checks if the new_correction_inference_feeback function correctly when another guess is verified
        """
        self.assertTrue(validator.is_valid_uuid(self.inference_id))
        new_top_ids = []
        previous_top_ids = []
        index = 0
        for box in self.registered_inference["boxes"]:
            box["label"] = box["topN"][1][
                "label"
            ]  # Setting another guess than the top one
            # Making the second guess the right seed
            box["classId"] = nachet.seed.get_seed_id(self.cursor, box["label"])
            new_top_ids.append(box["topN"][1]["object_id"])
            box["boxId"] = box["box_id"]

            object_db = nachet.inference.get_inference_object(
                self.cursor, self.boxes_id[index]
            )
            index += 1
            previous_top_ids.append(object_db[4])
        # temporary fix until we fix FE
        self.registered_inference["inferenceId"] = self.inference_id
        self.registered_inference["userId"] = self.user_id
        asyncio.run(
            nachet.new_correction_inference_feedback(
                cursor=self.cursor,
                inference_dict=self.registered_inference,
                type=nachet.ObjectType.SEED.value,
            )
        )
        for i in range(len(self.boxes_id)):
            object_db = nachet.inference.get_inference_object(
                self.cursor, self.boxes_id[i]
            )
            # verified_id must be equal to the expected top_id and different from the original id
            self.assertEqual(object_db[4], new_top_ids[i])
            self.assertNotEqual(object_db[4], previous_top_ids[i])
            # valid column must be true
            self.assertTrue(object_db[6])

    def test_new_correction_inference_feedback_box_edited(self):
        """
        This test checks if the new_correction_inference_feeback function correctly when the box metadata is updated
        """
        self.assertTrue(validator.is_valid_uuid(self.inference_id))
        for box in self.registered_inference["boxes"]:
            box["box"] = self.mock_box
            box["boxId"] = box["box_id"]
            # Making top guess the right seed
            box["classId"] = nachet.seed.get_seed_id(self.cursor, box["label"])
        # temporary fix until we fix FE
        self.registered_inference["inferenceId"] = self.inference_id
        self.registered_inference["userId"] = self.user_id
        asyncio.run(
            nachet.new_correction_inference_feedback(
                self.cursor, self.registered_inference, 1
            )
        )
        for box in self.registered_inference["boxes"]:
            object_db = nachet.inference.get_inference_object(
                self.cursor, box["box_id"]
            )
            # The new box metadata must be updated
            self.assertDictEqual(object_db[1], self.mock_box)
            # The top_id must be equal to the previous top_id
            self.assertEqual(object_db[4], box["top_id"])
            # valid column must be true
            self.assertTrue(object_db[6])

    def test_new_correction_inference_feedback_not_guess(self):
        """
        This test checks if the new_correction_inference_feeback function correctly when the box is not a guess
        """
        self.assertTrue(validator.is_valid_uuid(self.inference_id))
        for box in self.registered_inference["boxes"]:
            box["boxId"] = box["box_id"]
            # Making the right seed a seed not in the list of guess from the pipeline
            box["label"] = self.unreal_seed_name
            box["classId"] = self.unreal_seed_id
        # temporary fix until we fix FE
        self.registered_inference["inferenceId"] = self.inference_id
        self.registered_inference["userId"] = self.user_id
        asyncio.run(
            nachet.new_correction_inference_feedback(
                self.cursor, self.registered_inference, nachet.ObjectType.SEED.value
            )
        )
        for i in range(len(self.boxes_id)):
            object_db = nachet.inference.get_inference_object(
                self.cursor, self.boxes_id[i]
            )
            # verified_id must be equal to the new_top_id which was created during the correction
            new_top_id = nachet.inference.get_seed_object_id(
                self.cursor, self.unreal_seed_id, object_db[0]
            )
            self.assertTrue(validator.is_valid_uuid(new_top_id))
            self.assertEqual(object_db[4], new_top_id)
            # valid column must be true
            self.assertTrue(object_db[6])

    def test_new_correction_inference_feedback_not_valid(self):
        """
        This test checks if the new_correction_inference_feeback function correctly when the box is not a guess
        """
        self.assertTrue(validator.is_valid_uuid(self.inference_id))
        for box in self.registered_inference["boxes"]:
            box["boxId"] = box["box_id"]
            # Mocking User deleting Box -> There are no guess for that box
            box["label"] = ""
            box["classId"] = ""
        # temporary fix until we fix FE
        self.registered_inference["inferenceId"] = self.inference_id
        self.registered_inference["userId"] = self.user_id
        asyncio.run(
            nachet.new_correction_inference_feedback(
                self.cursor, self.registered_inference, 1
            )
        )
        for i in range(len(self.boxes_id)):
            object_db = nachet.inference.get_inference_object(
                self.cursor, self.boxes_id[i]
            )
            # The object still exists; The pipeline detected it and we must keep it for training purposes.
            self.assertTrue(validator.is_valid_uuid(object_db[0]))
            # verified_id must not be an id
            self.assertEqual(object_db[4], None)
            # valid column must be false
            self.assertFalse(object_db[6])

    def test_new_correction_inference_feedback_unknown_seed(self):
        """
        This test checks if the new_correction_inference_feeback function correctly when the box is not a guess
        """
        self.assertTrue(validator.is_valid_uuid(self.inference_id))
        unknown_seed = "unknown_seed_name_for_testing (Should not exists)"
        seeds = seed_query.get_all_seeds_names(cursor=self.cursor)
        self.assertNotIn(unknown_seed, seeds)
        for box in self.registered_inference["boxes"]:
            box["label"] = unknown_seed
            box["classId"] = ""
        # temporary fix until we fix FE
        self.registered_inference["inferenceId"] = self.inference_id
        self.registered_inference["userId"] = self.user_id
        for box in self.registered_inference["boxes"]:
            box["boxId"] = box["box_id"]
        asyncio.run(
            nachet.new_correction_inference_feedback(
                self.cursor, self.registered_inference, 1
            )
        )
        # verify a neew seed has been created for this:
        seeds = seed_query.get_all_seeds_names(cursor=self.cursor)
        self.assertNotIn(unknown_seed, seeds)

        for i in range(len(self.boxes_id)):
            object_db = nachet.inference.get_inference_object(
                self.cursor, self.boxes_id[i]
            )
            # verified_id must be equal to an id
            self.assertTrue(validator.is_valid_uuid(str(object_db[4])))
            # valid column must be true
            self.assertTrue(object_db[6])
