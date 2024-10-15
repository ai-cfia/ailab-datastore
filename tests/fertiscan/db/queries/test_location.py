import os
import unittest
import uuid

from dotenv import load_dotenv
from psycopg import Connection, connect

from datastore.db.queries.user import register_user
from fertiscan.db.models import (
    FullLocation,
    Location,
    OrganizationInformation,
    Province,
    Region,
)
from fertiscan.db.queries.location import (
    create_location,
    delete_location,
    get_full_location,
    query_locations,
    read_all_locations,
    read_location,
    update_location,
    upsert_location,
)
from fertiscan.db.queries.organization import new_organization
from fertiscan.db.queries.organization_information import (
    create_organization_information,
)
from fertiscan.db.queries.province import create_province
from fertiscan.db.queries.region import create_region

load_dotenv()

TEST_DB_CONNECTION_STRING = os.environ["FERTISCAN_DB_URL"]
TEST_DB_SCHEMA = os.environ["FERTISCAN_SCHEMA_TESTING"]


class TestLocationFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn: Connection = connect(
            TEST_DB_CONNECTION_STRING, options=f"-c search_path={TEST_DB_SCHEMA},public"
        )
        cls.conn.autocommit = False

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        self.cursor = self.conn.cursor()

        # Create necessary records for testing
        self.province = create_province(self.cursor, uuid.uuid4().hex)
        self.province = Province.model_validate(self.province)
        self.region = create_region(self.cursor, "Test Region", self.province.id)
        self.region = Region.model_validate(self.region)

        self.inspector_id = register_user(self.cursor, "inspector@example.com")

        # Create a placeholder organization with necessary info
        org_info = create_organization_information(
            self.cursor,
            "Test Organization",
            "https://example.org",
            "123456789",
            None,  # No location yet
        )
        org_info = OrganizationInformation.model_validate(org_info)
        self.organization_id = new_organization(
            self.cursor,
            org_info.id,
            None,  # No location yet
        )

    def tearDown(self):
        self.conn.rollback()
        self.cursor.close()

    def test_create_location(self):
        name = "Test Location A"
        address = "123 Test Address"

        # Create location with valid region and owner
        created_location = create_location(
            self.cursor, name, address, self.region.id, self.organization_id
        )
        created_location = Location.model_validate(created_location)

        self.assertEqual(created_location.name, name)
        self.assertEqual(created_location.address, address)
        self.assertEqual(created_location.region_id, self.region.id)
        self.assertEqual(created_location.owner_id, self.organization_id)

    def test_read_location(self):
        name = "Test Location B"
        address = "456 Test Address"

        # Create location
        created_location = create_location(
            self.cursor, name, address, self.region.id, self.organization_id
        )
        created_location = Location.model_validate(created_location)

        # Read location by ID
        fetched_location = read_location(self.cursor, created_location.id)
        fetched_location = Location.model_validate(fetched_location)

        self.assertEqual(fetched_location, created_location)
        self.assertEqual(fetched_location.name, name)
        self.assertEqual(fetched_location.address, address)

    def test_read_all_locations(self):
        initial_locations = read_all_locations(self.cursor)

        # Create two locations
        location_a = create_location(
            self.cursor,
            "Test Location C",
            "789 Test Address A",
            self.region.id,
            self.organization_id,
        )
        location_b = create_location(
            self.cursor,
            "Test Location D",
            "101 Test Address B",
            self.region.id,
            self.organization_id,
        )

        all_locations = read_all_locations(self.cursor)
        all_locations = [Location.model_validate(loc) for loc in all_locations]

        self.assertGreaterEqual(len(all_locations), len(initial_locations) + 2)
        self.assertIn(Location.model_validate(location_a), all_locations)
        self.assertIn(Location.model_validate(location_b), all_locations)

    def test_update_location(self):
        # Create a location to update
        location = create_location(
            self.cursor,
            "Test Location E",
            "102 Test Address",
            self.region.id,
            self.organization_id,
        )
        location = Location.model_validate(location)

        # Update the location
        new_name = "Updated Location E"
        new_address = "Updated Address"
        updated_location = update_location(
            self.cursor, location.id, name=new_name, address=new_address
        )
        updated_location = Location.model_validate(updated_location)

        self.assertEqual(updated_location.name, new_name)
        self.assertEqual(updated_location.address, new_address)

        # Verify changes persisted in the database
        fetched_location = read_location(self.cursor, location.id)
        validated_fetched = Location.model_validate(fetched_location)

        self.assertEqual(validated_fetched, updated_location)

    def test_delete_location(self):
        # Create a location to delete
        location = create_location(
            self.cursor,
            "Test Location F",
            "103 Test Address",
            self.region.id,
            self.organization_id,
        )
        location = Location.model_validate(location)

        # Delete the location
        deleted_location = delete_location(self.cursor, location.id)
        validated_deleted = Location.model_validate(deleted_location)

        self.assertEqual(location, validated_deleted)

        # Ensure the location no longer exists
        fetched_location = read_location(self.cursor, location.id)
        self.assertIsNone(fetched_location)

    def test_upsert_location_create(self):
        # Create a new location using upsert
        address = "New Location Address"
        location_id = upsert_location(self.cursor, address)

        # Fetch the location to verify creation
        fetched_location = read_location(self.cursor, location_id)
        fetched_location = Location.model_validate(fetched_location)

        self.assertIsNotNone(fetched_location)
        self.assertEqual(fetched_location.address, address)

    def test_upsert_location_update(self):
        # Create a location to update
        address = "Initial Address"
        location_id = upsert_location(self.cursor, address)

        # Update the address of the existing location
        new_address = "Updated Address"
        updated_location_id = upsert_location(self.cursor, new_address, location_id)

        # Ensure the location ID remains the same
        self.assertEqual(location_id, updated_location_id)

        # Fetch the location to verify the address update
        fetched_location = read_location(self.cursor, updated_location_id)
        fetched_location = Location.model_validate(fetched_location)

        self.assertIsNotNone(fetched_location)
        self.assertEqual(fetched_location.address, new_address)

    def test_upsert_location_null_address(self):
        # Attempt to upsert a location with no address (should raise an error)
        with self.assertRaises(ValueError):
            upsert_location(self.cursor, "")
        with self.assertRaises(ValueError):
            upsert_location(self.cursor, None)

    def test_upsert_location_create_with_null_region_and_owner(self):
        # Create a new location using upsert with NULL region and owner
        address = "New Location Address"
        name = "New Location"
        location_id = upsert_location(self.cursor, address, name=name)

        # Fetch the location to verify creation
        fetched_location = read_location(self.cursor, location_id)
        fetched_location = Location.model_validate(fetched_location)

        self.assertIsNotNone(fetched_location)
        self.assertEqual(fetched_location.address, address)
        self.assertEqual(fetched_location.name, name)
        self.assertIsNone(fetched_location.region_id)
        self.assertIsNone(fetched_location.owner_id)

    def test_upsert_location_update_to_null_region_and_owner(self):
        # Create a location with region and owner
        address = "Initial Address"
        name = "Initial Name"
        location_id = upsert_location(
            self.cursor,
            address,
            name=name,
            region_id=self.region.id,
            owner_id=self.organization_id,
        )

        # Update the location to set region and owner to NULL
        updated_address = "Updated Address"
        updated_name = "Updated Name"
        updated_location_id = upsert_location(
            self.cursor,
            updated_address,
            location_id,
            name=updated_name,
            region_id=None,
            owner_id=None,
        )

        # Ensure the location ID remains the same
        self.assertEqual(location_id, updated_location_id)

        # Fetch the location to verify the update
        fetched_location = read_location(self.cursor, updated_location_id)
        fetched_location = Location.model_validate(fetched_location)

        self.assertIsNotNone(fetched_location)
        self.assertEqual(fetched_location.address, updated_address)
        self.assertEqual(fetched_location.name, updated_name)
        self.assertIsNone(fetched_location.region_id)
        self.assertIsNone(fetched_location.owner_id)

    def test_get_full_location_with_region_and_province(self):
        # Create province and region
        province_name = uuid.uuid4().hex
        region_name = "Test Region"
        province = create_province(self.cursor, province_name)
        province = Province.model_validate(province)
        region = create_region(self.cursor, region_name, province.id)
        region = Region.model_validate(region)

        # Create a location with the new region
        address = "Test Address"
        name = "Test Location"
        location_id = upsert_location(
            self.cursor, address, name=name, region_id=region.id
        )

        # Fetch full location details
        full_location = get_full_location(self.cursor, location_id)
        full_location = FullLocation.model_validate(full_location)

        self.assertIsNotNone(full_location)
        self.assertEqual(full_location.id, location_id)
        self.assertEqual(full_location.name, name)
        self.assertEqual(full_location.address, address)
        self.assertEqual(full_location.region_name, region_name)
        self.assertEqual(full_location.province_name, province_name)

    def test_get_full_location_without_region_and_province(self):
        # Create a location without a region
        address = "Test Address without Region"
        name = "Test Location without Region"
        location_id = upsert_location(self.cursor, address, name=name)

        # Fetch full location details
        full_location = get_full_location(self.cursor, location_id)
        full_location = FullLocation.model_validate(full_location)

        self.assertIsNotNone(full_location)
        self.assertEqual(full_location.id, location_id)
        self.assertEqual(full_location.name, name)
        self.assertEqual(full_location.address, address)
        self.assertIsNone(full_location.region_name)
        self.assertIsNone(full_location.province_name)

    def test_get_full_location_invalid_id(self):
        # Try to fetch a location with an invalid ID
        invalid_location_id = uuid.uuid4()

        # Ensure that no location is returned for the invalid ID
        full_location = get_full_location(self.cursor, invalid_location_id)

        self.assertIsNone(full_location)

    def test_query_locations_without_filter(self):
        # Create two locations
        location1 = create_location(self.cursor, "Location A", "123 Main St")
        location2 = create_location(self.cursor, "Location B", "456 Elm St")

        # Query all locations
        locations = query_locations(self.cursor)

        # Check that the created locations are in the result
        self.assertGreaterEqual(len(locations), 2)
        self.assertIn(location1, locations)
        self.assertIn(location2, locations)

    def test_query_locations_with_name_filter(self):
        # Create a location with a specific name
        name = "Specific Location"
        create_location(self.cursor, name, "789 Maple St")

        # Query locations by name
        locations = query_locations(self.cursor, name=name)

        # Validate the result
        self.assertEqual(len(locations), 1)
        self.assertEqual(locations[0]["name"], name)

    def test_query_locations_with_address_filter(self):
        # Create a location with a specific address
        address = "Special Address"
        create_location(self.cursor, "Some Location", address)

        # Query locations by address
        locations = query_locations(self.cursor, address=address)

        # Validate the result
        self.assertEqual(len(locations), 1)
        self.assertEqual(locations[0]["address"], address)

    def test_query_locations_with_region_filter(self):
        # Create a location with a specific region
        region = create_region(self.cursor, "Region Filter Test", self.province.id)
        region = Region.model_validate(region)
        create_location(
            self.cursor,
            "Region Location",
            "111 Oak St",
            region_id=region.id,
        )

        # Query locations by region
        locations = query_locations(self.cursor, region_id=region.id)
        locations = [Location.model_validate(location) for location in locations]

        # Validate the result
        self.assertEqual(len(locations), 1)
        self.assertEqual(locations[0].region_id, region.id)

    def test_query_locations_with_owner_filter(self):
        # Create a location with a specific owner
        create_location(
            self.cursor,
            "Owner Location",
            "222 Pine St",
            owner_id=self.organization_id,
        )

        # Query locations by owner
        locations = query_locations(self.cursor, owner_id=self.organization_id)
        locations = [Location.model_validate(location) for location in locations]

        # Validate the result
        self.assertGreaterEqual(len(locations), 1)
        self.assertEqual(locations[0].owner_id, self.organization_id)

    def test_query_locations_with_nonexistent_filter(self):
        # Query with filters that don't match any location
        locations = query_locations(self.cursor, name="Nonexistent", address="No Way")

        # Validate that the result is empty
        self.assertEqual(len(locations), 0)


if __name__ == "__main__":
    unittest.main()
