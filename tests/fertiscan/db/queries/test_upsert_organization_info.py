import json
import os
import unittest

import psycopg
from dotenv import load_dotenv

from fertiscan.db.models import Location, OrganizationInformation
from fertiscan.db.queries import organization
from fertiscan.db.queries.location import read_location

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
        # TODO: writing missing organization_info functions
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
        ornanization_info = organization.get_organization_info(
            self.cursor, new_org_info_id
        )
        self.assertIsNotNone(ornanization_info, "Organization info should not be None")
        self.assertEqual(
            ornanization_info[0],
            "GreenGrow Fertilizers Inc.",
            "Name should match the inserted value",
        )
        self.assertEqual(
            ornanization_info[1],
            "http://www.greengrowfertilizers.com",
            "Website should match the inserted value",
        )
        self.assertEqual(
            ornanization_info[2],
            "+1 800 555 0199",
            "Phone number should match the inserted value",
        )

        location_id = ornanization_info[3]
        self.assertIsNotNone(location_id, "Location ID should be present")

        # Verify location data
        location = read_location(self.cursor, location_id)
        location = Location.model_validate(location)
        self.assertIsNotNone(location, "Location should not be None")
        self.assertEqual(
            location.address,
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

        # TODO: writing missing organization_info functions
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
        # TODO: writing missing organization_info functions
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
        ornanization_info = organization.get_organization_info(
            self.cursor, new_org_info_id
        )
        self.assertIsNotNone(ornanization_info, "Organization info should not be None")
        self.assertEqual(
            ornanization_info[0],
            sample_org_info_new.name,
            "Name should match the inserted value",
        )
        self.assertEqual(
            ornanization_info[1],
            sample_org_info_new.website,
            "Website should match the inserted value",
        )
        self.assertEqual(
            ornanization_info[2],
            sample_org_info_new.phone_number,
            "Phone number should match the inserted value",
        )

        location_id = ornanization_info[3]
        self.assertIsNotNone(location_id, "Location ID should be present")


if __name__ == "__main__":
    unittest.main()
