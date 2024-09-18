import json
import os
import unittest

import psycopg
from dotenv import load_dotenv

load_dotenv()

# Database connection and schema settings
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if not DB_CONNECTION_STRING:
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if not DB_SCHEMA:
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

INPUT_JSON_PATH = "tests/fertiscan/inspection_export.json"


class TestUpdateInspectionFunction(unittest.TestCase):
    def setUp(self):
        # Set up database connection and cursor
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Control transaction manually
        self.cursor = self.conn.cursor()

        # Create users for the test
        self.cursor.execute(
            "INSERT INTO users (email) VALUES ('inspector@example.com') RETURNING id;"
        )
        self.inspector_id = self.cursor.fetchone()[0]

        self.cursor.execute(
            "INSERT INTO users (email) VALUES ('other_user@example.com') RETURNING id;"
        )
        self.other_user_id = self.cursor.fetchone()[0]

        # Load the JSON data for creating a new inspection
        with open(INPUT_JSON_PATH, "r") as file:
            create_input_json = json.load(file)

        create_input_json_str = json.dumps(create_input_json)

        # Create initial inspection data in the database
        self.picture_set_id = None  # No picture set ID for this test case
        self.cursor.execute(
            "SELECT new_inspection(%s, %s, %s);",
            (self.inspector_id, self.picture_set_id, create_input_json_str),
        )
        self.created_data = self.cursor.fetchone()[0]

        # Store the inspection ID for later use
        self.inspection_id = self.created_data.get("inspection_id")

    def tearDown(self):
        # Roll back any changes to maintain database state
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_update_inspection_with_verified_false(self):
        # Update the JSON data for testing the update function
        updated_input_json = self.created_data.copy()
        new_value = 66.3
        user_feedback = "Updated feedback for inspection."
        updated_input_json["company"]["name"] = "Updated Company Name"
        updated_input_json["product"]["metrics"]["weight"][0]["value"] = new_value
        updated_input_json["product"]["metrics"]["density"]["value"] = new_value
        # updated_input_json["specifications"]["en"][0]["ph"] = 6.8
        # updated_input_json["ingredients"]["en"][0]["value"] = 5.5
        updated_input_json["guaranteed_analysis"]["en"][0]["value"] = new_value
        updated_input_json["verified"] = False  # Ensure verified is false
        updated_input_json["inspection_comments"] = user_feedback

        updated_input_json_str = json.dumps(updated_input_json)

        # Invoke the update_inspection function and capture the returned JSON
        self.cursor.execute(
            "SELECT update_inspection(%s, %s, %s);",
            (self.inspection_id, self.inspector_id, updated_input_json_str),
        )

        # Verify the inspection record was updated in the database
        self.cursor.execute(
            "SELECT id, label_info_id, inspector_id, verified, user_commment FROM inspection WHERE id = %s;",
            (self.inspection_id,),
        )
        updated_inspection = self.cursor.fetchone()
        self.assertIsNotNone(updated_inspection, "The inspection record should exist.")
        self.assertEqual(
            str(updated_inspection[0]),
            str(self.inspection_id),
            "The inspection ID should match the expected value.",
        )
        self.assertEqual(
            updated_inspection[2],
            self.inspector_id,
            "The inspector ID should match the expected value.",
        )
        self.assertFalse(
            updated_inspection[3],
            "The verified status should be False as updated.",
        )
        
        self.assertEqual(updated_inspection[4], 
                         user_feedback, 
                         "The user feedback should be updated.")

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

        # Verify the company name was updated in the database
        self.cursor.execute(
            "SELECT name FROM organization_information WHERE id = %s;",
            (self.created_data["company"]["id"],),
        )
        updated_company_name = self.cursor.fetchone()[0]
        self.assertEqual(
            updated_company_name,
            "Updated Company Name",
            "The company name should reflect the update.",
        )

        # Verify the metrics were updated
        self.cursor.execute(
            "SELECT value FROM metric WHERE label_id = %s AND metric_type = %s;",
            (self.created_data["product"]["label_id"], "weight"),
        )
        updated_weight_metric = self.cursor.fetchone()[0]
        self.assertEqual(
            updated_weight_metric,
            new_value,
            "The weight metric should reflect the updated value.",
        )

        self.cursor.execute(
            "SELECT value FROM metric WHERE label_id = %s AND metric_type = %s;",
            (self.created_data["product"]["label_id"], "density"),
        )
        updated_density_metric = self.cursor.fetchone()[0]
        self.assertEqual(
            updated_density_metric,
            new_value,
            "The density metric should reflect the updated value.",
        )

        # Verify the specifications were updated
        # self.cursor.execute(
        #     "SELECT ph FROM specification WHERE label_id = %s;",
        #     (self.created_data["product"]["label_id"],),
        # )
        # updated_ph = self.cursor.fetchone()[0]
        # self.assertEqual(
        #     updated_ph,
        #     6.8,
        #     "The pH specification should reflect the updated value.",
        # )

        # # Verify the ingredient value was updated
        # self.cursor.execute(
        #     "SELECT value FROM ingredient WHERE label_id = %s AND name = %s;",
        #     (self.created_data["product"]["label_id"], "Bone meal"),
        # )
        # updated_ingredient_value = self.cursor.fetchone()[0]
        # self.assertEqual(
        #     updated_ingredient_value,
        #     5.5,
        #     "The ingredient value should reflect the updated amount.",
        # )

        # Verify the guaranteed analysis value was updated
        self.cursor.execute(
            "SELECT value FROM guaranteed WHERE label_id = %s AND read_name = %s;",
            (self.created_data["product"]["label_id"], "Total Nitrogen (N)"),
        )
        updated_nitrogen_value = self.cursor.fetchone()[0]
        self.assertEqual(
            updated_nitrogen_value,
            new_value,
            "The guaranteed analysis value for Total Nitrogen (N) should reflect the updated amount.",
        )

    def test_update_inspection_with_verified_true(self):
        # Update the JSON data for testing the update function
        updated_input_json = self.created_data.copy()
        updated_input_json["verified"] = True  # Set verified to true

        updated_input_json_str = json.dumps(updated_input_json)

        # Invoke the update_inspection function
        self.cursor.execute(
            "SELECT update_inspection(%s, %s, %s);",
            (self.inspection_id, self.inspector_id, updated_input_json_str),
        )

        # Verify the inspection record was updated in the database
        self.cursor.execute(
            "SELECT id, label_info_id, inspector_id, verified FROM inspection WHERE id = %s;",
            (self.inspection_id,),
        )
        updated_inspection = self.cursor.fetchone()
        self.assertIsNotNone(updated_inspection, "The inspection record should exist.")
        self.assertEqual(
            str(updated_inspection[0]),
            str(self.inspection_id),
            "The inspection ID should match the expected value.",
        )
        self.assertEqual(
            updated_inspection[2],
            self.inspector_id,
            "The inspector ID should match the expected value.",
        )
        self.assertTrue(
            updated_inspection[3],
            "The verified status should be True as updated.",
        )

        # Verify that a fertilizer record was created
        self.cursor.execute(
            "SELECT id FROM fertilizer WHERE latest_inspection_id = %s;",
            (self.inspection_id,),
        )
        fertilizer_id = self.cursor.fetchone()[0]
        self.assertIsNotNone(
            fertilizer_id, "A fertilizer record should have been created."
        )

        # Verify the fertilizer details are correct
        self.cursor.execute(
            "SELECT name, registration_number, owner_id FROM fertilizer WHERE id = %s;",
            (fertilizer_id,),
        )
        fertilizer_data = self.cursor.fetchone()
        self.assertEqual(
            fertilizer_data[0],
            updated_input_json["product"]["name"],
            "The fertilizer name should match the product name in the input JSON.",
        )
        self.assertEqual(
            fertilizer_data[1],
            updated_input_json["product"]["registration_number"],
            "The registration number should match the input JSON.",
        )

        # Check if the owner_id matches the organization information created for the manufacturer
        self.cursor.execute(
            "SELECT information_id FROM organization WHERE id = %s;",
            (fertilizer_data[2],),
        )
        organization_information_id = self.cursor.fetchone()[0]

        self.cursor.execute(
            "SELECT name FROM organization_information WHERE id = %s;",
            (organization_information_id,),
        )
        organization_name = self.cursor.fetchone()[0]

        self.assertEqual(
            organization_name,
            updated_input_json["manufacturer"]["name"],
            "The organization's name should match the manufacturer's name in the input JSON.",
        )

    def test_update_inspection_unauthorized_user(self):
        # Update the JSON data for testing the update function
        updated_input_json = self.created_data.copy()
        updated_input_json["company"]["name"] = "Unauthorized Update"

        updated_input_json_str = json.dumps(updated_input_json)

        # Use a different inspector_id that is not associated with the inspection
        unauthorized_inspector_id = self.other_user_id

        # Attempt to invoke the update_inspection function with an unauthorized inspector_id
        with self.assertRaises(psycopg.errors.RaiseException) as context:
            self.cursor.execute(
                "SELECT update_inspection(%s, %s, %s);",
                (self.inspection_id, unauthorized_inspector_id, updated_input_json_str),
            )

        # Verify that the exception message indicates an authorization issue
        self.assertIn(
            "Unauthorized: Inspector ID mismatch or inspection not found",
            str(context.exception),
        )

    def test_update_inspection_with_null_company_and_manufacturer(self):
        # Update the JSON data with null company and manufacturer for testing
        updated_input_json = self.created_data.copy()
        updated_input_json["company"] = None  # Company is set to null
        updated_input_json["manufacturer"] = None  # Manufacturer is set to null
        updated_input_json["verified"] = False  # Ensure verified is false

        updated_input_json_str = json.dumps(updated_input_json)

        # Invoke the update_inspection function
        self.cursor.execute(
            "SELECT update_inspection(%s, %s, %s);",
            (self.inspection_id, self.inspector_id, updated_input_json_str),
        )

        # Verify that the inspection record was updated
        self.cursor.execute(
            "SELECT id, label_info_id, inspector_id, verified FROM inspection WHERE id = %s;",
            (self.inspection_id,),
        )
        updated_inspection = self.cursor.fetchone()
        self.assertIsNotNone(updated_inspection, "The inspection record should exist.")
        self.assertEqual(
            updated_inspection[2],
            self.inspector_id,
            "The inspector ID should match the expected value.",
        )
        self.assertFalse(
            updated_inspection[3],
            "The verified status should be False as updated.",
        )

        # Verify that no organization record was created for the null company or manufacturer
        self.cursor.execute(
            "SELECT COUNT(*) FROM organization WHERE information_id IS NULL;",
        )
        organization_count = self.cursor.fetchone()[0]
        self.assertEqual(
            organization_count,
            0,
            "No organization record should be created when company or manufacturer is null.",
        )

    def test_update_inspection_with_missing_company_and_manufacturer(self):
        # Update the JSON data with company and manufacturer keys missing
        updated_input_json = self.created_data.copy()
        del updated_input_json["company"]  # Remove company key
        del updated_input_json["manufacturer"]  # Remove manufacturer key
        updated_input_json["verified"] = False  # Ensure verified is false

        updated_input_json_str = json.dumps(updated_input_json)

        # Invoke the update_inspection function
        self.cursor.execute(
            "SELECT update_inspection(%s, %s, %s);",
            (self.inspection_id, self.inspector_id, updated_input_json_str),
        )

        # Verify that the inspection record was updated
        self.cursor.execute(
            "SELECT id, label_info_id, inspector_id, verified FROM inspection WHERE id = %s;",
            (self.inspection_id,),
        )
        updated_inspection = self.cursor.fetchone()
        self.assertIsNotNone(updated_inspection, "The inspection record should exist.")
        self.assertEqual(
            updated_inspection[2],
            self.inspector_id,
            "The inspector ID should match the expected value.",
        )
        self.assertFalse(
            updated_inspection[3],
            "The verified status should be False as updated.",
        )

        # Verify that no organization record was created for the missing company or manufacturer
        self.cursor.execute(
            "SELECT COUNT(*) FROM organization WHERE information_id IS NULL;",
        )
        organization_count = self.cursor.fetchone()[0]
        self.assertEqual(
            organization_count,
            0,
            "No organization record should be created when company or manufacturer is missing.",
        )

    def test_update_inspection_with_empty_company_and_manufacturer(self):
        # Update the JSON data with empty company and manufacturer for testing
        updated_input_json = self.created_data.copy()
        updated_input_json["company"] = {}  # Company is set to an empty object
        updated_input_json["manufacturer"] = (
            {}
        )  # Manufacturer is set to an empty object
        updated_input_json["verified"] = False  # Ensure verified is false

        updated_input_json_str = json.dumps(updated_input_json)

        # Invoke the update_inspection function
        self.cursor.execute(
            "SELECT update_inspection(%s, %s, %s);",
            (self.inspection_id, self.inspector_id, updated_input_json_str),
        )

        # Verify that the inspection record was updated
        self.cursor.execute(
            "SELECT id, label_info_id, inspector_id, verified FROM inspection WHERE id = %s;",
            (self.inspection_id,),
        )
        updated_inspection = self.cursor.fetchone()
        self.assertIsNotNone(updated_inspection, "The inspection record should exist.")
        self.assertEqual(
            updated_inspection[2],
            self.inspector_id,
            "The inspector ID should match the expected value.",
        )
        self.assertFalse(
            updated_inspection[3],
            "The verified status should be False as updated.",
        )

        # Verify that no organization record was created for the empty company or manufacturer
        self.cursor.execute(
            "SELECT COUNT(*) FROM organization WHERE information_id IS NULL;",
        )
        organization_count = self.cursor.fetchone()[0]
        self.assertEqual(
            organization_count,
            0,
            "No organization record should be created when company or manufacturer is empty.",
        )


if __name__ == "__main__":
    unittest.main()
