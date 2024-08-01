"""
This is a test script for the database packages. 
It tests the functions in the inspection.
"""

import unittest
from datastore.db.queries import inspection, user, picture
from datastore.db.metadata import validator, picture_set
import datastore.db.__init__ as db
import os

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

        self.user_email = "tester@email"
        self.user_id = user.register_user(self.cursor, self.user_email)
        self.folder_name = "test-folder"
        self.picture_set = picture_set.build_picture_set(self.user_id, 1)
        self.picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id, self.folder_name
        )

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_inspection(self):
        inspection_id = inspection.new_inspection(
            self.cursor, self.user_id, self.picture_set_id, False
        )
        self.assertTrue(validator.is_valid_uuid(inspection_id))

    def test_is_inspection_verified(self):
        inspection_id = inspection.new_inspection(
            self.cursor, self.user_id, self.picture_set_id, False
        )
        inspection_id2 = inspection.new_inspection(
            self.cursor, self.user_id, self.picture_set_id, True
        )
        self.assertFalse(inspection.is_inspection_verified(self.cursor, inspection_id))
        self.assertTrue(inspection.is_inspection_verified(self.cursor, inspection_id2))

    def test_get_inspection(self):
        inspection_id = inspection.new_inspection(
            self.cursor, self.user_id, self.picture_set_id, False
        )
        inspection_data = inspection.get_inspection(self.cursor, inspection_id)
        self.assertEqual(inspection_data[0], False)
        self.assertEqual(inspection_data[3], self.user_id)
        self.assertEqual(inspection_data[6], self.picture_set_id)
        self.assertIsNone(inspection_data[4])

    def test_get_all_user_inspection(self):
        inspection_id = inspection.new_inspection(
            self.cursor, self.user_id, self.picture_set_id, False
        )
        inspection_id2 = inspection.new_inspection(
            self.cursor, self.user_id, self.picture_set_id, True
        )
        inspection_data = inspection.get_all_user_inspection(self.cursor, self.user_id)
        self.assertEqual(len(inspection_data), 2)
        self.assertEqual(inspection_data[0][0], inspection_id)
        self.assertEqual(inspection_data[1][0], inspection_id2)

    def test_update_inspection(self):
        inspection_id = inspection.new_inspection(
            self.cursor, self.user_id, self.picture_set_id, False
        )
        verified = True
        inspection.update_inspection(
            self.cursor, inspection_id, verified, None, None, None, None,
        )
        inspection_data = inspection.get_inspection(self.cursor, inspection_id)
        self.assertEqual(inspection_data[0], verified)

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
