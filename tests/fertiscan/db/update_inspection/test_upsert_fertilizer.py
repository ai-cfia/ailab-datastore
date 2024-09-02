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


class TestUpsertFertilizerFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

        # Prepopulate organization_information table
        self.cursor.execute(
            "INSERT INTO organization_information (name, website, phone_number) "
            "VALUES (%s, %s, %s) RETURNING id;",
            (
                "Test Organization Information",
                "http://www.testorginfo.com",
                "+1 800 555 0101",
            ),
        )
        self.organization_info_id = self.cursor.fetchone()[0]

        # Prepopulate location table
        self.cursor.execute(
            "INSERT INTO location (name, address) " "VALUES (%s, %s) RETURNING id;",
            ("Test Location", "123 Test Address, Test City"),
        )
        self.location_id = self.cursor.fetchone()[0]

        # Prepopulate organization table with references to organization_information and location
        self.cursor.execute(
            "INSERT INTO organization (information_id, main_location_id) "
            "VALUES (%s, %s) RETURNING id;",
            (self.organization_info_id, self.location_id),
        )
        self.organization_id = self.cursor.fetchone()[0]

        # Insert a user to act as the inspector
        self.cursor.execute(
            "INSERT INTO users (email) VALUES (%s) RETURNING id;",
            ("test_inspector@example.com",),
        )
        self.inspector_id = self.cursor.fetchone()[0]

        # Insert a label information record to link with inspection
        self.cursor.execute(
            "INSERT INTO label_information (lot_number, npk, registration_number, n, p, k) "
            "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
            ("L123456789", "10-20-30", "R123456", 10.0, 20.0, 30.0),
        )
        self.label_info_id = self.cursor.fetchone()[0]

        # Insert an inspection record
        self.cursor.execute(
            "SELECT upsert_inspection(%s, %s, %s, %s, %s, %s, %s);",
            (None, self.label_info_id, self.inspector_id, None, None, False, None),
        )
        self.inspection_id = self.cursor.fetchone()[0]

    def tearDown(self):
        # Rollback any changes to leave the database state as it was before the test
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_insert_new_fertilizer(self):
        fertilizer_name = "Test Fertilizer"
        registration_number = "T12345"
        owner_id = self.organization_id
        latest_inspection_id = self.inspection_id  # Use the pre-inserted inspection ID

        # Insert new fertilizer
        self.cursor.execute(
            "SELECT upsert_fertilizer(%s, %s, %s, %s);",
            (fertilizer_name, registration_number, owner_id, latest_inspection_id),
        )
        fertilizer_id = self.cursor.fetchone()[0]

        # Assertions to verify insertion
        self.assertIsNotNone(fertilizer_id, "New fertilizer ID should not be None")

        # Verify that the data is correctly saved
        self.cursor.execute(
            "SELECT name, registration_number, owner_id, latest_inspection_id FROM fertilizer WHERE id = %s;",
            (fertilizer_id,),
        )
        saved_fertilizer_data = self.cursor.fetchone()
        self.assertIsNotNone(
            saved_fertilizer_data, "Saved fertilizer data should not be None"
        )
        self.assertEqual(
            saved_fertilizer_data[0],
            fertilizer_name,
            "Name should match the inserted value",
        )
        self.assertEqual(
            saved_fertilizer_data[1],
            registration_number,
            "Registration number should match the inserted value",
        )
        self.assertEqual(
            saved_fertilizer_data[2],
            owner_id,
            "Owner ID should match the inserted value",
        )
        self.assertEqual(
            saved_fertilizer_data[3],
            latest_inspection_id,
            "Latest inspection ID should match the inserted value",
        )

    def test_update_existing_fertilizer(self):
        fertilizer_name = "Test Fertilizer"
        registration_number = "T12345"
        owner_id = self.organization_id
        latest_inspection_id = self.inspection_id

        # Insert new fertilizer to get a valid fertilizer_id
        self.cursor.execute(
            "SELECT upsert_fertilizer(%s, %s, %s, %s);",
            (fertilizer_name, registration_number, owner_id, latest_inspection_id),
        )
        fertilizer_id = self.cursor.fetchone()[0]

        # Update the fertilizer information
        updated_registration_number = "T67890"

        self.cursor.execute(
            "SELECT upsert_fertilizer(%s, %s, %s, %s);",
            (
                fertilizer_name,
                updated_registration_number,
                owner_id,
                latest_inspection_id,
            ),
        )
        updated_fertilizer_id = self.cursor.fetchone()[0]

        # Assertions to verify update
        self.assertEqual(
            fertilizer_id,
            updated_fertilizer_id,
            "Fertilizer ID should remain the same after update",
        )

        # Verify that the data is correctly updated
        self.cursor.execute(
            "SELECT name, registration_number, owner_id, latest_inspection_id FROM fertilizer WHERE id = %s;",
            (updated_fertilizer_id,),
        )
        updated_fertilizer_data = self.cursor.fetchone()
        self.assertIsNotNone(
            updated_fertilizer_data, "Updated fertilizer data should not be None"
        )
        self.assertEqual(
            updated_fertilizer_data[1],
            updated_registration_number,
            "Registration number should match the updated value",
        )
        self.assertEqual(
            updated_fertilizer_data[3],
            latest_inspection_id,
            "Latest inspection ID should remain unchanged",
        )


if __name__ == "__main__":
    unittest.main()
