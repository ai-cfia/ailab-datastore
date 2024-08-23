"""
This is a test script for the database packages. 
It tests the functions in the ingredient module.
"""

import unittest
from datastore.db.queries import ingredient, label
from datastore.db.metadata import validator
import datastore.db.__init__ as db
import os

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class test_ingredient(unittest.TestCase):
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

        self.ingredient_name = "ingredient_name"
        self.value = 10.0
        self.unit = "unit"

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_ingredient(self):
        ingredient_id = ingredient.new_ingredient(
            self.cursor,
            self.ingredient_name,
            self.value,
            self.unit,
            self.label_id,
            self.language,
            False,
            False,
            False,
        )
        self.assertTrue(validator.is_valid_uuid(ingredient_id))

    def test_get_ingredient_json(self):
        nom = "nom_ingredient"
        name = "ingredient_name"
        ingredient.new_ingredient(
            self.cursor,
            nom,
            self.value,
            self.unit,
            self.label_id,
            "fr",
            False,
            False,
            False,
        )
        ingredient.new_ingredient(
            self.cursor,
            name,
            self.value,
            self.unit,
            self.label_id,
            "en",
            False,
            False,
            False,
        )

        ingredient_obj = ingredient.get_ingredient_json(self.cursor, self.label_id)
        self.assertIsNotNone(ingredient_obj["ingredients"]["en"])
        self.assertEqual(len(ingredient_obj.get("ingredients").get("en")), 1)
        self.assertEqual(len(ingredient_obj["ingredients"]["fr"]), 1)

    def test_get_ingredient_json_empty(self):
        ingredient_obj = ingredient.get_ingredient_json(self.cursor, self.label_id)
        self.assertIsNotNone(ingredient_obj.get("ingredients").get("en"))
        self.assertIsNotNone(ingredient_obj.get("ingredients").get("fr"))
        self.assertEqual(len(ingredient_obj.get("ingredients").get("en")), 0)
        self.assertEqual(len(ingredient_obj.get("ingredients").get("fr")), 0)
