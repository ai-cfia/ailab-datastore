"""
This is a test script for the database packages.
It tests the functions in the organization module.
"""

import os
import unittest
import uuid

import datastore.db as db
from datastore.db.metadata import validator
from fertiscan.db.models import Location, OrganizationInformation, Province, Region
from fertiscan.db.queries import organization
from fertiscan.db.queries.location import create_location
from fertiscan.db.queries.organization_information import (
    create_organization_information,
)
from fertiscan.db.queries.province import create_province
from fertiscan.db.queries.region import create_region

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


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
        self.org_info = create_organization_information(
            self.cursor, self.name, self.website, self.phone, self.location.id
        )
        self.org_info = OrganizationInformation.model_validate(self.org_info)

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_organization(self):
        organization_id = organization.new_organization(
            self.cursor, self.org_info.id, self.location.id
        )
        self.assertTrue(validator.is_valid_uuid(organization_id))

    def test_new_organization_no_location(self):
        organization_id = organization.new_organization(self.cursor, self.org_info.id)
        self.assertTrue(validator.is_valid_uuid(organization_id))

    def test_update_organization(self):
        organization_id = organization.new_organization(
            self.cursor, self.org_info.id, self.location.id
        )
        new_location = create_location(
            self.cursor, "new-location", "new-address", self.region.id
        )
        new_location = Location.model_validate(new_location)
        organization.update_organization(
            self.cursor, organization_id, self.org_info.id, new_location.id
        )
        organization_data = organization.get_organization(self.cursor, organization_id)
        self.assertEqual(organization_data[0], self.org_info.id)
        self.assertEqual(organization_data[1], new_location.id)

    def test_get_organization(self):
        organization_id = organization.new_organization(
            self.cursor, self.org_info.id, self.location.id
        )
        organization_data = organization.get_organization(self.cursor, organization_id)
        self.assertEqual(organization_data[0], self.org_info.id)
        self.assertEqual(organization_data[1], self.location.id)

    def test_get_organization_not_found(self):
        with self.assertRaises(organization.OrganizationNotFoundError):
            organization.get_organization(self.cursor, str(uuid.uuid4()))

    def test_get_full_organization(self):
        organization_id = organization.new_organization(
            self.cursor, self.org_info.id, self.location.id
        )
        organization_data = organization.get_full_organization(
            self.cursor, organization_id
        )
        self.assertEqual(organization_data[0], organization_id)
        self.assertEqual(organization_data[1], self.name)
        self.assertEqual(organization_data[5], self.location_name)
        self.assertEqual(organization_data[8], self.region_name)
        self.assertEqual(organization_data[10], self.province_name)
