"""
This is a test script for the database packages. 
It tests the functions in the organization module.
"""

import unittest
import uuid
from datastore.db.queries import organization, label
from datastore.db.metadata import validator
import datastore.db.__init__ as db
import os

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

# DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
DB_SCHEMA = "fertiscan_0.0.11"
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class test_province(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        self.name = "test-province"

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_province(self):
        province_id = organization.new_province(self.cursor, self.name)
        self.assertIsInstance(province_id, int)

    def test_get_province(self):
        province_id = organization.new_province(self.cursor, self.name)
        province_data = organization.get_province(self.cursor, province_id)
        self.assertEqual(province_data[0], self.name)

    def test_get_province_not_found(self):
        with self.assertRaises(organization.ProvinceNotFoundError):
            organization.get_province(self.cursor, 0)

    def test_get_all_province(self):
        province_id = organization.new_province(self.cursor, self.name)
        province_2_id = organization.new_province(self.cursor, "test-province-2")
        province_data = organization.get_all_province(self.cursor)
        self.assertEqual(len(province_data), 2)
        self.assertEqual(province_data[0][0], province_id)
        self.assertEqual(province_data[1][0], province_2_id)


class test_region(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        self.province_name = "test-province"
        self.name = "test-region"
        self.province_id = organization.new_province(self.cursor, self.province_name)

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_region(self):
        region_id = organization.new_region(self.cursor, self.name, self.province_id)
        self.assertTrue(validator.is_valid_uuid(region_id))

    def test_get_region(self):
        region_id = organization.new_region(self.cursor, self.name, self.province_id)
        region_data = organization.get_region(self.cursor, region_id)
        self.assertEqual(region_data[0], self.name)
        self.assertEqual(region_data[1], self.province_id)

    def test_get_region_not_found(self):
        with self.assertRaises(organization.RegionNotFoundError):
            organization.get_region(self.cursor, str(uuid.uuid4()))

    def test_get_full_region(self):
        region_id = organization.new_region(self.cursor, self.name, self.province_id)
        region_data = organization.get_full_region(self.cursor, region_id)
        self.assertEqual(region_data[0], region_id)
        self.assertEqual(region_data[1], self.name)
        self.assertEqual(region_data[2], self.province_name)

    def get_region_by_province(self):
        region_id = organization.new_region(self.cursor, self.name, self.province_id)
        region_data = organization.get_region_by_province(self.cursor, self.province_id)
        self.assertEqual(len(region_data), 1)
        self.assertEqual(region_data[0][0], region_id)
        self.assertEqual(region_data[0][1], self.name)


class test_location(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        self.province_name = "test-province"
        self.region_name = "test-region"
        self.name = "test-location"
        self.address = "test-address"
        self.province_id = organization.new_province(self.cursor, self.province_name)
        self.region_id = organization.new_region(
            self.cursor, self.region_name, self.province_id
        )

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_location(self):
        location_id = organization.new_location(
            self.cursor, self.name, self.address, self.region_id
        )
        self.assertTrue(validator.is_valid_uuid(location_id))

    def test_get_location(self):
        location_id = organization.new_location(
            self.cursor, self.name, self.address, self.region_id
        )
        location_data = organization.get_location(self.cursor, location_id)

        self.assertEqual(location_data[0], self.name)
        self.assertEqual(location_data[2], self.region_id)
        self.assertIsNone(location_data[3])

    def test_get_location_not_found(self):
        with self.assertRaises(organization.LocationNotFoundError):
            organization.get_location(self.cursor, str(uuid.uuid4()))

    def test_get_full_location(self):
        location_id = organization.new_location(
            self.cursor, self.name, self.address, self.region_id
        )
        location_data = organization.get_full_location(self.cursor, location_id)
        self.assertEqual(location_data[0], location_id)
        self.assertEqual(location_data[1], self.name)
        self.assertEqual(location_data[2], self.address)
        self.assertEqual(location_data[3], self.region_name)
        self.assertEqual(location_data[4], self.province_name)

    def get_location_by_region(self):
        location_id = organization.new_location(
            self.cursor, self.name, self.address, self.region_id
        )
        location_data = organization.get_location_by_region(self.cursor, self.region_id)
        self.assertEqual(len(location_data), 1)
        self.assertEqual(location_data[0][0], location_id)
        self.assertEqual(location_data[0][1], self.name)


class test_organization_information(unittest.TestCase):
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
        self.province_id = organization.new_province(self.cursor, self.province_name)

        self.region_id = organization.new_region(
            self.cursor, self.region_name, self.province_id
        )

        self.location_id = organization.new_location(
            self.cursor, self.location_name, self.location_address, self.region_id
        )

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_organization_info(self):
        id = organization.new_organization_info(
            self.cursor, self.name, self.website, self.phone, self.location_id
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
            self.cursor, self.name, self.website, self.phone
        )
        self.assertTrue(validator.is_valid_uuid(id))

    def test_get_organization_info(self):
        id = organization.new_organization_info(
            self.cursor, self.name, self.website, self.phone, self.location_id
        )
        data = organization.get_organization_info(self.cursor, id)
        self.assertEqual(data[0], self.name)
        self.assertEqual(data[1], self.website)
        self.assertEqual(data[2], self.phone)
        self.assertEqual(data[3], self.location_id)

    def test_get_organization_info_not_found(self):

        with self.assertRaises(organization.OrganizationNotFoundError):
            organization.get_organization_info(self.cursor, str(uuid.uuid4()))

    def test_update_organization_info(self):

        new_name = "new-name"
        new_website = "www.new.com"
        new_phone = "987654321"
        id = organization.new_organization_info(
            self.cursor, self.name, self.website, self.phone, self.location_id
        )
        old_data = organization.get_organization_info(self.cursor, id)
        self.assertEqual(old_data[0], self.name)
        self.assertEqual(old_data[1], self.website)
        self.assertEqual(old_data[2], self.phone)
        self.assertEqual(old_data[3], self.location_id)
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
            "warranty",
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
            "warranty",
            None,
            None,
        )
        with self.assertRaises(organization.OrganizationNotFoundError):
            organization.get_organizations_info_json(self.cursor, label_id)


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
        self.province_id = organization.new_province(self.cursor, self.province_name)
        self.region_id = organization.new_region(
            self.cursor, self.region_name, self.province_id
        )
        self.location_id = organization.new_location(
            self.cursor, self.location_name, self.location_address, self.region_id
        )
        self.org_info_id = organization.new_organization_info(
            self.cursor, self.name, self.website, self.phone, self.location_id
        )

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_organization(self):
        organization_id = organization.new_organization(
            self.cursor, self.org_info_id, self.location_id
        )
        self.assertTrue(validator.is_valid_uuid(organization_id))

    def test_new_organization_no_location(self):
        organization_id = organization.new_organization(self.cursor, self.org_info_id)
        self.assertTrue(validator.is_valid_uuid(organization_id))

    def test_update_organization(self):
        organization_id = organization.new_organization(
            self.cursor, self.org_info_id, self.location_id
        )
        new_location_id = organization.new_location(
            self.cursor, "new-location", "new-address", self.region_id
        )
        organization.update_organization(
            self.cursor, organization_id, self.org_info_id, new_location_id
        )
        organization_data = organization.get_organization(self.cursor, organization_id)
        self.assertEqual(organization_data[0], self.org_info_id)
        self.assertEqual(organization_data[1], new_location_id)

    def test_get_organization(self):
        organization_id = organization.new_organization(
            self.cursor, self.org_info_id, self.location_id
        )
        organization_data = organization.get_organization(self.cursor, organization_id)
        self.assertEqual(organization_data[0], self.org_info_id)
        self.assertEqual(organization_data[1], self.location_id)

    def test_get_organization_not_found(self):
        with self.assertRaises(organization.OrganizationNotFoundError):
            organization.get_organization(self.cursor, str(uuid.uuid4()))

    def test_get_full_organization(self):
        organization_id = organization.new_organization(
            self.cursor, self.org_info_id, self.location_id
        )
        organization_data = organization.get_full_organization(
            self.cursor, organization_id
        )
        self.assertEqual(organization_data[0], organization_id)
        self.assertEqual(organization_data[1], self.name)
        self.assertEqual(organization_data[5], self.location_name)
        self.assertEqual(organization_data[8], self.region_name)
        self.assertEqual(organization_data[10], self.province_name)
