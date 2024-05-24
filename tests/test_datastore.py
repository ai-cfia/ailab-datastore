"""
This is a test script for the highest level of the datastore packages. 
It tests the functions in the __init__.py files of the datastore packages.
"""

import unittest
from unittest.mock import MagicMock
import uuid
import json
import asyncio
import datastore.db.__init__ as db
import datastore.__init__ as datastore
import datastore.db.metadata.validator as validator


class test_ml_structure(unittest.TestCase):
    def setUp(self):
        with open("tests/ml_structure_exemple.json") as file:
            self.ml_dict= json.load(file)
        self.conn = db.connect_db()
        self.cursor = db.cursor(self.conn)
        db.create_search_path(self.conn, self.cursor)
        
    def tearDown(self):
        self.conn.rollback()
        db.end_query(self.conn, self.cursor)
        
        
    def test_import_ml_structure_from_json(self):
        """
        Test the import function.
        """
        try:
            asyncio.run(datastore.import_ml_structure_from_json_version(self.cursor,self.ml_dict))
            self.cursor.execute("SELECT id FROM model WHERE name='that_model_name'")
            model_id=self.cursor.fetchone()[0]
            self.assertTrue(validator.is_valid_uuid(str(model_id)))
            self.cursor.execute("SELECT id FROM pipeline WHERE name='Second Pipeline'")
            pipeline_id=self.cursor.fetchone()[0]
            self.assertTrue(validator.is_valid_uuid(str(pipeline_id)))
            self.cursor.execute("SELECT id FROM pipeline_model WHERE pipeline_id=%s AND model_id=%s",(pipeline_id,model_id,))
            self.assertTrue(validator.is_valid_uuid(self.cursor.fetchone()[0]))
        except Exception as e:
            raise e
        
    def test_get_ml_structure(self):
        """
        Test the get function.
        """
        try:
            #asyncio.run(datastore.import_ml_structure_from_json_version(self.cursor,self.ml_dict))
            ml_structure= asyncio.run(datastore.get_ml_structure(self.cursor))
            for key in ml_structure.keys():
                print("key: "+key+" value: "+str(ml_structure[key])) 
                #self.assertEqual(ml_structure[key],self.ml_dict[key])
        except Exception as e:
            raise e
        
if __name__ == "__main__":
    unittest.main()
