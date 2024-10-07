"""
This is a test script for the database packages.
It tests the functions in the user, seed and picture modules.
"""

import os
import unittest

import datastore.db.__init__ as db
from datastore.db.metadata import validator
from fertiscan.db.queries import label, nutrients

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class test_element(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        self.element_name_fr = "test-nutriment"
        self.element_name_en = "test-nutrient"
        self.element_symbol = "Xy"
        self.element_number = 700

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_element(self):
        element_id = nutrients.new_element(
            self.cursor,
            self.element_number,
            self.element_name_fr,
            self.element_name_en,
            self.element_symbol,
        )
        self.assertIsInstance(element_id, int)

    def test_get_element_id(self):
        element_id = nutrients.new_element(
            self.cursor,
            self.element_number,
            self.element_name_fr,
            self.element_name_en,
            self.element_symbol,
        )
        self.assertEqual(
            nutrients.get_element_id_full_search(self.cursor, self.element_symbol),
            element_id,
        )
        self.assertEqual(
            nutrients.get_element_id_full_search(self.cursor, self.element_name_fr),
            element_id,
        )
        self.assertEqual(
            nutrients.get_element_id_full_search(self.cursor, self.element_name_en),
            element_id,
        )
        self.assertEqual(
            nutrients.get_element_id_name(self.cursor, self.element_name_fr), element_id
        )
        self.assertEqual(
            nutrients.get_element_id_name(self.cursor, self.element_name_en), element_id
        )
        self.assertEqual(
            nutrients.get_element_id_symbol(self.cursor, self.element_symbol),
            element_id,
        )

    def test_get_element_error(self):
        self.assertRaises(
            nutrients.ElementNotFoundError,
            nutrients.get_element_id_full_search,
            self.cursor,
            "not-an-element",
        )
        self.assertRaises(
            nutrients.ElementNotFoundError,
            nutrients.get_element_id_name,
            self.cursor,
            "not-an-element",
        )
        self.assertRaises(
            nutrients.ElementNotFoundError,
            nutrients.get_element_id_symbol,
            self.cursor,
            "not-an-element",
        )


class test_micronutrient(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        self.element_name_fr = "test-nutriment"
        self.element_name_en = "test-nutrient"
        self.element_symbol = "Xy"
        self.element_number = 700
        self.element_id = nutrients.new_element(
            self.cursor,
            self.element_number,
            self.element_name_fr,
            self.element_name_en,
            self.element_symbol,
        )

        self.micronutrient_name = "test-micronutrient"
        self.micronutrient_value = 10
        self.micronutrient_unit = "%"

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
        self.label_information_id = label.new_label_information(
            self.cursor,
            self.product_name,
            self.lot_number,
            self.npk,
            self.registration_number,
            self.n,
            self.p,
            self.k,
            self.warranty,
            None,
            None,
        )
        self.language = "fr"

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_micronutrient(self):
        micronutrient_id = nutrients.new_micronutrient(
            self.cursor,
            self.micronutrient_name,
            self.micronutrient_value,
            self.micronutrient_unit,
            self.label_information_id,
            self.language,
            self.element_id,
            False,
        )
        self.assertTrue(validator.is_valid_uuid(micronutrient_id))

    def test_new_micronutrient_empty(self):
        with self.assertRaises(nutrients.MicronutrientCreationError):
            nutrients.new_micronutrient(
                self.cursor,
                None,
                None,
                None,
                self.label_information_id,
                self.language,
                self.element_id,
                False,
            )

    def test_get_micronutrient_json(self):
        name_fr = "test-nutriment"
        name_en = "test-nutrient"
        nutrients.new_micronutrient(
            self.cursor,
            name_fr,
            self.micronutrient_value,
            self.micronutrient_unit,
            self.label_information_id,
            "fr",
            self.element_id,
            False,
        )
        nutrients.new_micronutrient(
            self.cursor,
            name_en,
            self.micronutrient_value,
            self.micronutrient_unit,
            self.label_information_id,
            "en",
            self.element_id,
            False,
        )
        data = nutrients.get_micronutrient_json(
            self.cursor, label_id=self.label_information_id
        )
        self.assertEqual(data["micronutrients"]["en"][0]["name"], name_en)
        self.assertEqual(data["micronutrients"]["fr"][0]["name"], name_fr)

    def test_get_micronutrient_json_empty(self):
        data = nutrients.get_micronutrient_json(
            self.cursor, label_id=self.label_information_id
        )
        self.assertIsNotNone(data["micronutrients"]["en"])
        self.assertIsNotNone(data["micronutrients"]["fr"])
        self.assertEqual(data["micronutrients"]["en"], [])
        self.assertEqual(data["micronutrients"]["fr"], [])

    def test_get_micronutrient(self):
        micronutrient_id = nutrients.new_micronutrient(
            self.cursor,
            self.micronutrient_name,
            self.micronutrient_value,
            self.micronutrient_unit,
            self.label_information_id,
            self.language,
            self.element_id,
            False,
        )
        micronutrient_data = nutrients.get_micronutrient(self.cursor, micronutrient_id)
        self.assertEqual(micronutrient_data[0], self.micronutrient_name)
        self.assertEqual(micronutrient_data[1], self.micronutrient_value)
        self.assertEqual(micronutrient_data[2], self.micronutrient_unit)
        self.assertEqual(micronutrient_data[3], self.element_id)
        self.assertFalse(micronutrient_data[4])
        self.assertEqual(micronutrient_data[5], self.language)
        self.assertEqual(
            micronutrient_data[6],
            (
                self.micronutrient_name
                + " "
                + str(self.micronutrient_value)
                + " "
                + self.micronutrient_unit
            ),
        )

    def test_get_full_micronutrient(self):
        micronutrient_id = nutrients.new_micronutrient(
            self.cursor,
            self.micronutrient_name,
            self.micronutrient_value,
            self.micronutrient_unit,
            self.label_information_id,
            self.language,
            self.element_id,
            False,
        )
        micronutrient_data = nutrients.get_full_micronutrient(
            self.cursor, micronutrient_id
        )
        self.assertEqual(micronutrient_data[0], self.micronutrient_name)
        self.assertEqual(micronutrient_data[1], self.micronutrient_value)
        self.assertEqual(micronutrient_data[2], self.micronutrient_unit)
        self.assertEqual(micronutrient_data[3], self.element_name_fr)
        self.assertEqual(micronutrient_data[4], self.element_name_en)
        self.assertEqual(micronutrient_data[5], self.element_symbol)
        self.assertFalse(micronutrient_data[6])
        self.assertEqual(micronutrient_data[7], self.language)
        self.assertEqual(
            micronutrient_data[8],
            (
                self.micronutrient_name
                + " "
                + str(self.micronutrient_value)
                + " "
                + self.micronutrient_unit
            ),
        )

    def test_get_all_micronutrients(self):
        other_name = "other-nutrient"
        micronutrient_id = nutrients.new_micronutrient(
            self.cursor,
            self.micronutrient_name,
            self.micronutrient_value,
            self.micronutrient_unit,
            self.label_information_id,
            self.language,
            self.element_id,
            False,
        )
        micro_id = nutrients.new_micronutrient(
            self.cursor,
            other_name,
            self.micronutrient_value,
            self.micronutrient_unit,
            self.label_information_id,
            self.language,
            self.element_id,
            False,
        )
        micronutrient_data = nutrients.get_all_micronutrients(
            self.cursor, self.label_information_id
        )
        self.assertEqual(len(micronutrient_data), 2)

        data_by_id = {item[0]: item for item in micronutrient_data}
        self.assertIn(micronutrient_id, data_by_id)
        self.assertIn(micro_id, data_by_id)
        self.assertEqual(data_by_id[micronutrient_id][1], self.micronutrient_name)
        self.assertEqual(data_by_id[micro_id][1], other_name)


class test_guaranteed_analysis(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        self.element_name_fr = "test-nutriment"
        self.element_name_en = "test-nutrient"
        self.element_symbol = "Xy"
        self.element_number = 700
        self.element_id = nutrients.new_element(
            self.cursor,
            self.element_number,
            self.element_name_fr,
            self.element_name_en,
            self.element_symbol,
        )

        self.guaranteed_analysis_name = "test-micronutrient"
        self.guaranteed_analysis_value = 10
        self.guaranteed_analysis_unit = "%"

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
        self.label_information_id = label.new_label_information(
            self.cursor,
            self.product_name,
            self.lot_number,
            self.npk,
            self.registration_number,
            self.n,
            self.p,
            self.k,
            self.warranty,
            None,
            None,
        )
        self.language = "fr"

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_guaranteed_analysis(self):
        guaranteed_analysis_id = nutrients.new_guaranteed_analysis(
            self.cursor,
            self.guaranteed_analysis_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.label_information_id,
            self.element_id,
            False,
        )
        self.assertTrue(validator.is_valid_uuid(guaranteed_analysis_id))

    def test_new_guaranteed_analysis_empty(self):
        with self.assertRaises(nutrients.GuaranteedCreationError):
            nutrients.new_guaranteed_analysis(
                self.cursor,
                None,
                None,
                None,
                self.label_information_id,
                self.element_id,
                False,
            )

    def test_get_guaranteed_analysis_json(self):
        nutrients.new_guaranteed_analysis(
            self.cursor,
            self.guaranteed_analysis_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.label_information_id,
            self.element_id,
            False,
        )
        data = nutrients.get_guaranteed_analysis_json(
            self.cursor, label_id=self.label_information_id
        )
        self.assertEqual(
            data["guaranteed_analysis"][0]["name"], self.guaranteed_analysis_name
        )

    def test_get_guaranteed_analysis_json_empty(self):
        data = nutrients.get_guaranteed_analysis_json(
            self.cursor, label_id=self.label_information_id
        )
        self.assertIsNone(data["guaranteed_analysis"])

    def test_get_guaranteed_analysis(self):
        guaranteed_analysis_id = nutrients.new_guaranteed_analysis(
            self.cursor,
            self.guaranteed_analysis_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.label_information_id,
            self.element_id,
            False,
        )
        guaranteed_analysis_data = nutrients.get_guaranteed(
            self.cursor, guaranteed_analysis_id
        )
        self.assertEqual(guaranteed_analysis_data[0], self.guaranteed_analysis_name)
        self.assertEqual(guaranteed_analysis_data[1], self.guaranteed_analysis_value)
        self.assertEqual(guaranteed_analysis_data[2], self.guaranteed_analysis_unit)
        self.assertEqual(guaranteed_analysis_data[3], self.element_id)
        self.assertEqual(guaranteed_analysis_data[4], self.label_information_id)
        self.assertFalse(guaranteed_analysis_data[5])
        self.assertEqual(
            guaranteed_analysis_data[6],
            (
                self.guaranteed_analysis_name
                + " "
                + str(self.guaranteed_analysis_value)
                + " "
                + self.guaranteed_analysis_unit
            ),
        )

    def test_get_full_guaranteed_analysis(self):
        guaranteed_analysis_id = nutrients.new_guaranteed_analysis(
            self.cursor,
            self.guaranteed_analysis_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.label_information_id,
            self.element_id,
            False,
        )
        guaranteed_analysis_data = nutrients.get_full_guaranteed(
            self.cursor, guaranteed_analysis_id
        )
        self.assertEqual(guaranteed_analysis_data[0], self.guaranteed_analysis_name)
        self.assertEqual(guaranteed_analysis_data[1], self.guaranteed_analysis_value)
        self.assertEqual(guaranteed_analysis_data[2], self.guaranteed_analysis_unit)
        self.assertEqual(guaranteed_analysis_data[3], self.element_name_fr)
        self.assertEqual(guaranteed_analysis_data[4], self.element_name_en)
        self.assertEqual(guaranteed_analysis_data[5], self.element_symbol)
        self.assertFalse(guaranteed_analysis_data[6])
        self.assertEqual(
            guaranteed_analysis_data[7],
            (
                self.guaranteed_analysis_name
                + " "
                + str(self.guaranteed_analysis_value)
                + " "
                + self.guaranteed_analysis_unit
            ),
        )

    def test_get_all_guaranteed_analysis(self):
        other_name = "other-nutrient"
        guaranteed_analysis_id = nutrients.new_guaranteed_analysis(
            self.cursor,
            self.guaranteed_analysis_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.label_information_id,
            self.element_id,
            False,
        )
        guaranteed_id = nutrients.new_guaranteed_analysis(
            self.cursor,
            other_name,
            self.guaranteed_analysis_value,
            self.guaranteed_analysis_unit,
            self.label_information_id,
            self.element_id,
            False,
        )
        guaranteed_analysis_data = nutrients.get_all_guaranteeds(
            self.cursor, self.label_information_id
        )
        self.assertEqual(len(guaranteed_analysis_data), 2)

        data_by_id = {item[0]: item for item in guaranteed_analysis_data}
        self.assertIn(guaranteed_analysis_id, data_by_id)
        self.assertIn(guaranteed_id, data_by_id)
        self.assertEqual(
            data_by_id[guaranteed_analysis_id][1], self.guaranteed_analysis_name
        )
        self.assertEqual(data_by_id[guaranteed_id][1], other_name)
