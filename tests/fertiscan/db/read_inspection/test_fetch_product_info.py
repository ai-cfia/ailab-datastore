import json
import os
import unittest
import psycopg
from uuid import UUID
from dotenv import load_dotenv

load_dotenv()

# Database connection and schema settings
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if not DB_CONNECTION_STRING:
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if not DB_SCHEMA:
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

INPUT_JSON_PATH = "tests/fertiscan/analysis_returned.json"


class TestFetchProductInfoFunction(unittest.TestCase):
    def setUp(self):
        # Set up database connection and cursor
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Control transaction manually
        self.cursor = self.conn.cursor()

        # Create a user (inspector) for the test
        self.cursor.execute(
            "INSERT INTO users (email) VALUES ('user@example.com') RETURNING id;"
        )
        self.inspector_id = self.cursor.fetchone()[0]

        # Load the JSON data for creating a new inspection
        with open(INPUT_JSON_PATH, "r") as file:
            inspection_data = json.load(file)

        inspection_data_str = json.dumps(inspection_data)

        # Create initial inspection data in the database
        self.picture_set_id = None  # No picture set ID for this test case
        self.cursor.execute(
            "SELECT new_inspection(%s, %s, %s);",
            (self.inspector_id, self.picture_set_id, inspection_data_str),
        )
        self.created_data = self.cursor.fetchone()[0]

        # Store the label_info_id for later use
        self.label_info_id = self.created_data["product"]["id"]

    def tearDown(self):
        # Roll back any changes to maintain database state
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_fetch_product_info(self):
        # Execute the fetch_product_info function using the label_info_id
        self.cursor.execute("SELECT fetch_product_info(%s);", (self.label_info_id,))
        result = self.cursor.fetchone()[0]

        # Load the expected data from the same input JSON file
        with open(INPUT_JSON_PATH, "r") as file:
            expected_data = json.load(file)

        # Compare individual fields
        self.assertIsNotNone(result, "Result should not be None")
        
        # ID Comparison (convert UUIDs to strings)
        self.assertEqual(str(result["id"]), str(self.created_data["product"]["id"]), "Product ID should match")
        
        # N, P, K values (ensure comparison as floats)
        self.assertEqual(float(result["n"]), float(expected_data["product"]["n"]), "N value should match")
        self.assertEqual(float(result["p"]), float(expected_data["product"]["p"]), "P value should match")
        self.assertEqual(float(result["k"]), float(expected_data["product"]["k"]), "K value should match")
        
        # Compare other string fields
        self.assertEqual(result["npk"], expected_data["product"]["npk"], "NPK should match")
        self.assertEqual(result["lot_number"], expected_data["product"]["lot_number"], "Lot number should match")
        self.assertEqual(result["registration_number"], expected_data["product"]["registration_number"], "Registration number should match")
        self.assertEqual(result["verified"], expected_data["product"]["verified"], "Verified status should match")
        self.assertEqual(result["name"], expected_data["product"]["name"], "Product name should match")

        # Metrics comparison (assuming metrics is a dictionary with lists/values)
        self.assertEqual(result["metrics"], expected_data["product"]["metrics"], "Metrics should match")

        # Warranty comparison
        self.assertEqual(result["warranty"], "Placeholder for warranty text", "Warranty should match")

        # Optionally, print the result for debugging
        print(result)


if __name__ == "__main__":
    unittest.main()
