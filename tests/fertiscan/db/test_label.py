import os
import unittest
import uuid

import datastore.db as db
from datastore.db.metadata import validator
from fertiscan.db.queries import label

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
        self.product_name = "product_name"
        self.lot_number = "lot_number"
        self.npk = "npk"
        self.n = 10.0
        self.p = 20.0
        self.k = 30.0
        self.guaranteed_analysis_title_en = "guaranteed_analysis"
        self.guaranteed_analysis_title_fr = "analyse_garantie"
        self.guaranteed_is_minimal = False
        self.record_keeping = False

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_label_information(self):
        label_information_id = label.new_label_information(
            self.cursor,
            self.product_name,
            self.lot_number,
            self.npk,
            self.n,
            self.p,
            self.k,
            self.guaranteed_analysis_title_en,
            self.guaranteed_analysis_title_fr,
            self.guaranteed_is_minimal,
            None,
        )
        self.assertTrue(validator.is_valid_uuid(label_information_id))

    def test_get_label_information(self):
        label_information_id = label.new_label_information(
            self.cursor,
            self.product_name,
            self.lot_number,
            self.npk,
            self.n,
            self.p,
            self.k,
            self.guaranteed_analysis_title_en,
            self.guaranteed_analysis_title_fr,
            self.guaranteed_is_minimal,
            None,
        )
        label_data = label.get_label_information(self.cursor, label_information_id)

        self.assertEqual(label_data[0], label_information_id)
        self.assertEqual(label_data[1], self.product_name)
        self.assertEqual(label_data[2], self.lot_number)
        self.assertEqual(label_data[3], self.npk)
        self.assertEqual(label_data[4], self.n)
        self.assertEqual(label_data[5], self.p)
        self.assertEqual(label_data[6], self.k)
        self.assertEqual(label_data[7], self.guaranteed_analysis_title_en)
        self.assertEqual(label_data[8], self.guaranteed_analysis_title_fr)
        self.assertEqual(label_data[9], self.guaranteed_is_minimal)
        self.assertIsNone(label_data[10])

    def test_get_label_information_json(self):
        label_information_id = label.new_label_information(
            self.cursor,
            self.product_name,
            self.lot_number,
            self.npk,
            self.n,
            self.p,
            self.k,
            self.guaranteed_analysis_title_en,
            self.guaranteed_analysis_title_fr,
            self.guaranteed_is_minimal,
            None,
        )
        label_data = label.get_label_information_json(self.cursor, label_information_id)
        self.assertEqual(label_data["label_id"], str(label_information_id))
        self.assertEqual(label_data["name"], self.product_name)
        self.assertEqual(label_data["lot_number"], self.lot_number)
        self.assertEqual(label_data["npk"], self.npk)
        self.assertEqual(label_data["n"], self.n)
        self.assertEqual(label_data["p"], self.p)
        self.assertEqual(label_data["k"], self.k)

    def test_get_label_information_json_wrong_label_id(self):
        with self.assertRaises(label.LabelInformationNotFoundError):
            label.get_label_information_json(self.cursor, str(uuid.uuid4()))
            
    def test_update_sub_label(self):
        label_information_id = label.new_label_information(
            self.cursor,
            self.product_name,
            self.lot_number,
            self.npk,
            self.n,
            self.p,
            self.k,
            self.guaranteed_analysis_title_en,
            self.guaranteed_analysis_title_fr,
            self.guaranteed_is_minimal,
            self.record_keeping,
        )
        self.assertTrue(validator.is_valid_uuid(label_information_id))
        label_data = label.get_label_information(self.cursor, label_information_id)
        new_name = "new_name"
        new_lot_number = "new lot number"
        new_npk = "new npk"
        new_npk_numerical_val= 17
        new_english_title = "new title"
        
        label.update_label_info(
            cursor=self.cursor,
            label_id=label_information_id,
            name=new_name,
            lot_number=new_lot_number,
            npk=new_npk,
            n=new_npk_numerical_val,
            p=new_npk_numerical_val,
            k=self.k,
            title_en=new_english_title,
            title_fr=self.guaranteed_analysis_title_fr,
            is_minimal= not self.guaranteed_is_minimal,
            record_keeping= not self.record_keeping
        )
        
        updated_label = label.get_label_information(self.cursor, label_information_id)
        
        self.assertEqual(updated_label[0],label_data[0])
        self.assertEqual(updated_label[1],new_name)
        self.assertEqual(updated_label[2],new_lot_number)
        self.assertEqual(updated_label[3],new_npk)
        self.assertEqual(updated_label[4],new_npk_numerical_val)
        self.assertEqual(updated_label[5],new_npk_numerical_val)
        self.assertEqual(updated_label[6],self.k) # We did not change this one
        self.assertEqual(updated_label[7],new_english_title)
        self.assertEqual(updated_label[8],self.guaranteed_analysis_title_fr)
        self.assertEqual(updated_label[9],not self.guaranteed_is_minimal)
        self.assertEqual(updated_label[10],not self.record_keeping)
        
        