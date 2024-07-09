"""
This is a test script for the database packages. 
It tests the functions in the user, seed and picture modules.
"""

import unittest
from datastore.db.queries import metric
from datastore.db.metadata import validator
import datastore.db.__init__ as db

# ------------ unit ------------
class test_unit(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(db.FERTISCAN_DB_URL,db.FERTISCAN_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, db.FERTISCAN_SCHEMA)
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
        self.assertFalse(metric.is_a_unit(self.cursor, 'not-a-unit'))
        self.assertTrue(metric.is_a_unit(self.cursor, self.unit_unit))

class test_metric(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(db.FERTISCAN_DB_URL,db.FERTISCAN_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, db.FERTISCAN_SCHEMA)
        self.unit_unit = "milli-unite"
        self.unit_to_si_unit = 0.001
        self.unit_id = metric.new_unit(self.cursor, self.unit_unit, self.unit_to_si_unit)
        self.metric_value = 1.0
        self.metric_unit = "milli-unite"
        self.metric_edited = False

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)
    
    def test_new_metric(self):
        metric_id = metric.new_metric(self.cursor, self.metric_value, self.unit_id, self.metric_edited)
        self.assertTrue(validator.is_valid_uuid(metric_id))
    
    def test_get_metric(self):
        metric_id = metric.new_metric(self.cursor, self.metric_value, self.unit_id, self.metric_edited)
        metric_data = metric.get_metric(self.cursor, metric_id)
        self.assertEqual(metric_data[0], self.metric_value)
        self.assertEqual(metric_data[1], self.unit_id)
        self.assertEqual(metric_data[2], self.metric_edited)

    def test_get_full_metric(self):
        metric_id = metric.new_metric(self.cursor, self.metric_value, self.unit_id, self.metric_edited)
        metric_data = metric.get_full_metric(self.cursor, metric_id)
        self.assertEqual(metric_data[0], metric_id)
        self.assertEqual(metric_data[1], self.metric_value)
        self.assertEqual(metric_data[2], self.metric_unit)
        self.assertEqual(metric_data[3], self.unit_to_si_unit)
        self.assertEqual(metric_data[4], self.metric_edited)
