"""
This is a test script for the highest level of the datastore packages. 
It tests the functions in the __init__.py files of the datastore packages.
"""
import unittest
import json
import datastore.db.__init__ as db
import datastore.__init__ as datastore
import datastore.FertiScan as FertiScan
import datastore.db.metadata.validator as validator
from copy import deepcopy

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

class TestDatastore(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.analysis_json = json.loads('tests/analyse.json')

        con = db.connect_db(DB_CONNECTION_STRING)
        self.cursor = con.cursor()
        db.create_search_path(con, self.cursor, DB_SCHEMA)

        self.user_email = 'test@email'
        datastore.new_user(self.cursor, self.user_email)

        self.user_id = datastore.get_user_id(self.cursor, self.user_email)
        self.container_client = datastore.get_user_container_client(self.user_id, 'test-user')

        
    def tearDown(self):
        self.con.rollback()
        self.container_client.delete_container()
        db.end_query(self.con, self.cursor)

    def test_register_analysis(self):
        analysis = FertiScan.register_analysis(self.cursor, self.container_client, self.user_id, self.analysis_json)
        self.assertIsNotNone(analysis)
        self.assertTrue(validator.is_valid_uuid(analysis['inspection_id']))