import json
import os
import unittest
import uuid

import psycopg
from dotenv import load_dotenv
from psycopg import connect

from datastore.db.queries.picture import new_picture_set
from fertiscan.db.metadata.inspection import DBInspection
from fertiscan.db.queries.inspection import (
    delete_inspection,
    new_inspection_with_label_info,
)

load_dotenv()

# Constants for test configuration
TEST_DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if not TEST_DB_CONNECTION_STRING:
    raise ValueError("FERTISCAN_DB_URL is not set")

TEST_DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if not TEST_DB_SCHEMA:
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

TEST_INSPECTION_JSON_PATH = "tests/fertiscan/inspection.json"


class TestInspectionDeleteFunction(unittest.TestCase):
    def setUp(self):
        # Set up database connection and cursor
        self.conn = connect(
            TEST_DB_CONNECTION_STRING, options=f"-c search_path={TEST_DB_SCHEMA},public"
        )
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()

        # Create a user to act as inspector
        self.cursor.execute(
            "INSERT INTO users (email) VALUES (%s) RETURNING id;",
            ("inspector@example.com",),
        )
        self.inspector_id = str(self.cursor.fetchone()[0])

        # Load the JSON data for creating a new inspection
        with open(TEST_INSPECTION_JSON_PATH, "r") as file:
            self.input_json = json.load(file)

        self.picture_set_id = new_picture_set(
            self.cursor, json.dumps({}), self.inspector_id
        )
        self.input_json["picture_set_id"] = str(self.picture_set_id)

        # Create a new inspection record with the input JSON data
        inspection_data = new_inspection_with_label_info(
            self.cursor, self.inspector_id, json.dumps(self.input_json)
        )
        self.inspection_id = inspection_data["inspection_id"]
        self.label_info_id = inspection_data["product"]["label_id"]

    def tearDown(self):
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_delete_inspection(self):
        deleted_inspection = delete_inspection(
            self.cursor, self.inspection_id, self.inspector_id
        )
        deleted_inspection = DBInspection.model_validate(deleted_inspection)

        # Make sure picture_set_id is not null
        self.assertIsNotNone(deleted_inspection.picture_set_id)

        # Check if the returned object is a DBInspection instance
        self.assertIsInstance(deleted_inspection, DBInspection)

        # Verify that the inspection ID matches the one we deleted
        self.assertEqual(str(deleted_inspection.id), self.inspection_id)

        # Ensure that the inspection no longer exists in the database
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM inspection WHERE id = %s);",
            (self.inspection_id,),
        )
        inspection_exists = self.cursor.fetchone()[0]
        self.assertFalse(
            inspection_exists, "The inspection should be deleted from the database."
        )

        # Verify that the inspection record was deleted
        self.cursor.execute(
            "SELECT COUNT(*) FROM inspection WHERE id = %s;",
            (self.inspection_id,),
        )
        inspection_count = self.cursor.fetchone()[0]
        self.assertEqual(inspection_count, 0, "Inspection should be deleted.")

        # Verify that the related sample was deleted
        self.cursor.execute(
            "SELECT COUNT(*) FROM sample WHERE id = %s;",
            (deleted_inspection.sample_id,),
        )
        sample_count = self.cursor.fetchone()[0]
        self.assertEqual(sample_count, 0, "Sample should be deleted.")

        # Verify that related fertilizer information was deleted
        self.cursor.execute(
            "SELECT COUNT(*) FROM fertilizer WHERE latest_inspection_id = %s;",
            (self.inspection_id,),
        )
        sample_count = self.cursor.fetchone()[0]
        self.assertEqual(sample_count, 0, "Sample should be deleted.")

        # Verify that the label information was deleted
        self.cursor.execute(
            "SELECT COUNT(*) FROM label_information WHERE id = %s;",
            (self.label_info_id,),
        )
        label_count = self.cursor.fetchone()[0]
        self.assertEqual(label_count, 0, "Label information should be deleted.")

        # Verify that the related metrics were deleted
        self.cursor.execute(
            "SELECT COUNT(*) FROM metric WHERE label_id = %s;",
            (self.label_info_id,),
        )
        metric_count = self.cursor.fetchone()[0]
        self.assertEqual(metric_count, 0, "Metrics should be deleted.")

        # Verify that the related specifications were deleted
        self.cursor.execute(
            "SELECT COUNT(*) FROM specification WHERE label_id = %s;",
            (self.label_info_id,),
        )
        specification_count = self.cursor.fetchone()[0]
        self.assertEqual(specification_count, 0, "Specifications should be deleted.")

        # Verify that the related sub-labels were deleted
        self.cursor.execute(
            "SELECT COUNT(*) FROM sub_label WHERE label_id = %s;",
            (self.label_info_id,),
        )
        sub_label_count = self.cursor.fetchone()[0]
        self.assertEqual(sub_label_count, 0, "Sub-labels should be deleted.")

        # Verify that the related micronutrients were deleted
        self.cursor.execute(
            "SELECT COUNT(*) FROM micronutrient WHERE label_id = %s;",
            (self.label_info_id,),
        )
        micronutrient_count = self.cursor.fetchone()[0]
        self.assertEqual(micronutrient_count, 0, "Micronutrients should be deleted.")

        # Verify that the related guaranteed records were deleted
        self.cursor.execute(
            "SELECT COUNT(*) FROM guaranteed WHERE label_id = %s;",
            (self.label_info_id,),
        )
        guaranteed_count = self.cursor.fetchone()[0]
        self.assertEqual(guaranteed_count, 0, "Guaranteed records should be deleted.")

        # Verify that the related ingredients were deleted
        self.cursor.execute(
            "SELECT COUNT(*) FROM ingredient WHERE label_id = %s;",
            (self.label_info_id,),
        )
        ingredient_count = self.cursor.fetchone()[0]
        self.assertEqual(ingredient_count, 0, "Ingredients should be deleted.")

    def test_delete_inspection_unauthorized(self):
        # Generate a random UUID to simulate an unauthorized inspector
        unauthorized_inspector_id = str(uuid.uuid4())

        # Attempt to delete the inspection with a different inspector
        with self.assertRaises(psycopg.errors.RaiseException) as context:
            self.cursor.execute(
                "SELECT delete_inspection(%s, %s);",
                (
                    self.inspection_id,
                    unauthorized_inspector_id,
                ),  # Using a random UUID as unauthorized inspector ID
            )

        # Check that the exception message indicates unauthorized access
        self.assertIn(
            f"Inspector {unauthorized_inspector_id} is not the creator of inspection {self.inspection_id}",
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()
