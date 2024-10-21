import os
import unittest
import uuid

from dotenv import load_dotenv
from psycopg import Connection, connect

from fertiscan.db.models import FullRegion, Region
from fertiscan.db.queries.region import (
    create_region,
    delete_region,
    get_full_region,
    query_regions,
    read_all_regions,
    read_region,
    update_region,
)

load_dotenv()

TEST_DB_CONNECTION_STRING = os.environ["FERTISCAN_DB_URL"]
TEST_DB_SCHEMA = os.environ["FERTISCAN_SCHEMA_TESTING"]


class TestRegionFunctions(unittest.TestCase):
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
        self.province_name = uuid.uuid4().hex  # Unique province name to avoid conflicts
        self.province_id = self.create_province(self.province_name)

    def tearDown(self):
        self.conn.rollback()
        self.cursor.close()

    def create_province(self, name: str) -> int:
        """Helper method to create a province for testing."""
        query = "INSERT INTO province (name) VALUES (%s) RETURNING id;"
        self.cursor.execute(query, (name,))
        return self.cursor.fetchone()[0]

    def test_create_region(self):
        name = "Test Region A"
        created_region = create_region(self.cursor, name, self.province_id)
        created_region = Region.model_validate(created_region)

        self.assertEqual(created_region.name, name)
        self.assertEqual(created_region.province_id, self.province_id)

    def test_read_region(self):
        name = "Test Region B"
        created_region = create_region(self.cursor, name, self.province_id)
        validated_region = Region.model_validate(created_region)

        fetched_region = read_region(self.cursor, validated_region.id)
        fetched_region = Region.model_validate(fetched_region)

        self.assertEqual(fetched_region, validated_region)

    def test_read_all_regions(self):
        initial_regions = read_all_regions(self.cursor)

        region_a = create_region(self.cursor, "Test Region C", self.province_id)
        region_b = create_region(self.cursor, "Test Region D", self.province_id)

        all_regions = read_all_regions(self.cursor)
        all_regions = [Region.model_validate(r) for r in all_regions]

        self.assertGreaterEqual(len(all_regions), len(initial_regions) + 2)
        self.assertIn(Region.model_validate(region_a), all_regions)
        self.assertIn(Region.model_validate(region_b), all_regions)

    def test_update_region(self):
        region = create_region(self.cursor, "Test Region E", self.province_id)
        validated_region = Region.model_validate(region)

        new_name = "Updated Region E"
        updated_region = update_region(self.cursor, validated_region.id, name=new_name)
        validated_updated = Region.model_validate(updated_region)

        self.assertEqual(validated_updated.name, new_name)

        fetched_region = read_region(self.cursor, validated_region.id)
        fetched_region = Region.model_validate(fetched_region)

        self.assertEqual(fetched_region, validated_updated)

    def test_delete_region(self):
        region = create_region(self.cursor, "Test Region F", self.province_id)
        validated_region = Region.model_validate(region)

        deleted_region = delete_region(self.cursor, validated_region.id)
        deleted_region = Region.model_validate(deleted_region)

        self.assertEqual(validated_region, deleted_region)

        fetched_region = read_region(self.cursor, validated_region.id)
        self.assertIsNone(fetched_region)

    def test_query_region_by_name(self):
        name = uuid.uuid4().hex
        create_region(self.cursor, name, self.province_id)

        result = query_regions(self.cursor, name=name)
        regions = [Region.model_validate(r) for r in result]

        self.assertTrue(len(regions) > 0)
        self.assertEqual(regions[0].name, name)

    def test_query_region_by_province_id(self):
        name = uuid.uuid4().hex
        region = create_region(self.cursor, name, self.province_id)
        region = Region.model_validate(region)

        result = query_regions(self.cursor, province_id=self.province_id)
        regions = [Region.model_validate(r) for r in result]

        self.assertTrue(len(regions) > 0)
        self.assertIn(region, regions)

    def test_get_full_region(self):
        # Reuse the province created in the setUp method
        region_name = "Full Region"
        region = create_region(self.cursor, region_name, self.province_id)
        region = Region.model_validate(region)

        # Fetch full region details
        full_region = get_full_region(self.cursor, region.id)
        validated_full_region = FullRegion.model_validate(full_region)

        self.assertEqual(validated_full_region.name, region_name)
        self.assertEqual(validated_full_region.province_name, self.province_name)

    def test_get_full_region_invalid_id(self):
        invalid_region_id = uuid.uuid4()
        full_region = get_full_region(self.cursor, invalid_region_id)

        self.assertIsNone(full_region)


if __name__ == "__main__":
    unittest.main()
