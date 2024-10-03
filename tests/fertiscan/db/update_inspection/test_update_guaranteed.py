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


class TestUpdateGuaranteedFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

        # Set up test data for guaranteed analysis
        self.sample_guaranteed = json.dumps(
            [
                {"name": "Total Nitrogen (N)", "value": "20", "unit": "%"},
                {"name": "Available Phosphate (P2O5)", "value": "20", "unit": "%"},
                {"name": "Soluble Potash (K2O)", "value": "20", "unit": "%"},
            ]
        )

        self.updated_guaranteed = json.dumps(
            [
                {"name": "Total Nitrogen (N)", "value": "22", "unit": "%"},
                {"name": "Available Phosphate (P2O5)", "value": "21", "unit": "%"},
                {"name": "Soluble Potash (K2O)", "value": "23", "unit": "%"},
            ]
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

    def test_update_guaranteed(self):
        # Insert initial guaranteed analysis
        self.cursor.execute(
            "SELECT update_guaranteed(%s, %s);",
            (self.label_id, self.sample_guaranteed),
        )

        # Verify that the data is correctly saved
        self.cursor.execute(
            "SELECT read_name, value, unit FROM guaranteed WHERE label_id = %s;",
            (self.label_id,),
        )
        saved_data = self.cursor.fetchall()
        expected_data = [
            ("Total Nitrogen (N)", 20.0, "%"),
            ("Available Phosphate (P2O5)", 20.0, "%"),
            ("Soluble Potash (K2O)", 20.0, "%"),
        ]
        self.assertEqual(
            len(saved_data),
            3,
            "There should be three guaranteed analysis records inserted",
        )
        self.assertListEqual(
            saved_data, expected_data, "Saved data should match the expected values"
        )

        # Update guaranteed analysis
        self.cursor.execute(
            "SELECT update_guaranteed(%s, %s);",
            (self.label_id, self.updated_guaranteed),
        )

        # Verify that the data is correctly updated
        self.cursor.execute(
            "SELECT read_name, value, unit FROM guaranteed WHERE label_id = %s;",
            (self.label_id,),
        )
        updated_data = self.cursor.fetchall()
        expected_updated_data = [
            ("Total Nitrogen (N)", 22.0, "%"),
            ("Available Phosphate (P2O5)", 21.0, "%"),
            ("Soluble Potash (K2O)", 23.0, "%"),
        ]
        self.assertEqual(
            len(updated_data),
            3,
            "There should be three guaranteed analysis records after update",
        )
        self.assertListEqual(
            updated_data,
            expected_updated_data,
            "Updated data should match the new values",
        )


if __name__ == "__main__":
    unittest.main()
