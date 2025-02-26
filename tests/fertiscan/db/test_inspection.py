"""
This is a test script for the database packages.
It tests the functions in the inspection module.
"""

import os
import unittest

from datetime import datetime
from time import sleep

import datastore.db as db
from datastore import Role
from datastore.db.metadata import picture_set, validator
from datastore.db.queries import picture, user,container
from fertiscan.db.queries import inspection, label, organization

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class test_inspection(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        self.user_email = "testessr@email"
        self.user_id = user.register_user(self.cursor, self.user_email,Role.INSPECTOR.value)
        self.folder_name = "test-folder"
        self.picture_set = picture_set.build_picture_set_metadata(self.user_id, 1)
        self.container_id = container.create_container(self.cursor,'test-container',self.user_id,False,"test-fertiscan-user")
        self.picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id, self.folder_name,container_id=self.container_id,parent_id=None
        )

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_inspection(self):
        inspection_id,upload_date = inspection.new_inspection(
            cursor=self.cursor, 
            user_id=self.user_id, 
            picture_set_id=self.picture_set_id,
            label_id=None,
            container_id=self.container_id,
            verified=False
        )
        self.assertTrue(validator.is_valid_uuid(inspection_id))
        self.assertIsInstance(upload_date, datetime)

    def test_is_inspection_verified(self):
        inspection_id = inspection.new_inspection(
            cursor=self.cursor, 
            user_id=self.user_id, 
            picture_set_id=self.picture_set_id,
            label_id=None,
            container_id=self.container_id,
            verified=False
        )[0]
        inspection_id2 = inspection.new_inspection(
            cursor=self.cursor, 
            user_id=self.user_id, 
            picture_set_id=self.picture_set_id,
            label_id=None,
            container_id=self.container_id,
            verified=True
        )[0]
        self.assertFalse(inspection.is_inspection_verified(self.cursor, inspection_id))
        self.assertTrue(inspection.is_inspection_verified(self.cursor, inspection_id2))

    def test_get_inspection(self):
        inspection_id = inspection.new_inspection(
            cursor=self.cursor, 
            user_id=self.user_id, 
            picture_set_id=self.picture_set_id,
            label_id=None,
            container_id=self.container_id,
            verified=False
        )[0]
        inspection_data = inspection.get_inspection(self.cursor, inspection_id)
        self.assertEqual(inspection_data[0], False)
        self.assertEqual(inspection_data[3], self.user_id)
        self.assertEqual(inspection_data[6], self.picture_set_id)

    def test_get_all_user_inspection(self):
        inspection_id = inspection.new_inspection(
            cursor=self.cursor, 
            user_id=self.user_id, 
            picture_set_id=self.picture_set_id,
            label_id=None,
            container_id=self.container_id,
            verified=False
        )[0]
        inspection_id2 = inspection.new_inspection(
            cursor=self.cursor, 
            user_id=self.user_id, 
            picture_set_id=self.picture_set_id,
            label_id=None,
            container_id=self.container_id,
            verified=False
        )[0]
        inspection_data = inspection.get_all_user_inspection(self.cursor, self.user_id)
        self.assertEqual(len(inspection_data), 2)
        self.assertEqual(inspection_data[0][0], inspection_id)
        self.assertEqual(inspection_data[1][0], inspection_id2)

    def test_get_all_user_inspection_filter_verified(self):
        inspection_id = inspection.new_inspection(
            cursor=self.cursor, 
            user_id=self.user_id, 
            picture_set_id=self.picture_set_id,
            label_id=None,
            container_id=self.container_id,
            verified=False
        )[0]
        inspection_id2 = inspection.new_inspection(
            cursor=self.cursor, 
            user_id=self.user_id, 
            picture_set_id=self.picture_set_id,
            label_id=None,
            container_id=self.container_id,
            verified=True
        )[0]
        inspection_data = inspection.get_all_user_inspection_filter_verified(
            self.cursor, self.user_id, True
        )
        inspection_data2 = inspection.get_all_user_inspection_filter_verified(
            self.cursor, self.user_id, False
        )
        self.assertEqual(len(inspection_data), 1)
        self.assertEqual(inspection_data[0][0], inspection_id2)
        self.assertTrue(inspection_data[0][9])  # Verified
        self.assertEqual(len(inspection_data2), 1)
        self.assertEqual(inspection_data2[0][0], inspection_id)
        self.assertFalse(inspection_data2[0][9])  # Not verified

    # Deprecated function at the moment
    # def test_get_all_organization_inspection(self):
    #     company_id = organization.new_organization(
    #         self.cursor, "test-company", "test.website.com", "0123456789", None
    #     )
    #     inspection_id = inspection.new_inspection(
    #         self.cursor, self.user_id, self.picture_set_id, False
    #     )
    #     inspection_id2 = inspection.new_inspection(
    #         self.cursor, self.user_id, self.picture_set_id, True
    #     )
    #     inspection_data = inspection.get_all_organization_inspection(
    #         self.cursor, company_id
    #     )
    #     self.assertEqual(len(inspection_data), 2)
    #     self.assertEqual(inspection_data[0][0], inspection_id)
    #     self.assertEqual(inspection_data[1][0], inspection_id2)

    def test_search_inspection(self):
        
        product_name = "searched_product_name_test"
        lot_number = "lot_number"
        npk = "npk"
        n = 10.0
        p = 20.0
        k = 30.0
        guaranteed_analysis_title_en = "guaranteed_analysis"
        guaranteed_analysis_title_fr = "analyse_garantie"
        guaranteed_is_minimal = False
        record_keeping = False
        label_information_id = label.new_label_information(
            self.cursor,
            product_name,
            lot_number,
            npk,
            n,
            p,
            k,
            guaranteed_analysis_title_en,
            guaranteed_analysis_title_fr,
            guaranteed_is_minimal,
            record_keeping,
        )
        inspection_id = inspection.new_inspection(
            cursor=self.cursor, 
            user_id=self.user_id, 
            picture_set_id=self.picture_set_id,
            label_id=label_information_id,
            container_id=self.container_id,
            verified=False
        )
        
        other_product_name = product_name # this is to test the search function
        other_lot_number = "other_lot_number"
        other_npk = "other_npk"
        other_n = 100.0
        other_p = 200.0
        other_k = 300.0
        other_guaranteed_analysis_title_en = "other_guaranteed_analysis"
        other_guaranteed_analysis_title_fr = "other_analyse_garantie"
        other_guaranteed_is_minimal = True
        other_record_keeping = True
        other_label_information_id = label.new_label_information(
            self.cursor,
            other_product_name,
            other_lot_number,
            other_npk,
            other_n,
            other_p,
            other_k,
            other_guaranteed_analysis_title_en,
            other_guaranteed_analysis_title_fr,
            other_guaranteed_is_minimal,
            other_record_keeping,
        )
        other_inspection_id = inspection.new_inspection(
            cursor=self.cursor, 
            user_id=self.user_id, 
            picture_set_id=self.picture_set_id,
            label_id=other_label_information_id,
            container_id=self.container_id,
            verified=False
        )
        # Testing search by name
        inspection_data = inspection.search_inspection(
            self.cursor, 
            fertilizer_name=product_name,
            lower_bound_date=None,
            upper_bound_date=None,
            lot_number=None,
            label_ids=None,
        )
        self.assertEqual(len(inspection_data), 2)
        
        # Testing search by lot number
        inspection_data = inspection.search_inspection(
            self.cursor, 
            fertilizer_name=None,
            lower_bound_date=None,
            upper_bound_date=None,
            lot_number=lot_number,
            label_ids=None,
        )
        self.assertEqual(len(inspection_data), 1)
        self.assertEqual(inspection_data[0][0], inspection_id)
        
        # Testing search by dates
        # Testing search by lower bound date
        today = datetime.today()
        yesterday = today.replace(day=today.day-1)
        tomorrow = today.replace(day=today.day+1)
        inspection_data = inspection.search_inspection(
            self.cursor, 
            fertilizer_name=None,
            lower_bound_date=yesterday,
            upper_bound_date=None,
            lot_number=None,
            label_ids=None,
        )
        self.assertEqual(len(inspection_data), 2)
        inspection_data = inspection.search_inspection(
            self.cursor, 
            fertilizer_name=None,
            lower_bound_date=today,
            upper_bound_date=None,
            lot_number=None,
            label_ids=None,
        )
        self.assertEqual(len(inspection_data), 2)
        inspection_data = inspection.search_inspection(
            self.cursor, 
            fertilizer_name=None,
            lower_bound_date=tomorrow,
            upper_bound_date=None,
            lot_number=None,
            label_ids=None,
        )
        self.assertEqual(len(inspection_data),0)
        # Testing search by upper bound date
        inspection_data = inspection.search_inspection(
            self.cursor, 
            fertilizer_name=None,
            lower_bound_date=None,
            upper_bound_date=today,
            lot_number=None,
            label_ids=None,
        )
        self.assertEqual(len(inspection_data), 2)
        inspection_data = inspection.search_inspection(
            self.cursor, 
            fertilizer_name=None,
            lower_bound_date=None,
            upper_bound_date=yesterday,
            lot_number=None,
            label_ids=None,
        )
        self.assertEqual(len(inspection_data), 0)
        # Testing searching with both dates
        inspection_data = inspection.search_inspection(
            self.cursor, 
            fertilizer_name=None,
            lower_bound_date=yesterday,
            upper_bound_date=today,
            lot_number=None,
            label_ids=None,
        )
        self.assertEqual(len(inspection_data), 2)
        inspection_data = inspection.search_inspection(
            self.cursor, 
            fertilizer_name=None,
            lower_bound_date=today,
            upper_bound_date=today,
            lot_number=None,
            label_ids=None,
        )
        self.assertEqual(len(inspection_data), 2)
        # Testing search by label ids
        label_ids= [label_information_id, other_label_information_id]
        inspection_data = inspection.search_inspection(
            self.cursor, 
            fertilizer_name=None,
            lower_bound_date=None,
            upper_bound_date=None,
            lot_number=None,
            label_ids=label_ids,
        )
        self.assertEqual(len(inspection_data), 2)

    def test_update_inspection(self):
        inspection_id,upload_date = inspection.new_inspection(
            cursor=self.cursor, 
            user_id=self.user_id, 
            picture_set_id=self.picture_set_id,
            label_id=None,
            container_id=self.container_id,
            verified=False,
        )
        self.con.commit() # need to commit to get the time change
        sleep(2)
        updated_at = inspection.update_inspection(
            cursor=self.cursor, 
            inspection_id=inspection_id, 
            verified=True,
            inspection_comment="Test comment"
        )
        inspection_data = inspection.get_inspection(self.cursor, inspection_id)
        inspection.delete_inspection(self.cursor,inspection_id,self.user_id)
        picture.delete_picture_set(self.cursor,self.picture_set_id)
        container.delete_container(self.cursor,self.container_id)
        user.delete_user(self.cursor, self.user_id)
        self.con.commit()
        
        self.assertTrue(inspection_data[0])
        self.assertNotEqual(updated_at, upload_date)
        self.assertEqual(updated_at, inspection_data[2])

