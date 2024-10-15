import os
import unittest
import uuid

from dotenv import load_dotenv
from psycopg import Connection, connect

from fertiscan.db.models import Province
from fertiscan.db.queries.province import (
    create_province,
    delete_province,
    query_provinces,
    read_all_provinces,
    read_province,
    update_province,
)

load_dotenv()

TEST_DB_CONNECTION_STRING = os.environ["FERTISCAN_DB_URL"]
TEST_DB_SCHEMA = os.environ["FERTISCAN_SCHEMA_TESTING"]


class TestProvinceFunctions(unittest.TestCase):
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

    def tearDown(self):
        self.conn.rollback()
        self.cursor.close()

    def test_create_province(self):
        name = "Test Province A"
        created_province = create_province(self.cursor, name)
        validated_province = Province.model_validate(created_province)

        self.assertEqual(validated_province.name, name)

    def test_read_province(self):
        name = "Test Province B"
        created_province = create_province(self.cursor, name)
        validated_province = Province.model_validate(created_province)

        fetched_province = read_province(self.cursor, validated_province.id)
        fetched_province = Province.model_validate(fetched_province)

        self.assertEqual(fetched_province, validated_province)
        self.assertEqual(fetched_province.name, name)

    def test_read_all_provinces(self):
        initial_provinces = read_all_provinces(self.cursor)

        province_a = create_province(self.cursor, "Test Province C")
        province_b = create_province(self.cursor, "Test Province D")

        all_provinces = read_all_provinces(self.cursor)
        all_provinces = [Province.model_validate(p) for p in all_provinces]

        self.assertGreaterEqual(len(all_provinces), len(initial_provinces) + 2)
        self.assertIn(Province.model_validate(province_a), all_provinces)
        self.assertIn(Province.model_validate(province_b), all_provinces)

    def test_update_province(self):
        province = create_province(self.cursor, "Test Province E")
        validated_province = Province.model_validate(province)

        new_name = "Updated Province E"
        updated_province = update_province(self.cursor, validated_province.id, new_name)
        validated_updated = Province.model_validate(updated_province)

        self.assertEqual(validated_updated.name, new_name)

        fetched_province = read_province(self.cursor, validated_province.id)
        fetched_province = Province.model_validate(fetched_province)

        self.assertEqual(fetched_province, validated_updated)

    def test_delete_province(self):
        province = create_province(self.cursor, "Test Province F")
        validated_province = Province.model_validate(province)

        deleted_province = delete_province(self.cursor, validated_province.id)
        deleted_province = Province.model_validate(deleted_province)

        self.assertEqual(validated_province, deleted_province)

        fetched_province = read_province(self.cursor, validated_province.id)
        self.assertIsNone(fetched_province)

    def test_query_province_by_name(self):
        name = uuid.uuid4().hex
        create_province(self.cursor, name)

        result = query_provinces(self.cursor, name=name)
        provinces = [Province.model_validate(p) for p in result]

        self.assertTrue(len(provinces) > 0)
        self.assertEqual(provinces[0].name, name)

    def test_query_province_without_name(self):
        """Test querying provinces without any filter."""
        # Create two provinces for testing
        province_a = create_province(self.cursor, uuid.uuid4().hex)
        province_b = create_province(self.cursor, uuid.uuid4().hex)

        # Query without any filter
        result = query_provinces(self.cursor)
        provinces = [Province.model_validate(p) for p in result]

        # Ensure the newly created provinces are present in the results
        self.assertIn(Province.model_validate(province_a), provinces)
        self.assertIn(Province.model_validate(province_b), provinces)
        self.assertTrue(len(provinces) > 0)


if __name__ == "__main__":
    unittest.main()
