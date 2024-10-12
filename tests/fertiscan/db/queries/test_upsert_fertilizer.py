import os
import unittest
import uuid

import psycopg
from dotenv import load_dotenv

from datastore.db.queries import user
from fertiscan.db.queries import inspection, label, organization

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

        self.inspector_id = user.register_user(
            self.cursor, f"{uuid.uuid4().hex}@example.com"
        )

        self.province_name = "a-test-province"
        self.region_name = "test-region"
        self.name = "test-organization"
        self.website = "www.test.com"
        self.phone = "123456789"
        self.location_name = "test-location"
        self.location_address = "test-address"

        self.province_id = organization.new_province(self.cursor, self.province_name)
        self.region_id = organization.new_region(
            self.cursor, self.region_name, self.province_id
        )
        self.location_id = organization.new_location(
            self.cursor, self.location_name, self.location_address, self.region_id
        )
        self.organization_info_id = organization.new_organization_info(
            self.cursor, self.name, self.website, self.phone, self.location_id
        )
        self.organization_id = organization.new_organization(
            self.cursor, self.organization_info_id, self.location_id
        )

        self.label_id = label.new_label_information(
            self.cursor,
            "Test Label",
            "L123456789",
            "10-20-30",
            "R123456",
            10.0,
            20.0,
            30.0,
            None,
            None,
            None,
            self.organization_info_id,
            self.organization_info_id,
        )

        # Insert an inspection record
        self.inspection_id = inspection.new_inspection(
            self.cursor, self.inspector_id, None, False
        )

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
        # TODO: write missing fertilizer functions
        self.cursor.execute(
            "SELECT upsert_fertilizer(%s, %s, %s, %s);",
            (fertilizer_name, registration_number, owner_id, latest_inspection_id),
        )
        fertilizer_id = self.cursor.fetchone()[0]

        # Assertions to verify insertion
        self.assertIsNotNone(fertilizer_id, "New fertilizer ID should not be None")

        # Verify that the data is correctly saved
        # TODO: write missing fertilizer functions
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
        # TODO: write missing fertilizer functions
        self.cursor.execute(
            "SELECT upsert_fertilizer(%s, %s, %s, %s);",
            (fertilizer_name, registration_number, owner_id, latest_inspection_id),
        )
        fertilizer_id = self.cursor.fetchone()[0]

        # Update the fertilizer information
        updated_registration_number = "T67890"

        # TODO: write missing fertilizer functions
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
        # TODO: write missing fertilizer functions
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
