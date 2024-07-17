"""
This module represent the function for the table organization and its children tables: [location, region, province]

    
"""


class OrganizationCreationError(Exception):
    pass


class OrganizationNotFoundError(Exception):
    pass


class OrganizationUpdateError(Exception):
    pass


class LocationCreationError(Exception):
    pass


class LocationNotFoundError(Exception):
    pass


class RegionCreationError(Exception):
    pass


class RegionNotFoundError(Exception):
    pass


class ProvinceCreationError(Exception):
    pass


class ProvinceNotFoundError(Exception):
    pass


def new_organization(cursor, name, website, phone_number, location_id=None):
    """
    This function create a new organization in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - name (str): The name of the organization.
    - website (str): The website of the organization.
    - phone_number (str): The phone number of the organization.

    Returns:
    - str: The UUID of the organization
    """
    try:
        query = """
            INSERT INTO 
                organization (
                    name, 
                    website, 
                    phone_number,
                    main_location_id 
                    )
            VALUES 
                (%s, %s, %s, %s)
            RETURNING 
                id
            """
        cursor.execute(
            query,
            (
                name,
                website,
                phone_number,
                location_id,
            ),
        )
        return cursor.fetchone()[0]
    except Exception as e:
        raise OrganizationCreationError("Datastore organization unhandeled error" + e.__str__())


def update_organization(
    cursor, organization_id, name, website, phone_number, location_id
):
    """
    This function update a organization in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - organization_id (str): The UUID of the organization.
    - name (str): The name of the organization.
    - website (str): The website of the organization.
    - phone_number (str): The phone number of the organization.
    - location_id (str): The UUID of the location.

    Returns:
    - str: The UUID of the organization
    """
    try:
        query = """
            UPDATE 
                organization
            SET 
                name = COALESCE(%s,name), 
                website = COALESCE(%s,website),
                phone_number = COALESCE(%s,phone_number),
                main_location_id = COALESCE(%s,main_location_id)
            WHERE 
                id = %s
            """
        cursor.execute(
            query,
            (
                name,
                website,
                phone_number,
                location_id,
                organization_id,
            ),
        )
        return organization_id
    except Exception as e:
        raise OrganizationUpdateError("Datastore organization unhandeled error"+e.__str__())


def get_organization(cursor, organization_id):
    """
    This function get a organization from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - organization_id (str): The UUID of the organization.

    Returns:
    - dict: The organization
    """
    try:
        query = """
            SELECT 
                name, 
                website, 
                phone_number,
                main_location_id 
            FROM 
                organization
            WHERE 
                id = %s
            """
        cursor.execute(query, (organization_id,))
        res = cursor.fetchone()
        if res is None:
            raise OrganizationNotFoundError
        return res
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())


def get_full_organization(cursor, org_id):
    """
    This function get the full organization details from the database.
    This includes the location, region and province info of the organization.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - org_id (str): The UUID of the organization.

    Returns:
    - dict: The organization
    """
    try:
        query = """
            SELECT 
                organization.id, 
                organization.name, 
                organization.website, 
                organization.phone_number,
                location.id, 
                location.name,
                location.address,
                region.id,
                region.name,
                province.id,
                province.name
            FROM
                organization
            LEFT JOIN
                location
            ON
                organization.main_location_id = location.id
            LEFT JOIN
                region
            ON
                location.region_id = region.id
            LEFT JOIN
                province
            ON
                region.province_id = province.id
            WHERE 
                organization.id = %s
            """
        cursor.execute(query, (org_id,))
        return cursor.fetchone()
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())

def new_location(cursor, name, address, region_id, org_id=None):
    """
    This function create a new location in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - org_id (str): The UUID of the organization.
    - name (str): The name of the location.
    - address (str): The address of the location.
    - region_id (str): The UUID of the region.

    Returns:
    - str: The UUID of the location
    """
    try:
        query = """
            INSERT INTO 
                location (
                    name, 
                    address, 
                    region_id,
                    owner_id 
                    )
            VALUES 
                (%s, %s, %s, %s)
            RETURNING 
                id
            """
        cursor.execute(
            query,
            (
                name,
                address,
                region_id,
                org_id,
            ),
        )
        return cursor.fetchone()[0]
    except Exception as e:
        raise LocationCreationError("Datastore location unhandeled error"+e.__str__())


def get_location(cursor, location_id):
    """
    This function get a location from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - location_id (str): The UUID of the location.

    Returns:
    - dict: The location
    """
    try:
        query = """
            SELECT 
                name, 
                address, 
                region_id,
                owner_id 
            FROM 
                location
            WHERE 
                id = %s
            """
        cursor.execute(query, (location_id,))
        res = cursor.fetchone()
        if res is None:
            raise LocationNotFoundError
        return res
    except ValueError:
        raise LocationNotFoundError("location not found with location_id: " + location_id)
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())


def get_full_location(cursor, location_id):
    """
    This function get the full location details from the database.
    This includes the region and province info of the location.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - location_id (str): The UUID of the location.

    Returns:
    - dict: The location
    """
    try:
        query = """
            SELECT 
                location.id, 
                location.name,
                location.address,
                region.name,
                province.name
            FROM
                location
            LEFT JOIN
                region
            ON
                location.region_id = region.id
            LEFT JOIN
                province
            ON
                region.province_id = province.id
            WHERE 
                location.id = %s
            """
        cursor.execute(query, (location_id,))
        return cursor.fetchone()
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())


def get_location_by_region(cursor, region_id):
    """
    This function get a location from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - region_id (str): The UUID of the region.

    Returns:
    - dict: The location
    """
    try:
        query = """
            SELECT 
                id, 
                name, 
                address
            FROM 
                location
            WHERE 
                region_id = %s
            """
        cursor.execute(query, (region_id,))
        return cursor.fetchall()
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())


def get_location_by_organization(cursor, org_id):
    """
    This function get a location from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - org_id (str): The UUID of the organization.

    Returns:
    - dict: The location
    """
    try:
        query = """
            SELECT 
                id, 
                name, 
                address, 
                region_id 
            FROM 
                location
            WHERE 
                owner_id = %s
            """
        cursor.execute(query, (org_id,))
        return cursor.fetchall()
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())


def new_region(cursor, name, province_id):
    """
    This function create a new region in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - province_id (int): The id of the province.
    - name (str): The name of the region.

    Returns:
    - str: The UUID of the region
    """
    try:
        query = """
            INSERT INTO 
                region (
                    province_id, 
                    name 
                    )
            VALUES 
                (%s, %s)
            RETURNING 
                id
            """
        cursor.execute(
            query,
            (
                province_id,
                name,
            ),
        )
        return cursor.fetchone()[0]
    except Exception as e:
        raise RegionCreationError("Datastore region unhandeled error" + e.__str__())


def get_region(cursor, region_id):
    """
    This function get a region from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - region_id (str): The UUID of the region.

    Returns:
    - dict: The region
    """
    try:
        query = """
            SELECT 
                name,
                province_id
            FROM 
                region
            WHERE 
                id = %s
            """
        cursor.execute(query, (region_id,))
        res = cursor.fetchone()
        if res is None:
            raise RegionNotFoundError
        return res
    except ValueError:
        raise RegionNotFoundError("region not found with region_id: " + region_id)
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())


def get_full_region(cursor, region_id):
    """
    This function get the full region details from the database.
    This includes the province info of the region.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - region_id (str): The UUID of the region.

    Returns:
    - dict: The region
    """
    try:
        query = """
            SELECT 
                region.id, 
                region.name,
                province.name
            FROM
                region
            LEFT JOIN
                province
            ON
                region.province_id = province.id
            WHERE 
                region.id = %s
            """
        cursor.execute(query, (region_id,))
        return cursor.fetchone()
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())


def get_region_by_province(cursor, province_id):
    """
    This function get a region from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - province_id (str): The UUID of the province.

    Returns:
    - dict: The region
    """
    try:
        query = """
            SELECT 
                id, 
                province_id, 
                name 
            FROM 
                region
            WHERE 
                province_id = %s
            """
        cursor.execute(query, (province_id,))
        return cursor.fetchall()
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())


def new_province(cursor, name):
    """
    This function create a new province in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - name (str): The name of the province.

    Returns:
    - str: The UUID of the province
    """
    try:
        query = """
            INSERT INTO 
                province (
                    name 
                    )
            VALUES 
                (%s)
            RETURNING 
                id
            """
        cursor.execute(query, (name,))
        return cursor.fetchone()[0]
    except Exception as e:
        raise ProvinceCreationError("Datastore province unhandeled error" + e.__str__())


def get_province(cursor, province_id):
    """
    This function get a province from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - province_id (str): The UUID of the province.

    Returns:
    - dict: The province
    """
    try:
        query = """
            SELECT 
                name 
            FROM 
                province
            WHERE 
                id = %s
            """
        cursor.execute(query, (province_id,))
        res = cursor.fetchone()
        if res is None:
            raise ProvinceNotFoundError("province not found with province_id: " + province_id)
        return res
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())


def get_all_province(cursor):
    """
    This function get all province from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.

    Returns:
    - dict: The province
    """
    try:
        query = """
            SELECT 
                id, 
                name 
            FROM 
                province
            """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())
