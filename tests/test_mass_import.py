import os
import unittest

import datastore.bin.deployment_mass_import as mass_import
import datastore.db as db
import datastore.db.queries.seed as seed
import datastore.db.queries.user as user

DB_CONNECTION_STRING = os.environ.get("NACHET_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("NACHET_DB_URL is not set")

DB_SCHEMA = os.environ.get("NACHET_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("NACHET_SCHEMA_TESTING is not set")


class test_mass_import(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = db.cursor(self.con)
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        self.email = "test@email"
        self.user_id = user.register_user(self.cursor, self.email)

        self.seed_name = "test_seed"
        self.seed_id = seed.new_seed(self.cursor, self.seed_name)
        self.nb_pictures = 1
        self.nb_seeds = 1
        self.zoom = 1.0
        self.pic_path = "img"

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_mass_import(self):
        """
        This test checks if the mass_import function runs without issue
        """
        mass_import.local_import(
            self.pic_path,
            self.email,
            self.seed_name,
            self.zoom,
            self.nb_seeds,
            self.cursor,
        )
        self.assertTrue(True)

    def test_non_existing_seed(self):
        """
        This test checks if the mass_import function raises an exception when the seed does not exist
        """
        with self.assertRaises(seed.SeedNotFoundError):
            mass_import.local_import(
                self.pic_path,
                self.email,
                "non_existing_seed",
                self.zoom,
                self.nb_seeds,
                self.cursor,
            )

    def test_non_existing_user(self):
        """
        This test checks if the mass_import function raises an exception when the user does not exist
        """
        with self.assertRaises(user.UserNotFoundError):
            mass_import.local_import(
                self.pic_path,
                "non_existing_email",
                self.seed_name,
                self.zoom,
                self.nb_seeds,
                self.cursor,
            )

    # TODO: fix inexistent UnProcessedFilesException
    # def test_non_processed_file(self):
    #     """
    #     This test checks if the mass_import function raises an exception when the file is not processed
    #     """
    #     with self.assertRaises(mass_import.UnProcessedFilesException):
    #         mass_import.local_import(
    #             "datastore/tests/UnProcessedFilesException_test",
    #             self.email,
    #             self.seed_name,
    #             self.zoom,
    #             self.nb_seeds,
    #             self.cursor,
    #         )


if __name__ == "__main__":
    unittest.main()
