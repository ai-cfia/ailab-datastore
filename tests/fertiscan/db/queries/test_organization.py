"""
This is a test script for the database packages.
It tests the functions in the organization module.
"""

import os
import unittest
import uuid

import datastore.db as db
from datastore.db.metadata import validator
from fertiscan.db.models import Location, Province, Region
from fertiscan.db.queries import label, organization
from fertiscan.db.queries.location import create_location, query_locations
from fertiscan.db.queries.province import create_province
from fertiscan.db.queries.region import create_region

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class test_organization_information(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        self.province_name = "a-test-province"
        self.region_name = "test-region"
        self.name = "test-organization"
        self.website = "www.test.com"
        self.phone = "123456789"
        self.location_name = "test-location"
        self.location_address = "test-address"
        self.province = create_province(self.cursor, self.province_name)
        self.province = Province.model_validate(self.province)
        self.region = create_region(self.cursor, self.region_name, self.province.id)
        self.region = Region.model_validate(self.region)

        self.location = create_location(
            self.cursor, self.location_name, self.location_address, self.region.id
        )
        self.location = Location.model_validate(self.location)

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_organization_info(self):
        id = organization.new_organization_info(
            self.cursor, self.name, self.website, self.phone, self.location.id
        )
        self.assertTrue(validator.is_valid_uuid(id))

    def test_new_organization_located(self):
        id = organization.new_organization_info(
            self.cursor, self.name, self.website, self.phone
        )
        self.assertTrue(validator.is_valid_uuid(id))

    def test_new_organization_located_no_location(self):
        id = organization.new_organization_info(
            self.cursor, self.name, self.website, self.phone
        )
        self.assertTrue(validator.is_valid_uuid(id))

    def test_new_organization_info_no_location(self):
        id = organization.new_organization_info(
            self.cursor, self.name, self.website, self.phone, None
        )
        self.assertTrue(validator.is_valid_uuid(id))

    def test_new_organization_located_empty(self):
        with self.assertRaises(organization.OrganizationCreationError):
            organization.new_organization_info_located(
                self.cursor, None, None, None, None
            )

    def test_new_organization_located_no_address(self):
        org_id = organization.new_organization_info_located(
            self.cursor, None, self.name, self.website, self.phone
        )
        # Making sure that a location is not created
        self.assertListEqual(
            query_locations(self.cursor, owner_id=org_id),
            [],
            "Location should not be created",
        )

    def test_get_organization_info(self):
        id = organization.new_organization_info(
            self.cursor, self.name, self.website, self.phone, self.location.id
        )
        data = organization.get_organization_info(self.cursor, id)
        self.assertEqual(data[0], self.name)
        self.assertEqual(data[1], self.website)
        self.assertEqual(data[2], self.phone)
        self.assertEqual(data[3], self.location.id)

    def test_get_organization_info_not_found(self):
        with self.assertRaises(organization.OrganizationNotFoundError):
            organization.get_organization_info(self.cursor, str(uuid.uuid4()))

    def test_update_organization_info(self):
        new_name = "new-name"
        new_website = "www.new.com"
        new_phone = "987654321"
        id = organization.new_organization_info(
            self.cursor, self.name, self.website, self.phone, self.location.id
        )
        old_data = organization.get_organization_info(self.cursor, id)
        self.assertEqual(old_data[0], self.name)
        self.assertEqual(old_data[1], self.website)
        self.assertEqual(old_data[2], self.phone)
        self.assertEqual(old_data[3], self.location.id)
        organization.update_organization_info(
            self.cursor, id, new_name, new_website, new_phone
        )
        data = organization.get_organization_info(self.cursor, id)
        self.assertEqual(data[0], new_name)
        self.assertEqual(data[1], new_website)
        self.assertEqual(data[2], new_phone)

    def test_new_organization_info_located(self):
        id = organization.new_organization_info_located(
            self.cursor,
            address=self.location_address,
            name=self.location_name,
            website=self.website,
            phone_number=self.phone,
        )
        self.assertTrue(validator.is_valid_uuid(id))

    def test_get_organizations_info_json(self):
        company_id = organization.new_organization_info_located(
            self.cursor,
            address=self.location_address,
            name=self.location_name,
            website=self.website,
            phone_number=self.phone,
        )
        manufacturer_id = organization.new_organization_info_located(
            self.cursor,
            address=self.location_address,
            name=self.location_name,
            website=self.website,
            phone_number=self.phone,
        )
        label_id = label.new_label_information(
            self.cursor,
            "label_name",
            "lot_number",
            "10-10-10",
            "registration_number",
            10,
            10,
            10,
            "title_en",
            "title_fr",
            False,
            company_id,
            manufacturer_id,
        )
        data = organization.get_organizations_info_json(self.cursor, label_id)
        self.assertEqual(data["company"]["id"], str(company_id))
        self.assertEqual(data["manufacturer"]["id"], str(manufacturer_id))

    def test_get_organizations_info_json_not_found(self):
        label_id = label.new_label_information(
            self.cursor,
            "label_name",
            "lot_number",
            "10-10-10",
            "registration_number",
            10,
            10,
            10,
            "title_en",
            "title_fr",
            False,
            None,
            None,
        )
        data = organization.get_organizations_info_json(self.cursor, label_id)
        self.assertDictEqual(data, {})


class test_organization(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        self.province_name = "test-province"
        self.region_name = "test-region"
        self.name = "test-organization"
        self.website = "www.test.com"
        self.phone = "123456789"
        self.location_name = "test-location"
        self.location_address = "test-address"
        self.province = create_province(self.cursor, self.province_name)
        self.province = Province.model_validate(self.province)
        self.region = create_region(self.cursor, self.region_name, self.province.id)
        self.region = Region.model_validate(self.region)
        self.location = create_location(
            self.cursor, self.location_name, self.location_address, self.region.id
        )
        self.location = Location.model_validate(self.location)
        self.org_info_id = organization.new_organization_info(
            self.cursor, self.name, self.website, self.phone, self.location.id
        )

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_organization(self):
        organization_id = organization.new_organization(
            self.cursor, self.org_info_id, self.location.id
        )
        self.assertTrue(validator.is_valid_uuid(organization_id))

    def test_new_organization_no_location(self):
        organization_id = organization.new_organization(self.cursor, self.org_info_id)
        self.assertTrue(validator.is_valid_uuid(organization_id))

    def test_update_organization(self):
        organization_id = organization.new_organization(
            self.cursor, self.org_info_id, self.location.id
        )
        new_location = create_location(
            self.cursor, "new-location", "new-address", self.region.id
        )
        new_location = Location.model_validate(new_location)
        organization.update_organization(
            self.cursor, organization_id, self.org_info_id, new_location.id
        )
        organization_data = organization.get_organization(self.cursor, organization_id)
        self.assertEqual(organization_data[0], self.org_info_id)
        self.assertEqual(organization_data[1], new_location.id)

    def test_get_organization(self):
        organization_id = organization.new_organization(
            self.cursor, self.org_info_id, self.location.id
        )
        organization_data = organization.get_organization(self.cursor, organization_id)
        self.assertEqual(organization_data[0], self.org_info_id)
        self.assertEqual(organization_data[1], self.location.id)

    def test_get_organization_not_found(self):
        with self.assertRaises(organization.OrganizationNotFoundError):
            organization.get_organization(self.cursor, str(uuid.uuid4()))

    def test_get_full_organization(self):
        organization_id = organization.new_organization(
            self.cursor, self.org_info_id, self.location.id
        )
        organization_data = organization.get_full_organization(
            self.cursor, organization_id
        )
        self.assertEqual(organization_data[0], organization_id)
        self.assertEqual(organization_data[1], self.name)
        self.assertEqual(organization_data[5], self.location_name)
        self.assertEqual(organization_data[8], self.region_name)
        self.assertEqual(organization_data[10], self.province_name)
