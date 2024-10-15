import os
import unittest
import uuid

from dotenv import load_dotenv
from psycopg import Connection, connect

from fertiscan.db.models import (
    LocatedOrganizationInformation,
    Location,
    OrganizationInformation,
    Province,
    Region,
)
from fertiscan.db.queries.located_organization_information import (
    create_located_organization_information,
    delete_located_organization_information,
    query_located_organization_information,
    read_all_located_organization_information,
    read_located_organization_information,
    update_located_organization_information,
    upsert_located_organization_information,
)
from fertiscan.db.queries.location import create_location, read_location
from fertiscan.db.queries.organization_information import read_organization_information
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

        # Set up organization information data
        self.name = "Test Org"
        self.website = "https://test.org"
        self.phone_number = "123456789"

    def tearDown(self):
        # Roll back changes and close the cursor after each test
        self.conn.rollback()
        self.cursor.close()

    def test_create_located_organization_information(self):
        # Test the creation of a new organization information record
        org_info_id = create_located_organization_information(
            self.cursor,
            self.name,
            self.location_address,
            self.website,
            self.phone_number,
        )

        # Assert that the created record matches the expected data
        self.assertIsNotNone(org_info_id)
        org_info = read_organization_information(self.cursor, org_info_id)
        org_info = OrganizationInformation.model_validate(org_info)
        self.assertEqual(org_info.name, self.name)
        self.assertEqual(org_info.website, self.website)
        self.assertEqual(org_info.phone_number, self.phone_number)

        # Assert that a location was created and associated with the organization
        location = read_location(self.cursor, org_info.location_id)
        location = Location.model_validate(location)
        self.assertEqual(location.address, self.location_address)

    def test_read_located_organization_information(self):
        # Test reading an existing organization information record
        org_info_id = create_located_organization_information(
            self.cursor,
            self.name,
            self.location_address,
            self.website,
            self.phone_number,
        )

        # Fetch the organization information record
        fetched = read_located_organization_information(self.cursor, org_info_id)
        fetched = LocatedOrganizationInformation.model_validate(fetched)

        # Assert that the fetched record matches the expected data
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, self.name)
        self.assertEqual(fetched.address, self.location_address)
        self.assertEqual(fetched.website, self.website)
        self.assertEqual(fetched.phone_number, self.phone_number)

    def test_create_located_organization_information_with_no_address(self):
        # Test creating an organization information record with no location
        org_info_id = create_located_organization_information(
            self.cursor,
            name=self.name,
            website=self.website,
            phone_number=self.phone_number,
        )

        # Fetch the organization information record
        fetched = read_located_organization_information(self.cursor, org_info_id)
        fetched = LocatedOrganizationInformation.model_validate(fetched)

        # Assert that the fetched record matches the expected data
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, self.name)
        self.assertIsNone(fetched.address)
        self.assertEqual(fetched.website, self.website)
        self.assertEqual(fetched.phone_number, self.phone_number)

    def test_create_located_organization_information_with_no_data(self):
        # Test creating an organization information record with no data
        with self.assertRaises(ValueError):
            create_located_organization_information(self.cursor)

    def test_create_located_organization_information_with_existing_address(self):
        # Create a Location
        address = uuid.uuid4().hex
        location = create_location(self.cursor, name=self.name, address=address)
        location = Location.model_validate(location)

        # Test creating an organization information record with an existing location
        org_info_id = create_located_organization_information(
            self.cursor, name=self.name, address=address
        )
        org_info = read_organization_information(self.cursor, org_info_id)
        org_info = OrganizationInformation.model_validate(org_info)
        self.assertIsNotNone(org_info.location_id)
        self.assertEqual(org_info.location_id, location.id)

    def test_read_all_located_organization_information(self):
        # Test reading all organization information records
        org_info_id_1 = create_located_organization_information(
            self.cursor,
            self.name,
            self.location_address,
            self.website,
            self.phone_number,
        )

        org_info_id_2 = create_located_organization_information(
            self.cursor,
            self.name,
            self.location_address,
            self.website,
            self.phone_number,
        )

        # Fetch all organization information records
        fetched = read_all_located_organization_information(self.cursor)
        fetched = [
            LocatedOrganizationInformation.model_validate(org) for org in fetched
        ]

        # Assert that the fetched records match the expected data
        self.assertEqual(len(fetched), 2)
        self.assertEqual(fetched[0].id, org_info_id_1)
        self.assertEqual(fetched[1].id, org_info_id_2)

    def test_update_located_organization_information(self):
        # Test updating an existing organization information record
        org_info_id = create_located_organization_information(
            self.cursor,
            self.name,
            self.location_address,
            self.website,
            self.phone_number,
        )

        # Declare updated values
        updated_name = "Updated Org"
        updated_website = "https://updated.org"
        updated_phone_number = "987654321"
        updated_address = "updated-address"

        # Update the organization information record
        update_located_organization_information(
            self.cursor,
            id=org_info_id,
            name=updated_name,
            address=updated_address,
            website=updated_website,
            phone_number=updated_phone_number,
        )

        # Fetch the updated organization information record
        fetched = read_located_organization_information(self.cursor, org_info_id)
        fetched = LocatedOrganizationInformation.model_validate(fetched)

        # Assert that the fetched record matches the updated data
        self.assertEqual(fetched.name, updated_name)
        self.assertEqual(fetched.address, updated_address)
        self.assertEqual(fetched.website, updated_website)
        self.assertEqual(fetched.phone_number, updated_phone_number)

        # Assert that the location was updated
        # self.assertEqual(location_updated.id, location.id)

    def test_update_located_organization_information_no_id(self):
        # Test updating an organization information record without an ID
        with self.assertRaises(ValueError):
            update_located_organization_information(self.cursor, None)

    def test_update_located_organization_with_existing_address(self):
        # Create a Location
        address = uuid.uuid4().hex
        location = create_location(self.cursor, name=self.name, address=address)
        location = Location.model_validate(location)

        # Create an organization information record
        org_info_id = create_located_organization_information(
            self.cursor, name=self.name, address=address
        )

        # Test updating an organization information record with an existing location
        update_located_organization_information(
            self.cursor, id=org_info_id, name=self.name, address=address
        )

        org_info = read_organization_information(self.cursor, org_info_id)
        org_info = OrganizationInformation.model_validate(org_info)
        self.assertIsNotNone(org_info.location_id)
        self.assertEqual(org_info.location_id, location.id)
        location_updated = read_location(self.cursor, org_info.location_id)
        location_updated = Location.model_validate(location_updated)
        self.assertEqual(location_updated.address, address)

    def test_delete_located_organization_information(self):
        # Test deleting an organization information record
        org_info_id = create_located_organization_information(
            self.cursor,
            self.name,
            self.location_address,
            self.website,
            self.phone_number,
        )

        # Delete the organization information record
        deleted = delete_located_organization_information(self.cursor, id=org_info_id)

        # Assert that the record was deleted
        self.assertTrue(deleted)

        # Assert that the record is no longer in the database
        fetched = read_located_organization_information(self.cursor, org_info_id)
        self.assertIsNone(fetched)

    def test_delete_located_organization_information_no_id(self):
        # Test deleting a located organization information record without an ID
        with self.assertRaises(ValueError):
            delete_located_organization_information(self.cursor, None)

    def test_query_located_organization_information_by_name(self):
        # Test querying located organization information by name
        unique_name = uuid.uuid4().hex

        create_located_organization_information(
            self.cursor,
            unique_name,
            self.location_address,
            self.website,
            self.phone_number,
        )

        results = query_located_organization_information(self.cursor, name=unique_name)
        results = [LocatedOrganizationInformation.model_validate(r) for r in results]

        # Assert that exactly one matching result is found
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, unique_name)

    def test_query_located_organization_information_by_website(self):
        # Test querying located organization information by website
        unique_website = f"https://{uuid.uuid4().hex}.org"

        create_located_organization_information(
            self.cursor,
            self.name,
            self.location_address,
            unique_website,
            self.phone_number,
        )

        results = query_located_organization_information(
            self.cursor, website=unique_website
        )
        results = [LocatedOrganizationInformation.model_validate(r) for r in results]

        # Assert that exactly one matching result is found
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].website, unique_website)

    def test_query_located_organization_information_by_phone_number(self):
        # Test querying located organization information by phone number
        unique_phone_number = uuid.uuid4().hex

        create_located_organization_information(
            self.cursor,
            self.name,
            self.location_address,
            self.website,
            unique_phone_number,
        )

        results = query_located_organization_information(
            self.cursor, phone_number=unique_phone_number
        )
        results = [LocatedOrganizationInformation.model_validate(r) for r in results]

        # Assert that exactly one matching result is found
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].phone_number, unique_phone_number)

    def test_query_located_organization_information_by_address(self):
        # Test querying located organization information by address
        unique_address = f"{uuid.uuid4().hex} Test Street"

        created_id = create_located_organization_information(
            self.cursor,
            self.name,
            unique_address,
            self.website,
            self.phone_number,
        )
        created = read_located_organization_information(self.cursor, created_id)
        created = LocatedOrganizationInformation.model_validate(created)

        results = query_located_organization_information(
            self.cursor, address=unique_address
        )
        results = [LocatedOrganizationInformation.model_validate(r) for r in results]

        # Assert that exactly one matching result is found
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, created.id)
        self.assertEqual(results[0].address, unique_address)

    def test_query_located_organization_information_no_match(self):
        # Test querying for non-existent located organization information by name
        results = query_located_organization_information(
            self.cursor, name=uuid.uuid4().hex
        )

        # Assert that no results are found
        self.assertEqual(len(results), 0)

    def test_upsert_located_organization_information_create(self):
        # Test creating a new located organization information
        unique_name = uuid.uuid4().hex
        unique_address = f"{uuid.uuid4().hex} Test Street"
        unique_website = f"https://{uuid.uuid4().hex}.org"
        unique_phone_number = uuid.uuid4().hex

        # Upsert organization information
        created_id = upsert_located_organization_information(
            self.cursor,
            name=unique_name,
            address=unique_address,
            website=unique_website,
            phone_number=unique_phone_number,
        )

        # Read back the organization information
        created = read_located_organization_information(self.cursor, created_id)
        created = LocatedOrganizationInformation.model_validate(created)

        # Assert that the created organization information matches the input
        self.assertEqual(created.id, created_id)
        self.assertEqual(created.name, unique_name)
        self.assertEqual(created.address, unique_address)
        self.assertEqual(created.website, unique_website)
        self.assertEqual(created.phone_number, unique_phone_number)

    def test_upsert_located_organization_information_update(self):
        # First, create a new organization information
        created_id = upsert_located_organization_information(
            self.cursor,
            name=self.name,
            address=self.location_address,
            website=self.website,
            phone_number=self.phone_number,
        )

        # Now, update the existing organization information
        updated_address = f"{uuid.uuid4().hex} Test Street"
        updated_website = f"https://{uuid.uuid4().hex}.org"
        updated_phone_number = uuid.uuid4().hex
        upsert_located_organization_information(
            self.cursor,
            id=created_id,
            name=self.name,  # Name remains the same
            address=updated_address,
            website=updated_website,
            phone_number=updated_phone_number,
        )

        # Read back the updated organization information
        updated = read_located_organization_information(self.cursor, created_id)
        updated = LocatedOrganizationInformation.model_validate(updated)

        # Assert that the updated fields match the new input
        self.assertEqual(updated.id, created_id)
        self.assertEqual(updated.name, self.name)
        self.assertEqual(updated.address, updated_address)
        self.assertEqual(updated.website, updated_website)
        self.assertEqual(updated.phone_number, updated_phone_number)

    def test_upsert_located_organization_information_no_input(self):
        # Test upsert with no input values should raise ValueError
        with self.assertRaises(ValueError):
            upsert_located_organization_information(self.cursor)

    def test_upsert_located_organization_information_invalid_id(self):
        # Test upsert with an invalid UUID should raise ValueError
        invalid_id = "invalid-uuid-string"
        with self.assertRaises(Exception):
            upsert_located_organization_information(
                self.cursor,
                id=invalid_id,
                name=self.name,
                address=self.location_address,
            )

    def test_upsert_located_organization_information_missing_name(self):
        # Test upsert without a name but with other fields
        unique_address = f"{uuid.uuid4().hex} Test Street"
        unique_website = f"https://{uuid.uuid4().hex}.org"
        unique_phone_number = uuid.uuid4().hex

        # Upsert organization information without name
        created_id = upsert_located_organization_information(
            self.cursor,
            address=unique_address,
            website=unique_website,
            phone_number=unique_phone_number,
        )

        # Read back the organization information
        created = read_located_organization_information(self.cursor, created_id)
        created = LocatedOrganizationInformation.model_validate(created)

        # Assert that the created organization information matches the input
        self.assertEqual(created.id, created_id)
        self.assertIsNone(created.name)
        self.assertEqual(created.address, unique_address)
        self.assertEqual(created.website, unique_website)
        self.assertEqual(created.phone_number, unique_phone_number)


if __name__ == "__main__":
    unittest.main()
