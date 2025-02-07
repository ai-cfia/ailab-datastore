import asyncio
import json
import os
import unittest
import uuid

from dotenv import load_dotenv

import datastore.db.__init__ as db
from datastore.db.queries.picture import new_picture_set
from fertiscan import get_full_inspection_json
from fertiscan.db.metadata.inspection import DBInspection, Inspection
from fertiscan.db.queries.inspection import get_inspection_dict, update_inspection

load_dotenv()

# Constants for test configuration
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if not DB_CONNECTION_STRING:
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if not DB_SCHEMA:
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

TEST_INSPECTION_JSON_PATH = "tests/fertiscan/inspection.json"


class TestInspectionUpdatePythonFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = db.cursor(self.conn)
        db.create_search_path(self.conn, self.cursor, DB_SCHEMA)

        # Create a user to act as inspector
        self.cursor.execute(
            """
            INSERT INTO users (email) 
            VALUES (%s)
            ON CONFLICT (email) DO UPDATE 
            SET email = EXCLUDED.email 
            RETURNING id;
            """,
            ("inspector@example.com",),
        )
        self.inspector_id = self.cursor.fetchone()[0]

        # Load the JSON data for creating a new inspection
        with open(TEST_INSPECTION_JSON_PATH, "r") as file:
            create_input_json = json.load(file)

        self.picture_set_id = new_picture_set(
            self.cursor, json.dumps({}), self.inspector_id
        )
        create_input_json["picture_set_id"] = str(self.picture_set_id)
        create_input_json = json.dumps(create_input_json)

        # Create initial inspection data in the database
        self.cursor.execute(
            "SELECT new_inspection(%s, %s);", (self.inspector_id, create_input_json)
        )
        self.created_data = self.cursor.fetchone()[0]
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

        picture_set_id = new_picture_set(self.cursor, json.dumps({}), self.inspector_id)
        self.assertNotEqual(picture_set_id, self.picture_set_id)

        # Update model fields instead of dictionary keys
        altered_inspection.organizations[0].name = "Updated Company Name"
        altered_inspection.product.metrics.weight[0].value = new_value
        altered_inspection.product.metrics.density.value = new_value
        altered_inspection.guaranteed_analysis.en[0].value = new_value
        altered_inspection.verified = False  # Ensure verified is false
        altered_inspection.picture_set_id = picture_set_id

        # Use the updated model for the update
        update_inspection(
            self.cursor,
            self.inspection_id,
            self.inspector_id,
            altered_inspection.model_dump(mode="json"),
        )

        # Fetch the updated inspection data from the database using asyncio
        task = get_full_inspection_json(self.cursor, self.inspection_id)
        updated_inspection = asyncio.run(task)
        updated_inspection = json.loads(updated_inspection)
        updated_inspection = Inspection.model_validate(updated_inspection)

        # Assertions using the Inspection model
        self.assertEqual(
            updated_inspection.organizations[0].name,
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
        self.cursor.execute(
            "SELECT COUNT(*) FROM fertilizer WHERE latest_inspection_id = %s;",
            (self.inspection_id,),
        )
        fertilizer_count = self.cursor.fetchone()[0]
        self.assertEqual(
            fertilizer_count,
            0,
            "No fertilizer should be created when verified is false.",
        )

        self.assertEqual(updated_inspection.picture_set_id, picture_set_id)

    def test_python_function_update_inspection_with_verified_true(self):
        # Create a model copy and update the verified status via the model
        altered_inspection = self.created_inspection.model_copy()
        altered_inspection.verified = True

        # Use the updated model for the update
        update_inspection(
            self.cursor,
            self.inspection_id,
            self.inspector_id,
            altered_inspection.model_dump(mode="json"),
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

        self.cursor.execute(
            "SELECT id FROM fertilizer WHERE latest_inspection_id = %s;",
            (self.inspection_id,),
        )
        fertilizer_id = self.cursor.fetchone()
        self.assertIsNotNone(
            fertilizer_id, "A fertilizer record should have been created."
        )

    def test_update_inspection_unauthorized_user(self):
        # Update the inspection model for testing the update function
        altered_inspection = self.created_inspection.model_copy()

        # Modify the company name in the inspection model
        altered_inspection.organizations[0].name = "Unauthorized Update"

        # Use a different inspector_id that is not associated with the inspection
        unauthorized_inspector_id = uuid.uuid4()

        # Attempt to invoke the update_inspection function with an unauthorized inspector_id
        with self.assertRaises(Exception):
            update_inspection(
                self.cursor,
                self.inspection_id,
                unauthorized_inspector_id,
                altered_inspection.model_dump(mode="json"),
            )

    def test_update_inspection_without_organizations(self):
        # Update the inspection model with null company and manufacturer for testing
        altered_inspection = self.created_inspection.model_copy()
        altered_inspection.organizations = []  # orgs is empty
        altered_inspection.verified = False  # Ensure verified is false

        # Invoke the update_inspection function
        update_inspection(
            self.cursor,
            self.inspection_id,
            self.inspector_id,
            altered_inspection.model_dump(mode="json"),
        )

        # Verify that the inspection record was updated
        updated_inspection = get_inspection_dict(self.cursor, self.inspection_id)
        updated_inspection = DBInspection.model_validate(updated_inspection)

        self.assertIsNotNone(updated_inspection, "The inspection record should exist.")
        self.assertEqual(
            updated_inspection.inspector_id,
            self.inspector_id,
            "The inspector ID should match the expected value.",
        )
        self.assertFalse(
            updated_inspection.verified,
            "The verified status should be False as updated.",
        )

        # Verify that no organization record was created for the null company or manufacturer
        self.cursor.execute(
            "SELECT COUNT(*) FROM organization WHERE name IS NULL;",
        )
        organization_count = self.cursor.fetchone()[0]
        self.assertEqual(
            organization_count,
            0,
            "No organization record should be created when organizations is empty.",
        )


if __name__ == "__main__":
    unittest.main()
