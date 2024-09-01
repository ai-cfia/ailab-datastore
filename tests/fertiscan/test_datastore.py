"""
This is a test script for the highest level of the datastore packages.
It tests the functions in the __init__.py files of the datastore packages.
"""

import asyncio
import io
import json
import os
import unittest

# from azure.storage.blob import ContainerClient
from azure.storage.blob import ContainerClient
from dotenv import load_dotenv
from PIL import Image

import datastore.__init__ as datastore
import datastore.db.__init__ as db
import datastore.db.metadata.inspection as metadata
import datastore.db.metadata.validator as validator
import datastore.db.queries.metric as metric
import datastore.fertiscan as fertiscan
from datastore.db.queries import (
    inspection,
    label,
    nutrients,
    picture,
    specification,
    sub_label,
)

load_dotenv()

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

TEST_INSPECTION_JSON_PATH = "tests/fertiscan/inspection.json"


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
        self.tier = "test-user"
        self.user = asyncio.run(
            datastore.new_user(
                self.cursor, self.user_email, BLOB_CONNECTION_STRING, self.tier
            )
        )
        self.container_client = ContainerClient.from_connection_string(
            conn_str=BLOB_CONNECTION_STRING,
            container_name=f"{self.tier}-{self.user.id}",
        )

        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = self.image.tobytes()

        if len(self.analysis_json.get("cautions_en")) >= len(
            self.analysis_json.get("cautions_fr")
        ):
            self.nb_cautions = len(self.analysis_json.get("cautions_en"))
        elif len(self.analysis_json.get("cautions_en")) < len(
            self.analysis_json.get("cautions_fr")
        ):
            self.nb_cautions = len(self.analysis_json.get("cautions_fr"))

        if len(self.analysis_json.get("instructions_en")) >= len(
            self.analysis_json.get("instructions_fr")
        ):
            self.nb_instructions = len(self.analysis_json.get("instructions_en"))
        elif len(self.analysis_json.get("instructions_en")) < len(
            self.analysis_json.get("instructions_fr")
        ):
            self.nb_instructions = len(self.analysis_json.get("instructions_fr"))

        if len(self.analysis_json.get("first_aid_en")) >= len(
            self.analysis_json.get("first_aid_fr")
        ):
            self.nb_first_aid = len(self.analysis_json.get("first_aid_en"))
        elif len(self.analysis_json.get("first_aid_en")) < len(
            self.analysis_json.get("first_aid_fr")
        ):
            self.nb_first_aid = len(self.analysis_json.get("first_aid_fr"))

        self.nb_specifications = len(self.analysis_json.get("specifications_en")) + len(
            self.analysis_json.get("specifications_fr")
        )

        self.nb_guaranteed = len(self.analysis_json.get("guaranteed_analysis"))

        self.nb_ingredients = len(self.analysis_json.get("ingredients_en")) + len(
            self.analysis_json.get("ingredients_fr")
        )

        self.nb_micronutrients = len(self.analysis_json.get("micronutrients_en")) + len(
            self.analysis_json.get("micronutrients_fr")
        )

        self.nb_weight = len(self.analysis_json.get("weight"))

    def tearDown(self):
        try:
            self.con.rollback()
            db.end_query(self.con, self.cursor)
            self.container_client.delete_container()
        except Exception as e:
            print(e)

    def test_register_analysis(self):
        self.assertTrue(self.container_client.exists())
        analysis = asyncio.run(
            fertiscan.register_analysis(
                self.cursor,
                self.container_client,
                self.user.id,
                [self.pic_encoded, self.pic_encoded],
                self.analysis_json,
            )
        )
        self.assertIsNotNone(analysis)
        self.assertTrue(validator.is_valid_uuid(analysis["inspection_id"]))
        inspection_id = analysis["inspection_id"]

        self.assertTrue(validator.is_valid_uuid(analysis["product"]["label_id"]))
        label_id = analysis["product"]["label_id"]

        metrics = metric.get_metric_by_label(
            self.cursor, str(analysis["product"]["label_id"])
        )

        self.assertIsNotNone(metrics)
        self.assertEqual(
            len(metrics), 4
        )  # There are 4 metrics in the analysis_json (1 volume, 1 density, 2 weight )

        specifications = specification.get_all_specifications(
            cursor=self.cursor, label_id=str(analysis["product"]["label_id"])
        )
        self.assertIsNotNone(specifications)
        self.assertEqual(
            len(specifications), self.nb_specifications
        )  # There are 2 specifications in the analysis_json

        nutrients_data = nutrients.get_all_micronutrients(
            cursor=self.cursor, label_id=str(analysis["product"]["label_id"])
        )
        self.assertIsNotNone(nutrients_data)

        self.assertEqual(
            len(nutrients_data), self.nb_micronutrients
        )  # There are 2 nutrients in the analysis_json
        sub_labels = sub_label.get_sub_label_json(
            self.cursor, str(analysis["product"]["label_id"])
        )
        self.assertIsNotNone(sub_labels)

        # Test for original_dataset
        inspection_data = inspection.get_inspection(self.cursor, inspection_id)

        original_dataset = inspection_data[8]
        original_dataset["inspection_id"] = inspection_id
        self.maxDiff = None
        self.assertDictEqual(analysis, original_dataset)

        # Verify OLAP Layer

        query = "SELECT EXISTS (SELECT 1 FROM inspection_factual WHERE inspection_factual.inspection_id = %s)"

        self.cursor.execute(query, (inspection_id,))
        self.assertTrue(self.cursor.fetchone()[0])

        query = "SELECT EXISTS (SELECT 1 FROM label_dimension WHERE label_dimension.label_id = %s)"

        self.cursor.execute(query, (label_id,))
        self.assertTrue(self.cursor.fetchone()[0])

        # Verify if the saved ids are the same length as the ones in the analysis_json

        label_dimension = label.get_label_dimension(self.cursor, label_id)

        company_info_id = str(label_dimension[1])
        manufacturer_info_id = str(label_dimension[3])

        self.assertEqual(str(company_info_id), analysis["company"]["id"])
        self.assertEqual(str(manufacturer_info_id), analysis["manufacturer"]["id"])

        self.assertEqual(len(label_dimension[5]), self.nb_instructions)
        self.assertEqual(len(label_dimension[6]), self.nb_cautions)
        self.assertEqual(len(label_dimension[7]), self.nb_first_aid)

        self.assertEqual(len(label_dimension[9]), self.nb_specifications)
        self.assertEqual(len(label_dimension[10]), self.nb_ingredients)
        self.assertEqual(len(label_dimension[11]), self.nb_micronutrients)
        self.assertEqual(len(label_dimension[12]), self.nb_guaranteed)
        self.assertEqual(len(label_dimension[13]), self.nb_weight)
        self.assertEqual(len(label_dimension[14]), 1)
        self.assertEqual(len(label_dimension[15]), 1)

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
                    self.user.id,
                    [self.pic_encoded, self.pic_encoded],
                    {},
                )
            )

    def test_get_full_inspection_json(self):
        formatted_analysis = metadata.build_inspection_import(self.analysis_json)
        picture_set_id = picture.new_picture_set(
            self.cursor, json.dumps({}), self.user.id
        )

        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user.id, picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]

        data = asyncio.run(
            fertiscan.get_full_inspection_json(self.cursor, inspection_id)
        )
        data = json.loads(data)
        self.assertEqual(data["inspection_id"], str(inspection_id))

    def test_delete_inspection(self):
        # Create a new inspection to delete later
        with open(TEST_INSPECTION_JSON_PATH, "r") as file:
            input_json = json.load(file)

        picture_set_id = asyncio.run(
            datastore.create_picture_set(
                self.cursor, self.container_client, 0, self.user.id
            )
        )

        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user.id, picture_set_id, json.dumps(input_json)
        )
        inspection_id = inspection_dict["inspection_id"]

        # Verify the inspection was created by directly querying the database
        self.cursor.execute(
            "SELECT id FROM inspection WHERE id = %s;",
            (inspection_id,),
        )
        fetched_inspection_id = self.cursor.fetchone()
        self.assertIsNotNone(
            fetched_inspection_id, "The inspection should exist before deletion."
        )

        # Perform the delete operation
        deleted_inspection = asyncio.run(
            fertiscan.delete_inspection(
                self.cursor, inspection_id, self.user.id, self.container_client
            )
        )

        # Verify that the inspection ID matches the one we deleted
        self.assertIsInstance(deleted_inspection, metadata.DBInspection)
        self.assertEqual(str(deleted_inspection.id), inspection_id)

        # Ensure that the inspection no longer exists in the database
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM inspection WHERE id = %s);",
            (inspection_id,),
        )
        inspection_exists = self.cursor.fetchone()[0]
        self.assertFalse(
            inspection_exists, "The inspection should be deleted from the database."
        )

        # Verify that the picture set associated with the inspection was also deleted
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM picture_set WHERE id = %s);",
            (picture_set_id,),
        )
        picture_set_exists = self.cursor.fetchone()[0]
        self.assertFalse(
            picture_set_exists,
            "The picture set should be deleted from the database.",
        )

        # Verify that no blobs associated with the picture set ID remain in the container
        blobs_after = [blob.name for blob in self.container_client.list_blobs()]
        self.assertFalse(
            any(str(picture_set_id) in blob_name for blob_name in blobs_after),
            "The folder associated with the picture set ID should be deleted from the container.",
        )
