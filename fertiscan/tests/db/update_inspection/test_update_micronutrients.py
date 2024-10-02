import json
import os
import unittest

import psycopg
import datastore.db.queries.label as label
from dotenv import load_dotenv

load_dotenv()

# Fetch database connection URL and schema from environment variables
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestUpdateMicronutrientsFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

        # Set up test data for micronutrients
        self.sample_micronutrients = json.dumps(
            {
                "en": [
                    {"name": "Iron (Fe)", "value": "0.10", "unit": "%"},
                    {"name": "Zinc (Zn)", "value": "0.05", "unit": "%"},
                ],
                "fr": [
                    {"name": "Fer (Fe)", "value": "0.10", "unit": "%"},
                    {"name": "Zinc (Zn)", "value": "0.05", "unit": "%"},
                ],
            }
        )

        self.updated_micronutrients = json.dumps(
            {
                "en": [
                    {"name": "Iron (Fe)", "value": "0.15", "unit": "%"},
                    {"name": "Zinc (Zn)", "value": "0.07", "unit": "%"},
                ],
                "fr": [
                    {"name": "Fer (Fe)", "value": "0.15", "unit": "%"},
                    {"name": "Zinc (Zn)", "value": "0.07", "unit": "%"},
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
            "test-warranty",
            self.company_info_id,
            self.company_info_id,
        )

    def tearDown(self):
        # Rollback any changes to leave the database state as it was before the test
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_update_micronutrients(self):
        # Insert initial micronutrients
        self.cursor.execute(
            "SELECT update_micronutrients(%s, %s);",
            (self.label_id, self.sample_micronutrients),
        )

        # Verify that the data is correctly saved
        self.cursor.execute(
            "SELECT read_name, value, unit, language FROM micronutrient WHERE label_id = %s;",
            (self.label_id,),
        )
        saved_data = self.cursor.fetchall()
        expected_data = [
            ("Iron (Fe)", 0.10, "%", "en"),
            ("Zinc (Zn)", 0.05, "%", "en"),
            ("Fer (Fe)", 0.10, "%", "fr"),
            ("Zinc (Zn)", 0.05, "%", "fr"),
        ]
        self.assertEqual(
            len(saved_data), 4, "There should be four micronutrient records inserted"
        )
        self.assertListEqual(
            saved_data, expected_data, "Saved data should match the expected values"
        )

        # Update micronutrients
        self.cursor.execute(
            "SELECT update_micronutrients(%s, %s);",
            (self.label_id, self.updated_micronutrients),
        )

        # Verify that the data is correctly updated
        self.cursor.execute(
            "SELECT read_name, value, unit, language FROM micronutrient WHERE label_id = %s;",
            (self.label_id,),
        )
        updated_data = self.cursor.fetchall()
        expected_updated_data = [
            ("Iron (Fe)", 0.15, "%", "en"),
            ("Zinc (Zn)", 0.07, "%", "en"),
            ("Fer (Fe)", 0.15, "%", "fr"),
            ("Zinc (Zn)", 0.07, "%", "fr"),
        ]
        self.assertEqual(
            len(updated_data),
            4,
            "There should be four micronutrient records after update",
        )
        self.assertListEqual(
            updated_data,
            expected_updated_data,
            "Updated data should match the new values",
        )


if __name__ == "__main__":
    unittest.main()
