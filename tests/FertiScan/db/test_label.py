import unittest
from datastore.db.queries import label
from datastore.db.metadata import validator
import datastore.db.__init__ as db
import os

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

# ------------ label ------------


class test_label(unittest.TestCase):
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

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_label_information(self):
        label_information_id = label.new_label_information(
            self.cursor,
            self.lot_number,
            self.npk,
            self.registration_number,
            self.n,
            self.p,
            self.k,
            self.weight,
            self.density,
            self.volume,
        )
        self.assertTrue(validator.is_valid_uuid(label_information_id))

    def test_get_label_information(self):
        label_information_id = label.new_label_information(
            self.cursor,
            self.lot_number,
            self.npk,
            self.registration_number,
            self.n,
            self.p,
            self.k,
            self.weight,
            self.density,
            self.volume,
        )
        label_data = label.get_label_information(self.cursor, label_information_id)

        self.assertEqual(label_data[0], self.lot_number)
        self.assertEqual(label_data[1], self.npk)
        self.assertEqual(label_data[2], self.registration_number)
        self.assertEqual(label_data[3], self.n)
        self.assertEqual(label_data[4], self.p)
        self.assertEqual(label_data[5], self.k)
        self.assertIsNone(label_data[6])
        self.assertIsNone(label_data[7])
        self.assertIsNone(label_data[8])
