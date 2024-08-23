"""
This is a test script for the database packages. 
It tests the functions in the user, seed and picture modules.
"""

import unittest
import uuid
from datastore.db.queries import specification, label
from datastore.db.metadata import validator
import datastore.db.__init__ as db
import os

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class test_specification(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

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
        self.label_id = label.new_label_information(
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

        self.humidity = 10.0
        self.ph = 20.0
        self.solubility = 30.0

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_specification(self):
        specification_id = specification.new_specification(
            self.cursor,
            self.humidity,
            self.ph,
            self.solubility,
            self.label_id,
            self.language,
            False,
        )
        self.assertTrue(validator.is_valid_uuid(specification_id))

    def test_get_specification(self):
        specification_id = specification.new_specification(
            self.cursor,
            self.humidity,
            self.ph,
            self.solubility,
            self.label_id,
            self.language,
            False,
        )
        specification_data = specification.get_specification(
            self.cursor, specification_id
        )
        self.assertEqual(specification_data[0], self.humidity)
        self.assertEqual(specification_data[1], self.ph)
        self.assertEqual(specification_data[2], self.solubility)

    def test_get_specification_json(self):
        specification.new_specification(
            self.cursor,
            self.humidity,
            self.ph,
            self.solubility,
            self.label_id,
            self.language,
            False,
        )
        specification_data = specification.get_specification_json(
            self.cursor, self.label_id
        )
        specification_data = specification_data["specifications"]
        self.assertEqual(
            specification_data[self.language][0]["humidity"], self.humidity
        )
        self.assertEqual(specification_data[self.language][0]["ph"], self.ph)
        self.assertEqual(
            specification_data[self.language][0]["solubility"], self.solubility
        )

    def test_get_specification_json_not_found(self):
        empty = {"specifications": {"en": [], "fr": []}}
        data = specification.get_specification_json(self.cursor, str(uuid.uuid4()))
        self.assertDictEqual(data, empty)

    def test_get_specification_not_found(self):
        with self.assertRaises(specification.SpecificationNotFoundError):
            specification.get_specification(self.cursor, str(uuid.uuid4()))

    def test_has_specification(self):
        specification.new_specification(
            self.cursor,
            self.humidity,
            self.ph,
            self.solubility,
            self.label_id,
            self.language,
            False,
        )
        self.assertTrue(specification.has_specification(self.cursor, self.label_id))

    def test_has_specification_not_found(self):
        self.assertFalse(
            specification.has_specification(self.cursor, str(uuid.uuid4()))
        )

    def test_get_all_specification(self):
        other_humidity = 40
        specification_id = specification.new_specification(
            self.cursor,
            self.humidity,
            self.ph,
            self.solubility,
            self.label_id,
            self.language,
            False,
        )
        specif_id = specification.new_specification(
            self.cursor,
            other_humidity,
            self.ph,
            self.solubility,
            self.label_id,
            self.language,
            False,
        )
        specification_data = specification.get_all_specifications(
            self.cursor, self.label_id
        )
        self.assertEqual(len(specification_data), 2)

        self.assertTrue(validator.is_valid_uuid(specification_data[0][0]))
        self.assertEqual(specification_data[0][0], specification_id)
        self.assertTrue(validator.is_valid_uuid(specification_data[1][0]))
        self.assertEqual(specification_data[1][0], specif_id)

        self.assertEqual(specification_data[0][1], self.humidity)
        self.assertEqual(specification_data[1][1], other_humidity)

    def test_get_all_specification_not_found(self):
        with self.assertRaises(specification.SpecificationNotFoundError):
            specification.get_all_specifications(self.cursor, str(uuid.uuid4()))
