"""
This is a test script for the database packages. 
It tests the functions in the user, seed and picture modules.
"""

import unittest
from datastore.db.queries import metric,label
from datastore.db.metadata import validator
import datastore.db.__init__ as db
import os

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


# ------------ unit ------------
class test_unit(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        self.unit_unit = "milli-unite"
        self.unit_to_si_unit = 0.001

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_unit(self):
        unit_id = metric.new_unit(self.cursor, self.unit_unit, self.unit_to_si_unit)
        self.assertTrue(validator.is_valid_uuid(unit_id))

    def test_get_unit_id(self):
        unit_id = metric.new_unit(self.cursor, self.unit_unit, self.unit_to_si_unit)
        self.assertEqual(metric.get_unit_id(self.cursor, self.unit_unit), unit_id)

    def test_is_a_unit(self):
        metric.new_unit(self.cursor, self.unit_unit, self.unit_to_si_unit)
        self.assertFalse(metric.is_a_unit(self.cursor, "not-a-unit"))
        self.assertTrue(metric.is_a_unit(self.cursor, self.unit_unit))


class test_metric(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        self.unit_unit = "milli-unite"
        self.unit_to_si_unit = 0.001
        self.unit_id = metric.new_unit(
            self.cursor, self.unit_unit, self.unit_to_si_unit
        )
        self.metric_value = 1.0
        self.metric_unit = "milli-unite"
        self.metric_edited = False
        self.metric_type = "volume"

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

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_metric(self):
        metric_id = metric.new_metric(
            self.cursor, self.metric_value, self.unit_unit,self.label_id, self.metric_type, self.metric_edited
        )
        self.assertTrue(validator.is_valid_uuid(metric_id))

    def test_get_metric(self):
        metric_id = metric.new_metric(
            self.cursor, self.metric_value, self.unit_unit,self.label_id, self.metric_type, self.metric_edited
        )
        metric_data = metric.get_metric(self.cursor, metric_id)
        self.assertEqual(metric_data[0], self.metric_value)
        self.assertEqual(metric_data[1], self.unit_id)
        self.assertEqual(metric_data[2], self.metric_edited)
        self.assertEqual(metric_data[3], self.metric_type)

    def test_get_full_metric(self):
        metric_id = metric.new_metric(
            self.cursor, self.metric_value, self.unit_unit,self.label_id, self.metric_type, self.metric_edited
        )
        metric_data = metric.get_full_metric(self.cursor, metric_id)
        self.assertEqual(metric_data[0], metric_id)
        self.assertEqual(metric_data[1], self.metric_value)
        self.assertEqual(metric_data[2], self.metric_unit)
        self.assertEqual(metric_data[3], self.unit_to_si_unit)
        self.assertEqual(metric_data[4], self.metric_edited)
        self.assertEqual(metric_data[5], self.metric_type)
