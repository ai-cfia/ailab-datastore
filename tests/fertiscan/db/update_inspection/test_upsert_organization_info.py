import json
import os
import unittest

import psycopg
from dotenv import load_dotenv
from datastore.db.metadata.inspection import OrganizationInformation  # Assuming this Pydantic model exists

load_dotenv()

# Fetch database connection URL and schema from environment variables
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestUpsertOrganizationInfoFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

    def tearDown(self):
        # Rollback any changes to leave the database state as it was before the test
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_insert_new_organization(self):
        # Set up new organization info using the OrganizationInformation Pydantic model
        sample_org_info_new = OrganizationInformation(
            id=None,
            name="GreenGrow Fertilizers Inc.",
            address="123 Greenway Blvd, Springfield IL 62701 USA",
            website="http://www.greengrowfertilizers.com",
            phone_number="+1 800 555 0199",
        )

        # Insert new organization information
        self.cursor.execute(
            "SELECT upsert_organization_info(%s);",
            (json.dumps(sample_org_info_new.model_dump()),),
        )
        new_org_info_result = self.cursor.fetchone()

        # Assertions to verify insertion
        self.assertIsNotNone(
            new_org_info_result, "New organization info result should not be None"
        )
        new_org_info_id = new_org_info_result[0]
        self.assertTrue(new_org_info_id, "New organization info ID should be present")

        # Verify that the data is correctly saved
        self.cursor.execute(
            "SELECT name, website, phone_number, location_id FROM organization_information WHERE id = %s;",
            (new_org_info_id,),
        )
        saved_org_data = self.cursor.fetchone()
        self.assertIsNotNone(
            saved_org_data, "Saved organization data should not be None"
        )
        self.assertEqual(
            saved_org_data[0],
            "GreenGrow Fertilizers Inc.",
            "Name should match the inserted value",
        )
        self.assertEqual(
            saved_org_data[1],
            "http://www.greengrowfertilizers.com",
            "Website should match the inserted value",
        )
        self.assertEqual(
            saved_org_data[2],
            "+1 800 555 0199",
            "Phone number should match the inserted value",
        )

        location_id = saved_org_data[3]
        self.assertIsNotNone(location_id, "Location ID should be present")

        # Verify location data
        self.cursor.execute(
            "SELECT address FROM location WHERE id = %s;", (location_id,)
        )
        saved_location_data = self.cursor.fetchone()
        self.assertIsNotNone(
            saved_location_data, "Saved location data should not be None"
        )
        self.assertEqual(
            saved_location_data[0],
            "123 Greenway Blvd, Springfield IL 62701 USA",
            "Address should match the inserted value",
        )

    def test_update_existing_organization(self):
        # Insert new organization to retrieve an ID
        sample_org_info_new = OrganizationInformation(
            id=None,
            name="GreenGrow Fertilizers Inc.",
            address="123 Greenway Blvd, Springfield IL 62701 USA",
            website="http://www.greengrowfertilizers.com",
            phone_number="+1 800 555 0199",
        )

        self.cursor.execute(
            "SELECT upsert_organization_info(%s);",
            (json.dumps(sample_org_info_new.model_dump()),),
        )
        new_org_info_result = self.cursor.fetchone()
        new_org_info_id = new_org_info_result[0]

        # Modify the existing organization info for an update
        sample_org_info_new.name = "GreenGrow Fertilizers Inc. Updated"
        sample_org_info_new.website = "http://www.greengrowfertilizers-updated.com"
        sample_org_info_new.id = str(new_org_info_id)

        # Update existing organization information
        self.cursor.execute(
            "SELECT upsert_organization_info(%s);",
            (json.dumps(sample_org_info_new.model_dump()),),
        )
        updated_org_info_result = self.cursor.fetchone()

        # Assertions to verify update
        self.assertIsNotNone(
            updated_org_info_result,
            "Updated organization info result should not be None",
        )
        self.assertEqual(
            updated_org_info_result[0],
            new_org_info_id,
            "Organization info ID should remain the same after update",
        )

        # Verify that the data is correctly updated
        self.cursor.execute(
            "SELECT name, website, phone_number, location_id FROM organization_information WHERE id = %s;",
            (new_org_info_id,),
        )
        updated_org_data = self.cursor.fetchone()
        self.assertIsNotNone(updated_org_data, "Updated data should not be None")
        self.assertEqual(
            updated_org_data[0],
            "GreenGrow Fertilizers Inc. Updated",
            "Name should match the updated value",
        )
        self.assertEqual(
            updated_org_data[1],
            "http://www.greengrowfertilizers-updated.com",
            "Website should match the updated value",
        )

        location_id = updated_org_data[3]
        self.assertIsNotNone(location_id, "Location ID should be present after update")

        # Verify location data
        self.cursor.execute(
            "SELECT address FROM location WHERE id = %s;", (location_id,)
        )
        updated_location_data = self.cursor.fetchone()
        self.assertIsNotNone(
            updated_location_data, "Updated location data should not be None"
        )
        self.assertEqual(
            updated_location_data[0],
            "123 Greenway Blvd, Springfield IL 62701 USA",
            "Address should match the updated value",
        )


if __name__ == "__main__":
    unittest.main()
