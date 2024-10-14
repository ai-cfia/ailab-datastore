import asyncio
import json
import os
import unittest
import uuid

from dotenv import load_dotenv
from psycopg import connect

from datastore.db.queries import user
from fertiscan import get_full_inspection_json
from fertiscan.db.models import Fertilizer, Inspection
from fertiscan.db.queries import inspection
from fertiscan.db.queries.fertilizer import query_fertilizers
from fertiscan.db.queries.inspection import update_inspection

load_dotenv()

# Constants for test configuration
TEST_DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if not TEST_DB_CONNECTION_STRING:
    raise ValueError("FERTISCAN_DB_URL is not set")

TEST_DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if not TEST_DB_SCHEMA:
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

TEST_INSPECTION_JSON_PATH = "tests/fertiscan/inspection.json"


class TestInspectionUpdatePythonFunction(unittest.TestCase):
    def setUp(self):
        # Set up database connection and cursor
        self.conn = connect(
            TEST_DB_CONNECTION_STRING, options=f"-c search_path={TEST_DB_SCHEMA},public"
        )
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()

        # Create a user to act as inspector
        self.username = uuid.uuid4().hex
        self.inspector_id = user.register_user(
            self.cursor, f"{self.username}@example.com"
        )

        # Load the JSON data for creating a new inspection
        with open(TEST_INSPECTION_JSON_PATH, "r") as file:
            create_input_json = json.load(file)

        create_input_json_str = json.dumps(create_input_json)

        # Create initial inspection data in the database
        self.picture_set_id = None
        self.created_data = inspection.new_inspection_with_label_info(
            self.cursor, self.inspector_id, self.picture_set_id, create_input_json_str
        )
        self.created_inspection = Inspection.model_validate(self.created_data)

        # Store the inspection ID for later use
        self.inspection_id = str(self.created_data.get("inspection_id"))

    def tearDown(self):
        # Roll back any changes to maintain database state
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_python_function_update_inspection_with_verified_false(self):
        # Create a model copy and update fields directly via the model
        altered_inspection = self.created_inspection.model_copy()
        new_value = 66.6

        # Update model fields instead of dictionary keys
        altered_inspection.company.name = "Updated Company Name"
        altered_inspection.product.metrics.weight[0].value = new_value
        altered_inspection.product.metrics.density.value = new_value
        altered_inspection.guaranteed_analysis.en[0].value = new_value
        altered_inspection.verified = False  # Ensure verified is false

        # Use the updated model for the update
        update_inspection(
            self.cursor,
            self.inspection_id,
            self.inspector_id,
            altered_inspection.model_dump(),
        )

        # Fetch the updated inspection data from the database using asyncio
        task = get_full_inspection_json(self.cursor, self.inspection_id)
        updated_inspection = asyncio.run(task)
        updated_inspection = json.loads(updated_inspection)
        updated_inspection = Inspection.model_validate(updated_inspection)

        # Assertions using the Inspection model
        self.assertEqual(
            updated_inspection.company.name,
            "Updated Company Name",
            "The company name should reflect the update.",
        )
        self.assertEqual(
            updated_inspection.product.metrics.weight[0].value,
            new_value,
            "The weight metric should reflect the updated value.",
        )
        self.assertEqual(
            updated_inspection.product.metrics.density.value,
            new_value,
            "The density metric should reflect the updated value.",
        )
        self.assertEqual(
            updated_inspection.guaranteed_analysis.en[0].value,
            new_value,
            "The guaranteed analysis value should reflect the updated amount.",
        )

        # Verify that no fertilizer record was created
        fertilizers = query_fertilizers(
            cursor=self.cursor, latest_inspection_id=self.inspection_id
        )
        self.assertListEqual(fertilizers, [])

    def test_python_function_update_inspection_with_verified_true(self):
        # Create a model copy and update the verified status via the model
        altered_inspection = self.created_inspection.model_copy()
        altered_inspection.verified = True

        # Use the updated model for the update
        update_inspection(
            self.cursor,
            self.inspection_id,
            self.inspector_id,
            altered_inspection.model_dump(),
        )

        # Fetch the updated inspection data from the database using asyncio
        task = get_full_inspection_json(self.cursor, self.inspection_id)
        updated_inspection = asyncio.run(task)
        updated_inspection = json.loads(updated_inspection)
        updated_inspection = Inspection.model_validate(updated_inspection)

        # Assertions using the Inspection model
        self.assertTrue(
            updated_inspection.verified,
            "The verified status should be True as updated.",
        )

        # Verify that a fertilizer record was created
        fertilizers = query_fertilizers(
            cursor=self.cursor, latest_inspection_id=self.inspection_id
        )
        self.assertEqual(len(fertilizers), 1)
        created_fertilizer = Fertilizer.model_validate(fertilizers[0])
        self.assertIsNotNone(created_fertilizer)
        self.assertEqual(created_fertilizer.name, updated_inspection.product.name)
        self.assertEqual(
            created_fertilizer.registration_number,
            updated_inspection.product.registration_number,
        )


if __name__ == "__main__":
    unittest.main()
