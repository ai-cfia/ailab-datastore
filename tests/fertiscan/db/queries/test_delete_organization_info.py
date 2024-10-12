import os
import unittest

import psycopg
from dotenv import load_dotenv

from fertiscan.db.queries import organization

load_dotenv()

# Database connection and schema settings
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if not DB_CONNECTION_STRING:
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if not DB_SCHEMA:
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestDeleteOrganizationInformationFunction(unittest.TestCase):
    def setUp(self):
        # Set up database connection and cursor
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Control transaction manually
        self.cursor = self.conn.cursor()

        # Insert a location record for testing
        self.location_id = organization.new_location(
            self.cursor, "Test Location", "123 Test St", None
        )

        # Insert an organization information record for testing
        self.organization_information_id = organization.new_organization_info(
            self.cursor, "Test Organization", None, None, self.location_id
        )

    def tearDown(self):
        # Roll back any changes to maintain database state
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_delete_organization_information_success(self):
        # Delete the organization information
        # TODO: write delete orga function
        self.cursor.execute(
            """
            DELETE FROM organization_information
            WHERE id = %s;
            """,
            (self.organization_information_id,),
        )

        # Verify that the organization information was deleted
        with self.assertRaises(organization.OrganizationNotFoundError):
            organization.get_organization_info(
                self.cursor, self.organization_information_id
            )

        # Verify that the associated location was also deleted
        with self.assertRaises(organization.LocationNotFoundError):
            organization.get_location(self.cursor, self.location_id)

    def test_delete_organization_information_with_linked_records(self):
        # Insert an organization that links to the organization_information
        organization.new_organization(
            self.cursor, self.organization_information_id, self.location_id
        )

        # Attempt to delete the organization information and expect a foreign key violation
        with self.assertRaises(psycopg.errors.ForeignKeyViolation) as context:
            # TODO: write delete orga function
            self.cursor.execute(
                """
                DELETE FROM organization_information
                WHERE id = %s;
                """,
                (self.organization_information_id,),
            )

        self.assertIn(
            "violates foreign key constraint",
            str(context.exception),
            "Expected a foreign key violation error.",
        )

    def test_delete_organization_information_with_shared_location(self):
        # Insert another organization information that shares the same location
        another_organization_information_id = organization.new_organization_info(
            self.cursor, "Another Test Organization", None, None, self.location_id
        )

        # Delete the first organization information
        # TODO: write delete orga function
        self.cursor.execute(
            """
            DELETE FROM organization_information
            WHERE id = %s;
            """,
            (self.organization_information_id,),
        )

        # Verify that the first organization information was deleted
        with self.assertRaises(organization.OrganizationNotFoundError):
            organization.get_organization_info(
                self.cursor, self.organization_information_id
            )

        # Verify that the location was not deleted since it is still referenced by the second organization information
        location = organization.get_location(self.cursor, self.location_id)
        self.assertIsNotNone(
            location,
            "The location should not be deleted because it is still referenced.",
        )

        # Verify that the second organization information still exists
        org_info = organization.get_organization_info(
            self.cursor, another_organization_information_id
        )
        self.assertIsNotNone(
            org_info,
            "The second organization information should still exist.",
        )


if __name__ == "__main__":
    unittest.main()
