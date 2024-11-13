import json
import os
import unittest

import psycopg
from dotenv import load_dotenv

import fertiscan.db.queries.label as label

load_dotenv()

# Fetch database connection URL and schema from environment variables
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL_TESTING")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestUpdateIngredientsFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

        # Set up test data for ingredients
        self.sample_organic_ingredients = json.dumps(
            {
                "en": [
                    {"name": "Bone meal", "value": "5", "unit": "%"},
                    {"name": "Seaweed extract", "value": "3", "unit": "%"},
                ],
                "fr": [
                    {"name": "Farine d'os", "value": "5", "unit": "%"},
                    {"name": "Extrait d'algues", "value": "3", "unit": "%"},
                ],
            }
        )

        self.updated_organic_ingredients = json.dumps(
            {
                "en": [
                    {"name": "Bone meal", "value": "6", "unit": "%"},
                    {"name": "Seaweed extract", "value": "4", "unit": "%"},
                ],
                "fr": [
                    {"name": "Farine d'os", "value": "6", "unit": "%"},
                    {"name": "Extrait d'algues", "value": "4", "unit": "%"},
                ],
            }
        )

        # Insert test data to obtain a valid label_id
        sample_org_info = json.dumps(
            {
                "name": "Test Company",
                "address": "123 Test Address",
                "website": "http://www.testcompany.com",
                "phone_number": "+1 800 555 0123",
            }
        )
        self.cursor.execute("SELECT upsert_organization_info(%s);", (sample_org_info,))
        self.company_info_id = self.cursor.fetchone()[0]

        self.label_id = label.new_label_information(
            self.cursor,
            "test-label",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            False,
            self.company_info_id,
            self.company_info_id,
            None,
        )

    def tearDown(self):
        # Rollback any changes to leave the database state as it was before the test
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_update_organic_ingredients(self):
        # Insert initial organic ingredients
        self.cursor.execute(
            "SELECT update_ingredients(%s, %s);",
            (self.label_id, self.sample_organic_ingredients),
        )

        # Verify that the data is correctly saved
        self.cursor.execute(
            "SELECT name, value, unit, language FROM ingredient WHERE label_id = %s;",
            (self.label_id,),
        )
        saved_data = self.cursor.fetchall()
        expected_data = [
            ("Bone meal", 5.0, "%", "en"),
            ("Seaweed extract", 3.0, "%", "en"),
            ("Farine d'os", 5.0, "%", "fr"),
            ("Extrait d'algues", 3.0, "%", "fr"),
        ]
        self.assertEqual(
            len(saved_data), 4, "There should be four organic ingredients inserted"
        )
        self.assertListEqual(
            saved_data, expected_data, "Saved data should match the expected values"
        )

        # Update organic ingredients
        self.cursor.execute(
            "SELECT update_ingredients(%s, %s);",
            (self.label_id, self.updated_organic_ingredients),
        )

        # Verify that the data is correctly updated
        self.cursor.execute(
            "SELECT name, value, unit, language FROM ingredient WHERE label_id = %s;",
            (self.label_id,),
        )
        updated_data = self.cursor.fetchall()
        expected_updated_data = [
            ("Bone meal", 6.0, "%", "en"),
            ("Seaweed extract", 4.0, "%", "en"),
            ("Farine d'os", 6.0, "%", "fr"),
            ("Extrait d'algues", 4.0, "%", "fr"),
        ]
        self.assertEqual(
            len(updated_data),
            4,
            "There should be four organic ingredients after update",
        )
        self.assertListEqual(
            updated_data,
            expected_updated_data,
            "Updated data should match the new values",
        )



if __name__ == "__main__":
    unittest.main()
