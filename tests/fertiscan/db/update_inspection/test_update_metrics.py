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


class TestUpdateMetricsFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

        # Set up test data for metrics
        self.sample_metrics = json.dumps(
            {
                "weight": [{"value": "5", "unit": "kg"}, {"value": "11", "unit": "lb"}],
                "density": {"value": "1.2", "unit": "g/cm³"},
                "volume": {"value": "20.8", "unit": "L"},
            }
        )

        self.updated_metrics = json.dumps(
            {
                "weight": [{"value": "6", "unit": "kg"}, {"value": "13", "unit": "lb"}],
                "density": {"value": "1.3", "unit": "g/cm³"},
                "volume": {"value": "25.0", "unit": "L"},
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
        self.cursor.execute(
            'SELECT upsert_organization_info(%s);', (sample_org_info,)
        )
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

    def test_update_metrics(self):
        # Insert initial metrics
        self.cursor.execute(
            'SELECT update_metrics(%s, %s);',
            (self.label_id, self.sample_metrics),
        )

        # Verify that the data is correctly saved
        self.cursor.execute(
            'SELECT value, unit_id FROM metric WHERE label_id = %s;',
            (self.label_id,),
        )
        saved_data = self.cursor.fetchall()
        expected_data = [
            (5.0, "kg"),  # weight kg
            (11.0, "lb"),  # weight lb
            (1.2, "g/cm³"),  # density
            (20.8, "L"),  # volume
        ]
        self.assertEqual(len(saved_data), 4, "There should be four metrics inserted")
        self.assertListEqual(
            [(d[0], self._get_unit_name(d[1])) for d in saved_data],
            expected_data,
            "Saved data should match the expected values",
        )

        # Update metrics
        self.cursor.execute(
            'SELECT update_metrics(%s, %s);',
            (self.label_id, self.updated_metrics),
        )

        # Verify that the data is correctly updated
        self.cursor.execute(
            'SELECT value, unit_id FROM metric WHERE label_id = %s;',
            (self.label_id,),
        )
        updated_data = self.cursor.fetchall()
        expected_updated_data = [
            (6.0, "kg"),  # weight kg
            (13.0, "lb"),  # weight lb
            (1.3, "g/cm³"),  # density
            (25.0, "L"),  # volume
        ]
        self.assertEqual(
            len(updated_data), 4, "There should be four metrics after update"
        )
        self.assertListEqual(
            [(d[0], self._get_unit_name(d[1])) for d in updated_data],
            expected_updated_data,
            "Updated data should match the new values",
        )

    def _get_unit_name(self, unit_id):
        # Helper function to fetch the unit name by unit_id
        self.cursor.execute(
            'SELECT unit FROM unit WHERE id = %s;', (unit_id,)
        )
        return self.cursor.fetchone()[0]


if __name__ == "__main__":
    unittest.main()
