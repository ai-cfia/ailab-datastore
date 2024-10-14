import os
import unittest
import uuid
from datetime import timedelta

from dotenv import load_dotenv
from psycopg import Connection, connect

from datastore.db.queries.user import register_user
from fertiscan.db.models import Fertilizer
from fertiscan.db.queries.fertilizer import (
    create_fertilizer,
    delete_fertilizer,
    query_fertilizers,
    read_all_fertilizers,
    read_fertilizer,
    update_fertilizer,
    upsert_fertilizer,
)
from fertiscan.db.queries.inspection import new_inspection
from fertiscan.db.queries.organization import (
    new_location,
    new_organization,
    new_organization_info,
    new_province,
    new_region,
)

load_dotenv()

TEST_DB_CONNECTION_STRING = os.environ["FERTISCAN_DB_URL"]
TEST_DB_SCHEMA = os.environ["FERTISCAN_SCHEMA_TESTING"]


class TestFertilizerFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn: Connection = connect(
            TEST_DB_CONNECTION_STRING, options=f"-c search_path={TEST_DB_SCHEMA},public"
        )
        cls.conn.autocommit = False

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        self.cursor = self.conn.cursor()

        # Create necessary records for testing
        self.inspector_id = register_user(
            self.cursor, f"{uuid.uuid4().hex}@example.com"
        )
        self.province_id = new_province(self.cursor, "a-test-province")
        self.region_id = new_region(self.cursor, "test-region", self.province_id)
        self.location_id = new_location(
            self.cursor, "test-location", "test-address", self.region_id
        )
        self.organization_info_id = new_organization_info(
            self.cursor,
            "test-organization",
            "www.test.com",
            "123456789",
            self.location_id,
        )
        self.organization_id = new_organization(
            self.cursor, self.organization_info_id, self.location_id
        )
        self.inspection_id = new_inspection(self.cursor, self.inspector_id, None, False)

    def tearDown(self):
        self.conn.rollback()
        self.cursor.close()

    def test_create_fertilizer(self):
        name = uuid.uuid4().hex
        registration_number = "1234567A"

        created_fertilizer = create_fertilizer(
            self.cursor,
            name,
            registration_number,
            self.inspection_id,
            self.organization_id,
        )
        created_fertilizer = Fertilizer.model_validate(created_fertilizer)

        self.assertEqual(created_fertilizer.name, name)
        self.assertEqual(created_fertilizer.registration_number, registration_number)

    def test_read_fertilizer(self):
        name = uuid.uuid4().hex
        registration_number = "7654321B"

        created_fertilizer = create_fertilizer(
            self.cursor,
            name,
            registration_number,
            self.inspection_id,
            self.organization_id,
        )
        created_fertilizer = Fertilizer.model_validate(created_fertilizer)

        fetched_fertilizer = read_fertilizer(self.cursor, created_fertilizer.id)
        fetched_fertilizer = Fertilizer.model_validate(fetched_fertilizer)

        self.assertEqual(fetched_fertilizer.name, name)
        self.assertEqual(fetched_fertilizer.registration_number, registration_number)

    def test_read_all_fertilizers(self):
        initial_fertilizers = read_all_fertilizers(self.cursor)

        # Create two new fertilizers
        fertilizer_a = create_fertilizer(
            self.cursor,
            uuid.uuid4().hex,
            "1234567C",
            self.inspection_id,
            self.organization_id,
        )
        fertilizer_b = create_fertilizer(
            self.cursor,
            uuid.uuid4().hex,
            "7654321D",
            self.inspection_id,
            self.organization_id,
        )

        all_fertilizers = read_all_fertilizers(self.cursor)
        all_fertilizers = [Fertilizer.model_validate(f) for f in all_fertilizers]

        self.assertGreaterEqual(len(all_fertilizers), len(initial_fertilizers) + 2)
        self.assertIn(Fertilizer.model_validate(fertilizer_a), all_fertilizers)
        self.assertIn(Fertilizer.model_validate(fertilizer_b), all_fertilizers)

    def test_update_fertilizer(self):
        # Create a fertilizer to update
        fertilizer = create_fertilizer(
            self.cursor,
            uuid.uuid4().hex,
            "1234567E",
            self.inspection_id,
            self.organization_id,
        )
        fertilizer = Fertilizer.model_validate(fertilizer)

        # Update the fertilizer
        name = uuid.uuid4().hex
        registration_number = "7654321F"
        updated_fertilizer = update_fertilizer(
            self.cursor,
            fertilizer.id,
            name=name,
            registration_number=registration_number,
        )
        updated_fertilizer = Fertilizer.model_validate(updated_fertilizer)

        self.assertEqual(updated_fertilizer.name, name)
        self.assertEqual(updated_fertilizer.registration_number, registration_number)

        # Fetch from DB and confirm the changes persist
        fetched_fertilizer = read_fertilizer(self.cursor, fertilizer.id)
        validated_fetched = Fertilizer.model_validate(fetched_fertilizer)

        self.assertEqual(validated_fetched, updated_fertilizer)

    def test_delete_fertilizer(self):
        # Create a fertilizer to delete
        fertilizer = create_fertilizer(
            self.cursor,
            uuid.uuid4().hex,
            "9876543G",
            self.inspection_id,
            self.organization_id,
        )
        fertilizer = Fertilizer.model_validate(fertilizer)

        # Delete the fertilizer
        deleted_fertilizer = delete_fertilizer(self.cursor, fertilizer.id)
        validated_deleted = Fertilizer.model_validate(deleted_fertilizer)

        # Verify the deleted fertilizer matches the original one
        self.assertEqual(fertilizer, validated_deleted)

        # Ensure the fertilizer no longer exists
        fetched_fertilizer = read_fertilizer(self.cursor, fertilizer.id)
        self.assertIsNone(fetched_fertilizer)

    def test_query_fertilizers_no_filters(self):
        # Create a fertilizer to ensure at least one exists
        fertilizer = create_fertilizer(
            self.cursor,
            uuid.uuid4().hex,
            "1111111A",
            self.inspection_id,
            self.organization_id,
        )

        # Query without filters (should return all fertilizers)
        results = query_fertilizers(self.cursor)
        validated_results = [Fertilizer.model_validate(f) for f in results]

        # Ensure the created fertilizer is present
        self.assertIn(Fertilizer.model_validate(fertilizer), validated_results)

    def test_query_fertilizers_with_name(self):
        # Create a fertilizer with a unique name
        fertilizer = create_fertilizer(
            self.cursor,
            uuid.uuid4().hex,
            "2222222B",
            self.inspection_id,
            self.organization_id,
        )
        fertilizer = Fertilizer.model_validate(fertilizer)

        # Query by name
        results = query_fertilizers(self.cursor, name=fertilizer.name)

        # Validate the results
        validated_results = [Fertilizer.model_validate(f) for f in results]

        # Ensure the correct fertilizer is returned
        self.assertEqual(len(validated_results), 1)
        self.assertEqual(validated_results[0], fertilizer)

    def test_query_fertilizers_with_multiple_filters(self):
        # Create a fertilizer with known properties
        fertilizer = create_fertilizer(
            self.cursor,
            uuid.uuid4().hex,
            "3333333C",
            self.inspection_id,
            self.organization_id,
        )
        fertilizer = Fertilizer.model_validate(fertilizer)

        # Query by multiple filters (name and registration number)
        results = query_fertilizers(
            self.cursor,
            name=fertilizer.name,
            registration_number=fertilizer.registration_number,
        )

        # Validate the results
        validated_results = [Fertilizer.model_validate(f) for f in results]

        # Ensure the correct fertilizer is returned
        self.assertEqual(len(validated_results), 1)
        self.assertEqual(validated_results[0], fertilizer)

    def test_query_fertilizers_no_match(self):
        # Query for a non-existent fertilizer
        results = query_fertilizers(self.cursor, name=uuid.uuid4().hex)

        # Ensure no results are returned
        self.assertEqual(len(results), 0)

    def test_query_fertilizers_by_upload_date(self):
        # Create a fertilizer and validate it
        created_fertilizer = create_fertilizer(
            self.cursor,
            uuid.uuid4().hex,
            "4444444D",
            self.inspection_id,
            self.organization_id,
        )
        created_fertilizer = Fertilizer.model_validate(created_fertilizer)

        # Use a slight buffer around the creation timestamp
        lower_bound = created_fertilizer.upload_date - timedelta(seconds=1)
        upper_bound = created_fertilizer.upload_date + timedelta(seconds=1)

        # Query within the temporal range
        fertilizers = query_fertilizers(
            self.cursor, upload_date_from=lower_bound, upload_date_to=upper_bound
        )
        fertilizers = [Fertilizer.model_validate(f) for f in fertilizers]

        # Ensure the created fertilizer is present
        self.assertIn(created_fertilizer, fertilizers)

    def test_query_fertilizers_by_update_at(self):
        # Create a fertilizer and validate it
        created_fertilizer = create_fertilizer(
            self.cursor,
            uuid.uuid4().hex,
            "5555555E",
            self.inspection_id,
            self.organization_id,
        )
        created_fertilizer = Fertilizer.model_validate(created_fertilizer)

        # Update the fertilizer and validate it
        updated_fertilizer = update_fertilizer(
            self.cursor, created_fertilizer.id, name=uuid.uuid4().hex
        )
        updated_fertilizer = Fertilizer.model_validate(updated_fertilizer)

        # Use a slight buffer around the update timestamp
        lower_bound = updated_fertilizer.update_at - timedelta(seconds=1)
        upper_bound = updated_fertilizer.update_at + timedelta(seconds=1)

        # Query within the temporal range
        results = query_fertilizers(
            self.cursor, update_at_from=lower_bound, update_at_to=upper_bound
        )
        validated_results = [Fertilizer.model_validate(f) for f in results]

        # Ensure the updated fertilizer is present
        self.assertIn(updated_fertilizer, validated_results)

    def test_query_fertilizers_by_inspection_id(self):
        # Create a fertilizer and validate it
        fertilizer = create_fertilizer(
            self.cursor,
            uuid.uuid4().hex,
            "6666666F",
            self.inspection_id,
            self.organization_id,
        )
        fertilizer = Fertilizer.model_validate(fertilizer)

        # Query by inspection ID
        fertilizers = query_fertilizers(
            self.cursor, latest_inspection_id=self.inspection_id
        )
        fertilizers = [Fertilizer.model_validate(f) for f in fertilizers]

        # Ensure the fertilizer is present
        self.assertIn(fertilizer, fertilizers)

    def test_query_fertilizers_by_owner_id(self):
        # Create a fertilizer and validate it
        fertilizer = create_fertilizer(
            self.cursor,
            uuid.uuid4().hex,
            "7777777G",
            self.inspection_id,
            self.organization_id,
        )
        fertilizer = Fertilizer.model_validate(fertilizer)

        # Query by owner ID
        fertilizers = query_fertilizers(self.cursor, owner_id=self.organization_id)
        fertilizers = [Fertilizer.model_validate(f) for f in fertilizers]

        # Ensure the fertilizer is present
        self.assertIn(fertilizer, fertilizers)

    def test_upsert_fertilizer(self):
        # Create a fertilizer and validate it
        name = uuid.uuid4().hex
        registration_number = "8888888H"
        fertilizer = upsert_fertilizer(
            self.cursor,
            name=name,
            registration_number=registration_number,
            latest_inspection_id=self.inspection_id,
            owner_id=self.organization_id,
        )

        # Ensure the fertilizer was created
        fertilizer = read_fertilizer(self.cursor, fertilizer[0])
        fertilizer = Fertilizer.model_validate(fertilizer)
        self.assertIsNotNone(fertilizer)
        self.assertEqual(fertilizer.name, name)
        self.assertEqual(fertilizer.registration_number, registration_number)

        # Replace the fertilizer with new data
        new_reg_number = "9999999I"
        replaced_fertilizer = upsert_fertilizer(
            self.cursor,
            name=name,  # same name
            registration_number=new_reg_number,
            latest_inspection_id=self.inspection_id,
            owner_id=self.organization_id,
        )

        # Ensure the fertilizer was replaced
        replaced_fertilizer = read_fertilizer(self.cursor, replaced_fertilizer[0])
        replaced_fertilizer = Fertilizer.model_validate(replaced_fertilizer)
        self.assertIsNotNone(replaced_fertilizer)
        self.assertEqual(fertilizer.id, replaced_fertilizer.id)
        self.assertEqual(replaced_fertilizer.name, fertilizer.name)
        self.assertEqual(replaced_fertilizer.registration_number, new_reg_number)


if __name__ == "__main__":
    unittest.main()
