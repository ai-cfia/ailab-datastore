import os
import unittest
import uuid

from dotenv import load_dotenv
from psycopg import Connection, connect
from psycopg.errors import ForeignKeyViolation

from fertiscan.db.models import Location, OrganizationInformation, Province, Region
from fertiscan.db.queries import organization
from fertiscan.db.queries.location import create_location, read_location
from fertiscan.db.queries.organization_information import (
    create_organization_information,
    delete_organization_information,
    query_organization_information,
    read_all_organization_information,
    read_organization_information,
    update_organization_information,
)
from fertiscan.db.queries.province import create_province
from fertiscan.db.queries.region import create_region

load_dotenv()

TEST_DB_CONNECTION_STRING = os.environ["FERTISCAN_DB_URL"]
TEST_DB_SCHEMA = os.environ["FERTISCAN_SCHEMA_TESTING"]


class TestOrganizationInformationFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Establish database connection before all tests
        cls.conn: Connection = connect(
            TEST_DB_CONNECTION_STRING, options=f"-c search_path={TEST_DB_SCHEMA},public"
        )
        cls.conn.autocommit = False

    @classmethod
    def tearDownClass(cls):
        # Close the database connection after all tests
        cls.conn.close()

    def setUp(self):
        # Set up test data and reusable resources before each test
        self.cursor = self.conn.cursor()

        self.province_name = "a-test-province"
        self.region_name = "test-region"
        self.location_name = "test-location"
        self.location_address = "test-address"

        # Create province, region, and location for testing
        self.province = create_province(self.cursor, self.province_name)
        self.province = Province.model_validate(self.province)

        self.region = create_region(self.cursor, self.region_name, self.province.id)
        self.region = Region.model_validate(self.region)

        self.location = create_location(
            self.cursor, self.location_name, self.location_address, self.region.id
        )
        self.location = Location.model_validate(self.location)

        # Set up organization information data
        self.name = "Test Org"
        self.website = "https://test.org"
        self.phone_number = "123456789"

    def tearDown(self):
        # Roll back changes and close the cursor after each test
        self.conn.rollback()
        self.cursor.close()

    def test_create_organization_information(self):
        # Test the creation of a new organization information record
        organization_information = create_organization_information(
            self.cursor, self.name, self.website, self.phone_number, self.location.id
        )
        organization_information = OrganizationInformation.model_validate(
            organization_information
        )

        # Assert that the created record matches the expected data
        self.assertEqual(organization_information.name, self.name)
        self.assertEqual(organization_information.website, self.website)
        self.assertEqual(organization_information.phone_number, self.phone_number)

    def test_create_organization_information_with_no_location(self):
        # Test creating an organization information record with no location
        organization_information = create_organization_information(
            self.cursor, self.name, self.website, self.phone_number, None
        )
        organization_information = OrganizationInformation.model_validate(
            organization_information
        )

        # Assert that the created record matches the expected data
        self.assertEqual(organization_information.name, self.name)
        self.assertEqual(organization_information.website, self.website)
        self.assertEqual(organization_information.phone_number, self.phone_number)

    def test_create_organization_information_with_invalid_location(self):
        # Test creating an organization information record with an invalid location
        with self.assertRaises(ForeignKeyViolation):
            create_organization_information(
                self.cursor, self.name, self.website, self.phone_number, uuid.uuid4()
            )

    def test_read_organization_information(self):
        # Test fetching a single organization information record by ID
        created = create_organization_information(
            self.cursor, self.name, self.website, self.phone_number, self.location.id
        )
        created = OrganizationInformation.model_validate(created)

        fetched = read_organization_information(self.cursor, created.id)
        fetched = OrganizationInformation.model_validate(fetched)

        # Assert that the fetched record matches the created one
        self.assertEqual(fetched, created)

    def test_read_all_organization_information(self):
        # Test fetching all organization information records
        initial_count = len(read_all_organization_information(self.cursor))

        # Create additional organization information records
        create_organization_information(
            self.cursor, "Org A", "https://orga.com", "111111111", self.location.id
        )
        create_organization_information(
            self.cursor, "Org B", "https://orgb.com", "222222222", self.location.id
        )

        all_organizations = read_all_organization_information(self.cursor)
        all_organizations = [
            OrganizationInformation.model_validate(o) for o in all_organizations
        ]

        # Assert that the total count of organizations increased
        self.assertGreaterEqual(len(all_organizations), initial_count + 2)

    def test_update_organization_information(self):
        # Test updating an existing organization information record
        created = create_organization_information(
            self.cursor, self.name, self.website, self.phone_number, self.location.id
        )
        created = OrganizationInformation.model_validate(created)

        # Update the organization information
        name = "Updated Org"
        website = "https://updated.org"
        phone_number = "987654321"
        updated = update_organization_information(
            self.cursor,
            id=created.id,
            name=name,
            website=website,
            phone_number=phone_number,
            edited=True,
        )
        updated = OrganizationInformation.model_validate(updated)

        # Assert that the updated record matches the new data
        self.assertEqual(updated.name, name)
        self.assertEqual(updated.website, website)
        self.assertEqual(updated.phone_number, phone_number)

    def test_update_organization_information_no_id(self):
        # Test updating with no organization ID (should raise ValueError)
        with self.assertRaises(ValueError):
            update_organization_information(self.cursor, None)

    def test_delete_organization_information(self):
        # Test deleting an organization information record
        created = create_organization_information(
            self.cursor, self.name, self.website, self.phone_number, self.location.id
        )
        created = OrganizationInformation.model_validate(created)

        # Delete the created record
        deleted = delete_organization_information(self.cursor, created.id)
        deleted = OrganizationInformation.model_validate(deleted)

        # Assert that the deleted record matches the created one
        self.assertEqual(deleted.id, created.id)

        # Verify that the record no longer exists
        fetched = read_organization_information(self.cursor, created.id)
        self.assertIsNone(fetched)

    def test_delete_organization_information_with_linked_records(self):
        # Test deletion with linked organization records (expecting ForeignKeyViolation)
        created = create_organization_information(
            self.cursor, self.name, self.website, self.phone_number, self.location.id
        )
        created = OrganizationInformation.model_validate(created)

        # Create an organization that references the organization information
        organization.new_organization(self.cursor, created.id, self.location.id)

        # Assert that a foreign key violation is raised upon deletion
        with self.assertRaises(ForeignKeyViolation):
            delete_organization_information(self.cursor, created.id)

    def test_delete_organization_information_with_shared_location(self):
        # Test deleting an organization information while its location is shared
        created_a = create_organization_information(
            self.cursor, self.name, self.website, self.phone_number, self.location.id
        )
        created_a = OrganizationInformation.model_validate(created_a)

        created_b = create_organization_information(
            self.cursor,
            "Another Org",
            "https://another.org",
            "987654321",
            self.location.id,
        )
        created_b = OrganizationInformation.model_validate(created_b)

        # Delete the first organization information
        delete_organization_information(self.cursor, created_a.id)

        # Verify that the first organization information was deleted
        fetched_a = read_organization_information(self.cursor, created_a.id)
        self.assertIsNone(fetched_a)

        # Verify that the shared location was not deleted
        location = read_location(self.cursor, self.location.id)
        self.assertIsNotNone(location)

        # Verify that the second organization information still exists
        fetched_b = read_organization_information(self.cursor, created_b.id)
        self.assertIsNotNone(fetched_b)

    def test_delete_organization_information_no_id(self):
        # Test deleting an organization information record without an ID
        with self.assertRaises(ValueError):
            delete_organization_information(self.cursor, None)

    def test_query_organization_information_by_name(self):
        # Test querying organization information by name
        unique_name = uuid.uuid4().hex

        create_organization_information(
            self.cursor, unique_name, self.website, self.phone_number, self.location.id
        )

        results = query_organization_information(self.cursor, name=unique_name)
        results = [OrganizationInformation.model_validate(r) for r in results]

        # Assert that exactly one matching result is found
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, unique_name)

    def test_query_organization_information_by_website(self):
        # Test querying organization information by website
        unique_website = f"https://{uuid.uuid4().hex}.org"

        create_organization_information(
            self.cursor, self.name, unique_website, self.phone_number, self.location.id
        )

        results = query_organization_information(self.cursor, website=unique_website)
        results = [OrganizationInformation.model_validate(r) for r in results]

        # Assert that exactly one matching result is found
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].website, unique_website)

    def test_query_organization_information_by_phone_number(self):
        # Test querying organization information by phone number
        unique_phone_number = uuid.uuid4().hex

        create_organization_information(
            self.cursor, self.name, self.website, unique_phone_number, self.location.id
        )

        results = query_organization_information(
            self.cursor, phone_number=unique_phone_number
        )
        results = [OrganizationInformation.model_validate(r) for r in results]

        # Assert that exactly one matching result is found
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].phone_number, unique_phone_number)

    def test_query_organization_information_by_location(self):
        # Test querying organization information by location ID
        org_in_location = create_organization_information(
            self.cursor, self.name, self.website, self.phone_number, self.location.id
        )
        org_in_location = OrganizationInformation.model_validate(org_in_location)

        results = query_organization_information(
            self.cursor, location_id=self.location.id
        )
        results = [OrganizationInformation.model_validate(r) for r in results]

        # Assert that the organization in the location is in the results
        self.assertIn(org_in_location, results)

    def test_query_organization_information_no_match(self):
        # Test querying for non-existent organization information by name
        results = query_organization_information(self.cursor, name=uuid.uuid4().hex)

        # Assert that no results are found
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
