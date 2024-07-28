import json
import os
import unittest

import psycopg

from datastore.db.queries.inspection import InspectionUpdateError, update_inspection

# Constants for test configuration
TEST_DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if not TEST_DB_CONNECTION_STRING:
    raise ValueError("FERTISCAN_DB_URL is not set")

TEST_DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if not TEST_DB_SCHEMA:
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

TEST_INPUT_JSON_PATH = "tests/FertiScan/analysis_returned.json"


class TestInspectionUpdatePythonFunction(unittest.TestCase):
    def setUp(self):
        # Set up database connection and cursor
        self.conn = psycopg.connect(
            TEST_DB_CONNECTION_STRING, options=f"-c search_path={TEST_DB_SCHEMA},public"
        )
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()

        # Create a user to act as inspector
        self.cursor.execute(
            f'INSERT INTO "{TEST_DB_SCHEMA}".users (email) VALUES (%s) RETURNING id;',
            ("inspector@example.com",),
        )
        self.inspector_id = str(self.cursor.fetchone()[0])

        # Load the JSON data for creating a new inspection
        with open(TEST_INPUT_JSON_PATH, "r") as file:
            create_input_json = json.load(file)

        create_input_json_str = json.dumps(create_input_json)

        # Create initial inspection data in the database
        self.picture_set_id = None
        self.cursor.execute(
            f'SELECT "{TEST_DB_SCHEMA}".new_inspection(%s, %s, %s);',
            (self.inspector_id, self.picture_set_id, create_input_json_str),
        )
        self.created_data = self.cursor.fetchone()[0]

        # Store the inspection ID for later use
        self.inspection_id = str(self.created_data.get("inspection_id"))

    def tearDown(self):
        # Roll back any changes to maintain database state
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_python_function_update_inspection_with_verified_false(self):
        updated_input_json = self.created_data.copy()
        updated_input_json["company"]["name"] = "Updated Company Name"
        updated_input_json["product"]["metrics"]["weight"][0]["value"] = 26.0
        updated_input_json["product"]["metrics"]["density"]["value"] = 1.3
        updated_input_json["specifications"]["en"][0]["ph"] = 6.8
        updated_input_json["ingredients"]["en"][0]["value"] = 5.5
        updated_input_json["guaranteed_analysis"][0]["value"] = 21.0
        updated_input_json["verified"] = False

        try:
            updated_result = update_inspection(
                self.cursor,
                self.inspection_id,
                self.inspector_id,
                updated_input_json,
            )
        except InspectionUpdateError as e:
            self.fail(f"update_inspection raised an unexpected error: {str(e)}")

        self.assertEqual(
            updated_result["company"]["name"],
            "Updated Company Name",
            "The company name should reflect the update.",
        )
        self.assertEqual(
            updated_result["product"]["metrics"]["weight"][0]["value"],
            26.0,
            "The weight metric should reflect the updated value.",
        )
        self.assertEqual(
            updated_result["product"]["metrics"]["density"]["value"],
            1.3,
            "The density metric should reflect the updated value.",
        )
        self.assertEqual(
            updated_result["specifications"]["en"][0]["ph"],
            6.8,
            "The pH specification should reflect the updated value.",
        )
        self.assertEqual(
            updated_result["ingredients"]["en"][0]["value"],
            5.5,
            "The ingredient value should reflect the updated amount.",
        )
        self.assertEqual(
            updated_result["guaranteed_analysis"][0]["value"],
            21.0,
            "The guaranteed analysis value for Total Nitrogen (N) should reflect the updated amount.",
        )

    def test_python_function_update_inspection_with_verified_true(self):
        updated_input_json = self.created_data.copy()
        updated_input_json["verified"] = True

        try:
            updated_result = update_inspection(
                self.cursor,
                self.inspection_id,
                self.inspector_id,
                updated_input_json,
            )
        except InspectionUpdateError as e:
            self.fail(f"update_inspection raised an unexpected error: {str(e)}")

        self.assertTrue(
            updated_result["verified"], "The verified status should be True as updated."
        )

        self.cursor.execute(
            f'SELECT id FROM "{TEST_DB_SCHEMA}".fertilizer WHERE latest_inspection_id = %s;',
            (self.inspection_id,),
        )
        fertilizer_id = self.cursor.fetchone()
        self.assertIsNotNone(
            fertilizer_id, "A fertilizer record should have been created."
        )


if __name__ == "__main__":
    unittest.main()
