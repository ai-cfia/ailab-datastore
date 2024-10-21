import os
import unittest
import uuid

from dotenv import load_dotenv
from psycopg import Connection, connect

from fertiscan.db.models import Unit
from fertiscan.db.queries.unit import (
    create_unit,
    delete_unit,
    query_units,
    read_all_units,
    read_unit,
    update_unit,
)

load_dotenv()

TEST_DB_CONNECTION_STRING = os.environ["FERTISCAN_DB_URL"]
TEST_DB_SCHEMA = os.environ["FERTISCAN_SCHEMA_TESTING"]


class TestUnitFunctions(unittest.TestCase):
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

    def test_create_unit_success(self):
        unit_name = f"unit-{uuid.uuid4().hex[:5]}"
        to_si_unit = 1.0

        # Attempt to create the unit
        unit = create_unit(self.cursor, unit_name, to_si_unit)
        unit = Unit.model_validate(unit)

        # Check if the returned record matches the input
        self.assertIsNotNone(unit)
        self.assertEqual(unit.unit, unit_name)
        self.assertEqual(unit.to_si_unit, to_si_unit)

    def test_create_unit_without_conversion_factor(self):
        unit_name = f"unit-{uuid.uuid4().hex[:5]}"
        to_si_unit = None

        # Attempt to create the unit without conversion factor
        unit = create_unit(self.cursor, unit_name, to_si_unit)
        unit = Unit.model_validate(unit)

        # Check if the returned record matches the input
        self.assertIsNotNone(unit)
        self.assertEqual(unit.unit, unit_name)
        self.assertIsNone(unit.to_si_unit)

    def test_create_unit_missing_unit_name(self):
        unit_name = None
        to_si_unit = 1.0

        # Expect a ValueError when trying to create with missing unit name
        with self.assertRaises(ValueError):
            create_unit(self.cursor, unit_name, to_si_unit)

    def test_read_unit_success(self):
        # Create a test unit
        unit_name = f"unit-{uuid.uuid4().hex[:5]}"
        to_si_unit = 1.0
        created_unit = create_unit(self.cursor, unit_name, to_si_unit)
        created_unit = Unit.model_validate(created_unit)

        # Read the created unit by ID
        unit = read_unit(self.cursor, created_unit.id)
        unit = Unit.model_validate(unit)

        # Check if the returned record matches the created one
        self.assertIsNotNone(unit)
        self.assertEqual(unit, created_unit)

    def test_read_unit_not_found(self):
        # Attempt to read a unit with a non-existent ID
        result = read_unit(self.cursor, str(uuid.uuid4()))

        # Check that the result is None
        self.assertIsNone(result)

    def test_read_unit_invalid_id(self):
        # Attempt to read a unit with an invalid ID (None)
        with self.assertRaises(ValueError):
            read_unit(self.cursor, None)

    def test_read_all_units(self):
        # Create a new test unit
        unit_name = f"unit-{uuid.uuid4().hex[:5]}"
        to_si_unit = 1.0
        created_unit = create_unit(self.cursor, unit_name, to_si_unit)
        created_unit = Unit.model_validate(created_unit)

        # Read all units
        units = read_all_units(self.cursor)
        validated_units = [Unit.model_validate(u) for u in units]

        # Check if the created unit is in the list
        self.assertIn(created_unit, validated_units)

    def test_update_unit_success(self):
        # Create a test unit
        unit_name = f"unit-{uuid.uuid4().hex[:5]}"
        to_si_unit = 1.0
        created_unit = create_unit(self.cursor, unit_name, to_si_unit)
        created_unit = Unit.model_validate(created_unit)

        # Update the created unit
        new_unit_name = f"updated-unit-{uuid.uuid4().hex[:5]}"
        new_to_si_unit = 2.0
        updated_unit = update_unit(
            self.cursor, created_unit.id, new_unit_name, new_to_si_unit
        )
        updated_unit = Unit.model_validate(updated_unit)

        # Check if the updated unit matches the new values
        self.assertEqual(updated_unit.id, created_unit.id)
        self.assertEqual(updated_unit.unit, new_unit_name)
        self.assertEqual(updated_unit.to_si_unit, new_to_si_unit)

    def test_update_unit_not_found(self):
        # Attempt to update a unit with a non-existent ID
        updated_unit = update_unit(self.cursor, str(uuid.uuid4()), "new-unit", 2.0)

        # Check that the result is None
        self.assertIsNone(updated_unit)

    def test_update_unit_invalid_id(self):
        # Attempt to update a unit with an invalid ID (None)
        with self.assertRaises(ValueError):
            update_unit(self.cursor, None, "new-unit", 2.0)

    def test_update_unit_missing_unit_name(self):
        # Create a test unit
        unit_name = f"unit-{uuid.uuid4().hex[:5]}"
        to_si_unit = 1.0
        created_unit = create_unit(self.cursor, unit_name, to_si_unit)
        created_unit = Unit.model_validate(created_unit)

        # Attempt to update with a missing unit name
        with self.assertRaises(ValueError):
            update_unit(self.cursor, created_unit.id, None, 2.0)

    def test_delete_unit_success(self):
        # Create a test unit
        unit_name = f"unit-{uuid.uuid4().hex[:5]}"
        to_si_unit = 1.0
        created_unit = create_unit(self.cursor, unit_name, to_si_unit)
        created_unit = Unit.model_validate(created_unit)

        # Delete the created unit
        deleted_unit = delete_unit(self.cursor, created_unit.id)
        deleted_unit = Unit.model_validate(deleted_unit)

        # Check if the deleted unit matches the created one
        self.assertEqual(deleted_unit, created_unit)

        # Ensure the unit no longer exists
        self.assertIsNone(read_unit(self.cursor, created_unit.id))

    def test_delete_unit_not_found(self):
        # Attempt to delete a unit with a non-existent ID
        result = delete_unit(self.cursor, str(uuid.uuid4()))

        # Check that the result is None
        self.assertIsNone(result)

    def test_delete_unit_invalid_id(self):
        # Attempt to delete a unit with an invalid ID (None)
        with self.assertRaises(ValueError):
            delete_unit(self.cursor, None)

    def test_query_units_by_unit_name(self):
        # Create a test unit
        unit_name = f"unit-{uuid.uuid4().hex[:5]}"
        to_si_unit = 1.0
        created_unit = create_unit(self.cursor, unit_name, to_si_unit)
        created_unit = Unit.model_validate(created_unit)

        # Query by unit name
        results = query_units(self.cursor, unit=unit_name)
        validated_results = [Unit.model_validate(u) for u in results]

        # Check if the created unit is in the results
        self.assertIn(created_unit, validated_results)

    def test_query_units_by_to_si_unit(self):
        # Create a test unit
        unit_name = f"unit-{uuid.uuid4().hex[:5]}"
        to_si_unit = 1.0
        created_unit = create_unit(self.cursor, unit_name, to_si_unit)
        created_unit = Unit.model_validate(created_unit)

        # Query by to_si_unit
        results = query_units(self.cursor, to_si_unit=to_si_unit)
        validated_results = [Unit.model_validate(u) for u in results]

        # Check if the created unit is in the results
        self.assertIn(created_unit, validated_results)

    def test_query_units_by_multiple_fields(self):
        # Create a test unit
        unit_name = f"unit-{uuid.uuid4().hex[:5]}"
        to_si_unit = 1.0
        created_unit = create_unit(self.cursor, unit_name, to_si_unit)
        created_unit = Unit.model_validate(created_unit)

        # Query by both unit name and to_si_unit
        results = query_units(self.cursor, unit=unit_name, to_si_unit=to_si_unit)
        validated_results = [Unit.model_validate(u) for u in results]

        # Check if the created unit is in the results
        self.assertIn(created_unit, validated_results)

    def test_query_units_no_filters(self):
        # Create a test unit
        unit_name = f"unit-{uuid.uuid4().hex[:5]}"
        to_si_unit = 1.0
        created_unit = create_unit(self.cursor, unit_name, to_si_unit)
        created_unit = Unit.model_validate(created_unit)

        # Query with no filters
        results = query_units(self.cursor)
        validated_results = [Unit.model_validate(u) for u in results]

        # Check if the created unit is in the results
        self.assertIn(created_unit, validated_results)


if __name__ == "__main__":
    unittest.main()
