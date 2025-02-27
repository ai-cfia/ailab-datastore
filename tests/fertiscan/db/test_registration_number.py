"""
This is a test script for the database packages.
It tests the functions in the registration number modules.
"""

import os
import unittest
import json

import datastore.db as db
from datastore.db.metadata import validator
from fertiscan.db.metadata.inspection import RegistrationNumber
from fertiscan.db.queries import label, registration_number

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class test_registration_number(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        self.registration_number = "123456"

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
            self.n,
            self.p,
            self.k,
            None,
            None,
            False,
            None,
        )

        self.is_an_ingredient = False
        self.read_name = "read_name"
        self.edited = False

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_registration_number(self):
        registration_number_id = registration_number.new_registration_number(
            self.cursor,
            self.registration_number,
            self.label_id,
            self.is_an_ingredient,
            self.read_name,
            self.edited,
        )
        self.assertTrue(validator.is_valid_uuid(registration_number_id))

    def test_get_registration_numbers_json(self):
        registration_number.new_registration_number(
            self.cursor,
            self.registration_number,
            self.label_id,
            self.is_an_ingredient,
            self.read_name,
            self.edited,
        )
        registration_numbers = registration_number.get_registration_numbers_json(
            self.cursor, self.label_id
        )
        RegistrationNumber.model_validate(registration_numbers)
        self.assertEqual(len(registration_numbers), 1)

    def test_get_registration_numbers_json_empty(self):
        registration_numbers = registration_number.get_registration_numbers_json(
            self.cursor, self.label_id
        )
        RegistrationNumber.model_validate(registration_numbers)
        self.assertEqual(len(registration_numbers["registration_numbers"]), 0)

    def test_update_registration_number(self):
        registration_number.new_registration_number(
            self.cursor,
            self.registration_number,
            self.label_id,
            self.is_an_ingredient,
            self.read_name,
            self.edited,
        )
        old_data = registration_number.get_registration_numbers_json(
            self.cursor, self.label_id
        )
        reg_number_model = RegistrationNumber.model_validate(old_data["registration_numbers"][0])
        self.assertEqual(
            reg_number_model.registration_number,
            self.registration_number,
        )
        new_reg_number = "654321"
        reg_number_model.registration_number = new_reg_number
        reg_number_model.edited = True
        reg_number_model.is_an_ingredient = not self.is_an_ingredient
        
        
        registration_number.update_registration_number(
            cursor=self.cursor,
            registration_numbers=[reg_number_model.model_dump()],
            label_id=self.label_id,
        )
        new_data = registration_number.get_registration_numbers_from_label(
            self.cursor, self.label_id
        )[0]
        
        self.assertEqual(new_data[0],new_reg_number)
        self.assertNotEqual(new_data[0],self.registration_number)
        self.assertTrue(new_data[3])
        self.assertEqual(new_data[1],not self.is_an_ingredient)
        
    def test_delete_registration_numbers(self):
        registration_number.new_registration_number(
            self.cursor,
            self.registration_number,
            self.label_id,
            self.is_an_ingredient,
            self.read_name,
            self.edited,
        )
        
        og_data = registration_number.get_registration_numbers_from_label(self.cursor,self.label_id)

        self.assertEqual(len(og_data),1)
        
        affected_row = registration_number.delete_registration_numbers(cursor=self.cursor,label_id=self.label_id)
        self.assertEqual(len(og_data),affected_row)
        deleted_data = registration_number.get_registration_numbers_from_label(self.cursor,self.label_id)
            
        self.assertEqual(len(deleted_data),0)
