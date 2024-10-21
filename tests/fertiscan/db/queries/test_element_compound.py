import os
import unittest
import uuid

from dotenv import load_dotenv
from psycopg import Connection, connect

from fertiscan.db.models import ElementCompound
from fertiscan.db.queries.element_compound import (
    create_element_compound,
    delete_element_compound,
    query_element_compounds,
    read_all_element_compounds,
    read_element_compound,
    update_element_compound,
)

load_dotenv()

TEST_DB_CONNECTION_STRING = os.environ["FERTISCAN_DB_URL"]
TEST_DB_SCHEMA = os.environ["FERTISCAN_SCHEMA_TESTING"]


class TestElementCompoundFunctions(unittest.TestCase):
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

    def test_create_element_compound_success(self):
        number = 1
        name_fr = f"Hydrogène-{uuid.uuid4().hex[:5]}"
        name_en = "Hydrogen"
        symbol = f"H-{uuid.uuid4().hex[:5]}"

        # Attempt to create the element_compound
        element = create_element_compound(self.cursor, number, name_fr, name_en, symbol)
        element = ElementCompound.model_validate(element)

        # Check if the returned record matches the input
        self.assertIsNotNone(element)
        self.assertEqual(element.number, number)
        self.assertEqual(element.name_fr, name_fr)
        self.assertEqual(element.name_en, name_en)
        self.assertEqual(element.symbol, symbol)

    def test_create_element_compound_missing_field(self):
        number = 1
        name_fr = "Hydrogène"
        name_en = "Hydrogen"
        symbol = None  # Missing field

        # Expect a ValueError when trying to create with missing field
        with self.assertRaises(ValueError):
            create_element_compound(self.cursor, number, name_fr, name_en, symbol)

    def test_create_element_compound_duplicate_symbol(self):
        number = 2
        name_fr = f"Hélium-{uuid.uuid4().hex[:5]}"
        name_en = "Helium"
        symbol = f"He-{uuid.uuid4().hex[:5]}"

        # Create the first element_compound
        create_element_compound(self.cursor, number, name_fr, name_en, symbol)

        # Attempt to create a second element_compound with the same symbol
        with self.assertRaises(Exception):  # Expecting a unique constraint violation
            create_element_compound(self.cursor, number, name_fr, name_en, symbol)

    def test_read_element_compound_success(self):
        # Create a test element_compound
        number = 1
        name_fr = f"Hydrogène-{uuid.uuid4().hex[:5]}"
        name_en = "Hydrogen"
        symbol = f"H-{uuid.uuid4().hex[:5]}"
        created_element = create_element_compound(
            self.cursor, number, name_fr, name_en, symbol
        )
        created_element = ElementCompound.model_validate(created_element)

        # Attempt to read the created element_compound
        element = read_element_compound(self.cursor, created_element.id)
        element = ElementCompound.model_validate(element)

        # Check if the returned record matches the created one
        self.assertIsNotNone(element)
        self.assertEqual(element, created_element)

    def test_read_element_compound_not_found(self):
        # Attempt to read an element_compound with a non-existent ID
        result = read_element_compound(self.cursor, -1)

        # Check that the result is None
        self.assertIsNone(result)

    def test_read_element_compound_invalid_id(self):
        # Attempt to read an element_compound with an invalid ID (None)
        with self.assertRaises(ValueError):
            read_element_compound(self.cursor, None)

    def test_read_all_element_compounds(self):
        # Create a new test element_compound
        number = 1
        name_fr = f"Hydrogène-{uuid.uuid4().hex[:5]}"
        name_en = "Hydrogen"
        symbol = f"H-{uuid.uuid4().hex[:5]}"
        created_element = create_element_compound(
            self.cursor, number, name_fr, name_en, symbol
        )
        created_element = ElementCompound.model_validate(created_element)

        # Read all element_compounds
        elements = read_all_element_compounds(self.cursor)
        validated_elements = [ElementCompound.model_validate(e) for e in elements]

        # Check if the created element is in the list
        self.assertIn(created_element, validated_elements)

    def test_update_element_compound_success(self):
        # Create a test element_compound
        number = 1
        name_fr = f"Hydrogène-{uuid.uuid4().hex[:5]}"
        name_en = "Hydrogen"
        symbol = f"H-{uuid.uuid4().hex[:5]}"
        created_element = create_element_compound(
            self.cursor, number, name_fr, name_en, symbol
        )
        created_element = ElementCompound.model_validate(created_element)

        # Update the created element_compound
        new_number = 2
        new_name_fr = f"Hélium-{uuid.uuid4().hex[:5]}"
        new_name_en = "Helium"
        new_symbol = f"He-{uuid.uuid4().hex[:5]}"
        updated_element = update_element_compound(
            self.cursor,
            created_element.id,
            new_number,
            new_name_fr,
            new_name_en,
            new_symbol,
        )
        updated_element = ElementCompound.model_validate(updated_element)

        # Check if the updated element matches the new values
        self.assertEqual(updated_element.id, created_element.id)
        self.assertEqual(updated_element.number, new_number)
        self.assertEqual(updated_element.name_fr, new_name_fr)
        self.assertEqual(updated_element.name_en, new_name_en)
        self.assertEqual(updated_element.symbol, new_symbol)

    def test_update_element_compound_not_found(self):
        # Attempt to update an element_compound with a non-existent ID
        element = update_element_compound(self.cursor, -1, 2, "Hélium", "Helium", "He")
        self.assertIsNone(element)

    def test_update_element_compound_invalid_id(self):
        # Attempt to update an element_compound with an invalid ID (None)
        with self.assertRaises(ValueError):
            update_element_compound(self.cursor, None, 2, "Hélium", "Helium", "He")

    def test_update_element_compound_missing_field(self):
        # Create a test element_compound
        number = 1
        name_fr = f"Hydrogène-{uuid.uuid4().hex[:5]}"
        name_en = "Hydrogen"
        symbol = f"H-{uuid.uuid4().hex[:5]}"
        created_element = create_element_compound(
            self.cursor, number, name_fr, name_en, symbol
        )

        # Attempt to update with a missing field (e.g., None for symbol)
        with self.assertRaises(ValueError):
            update_element_compound(
                self.cursor, created_element["id"], 2, "Hélium", "Helium", None
            )

    def test_delete_element_compound_success(self):
        # Create a test element_compound
        number = 1
        name_fr = f"Hydrogène-{uuid.uuid4().hex[:5]}"
        name_en = "Hydrogen"
        symbol = f"H-{uuid.uuid4().hex[:5]}"
        created_element = create_element_compound(
            self.cursor, number, name_fr, name_en, symbol
        )
        created_element = ElementCompound.model_validate(created_element)

        # Delete the created element_compound
        deleted_element = delete_element_compound(self.cursor, created_element.id)
        deleted_element = ElementCompound.model_validate(deleted_element)

        # Check if the deleted element matches the created one
        self.assertEqual(deleted_element.id, created_element.id)
        self.assertEqual(deleted_element.number, created_element.number)
        self.assertEqual(deleted_element.name_fr, created_element.name_fr)
        self.assertEqual(deleted_element.name_en, created_element.name_en)
        self.assertEqual(deleted_element.symbol, created_element.symbol)

        # Ensure the element_compound no longer exists
        self.assertIsNone(read_element_compound(self.cursor, created_element.id))

    def test_delete_element_compound_not_found(self):
        # Attempt to delete an element_compound with a non-existent ID
        result = delete_element_compound(self.cursor, -1)

        # Ensure the result is None, indicating no deletion occurred
        self.assertIsNone(result)

    def test_delete_element_compound_invalid_id(self):
        # Attempt to delete an element_compound with an invalid ID (None)
        with self.assertRaises(ValueError):
            delete_element_compound(self.cursor, None)

    def test_query_element_compounds_by_number(self):
        # Create a test element_compound
        number = 1
        name_fr = f"Hydrogène-{uuid.uuid4().hex[:5]}"
        name_en = "Hydrogen"
        symbol = f"H-{uuid.uuid4().hex[:5]}"
        created_element = create_element_compound(
            self.cursor, number, name_fr, name_en, symbol
        )
        created_element = ElementCompound.model_validate(created_element)

        # Query by number
        results = query_element_compounds(self.cursor, number=number)
        validated_results = [ElementCompound.model_validate(e) for e in results]

        # Check if the created element is in the results
        self.assertIn(created_element, validated_results)

    def test_query_element_compounds_by_name_fr(self):
        # Create a test element_compound
        number = 1
        name_fr = f"Hydrogène-{uuid.uuid4().hex[:5]}"
        name_en = "Hydrogen"
        symbol = f"H-{uuid.uuid4().hex[:5]}"
        created_element = create_element_compound(
            self.cursor, number, name_fr, name_en, symbol
        )
        created_element = ElementCompound.model_validate(created_element)

        # Query by French name
        results = query_element_compounds(self.cursor, name_fr=name_fr)
        validated_results = [ElementCompound.model_validate(e) for e in results]

        # Check if the created element is in the results
        self.assertIn(created_element, validated_results)

    def test_query_element_compounds_by_name_en(self):
        # Create a test element_compound
        number = 1
        name_fr = f"Hydrogène-{uuid.uuid4().hex[:5]}"
        name_en = f"Hydrogen-{uuid.uuid4().hex[:5]}"
        symbol = f"H-{uuid.uuid4().hex[:5]}"
        created_element = create_element_compound(
            self.cursor, number, name_fr, name_en, symbol
        )
        created_element = ElementCompound.model_validate(created_element)

        # Query by English name
        results = query_element_compounds(self.cursor, name_en=name_en)
        validated_results = [ElementCompound.model_validate(e) for e in results]

        # Check if the created element is in the results
        self.assertIn(created_element, validated_results)

    def test_query_element_compounds_by_symbol(self):
        # Create a test element_compound
        number = 1
        name_fr = f"Hydrogène-{uuid.uuid4().hex[:5]}"
        name_en = "Hydrogen"
        symbol = f"H-{uuid.uuid4().hex[:5]}"
        created_element = create_element_compound(
            self.cursor, number, name_fr, name_en, symbol
        )
        created_element = ElementCompound.model_validate(created_element)

        # Query by symbol
        results = query_element_compounds(self.cursor, symbol=symbol)
        validated_results = [ElementCompound.model_validate(e) for e in results]

        # Check if the created element is in the results
        self.assertIn(created_element, validated_results)

    def test_query_element_compounds_by_multiple_fields(self):
        # Create a test element_compound
        number = 1
        name_fr = f"Hydrogène-{uuid.uuid4().hex[:5]}"
        name_en = f"Hydrogen-{uuid.uuid4().hex[:5]}"
        symbol = f"H-{uuid.uuid4().hex[:5]}"
        created_element = create_element_compound(
            self.cursor, number, name_fr, name_en, symbol
        )
        created_element = ElementCompound.model_validate(created_element)

        # Query by multiple fields
        results = query_element_compounds(
            self.cursor, number=number, name_fr=name_fr, name_en=name_en, symbol=symbol
        )
        validated_results = [ElementCompound.model_validate(e) for e in results]

        # Check if the created element is in the results
        self.assertIn(created_element, validated_results)

    def test_query_element_compounds_no_filters(self):
        # Create a test element_compound
        number = 1
        name_fr = f"Hydrogène-{uuid.uuid4().hex[:5]}"
        name_en = "Hydrogen"
        symbol = f"H-{uuid.uuid4().hex[:5]}"
        created_element = create_element_compound(
            self.cursor, number, name_fr, name_en, symbol
        )
        created_element = ElementCompound.model_validate(created_element)

        # Query with no filters
        results = query_element_compounds(self.cursor)
        validated_results = [ElementCompound.model_validate(e) for e in results]

        # Check if the created element is in the results
        self.assertIn(created_element, validated_results)


if __name__ == "__main__":
    unittest.main()
