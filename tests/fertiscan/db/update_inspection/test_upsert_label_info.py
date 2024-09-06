import json
import os
import unittest

import psycopg
from dotenv import load_dotenv

load_dotenv()

# Fetch database connection URL and schema from environment variables
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestUpsertLabelInformationFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

        # Set up test data for organization to use in the tests
        self.sample_org_info = json.dumps(
            {
                "name": "Test Organization",
                "address": "123 Test Address",
                "website": "http://www.testorg.com",
                "phone_number": "+1 800 555 0100",
            }
        )
        self.cursor.execute(
            "SELECT upsert_organization_info(%s);",
            (self.sample_org_info,),
        )
        self.organization_info_id = self.cursor.fetchone()[0]

    def tearDown(self):
        # Rollback any changes to leave the database state as it was before the test
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_insert_new_label_information(self):
        sample_label_info = json.dumps(
            {
                "name": "SuperGrow 20-20-20",
                "lot_number": "L123456789",
                "npk": "10-20-30",
                "registration_number": "R123456",
                "n": 10.0,
                "p": 20.0,
                "k": 30.0,
                "warranty": "Guaranteed analysis of nutrients.",
            }
        )

        # Insert new label information
        with self.assertRaises(psycopg.errors.Error):
            self.cursor.execute(
                "SELECT upsert_label_information(%s, %s, %s);",
                (sample_label_info, self.organization_info_id, self.organization_info_id),
            )
        # label_info_id = self.cursor.fetchone()[0]

        # # Assertions to verify insertion
        # self.assertIsNotNone(label_info_id, "New label info ID should not be None")

        # # Verify that the data is correctly saved
        # self.cursor.execute(
        #     "SELECT product_name, lot_number, npk, registration_number, n, p, k, warranty, company_info_id, manufacturer_info_id FROM label_information WHERE id = %s;",
        #     (label_info_id,),
        # )
        # saved_label_data = self.cursor.fetchone()
        # self.assertIsNotNone(saved_label_data, "Saved label data should not be None")
        # self.assertEqual(
        #     saved_label_data[0], "SuperGrow 20-20-20", "Name should match the inserted value"
        # )
        # self.assertEqual(
        #     saved_label_data[1],
        #     "L123456789",
        #     "Lot number should match the inserted value",
        # )
        # self.assertEqual(
        #     saved_label_data[2], "10-20-30", "NPK should match the inserted value"
        # )
        # self.assertEqual(
        #     saved_label_data[3],
        #     "R123456",
        #     "Registration number should match the inserted value",
        # )
        # self.assertEqual(
        #     saved_label_data[4], 10.0, "N value should match the inserted value"
        # )
        # self.assertEqual(
        #     saved_label_data[5], 20.0, "P value should match the inserted value"
        # )
        # self.assertEqual(
        #     saved_label_data[6], 30.0, "K value should match the inserted value"
        # )
        # self.assertEqual(
        #     saved_label_data[7],
        #     "Guaranteed analysis of nutrients.",
        #     "Warranty should match the inserted value",
        # )
        # self.assertEqual(
        #     saved_label_data[8],
        #     self.organization_info_id,
        #     "Company info ID should match",
        # )
        # self.assertEqual(
        #     saved_label_data[9],
        #     self.organization_info_id,
        #     "Manufacturer info ID should match",
        # )

    def test_update_existing_label_information(self):
        sample_label_info = json.dumps(
            {
                "name": "SuperGrow 20-20-20",
                "lot_number": "L123456789",
                "npk": "10-20-30",
                "registration_number": "R123456",
                "n": 10.0,
                "p": 20.0,
                "k": 30.0,
                "warranty": "Guaranteed analysis of nutrients.",
            }
        )

        # Insert new label information to get a valid label_info_id
        with self.assertRaises(psycopg.errors.Error):
            self.cursor.execute(
                "SELECT upsert_label_information(%s, %s, %s);",
                (sample_label_info, self.organization_info_id, self.organization_info_id),
            )
        # label_info_id = self.cursor.fetchone()[0]

        # # Prepare data for updating the existing label
        # updated_label_info = json.dumps(
        #     {
        #         "name": "SuperGrow 20-20-20",
        #         "lot_number": "L987654321",
        #         "npk": "15-25-35",
        #         "registration_number": "R654321",
        #         "n": 15.0,
        #         "p": 25.0,
        #         "k": 35.0,
        #         "warranty": "Guaranteed analysis of nutrients.",
        #         "label_id": str(label_info_id),  # Include ID to target the correct record
        #     }
        # )

        # # Update existing label information
        # self.cursor.execute(
        #     "SELECT upsert_label_information(%s, %s, %s);",
        #     (updated_label_info, self.organization_info_id, self.organization_info_id),
        # )
        # updated_label_info_id = self.cursor.fetchone()[0]

        # # Assertions to verify update
        # self.assertEqual(
        #     label_info_id,
        #     updated_label_info_id,
        #     "Label info ID should remain the same after update",
        # )

        # # Verify that the data is correctly updated
        # self.cursor.execute(
        #     "SELECT product_name, lot_number, npk, registration_number, n, p, k, warranty, company_info_id, manufacturer_info_id FROM label_information WHERE id = %s;",
        #     (updated_label_info_id,),
        # )
        # updated_label_data = self.cursor.fetchone()
        # self.assertIsNotNone(
        #     updated_label_data, "Updated label data should not be None"
        # )
        # self.assertEqual(
        #     updated_label_data[0], "SuperGrow 20-20-20", "Name should match the updated value"
        # )
        # self.assertEqual(
        #     updated_label_data[1],
        #     "L987654321",
        #     "Lot number should match the updated value",
        # )
        # self.assertEqual(
        #     updated_label_data[2], "15-25-35", "NPK should match the updated value"
        # )
        # self.assertEqual(
        #     updated_label_data[3],
        #     "R654321",
        #     "Registration number should match the updated value",
        # )
        # self.assertEqual(
        #     updated_label_data[4], 15.0, "N value should match the updated value"
        # )
        # self.assertEqual(
        #     updated_label_data[5], 25.0, "P value should match the updated value"
        # )
        # self.assertEqual(
        #     updated_label_data[6], 35.0, "K value should match the updated value"
        # )
        # self.assertEqual(
        #     updated_label_data[7],
        #     "Guaranteed analysis of nutrients.",
        #     "Warranty should match the updated value",
        # )
        # self.assertEqual(
        #     updated_label_data[8],
        #     self.organization_info_id,
        #     "Company info ID should match",
        # )
        # self.assertEqual(
        #     updated_label_data[9],
        #     self.organization_info_id,
        #     "Manufacturer info ID should match",
        # )


if __name__ == "__main__":
    unittest.main()
