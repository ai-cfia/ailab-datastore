"""
This is a test script for the database packages. 
It tests the functions in the user, seed and picture modules.
"""

import unittest

from datastore.db.queries import sub_label,label
from datastore.db.metadata import validator
import datastore.db.__init__ as db

class test_specification(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(db.FERTISCAN_DB_URL,db.FERTISCAN_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, db.FERTISCAN_SCHEMA)
        
        self.lot_number = "lot_number"
        self.npk = "npk"
        self.registration_number = "registration_number"
        self.n = 10.0
        self.p = 20.0
        self.k = 30.0
        self.weight = None
        self.density = None
        self.volume = None
        self.label_id = label.new_label_information(self.cursor, self.lot_number, self.npk, self.registration_number, self.n, self.p, self.k, self.weight, self.density, self.volume)
        
        self.humidity = 10.0
        self.ph = 20.0
        self.solubility = 30.0
    
    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_specification(self):
        specification_id = sub_label.new_specification(self.cursor, self.humidity, self.ph, self.solubility,self.label_id)
        self.assertTrue(validator.is_valid_uuid(specification_id))

    def test_get_specification(self):
        specification_id = sub_label.new_specification(self.cursor, self.humidity, self.ph, self.solubility,self.label_id)
        specification_data = sub_label.get_specification(self.cursor, specification_id)
        self.assertEqual(specification_data[0], self.humidity)
        self.assertEqual(specification_data[1], self.ph)
        self.assertEqual(specification_data[2], self.solubility)

    def test_get_all_specification(self):
        other_humidity = 40
        specification_id = sub_label.new_specification(self.cursor, self.humidity, self.ph, self.solubility,self.label_id)
        specif_id= sub_label.new_specification(self.cursor, other_humidity, self.ph, self.solubility,self.label_id)
        specification_data = sub_label.get_all_specifications(self.cursor,self.label_id)
        self.assertEqual(len(specification_data), 2)

        self.assertTrue(validator.is_valid_uuid(specification_data[0][0]))
        self.assertEqual(specification_data[0][0], specification_id)
        self.assertTrue(validator.is_valid_uuid(specification_data[1][0]))
        self.assertEqual(specification_data[1][0], specif_id)

        self.assertEqual(specification_data[0][1], self.humidity)
        self.assertEqual(specification_data[1][1], other_humidity)

class test_first_aid(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(db.FERTISCAN_DB_URL,db.FERTISCAN_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, db.FERTISCAN_SCHEMA)
        
        self.lot_number = "lot_number"
        self.npk = "npk"
        self.registration_number = "registration_number"
        self.n = 10.0
        self.p = 20.0
        self.k = 30.0
        self.weight = None
        self.density = None
        self.volume = None
        self.label_id = label.new_label_information(self.cursor, self.lot_number, self.npk, self.registration_number, self.n, self.p, self.k, self.weight, self.density, self.volume)
        
        self.fr = "test-fr"
        self.en = "test-en"
    
    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_first_aid(self):
        first_aid_id = sub_label.new_first_aid(self.cursor, self.fr, self.en,self.label_id)
        self.assertTrue(validator.is_valid_uuid(first_aid_id))

    def test_get_first_aid(self):
        first_aid_id = sub_label.new_first_aid(self.cursor, self.fr, self.en,self.label_id)
        first_aid_data = sub_label.get_first_aid(self.cursor, first_aid_id)
        self.assertEqual(first_aid_data[0], self.fr)
        self.assertEqual(first_aid_data[1], self.en)
        self.assertFalse(first_aid_data[2])

    def test_get_all_first_aid(self):
        other_fr = "other-fr"
        first_aid_id = sub_label.new_first_aid(self.cursor, self.fr, self.en,self.label_id)
        first_aid_id2 = sub_label.new_first_aid(self.cursor, other_fr, self.en,self.label_id)
        first_aid_data = sub_label.get_all_first_aids(self.cursor,self.label_id)
        self.assertEqual(len(first_aid_data), 2)

        self.assertTrue(validator.is_valid_uuid(first_aid_data[0][0]))
        self.assertEqual(first_aid_data[0][0], first_aid_id)
        self.assertTrue(validator.is_valid_uuid(first_aid_data[1][0]))
        self.assertEqual(first_aid_data[1][0], first_aid_id2)

        self.assertEqual(first_aid_data[0][1], self.fr)
        self.assertEqual(first_aid_data[1][1], other_fr)

class test_warranty(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(db.FERTISCAN_DB_URL,db.FERTISCAN_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, db.FERTISCAN_SCHEMA)
        
        self.lot_number = "lot_number"
        self.npk = "npk"
        self.registration_number = "registration_number"
        self.n = 10.0
        self.p = 20.0
        self.k = 30.0
        self.weight = None
        self.density = None
        self.volume = None
        self.label_id = label.new_label_information(self.cursor, self.lot_number, self.npk, self.registration_number, self.n, self.p, self.k, self.weight, self.density, self.volume)
        
        self.fr = "test-fr"
        self.en = "test-en"
    
    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_warranty(self):
        warranty_id = sub_label.new_warranty(self.cursor, self.fr, self.en,self.label_id)
        self.assertTrue(validator.is_valid_uuid(warranty_id))

    def test_get_warranty(self):
        warranty_id = sub_label.new_warranty(self.cursor, self.fr, self.en,self.label_id)
        warranty_data = sub_label.get_warranty(self.cursor, warranty_id)
        self.assertEqual(warranty_data[0], self.fr)
        self.assertEqual(warranty_data[1], self.en)
        self.assertFalse(warranty_data[2])

    def test_get_all_warranties(self):
        other_fr = "other-fr"
        warranty_id = sub_label.new_warranty(self.cursor, self.fr, self.en,self.label_id)
        warranty_id2 = sub_label.new_warranty(self.cursor, other_fr, self.en,self.label_id)
        warranty_data = sub_label.get_all_warranties(self.cursor,self.label_id)
        self.assertEqual(len(warranty_data), 2)

        self.assertTrue(validator.is_valid_uuid(warranty_data[0][0]))
        self.assertEqual(warranty_data[0][0], warranty_id)
        self.assertTrue(validator.is_valid_uuid(warranty_data[1][0]))
        self.assertEqual(warranty_data[1][0], warranty_id2)

        self.assertEqual(warranty_data[0][1], self.fr)
        self.assertEqual(warranty_data[1][1], other_fr)

class test_instruction(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(db.FERTISCAN_DB_URL,db.FERTISCAN_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, db.FERTISCAN_SCHEMA)
        
        self.lot_number = "lot_number"
        self.npk = "npk"
        self.registration_number = "registration_number"
        self.n = 10.0
        self.p = 20.0
        self.k = 30.0
        self.weight = None
        self.density = None
        self.volume = None
        self.label_id = label.new_label_information(self.cursor, self.lot_number, self.npk, self.registration_number, self.n, self.p, self.k, self.weight, self.density, self.volume)
        
        self.fr = "test-fr"
        self.en = "test-en"
    
    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_instruction(self):
        instruction_id = sub_label.new_instruction(self.cursor, self.fr, self.en,self.label_id)
        self.assertTrue(validator.is_valid_uuid(instruction_id))

    def test_get_instruction(self):
        instruction_id = sub_label.new_instruction(self.cursor, self.fr, self.en,self.label_id)
        instruction_data = sub_label.get_instruction(self.cursor, instruction_id)
        self.assertEqual(instruction_data[0], self.fr)
        self.assertEqual(instruction_data[1], self.en)
        self.assertFalse(instruction_data[2])

    def test_get_all_instructions(self):
        other_fr = "other-fr"
        instruction_id = sub_label.new_instruction(self.cursor, self.fr, self.en,self.label_id)
        instruction_id2 = sub_label.new_instruction(self.cursor, other_fr, self.en,self.label_id)
        instruction_data = sub_label.get_all_instructions(self.cursor,self.label_id)
        self.assertEqual(len(instruction_data), 2)

        self.assertTrue(validator.is_valid_uuid(instruction_data[0][0]))
        self.assertEqual(instruction_data[0][0], instruction_id)
        self.assertTrue(validator.is_valid_uuid(instruction_data[1][0]))
        self.assertEqual(instruction_data[1][0], instruction_id2)

        self.assertEqual(instruction_data[0][1], self.fr)
        self.assertEqual(instruction_data[1][1], other_fr)


class test_caution(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(db.FERTISCAN_DB_URL,db.FERTISCAN_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, db.FERTISCAN_SCHEMA)
        
        self.lot_number = "lot_number"
        self.npk = "npk"
        self.registration_number = "registration_number"
        self.n = 10.0
        self.p = 20.0
        self.k = 30.0
        self.weight = None
        self.density = None
        self.volume = None
        self.label_id = label.new_label_information(self.cursor, self.lot_number, self.npk, self.registration_number, self.n, self.p, self.k, self.weight, self.density, self.volume)
        
        self.fr = "test-fr"
        self.en = "test-en"
    
    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_caution(self):
        caution_id = sub_label.new_caution(self.cursor, self.fr, self.en,self.label_id)
        self.assertTrue(validator.is_valid_uuid(caution_id))

    def test_get_caution(self):
        caution_id = sub_label.new_caution(self.cursor, self.fr, self.en,self.label_id)
        caution_data = sub_label.get_caution(self.cursor, caution_id)
        self.assertEqual(caution_data[0], self.fr)
        self.assertEqual(caution_data[1], self.en)
        self.assertFalse(caution_data[2])

    def test_get_all_cautions(self):
        other_fr = "other-fr"
        caution_id = sub_label.new_caution(self.cursor, self.fr, self.en,self.label_id)
        caution_id2 = sub_label.new_caution(self.cursor, other_fr, self.en,self.label_id)
        caution_data = sub_label.get_all_cautions(self.cursor,self.label_id)
        self.assertEqual(len(caution_data), 2)

        self.assertTrue(validator.is_valid_uuid(caution_data[0][0]))
        self.assertEqual(caution_data[0][0], caution_id)
        self.assertTrue(validator.is_valid_uuid(caution_data[1][0]))
        self.assertEqual(caution_data[1][0], caution_id2)

        self.assertEqual(caution_data[0][1], self.fr)
        self.assertEqual(caution_data[1][1], other_fr)


class test_ingredient(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(db.FERTISCAN_DB_URL,db.FERTISCAN_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, db.FERTISCAN_SCHEMA)
        
        self.lot_number = "lot_number"
        self.npk = "npk"
        self.registration_number = "registration_number"
        self.n = 10.0
        self.p = 20.0
        self.k = 30.0
        self.weight = None
        self.density = None
        self.volume = None
        self.label_id = label.new_label_information(self.cursor, self.lot_number, self.npk, self.registration_number, self.n, self.p, self.k, self.weight, self.density, self.volume)
        
        self.name = "test-fr"
        self.organic = False
    
    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_ingredient(self):
        ingredient_id = sub_label.new_ingredient(self.cursor, self.name, self.label_id, self.organic)
        self.assertTrue(validator.is_valid_uuid(ingredient_id))

    def test_get_ingredient(self):
        ingredient_id = sub_label.new_ingredient(self.cursor, self.name, self.label_id, self.organic)
        ingredient_data = sub_label.get_ingredient(self.cursor, ingredient_id)
        self.assertEqual(ingredient_data[0], self.name)
        self.assertEqual(ingredient_data[1], self.organic)
        self.assertFalse(ingredient_data[2])

    def test_get_all_ingredient(self):
        other_name = "other-name"
        ingredient_id = sub_label.new_ingredient(self.cursor, self.name, self.label_id, self.organic)
        ingredient_id2 = sub_label.new_ingredient(self.cursor, other_name, self.label_id, True)
        ingredient_data = sub_label.get_all_ingredients(self.cursor,self.label_id)
        self.assertEqual(len(ingredient_data), 2)

        self.assertTrue(validator.is_valid_uuid(ingredient_data[0][0]))
        self.assertEqual(ingredient_data[0][0], ingredient_id)
        self.assertTrue(validator.is_valid_uuid(ingredient_data[1][0]))
        self.assertEqual(ingredient_data[1][0], ingredient_id2)

        self.assertEqual(ingredient_data[0][1], self.name)
        self.assertEqual(ingredient_data[1][1], other_name)

        self.assertFalse(ingredient_data[0][2])
        self.assertTrue(ingredient_data[1][2])

    








