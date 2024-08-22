"""
This is a test script for the highest level of the datastore packages. 
It tests the functions in the __init__.py files of the datastore packages.
"""

import asyncio
import io
from PIL import Image
import unittest
import json
import datastore.db.__init__ as db
import datastore.__init__ as datastore
import datastore.fertiscan as fertiscan
import datastore.db.metadata.inspection as metadata
import datastore.db.metadata.validator as validator
import datastore.db.queries.metric as metric
from datastore.db.queries import sub_label, nutrients, inspection, picture
import os

BLOB_CONNECTION_STRING = os.environ["FERTISCAN_STORAGE_URL"]
if BLOB_CONNECTION_STRING is None or BLOB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_STORAGE_URL_TESTING is not set")

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

BLOB_ACCOUNT = os.environ["FERTISCAN_BLOB_ACCOUNT"]
if BLOB_ACCOUNT is None or BLOB_ACCOUNT == "":
    raise ValueError("NACHET_BLOB_ACCOUNT is not set")

BLOB_KEY = os.environ["FERTISCAN_BLOB_KEY"]
if BLOB_KEY is None or BLOB_KEY == "":
    raise ValueError("NACHET_BLOB_KEY is not set")


class TestDatastore(unittest.IsolatedAsyncioTestCase):
    def setUp(self):

        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "analyse.json")
        with open(file_path, "r") as file:
            self.analysis_json = json.load(file)
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        self.user_email = "testesss@email"
        self.user_obj = asyncio.run(
            datastore.new_user(
                self.cursor, self.user_email, BLOB_CONNECTION_STRING, "test-user"
            )
        )

        self.user_id = datastore.User.get_id(self.user_obj)
        self.container_client = asyncio.run(
            datastore.get_user_container_client(
                user_id=self.user_id,
                storage_url=BLOB_CONNECTION_STRING,
                account=BLOB_ACCOUNT,
                key=BLOB_KEY,
                tier="test-user",
            )
        )

        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = self.image.tobytes()

    def tearDown(self):
        self.con.rollback()
        self.container_client.delete_container()
        db.end_query(self.con, self.cursor)

    def test_register_analysis(self):
        self.assertTrue(self.container_client.exists())
        analysis = asyncio.run(
            fertiscan.register_analysis(
                self.cursor,
                self.container_client,
                self.user_id,
                [self.pic_encoded, self.pic_encoded],
                self.analysis_json,
            )
        )
        self.assertIsNotNone(analysis)
        self.assertTrue(validator.is_valid_uuid(analysis["inspection_id"]))

        metrics = metric.get_metric_by_label(
            self.cursor, str(analysis["product"]["label_id"])
        )

        self.assertIsNotNone(metrics)
        self.assertEqual(
            len(metrics), 4
        )  # There are 4 metrics in the analysis_json (1 volume, 1 density, 2 weight )

        nutrients_data = nutrients.get_all_micronutrients(
            cursor=self.cursor, label_id=str(analysis["product"]["label_id"])
        )
        self.assertIsNotNone(nutrients_data)

        self.assertEqual(
            len(nutrients_data), 6
        )  # There are 2 nutrients in the analysis_json
        sub_labels = sub_label.get_sub_label_json(
            self.cursor, str(analysis["product"]["label_id"])
        )
        self.assertIsNotNone(sub_labels)

    def test_register_analysis_invalid_user(self):
        with self.assertRaises(Exception):
            asyncio.run(
                fertiscan.register_analysis(
                    self.cursor,
                    self.container_client,
                    "invalid_user_id",
                    [self.pic_encoded, self.pic_encoded],
                    self.analysis_json,
                )
            )

    def test_register_analysy_missing_key(self):
        self.analysis_json.pop("specification_en", None)
        with self.assertRaises(fertiscan.data_inspection.MissingKeyError):
            asyncio.run(
                fertiscan.register_analysis(
                    self.cursor,
                    self.container_client,
                    self.user_id,
                    [self.pic_encoded, self.pic_encoded],
                    {},
                )
            )

    def test_get_full_inspection_json(self):
        formatted_analysis = metadata.build_inspection_import(self.analysis_json)
        picture_set_id = picture.new_picture_set(
            self.cursor, json.dumps({}), self.user_id
        )

        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]

        data = asyncio.run(
            fertiscan.get_full_inspection_json(self.cursor, inspection_id)
        )
        data = json.loads(data)
        self.assertEqual(data["inspection_id"], str(inspection_id))
