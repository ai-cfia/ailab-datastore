"""
This is a test script for the database packages. 
It tests the functions in the user, seed and picture modules.
"""

import unittest

from datastore.db.queries import nutrients,label
from datastore.db.metadata import validator
import datastore.db.__init__ as db
import os

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

class test_element(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING,DB_SCHEMA)
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
        element_id = nutrients.new_element(self.cursor, self.element_number,self.element_name_fr, self.element_name_en, self.element_symbol)
        self.assertIsInstance(element_id, int)

    def test_get_element_id(self):
        element_id = nutrients.new_element(self.cursor, self.element_number,self.element_name_fr, self.element_name_en, self.element_symbol)
        self.assertEqual(nutrients.get_element_id_full_search(self.cursor, self.element_symbol), element_id)
        self.assertEqual(nutrients.get_element_id_full_search(self.cursor, self.element_name_fr), element_id)
        self.assertEqual(nutrients.get_element_id_full_search(self.cursor, self.element_name_en), element_id)
        self.assertEqual(nutrients.get_element_id_name(self.cursor, self.element_name_fr), element_id)
        self.assertEqual(nutrients.get_element_id_name(self.cursor, self.element_name_en), element_id)
        self.assertEqual(nutrients.get_element_id_symbol(self.cursor, self.element_symbol), element_id)

    def test_get_element_error(self):
        self.assertRaises(nutrients.ElementNotFoundError, nutrients.get_element_id_full_search, self.cursor, "not-an-element")
        self.assertRaises(nutrients.ElementNotFoundError, nutrients.get_element_id_name, self.cursor, "not-an-element")
        self.assertRaises(nutrients.ElementNotFoundError, nutrients.get_element_id_symbol, self.cursor, "not-an-element")

class test_micronutrient(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING,DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        
        self.element_name_fr = "test-nutriment"
        self.element_name_en = "test-nutrient"
        self.element_symbol = "Xy"
        self.element_number = 700
        self.element_id = nutrients.new_element(self.cursor, self.element_number,self.element_name_fr, self.element_name_en, self.element_symbol)

        self.micronutrient_name = "test-micronutrient"
        self.micronutrient_value= 10
        self.micronutrient_unit = "%"

        self.lot_number = "lot_number"
        self.npk = "npk"
        self.registration_number = "registration_number"
        self.n = 10.0
        self.p = 20.0
        self.k = 30.0
        self.weight = None
        self.density = None
        self.volume = None
        self.label_information_id = label.new_label_information(self.cursor, self.lot_number, self.npk, self.registration_number, self.n, self.p, self.k, self.weight, self.density, self.volume)
        
    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_micronutrient(self):
        micronutrient_id = nutrients.new_micronutrient(self.cursor, self.micronutrient_name, self.micronutrient_value, self.micronutrient_unit, self.element_id, self.label_information_id)
        self.assertTrue(validator.is_valid_uuid(micronutrient_id))

    def test_get_micronutrient(self):
        micronutrient_id = nutrients.new_micronutrient(self.cursor, self.micronutrient_name, self.micronutrient_value, self.micronutrient_unit, self.element_id, self.label_information_id)
        micronutrient_data = nutrients.get_micronutrient(self.cursor, micronutrient_id)
        self.assertEqual(micronutrient_data[0], self.micronutrient_name)
        self.assertEqual(micronutrient_data[1], self.micronutrient_value)
        self.assertEqual(micronutrient_data[2], self.micronutrient_unit)
        self.assertEqual(micronutrient_data[3], self.element_id)
        self.assertFalse(micronutrient_data[4])
        self.assertEqual(micronutrient_data[5], (self.micronutrient_name+" "+str(self.micronutrient_value)+" "+self.micronutrient_unit))

    def test_get_full_micronutrient(self):
        micronutrient_id = nutrients.new_micronutrient(self.cursor, self.micronutrient_name, self.micronutrient_value, self.micronutrient_unit, self.element_id, self.label_information_id)
        micronutrient_data = nutrients.get_full_micronutrient(self.cursor, micronutrient_id)
        self.assertEqual(micronutrient_data[0], self.micronutrient_name)
        self.assertEqual(micronutrient_data[1], self.micronutrient_value)
        self.assertEqual(micronutrient_data[2], self.micronutrient_unit)
        self.assertEqual(micronutrient_data[3], self.element_name_fr)
        self.assertEqual(micronutrient_data[4], self.element_name_en)
        self.assertEqual(micronutrient_data[5], self.element_symbol)
        self.assertFalse(micronutrient_data[6])
        self.assertEqual(micronutrient_data[7], (self.micronutrient_name+" "+str(self.micronutrient_value)+" "+self.micronutrient_unit))

    def test_get_all_micronutrients(self):
        other_name = "other-nutrient"
        micronutrient_id = nutrients.new_micronutrient(self.cursor, self.micronutrient_name, self.micronutrient_value, self.micronutrient_unit, self.element_id, self.label_information_id)
        micro_id = nutrients.new_micronutrient(self.cursor, other_name, self.micronutrient_value, self.micronutrient_unit, self.element_id, self.label_information_id)
        micronutrient_data = nutrients.get_all_micronutrients(self.cursor,self.label_information_id)
        self.assertEqual(len(micronutrient_data), 2)
        self.assertEqual(micronutrient_data[0][0], micronutrient_id)
        self.assertEqual(micronutrient_data[1][0], micro_id)
        
        self.assertEqual(micronutrient_data[0][1], self.micronutrient_name)
        self.assertEqual(micronutrient_data[1][1], other_name)
    
class test_guaranteed_analysis(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING,DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        
        self.element_name_fr = "test-nutriment"
        self.element_name_en = "test-nutrient"
        self.element_symbol = "Xy"
        self.element_number = 700
        self.element_id = nutrients.new_element(self.cursor, self.element_number,self.element_name_fr, self.element_name_en, self.element_symbol)

        self.guaranteed_analysis_name = "test-micronutrient"
        self.guaranteed_analysis_value= 10
        self.guaranteed_analysis_unit = "%"

        self.lot_number = "lot_number"
        self.npk = "npk"
        self.registration_number = "registration_number"
        self.n = 10.0
        self.p = 20.0
        self.k = 30.0
        self.weight = None
        self.density = None
        self.volume = None
        self.label_information_id = label.new_label_information(self.cursor, self.lot_number, self.npk, self.registration_number, self.n, self.p, self.k, self.weight, self.density, self.volume)
        
    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)


    def test_new_guaranteed_analysis(self):
        guaranteed_analysis_id = nutrients.new_guaranteed(self.cursor, self.guaranteed_analysis_name, self.guaranteed_analysis_value, self.guaranteed_analysis_unit, self.element_id,self.label_information_id)
        self.assertTrue(validator.is_valid_uuid(guaranteed_analysis_id))

    def test_get_guaranteed_analysis(self):
        guaranteed_analysis_id = nutrients.new_guaranteed(self.cursor, self.guaranteed_analysis_name, self.guaranteed_analysis_value, self.guaranteed_analysis_unit, self.element_id, self.label_information_id)
        guaranteed_analysis_data = nutrients.get_guaranteed(self.cursor, guaranteed_analysis_id)
        self.assertEqual(guaranteed_analysis_data[0], self.guaranteed_analysis_name)
        self.assertEqual(guaranteed_analysis_data[1], self.guaranteed_analysis_value)
        self.assertEqual(guaranteed_analysis_data[2], self.guaranteed_analysis_unit)
        self.assertEqual(guaranteed_analysis_data[3], self.element_id)
        self.assertEqual(guaranteed_analysis_data[4], self.label_information_id)
        self.assertFalse(guaranteed_analysis_data[5])
        self.assertEqual(guaranteed_analysis_data[6], (self.guaranteed_analysis_name+" "+str(self.guaranteed_analysis_value)+" "+self.guaranteed_analysis_unit))

    def test_get_full_guaranteed_analysis(self):
        guaranteed_analysis_id = nutrients.new_guaranteed(self.cursor, self.guaranteed_analysis_name, self.guaranteed_analysis_value, self.guaranteed_analysis_unit, self.element_id, self.label_information_id)
        guaranteed_analysis_data = nutrients.get_full_guaranteed(self.cursor, guaranteed_analysis_id)
        self.assertEqual(guaranteed_analysis_data[0], self.guaranteed_analysis_name)
        self.assertEqual(guaranteed_analysis_data[1], self.guaranteed_analysis_value)
        self.assertEqual(guaranteed_analysis_data[2], self.guaranteed_analysis_unit)
        self.assertEqual(guaranteed_analysis_data[3], self.element_name_fr)
        self.assertEqual(guaranteed_analysis_data[4], self.element_name_en)
        self.assertEqual(guaranteed_analysis_data[5], self.element_symbol)
        self.assertFalse(guaranteed_analysis_data[6])
        self.assertEqual(guaranteed_analysis_data[7], (self.guaranteed_analysis_name+" "+str(self.guaranteed_analysis_value)+ " "+self.guaranteed_analysis_unit))

    def test_get_all_guaranteed_analysis(self):
        other_name = "other-nutrient"
        guaranteed_analysis_id = nutrients.new_guaranteed(self.cursor, self.guaranteed_analysis_name, self.guaranteed_analysis_value, self.guaranteed_analysis_unit, self.element_id, self.label_information_id)
        guaranteed_id = nutrients.new_guaranteed(self.cursor, other_name, self.guaranteed_analysis_value, self.guaranteed_analysis_unit, self.element_id, self.label_information_id)
        guaranteed_analysis_data = nutrients.get_all_guaranteeds(self.cursor,self.label_information_id)
        self.assertEqual(len(guaranteed_analysis_data), 2)
        self.assertEqual(guaranteed_analysis_data[0][0], guaranteed_analysis_id)
        self.assertEqual(guaranteed_analysis_data[1][0], guaranteed_id)
        
        self.assertEqual(guaranteed_analysis_data[0][1], self.guaranteed_analysis_name)
        self.assertEqual(guaranteed_analysis_data[1][1], other_name)
