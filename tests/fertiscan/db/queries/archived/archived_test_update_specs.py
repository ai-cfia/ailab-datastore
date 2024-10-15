import json
import os
import unittest

import psycopg
from dotenv import load_dotenv

import fertiscan.db.queries.label as label

load_dotenv()

# Fetch database connection URL and schema from environment variables
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestUpdateSpecificationsFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

        # Set up test data
        self.sample_specifications = json.dumps(
            {
                "en": [{"humidity": "10.0", "ph": "6.5", "solubility": "90.0"}],
                "fr": [{"humidity": "10.0", "ph": "6.5", "solubility": "90.0"}],
            }
        )

        self.updated_specifications = json.dumps(
            {
                "en": [{"humidity": "20.0", "ph": "7.0", "solubility": "85.0"}],
                "fr": [{"humidity": "20.0", "ph": "7.0", "solubility": "85.0"}],
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

    def test_update_specifications(self):
        # Update specifications for the given label_id with initial data
        self.cursor.execute(
            "SELECT update_specifications(%s, %s);",
            (self.label_id, self.sample_specifications),
        )

        # Verify that the initial data is correctly saved
        self.cursor.execute(
            "SELECT humidity, ph, solubility, language FROM specification WHERE label_id = %s;",
            (self.label_id,),
        )
        saved_data = self.cursor.fetchall()
        expected_data = [(10.0, 6.5, 90.0, "en"), (10.0, 6.5, 90.0, "fr")]
        self.assertEqual(
            len(saved_data), 2, "There should be two specifications inserted"
        )
        self.assertListEqual(
            saved_data, expected_data, "Saved data should match the expected values"
        )

        # Update specifications for the given label_id with new data
        self.cursor.execute(
            "SELECT update_specifications(%s, %s);",
            (self.label_id, self.updated_specifications),
        )

        # Verify that the data is correctly updated
        self.cursor.execute(
            "SELECT humidity, ph, solubility, language FROM specification WHERE label_id = %s;",
            (self.label_id,),
        )
        updated_data = self.cursor.fetchall()
        expected_updated_data = [(20.0, 7.0, 85.0, "en"), (20.0, 7.0, 85.0, "fr")]
        self.assertEqual(
            len(updated_data),
            2,
            "There should still be two specifications after update",
        )
        self.assertListEqual(
            updated_data,
            expected_updated_data,
            "Updated data should match the new values",
        )


if __name__ == "__main__":
    unittest.main()
