"""
This is a test script for the database packages. 
It tests the functions in the user, seed and picture modules.
"""

import unittest

from datastore.db.queries import sub_label, label
from datastore.db.metadata import validator
import datastore.db.__init__ as db
import os

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")
DB_SCHEMA = "fertiscan_0.0.11"

#DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class test_sub_type(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        self.type_fr = "text_fr"
        self.type_en = "text_en"

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_sub_type(self):
        sub_type_id = sub_label.new_sub_type(self.cursor, self.type_fr, self.type_en)
        self.assertTrue(validator.is_valid_uuid(sub_type_id))

    def test_new_sub_type_duplicate(self):
        sub_label.new_sub_type(self.cursor, self.type_fr, self.type_en)
        with self.assertRaises(sub_label.SubTypeCreationError):
            sub_label.new_sub_type(self.cursor, self.type_fr, self.type_en)

    def test_get_sub_type_id(self):
        sub_type_id = sub_label.new_sub_type(self.cursor, self.type_fr, self.type_en)
        data_en = sub_label.get_sub_type_id(self.cursor, self.type_en)
        data_fr = sub_label.get_sub_type_id(self.cursor, self.type_fr)
        self.assertEqual(str(data_en), str(sub_type_id))
        self.assertEqual(str(data_fr), str(sub_type_id))

    def test_get_sub_type_id_not_found(self):
        with self.assertRaises(sub_label.SubTypeNotFoundError):
            sub_label.get_sub_type_id(self.cursor, "not-a-type")


class test_sub_label(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        self.lot_number = "lot_number"
        self.npk = "npk"
        self.registration_number = "registration_number"
        self.n = 10.0
        self.p = 20.0
        self.k = 30.0
        self.weight = None
        self.density = None
        self.volume = None
        self.label_id = label.new_label_information(
            self.cursor,
            self.lot_number,
            self.npk,
            self.registration_number,
            self.n,
            self.p,
            self.k,
            None,
            None
        )
        self.language = "fr"

        self.type_fr = "test-type-fr"
        self.type_en = "test-type-en"
        self.sub_type_id = sub_label.new_sub_type(
            self.cursor, self.type_fr, self.type_en
        )

        self.text_fr = "text_fr"
        self.text_en = "text_en"

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_sub_label(self):
        sub_label_id = sub_label.new_sub_label(
            self.cursor, self.text_fr, self.text_en, self.label_id, self.sub_type_id, False
        )
        self.assertTrue(validator.is_valid_uuid(sub_label_id))

    def test_get_sub_label(self):
        sub_label_id = sub_label.new_sub_label(
            self.cursor, self.text_fr, self.text_en, self.label_id, self.sub_type_id, False
        )
        sub_label_data = sub_label.get_sub_label(self.cursor, sub_label_id)
        self.assertEqual(sub_label_data[0], self.text_fr)
        self.assertEqual(sub_label_data[1], self.text_en)

    def test_get_full_sub_label(self):
        sub_label_id = sub_label.new_sub_label(
            self.cursor, self.text_fr, self.text_en, self.label_id, self.sub_type_id, False
        )
        sub_label_data = sub_label.get_full_sub_label(self.cursor, sub_label_id)
        self.assertEqual(sub_label_data[0], sub_label_id)
        self.assertEqual(sub_label_data[1], self.text_fr)
        self.assertEqual(sub_label_data[2], self.text_en)
        self.assertEqual(sub_label_data[4], self.type_fr)
        self.assertEqual(sub_label_data[5], self.type_en)

    def test_get_all_sub_label(self):
        other_fr = "other_fr"
        other_en = "other_en"

        sub_label_id = sub_label.new_sub_label(
            self.cursor, self.text_fr, self.text_en, self.label_id, self.sub_type_id, False
        )
        sub_id = sub_label.new_sub_label(
            self.cursor, other_fr, other_en, self.label_id, self.sub_type_id, False
        )
        sub_label_data = sub_label.get_all_sub_label(self.cursor, self.label_id)
        self.assertEqual(len(sub_label_data), 2)

        self.assertTrue(validator.is_valid_uuid(sub_label_data[0][0]))
        self.assertEqual(sub_label_data[0][0], sub_label_id)
        self.assertTrue(validator.is_valid_uuid(sub_label_data[1][0]))
        self.assertEqual(sub_label_data[1][0], sub_id)

        self.assertEqual(sub_label_data[0][1], self.text_fr)
        self.assertEqual(sub_label_data[1][1], other_fr)
