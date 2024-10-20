"""
This is a test script for the database packages.
It tests the functions in the user, seed and picture modules.
"""

import os
import unittest
import uuid

import datastore.db as db
from fertiscan.db.models import ElementCompound, FullGuaranteed, Guaranteed
from fertiscan.db.queries.element_compound import create_element_compound
from fertiscan.db.queries.guaranteed import (
    create_guaranteed,
    query_guaranteed,
    read_all_guaranteed,
    read_full_guaranteed,
    read_guaranteed,
)
from fertiscan.db.queries.label import new_label_information

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestGuaranteedAnalysis(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        self.element_name_fr = "test-nutriment"
        self.element_name_en = "test-nutrient"
        self.element_symbol = "Xy"
        self.element_number = 700
        self.element = create_element_compound(
            self.cursor,
            self.element_number,
            self.element_name_fr,
            self.element_name_en,
            self.element_symbol,
        )
        self.element = ElementCompound.model_validate(self.element)

        self.guaranteed_analysis_name = "test-micronutrient"
        self.guaranteed_analysis_value = 10
        self.guaranteed_analysis_unit = "%"

        self.title_en = "title_en"
        self.title_fr = "title_fr"
        self.is_minimal = False

        self.lot_number = "lot_number"
        self.product_name = "product_name"
        self.npk = "npk"
        self.registration_number = "registration_number"
        self.n = 10.0
        self.p = 20.0
        self.k = 30.0
        self.weight = None
        self.density = None
        self.volume = None
        self.warranty = "warranty"

        self.label_information_id = new_label_information(
            self.cursor,
            self.product_name,
            self.lot_number,
            self.npk,
            self.registration_number,
            self.n,
            self.p,
            self.k,
            self.title_en,
            self.title_fr,
            self.is_minimal,
            None,
            None,
        )
        self.language = "fr"

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_create_guaranteed_analysis(self):
        guaranteed = create_guaranteed(
            self.cursor,
            self.guaranteed_analysis_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.language,
            self.element.id,
            self.label_information_id,
            False,
        )
        guaranteed = Guaranteed.model_validate(guaranteed)
        self.assertIsNotNone(guaranteed)
        self.assertEqual(guaranteed.read_name, self.guaranteed_analysis_name)
        self.assertEqual(guaranteed.value, self.guaranteed_analysis_value)
        self.assertEqual(guaranteed.unit, self.guaranteed_analysis_unit)
        self.assertEqual(guaranteed.language, self.language)
        self.assertEqual(guaranteed.element_id, self.element.id)
        self.assertEqual(guaranteed.label_id, self.label_information_id)

    def test_create_guaranteed_analysis_empty(self):
        with self.assertRaises(ValueError):
            create_guaranteed(
                self.cursor,
                None,
                None,
                None,
                self.language,
                self.element.id,
                self.label_information_id,
                False,
            )

    def test_read_guaranteed_analysis(self):
        created = create_guaranteed(
            self.cursor,
            self.guaranteed_analysis_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.language,
            self.element.id,
            self.label_information_id,
            False,
        )
        created = Guaranteed.model_validate(created)

        fetched = read_guaranteed(self.cursor, created.id)
        fetched = Guaranteed.model_validate(fetched)

        self.assertEqual(fetched.read_name, self.guaranteed_analysis_name)
        self.assertEqual(fetched.value, self.guaranteed_analysis_value)
        self.assertEqual(fetched.unit, self.guaranteed_analysis_unit)
        self.assertEqual(fetched.language, self.language)
        self.assertEqual(fetched.element_id, self.element.id)
        self.assertEqual(fetched.label_id, self.label_information_id)

    def test_read_full_guaranteed_analysis(self):
        created = create_guaranteed(
            self.cursor,
            self.guaranteed_analysis_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.language,
            self.element.id,
            self.label_information_id,
            False,
        )
        created = Guaranteed.model_validate(created)

        full_guaranteed = read_full_guaranteed(self.cursor, created.id)
        full_guaranteed = FullGuaranteed.model_validate(full_guaranteed)

        self.assertEqual(full_guaranteed.read_name, self.guaranteed_analysis_name)
        self.assertEqual(full_guaranteed.value, self.guaranteed_analysis_value)
        self.assertEqual(full_guaranteed.unit, self.guaranteed_analysis_unit)
        self.assertEqual(full_guaranteed.element_name_fr, self.element_name_fr)
        self.assertEqual(full_guaranteed.element_name_en, self.element_name_en)
        self.assertEqual(full_guaranteed.element_symbol, self.element_symbol)
        self.assertFalse(full_guaranteed.edited)
        self.assertEqual(
            full_guaranteed.reading,
            f"{self.guaranteed_analysis_name} {self.guaranteed_analysis_value} {self.guaranteed_analysis_unit}",
        )

    def test_read_all_guaranteed_analysis(self):
        # Get the initial count of guaranteed analysis records
        initial_count = len(read_all_guaranteed(self.cursor))

        # Create additional guaranteed analysis records using setup data
        create_guaranteed(
            self.cursor,
            self.guaranteed_analysis_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.language,
            self.element.id,
            self.label_information_id,
            False,
        )
        create_guaranteed(
            self.cursor,
            self.guaranteed_analysis_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.language,
            self.element.id,
            self.label_information_id,
            False,
        )

        # Fetch all guaranteed analysis records
        all_guaranteed = read_all_guaranteed(self.cursor)
        all_guaranteed = [Guaranteed.model_validate(g) for g in all_guaranteed]

        # Assert that the total count has increased by at least 2
        self.assertGreaterEqual(len(all_guaranteed), initial_count + 2)

        # Assert that all records have the expected values
        for guaranteed in all_guaranteed:
            self.assertEqual(guaranteed.read_name, self.guaranteed_analysis_name)
            self.assertEqual(guaranteed.value, self.guaranteed_analysis_value)
            self.assertEqual(guaranteed.unit, self.guaranteed_analysis_unit)
            self.assertEqual(guaranteed.language, self.language)
            self.assertEqual(guaranteed.element_id, self.element.id)
            self.assertEqual(guaranteed.label_id, self.label_information_id)

    def test_query_guaranteed_analysis_no_filters(self):
        # Create guaranteed analysis records using setup data
        create_guaranteed(
            self.cursor,
            self.guaranteed_analysis_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.language,
            self.element.id,
            self.label_information_id,
            False,
        )

        # Query with no filters
        results = query_guaranteed(self.cursor)
        results = [Guaranteed.model_validate(g) for g in results]

        # Assert that at least one record is returned
        self.assertGreaterEqual(len(results), 1)

    def test_query_guaranteed_analysis_with_filters(self):
        # Create guaranteed analysis records using setup data
        create_guaranteed(
            self.cursor,
            self.guaranteed_analysis_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.language,
            self.element.id,
            self.label_information_id,
            False,
        )

        # Query using specific filters
        results = query_guaranteed(
            self.cursor,
            read_name=self.guaranteed_analysis_name,
            value=self.guaranteed_analysis_value,
            unit=self.guaranteed_analysis_unit,
            language=self.language,
            element_id=self.element.id,
            label_id=self.label_information_id,
            edited=False,
        )
        results = [Guaranteed.model_validate(g) for g in results]

        # Assert that the result matches the expected values
        self.assertEqual(len(results), 1)
        record = results[0]
        self.assertEqual(record.read_name, self.guaranteed_analysis_name)
        self.assertEqual(record.value, self.guaranteed_analysis_value)
        self.assertEqual(record.unit, self.guaranteed_analysis_unit)
        self.assertEqual(record.language, self.language)
        self.assertEqual(record.element_id, self.element.id)
        self.assertEqual(record.label_id, self.label_information_id)

    def test_query_guaranteed_analysis_no_results(self):
        # Query using non-existent filters
        results = query_guaranteed(
            self.cursor,
            read_name=uuid.uuid4().hex,
            value=9999.99,
        )
        results = [Guaranteed.model_validate(g) for g in results]

        # Assert that no results are returned
        self.assertEqual(len(results), 0)
