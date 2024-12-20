"""
This module represent the function for the table organization and its children tables: [location, region, province]
"""

from psycopg import Cursor

from fertiscan.db.queries.errors import (
    LocationCreationError,
    LocationNotFoundError,
    LocationRetrievalError,
    OrganizationCreationError,
    OrganizationInformationCreationError,
    OrganizationInformationNotFoundError,
    OrganizationInformationRetrievalError,
    OrganizationInformationUpdateError,
    OrganizationNotFoundError,
    OrganizationRetrievalError,
    OrganizationUpdateError,
    ProvinceCreationError,
    ProvinceNotFoundError,
    ProvinceRetrievalError,
    RegionCreationError,
    RegionNotFoundError,
    RegionRetrievalError,
    handle_query_errors,
)


@handle_query_errors(OrganizationInformationCreationError)
def new_organization(cursor: Cursor, information_id, location_id=None):
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
    if location_id is None:
        query = """
            SELECT 
                location_id
            FROM
                organization_information
            WHERE
                id = %s
            """
        cursor.execute(query, (information_id,))
        location_id = cursor.fetchone()[0]
    query = """
        INSERT INTO 
            organization (
                information_id,
                main_location_id 
                )
        VALUES 
            (%s, %s)
        RETURNING 
            id
        """
    cursor.execute(query, (information_id, location_id))
    if result := cursor.fetchone():
        return result[0]
    raise OrganizationCreationError("Failed to create Organization. No data returned.")


@handle_query_errors(OrganizationInformationCreationError)
def new_organization_info_located(
    cursor: Cursor, address: str, name: str, website: str, phone_number: str
):
    """
    This function create a new organization information in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - name (str): The name of the organization.
    - website (str): The website of the organization.
    - phone_number (str): The phone number of the organization.

    Returns:
    - str: The UUID of the organization information
    """
    query = """
        SELECT new_organization_info_located(%s, %s, %s, %s);
        """
    cursor.execute(
        query,
        (
            name,
            address,
            website,
            phone_number,
        ),
    )
    if result := cursor.fetchone():
        return result[0]
    raise OrganizationCreationError("Failed to create Organization. No data returned.")


@handle_query_errors(OrganizationInformationCreationError)
def new_organization_info(
    cursor: Cursor, name, website, phone_number, location_id=None
):
    """
    This function create a new organization information in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - name (str): The name of the organization.
    - website (str): The website of the organization.
    - phone_number (str): The phone number of the organization.

    Returns:
    - str: The UUID of the organization information
    """
    query = """
        INSERT INTO 
            organization_information (
                name, 
                website, 
                phone_number,
                location_id
                )
        VALUES 
            (%s, %s, %s, %s)
        RETURNING 
            id
        """
    cursor.execute(
        query,
        (name, website, phone_number, location_id),
    )
    if result := cursor.fetchone():
        return result[0]
    raise OrganizationCreationError("Failed to create Organization. No data returned.")


@handle_query_errors(OrganizationInformationRetrievalError)
def get_organization_info(cursor: Cursor, information_id):
    """
    This function get a organization information from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - information_id (str): The UUID of the organization information.

    Returns:
    - dict: The organization information
    """
    query = """
        SELECT 
            name, 
            website, 
            phone_number,
            location_id
        FROM 
            organization_information
        WHERE 
            id = %s
        """
    cursor.execute(query, (information_id,))
    if result := cursor.fetchone():
        return result
    raise OrganizationInformationNotFoundError(
        "Organization information not found with information_id: " + information_id
    )


@handle_query_errors(OrganizationInformationRetrievalError)
def get_organizations_info_json(cursor: Cursor, label_id) -> dict:
    """
    This function get a organization information from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - information_id (str): The UUID of the organization information.

    Returns:
    - dict: The organization information
    """
    query = """
        SELECT get_organizations_information_json(%s);
        """
    cursor.execute(query, (str(label_id),))

    res = cursor.fetchone()
    if res is None or res[0] is None:
        # raise OrganizationNotFoundError
        # There might not be any organization information
        return {}
    if len(res[0]) == 2:
        return {**res[0][0], **res[0][1]}
    elif len(res[0]) == 1:
        return res[0][0]
    else:
        return {}


@handle_query_errors(OrganizationUpdateError)
def update_organization(cursor: Cursor, organization_id, information_id, location_id):
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
    query = """
        UPDATE 
            organization
        SET 
            information_id = COALESCE(%s,information_id),
            main_location_id = COALESCE(%s,main_location_id)
        WHERE 
            id = %s
        """
    cursor.execute(
        query,
        (
            information_id,
            location_id,
            organization_id,
        ),
    )
    return organization_id


@handle_query_errors(OrganizationInformationUpdateError)
def update_organization_info(
    cursor: Cursor, information_id, name, website, phone_number
):
    """
    This function update a organization information in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - information_id (str): The UUID of the organization information.
    - name (str): The name of the organization.
    - website (str): The website of the organization.
    - phone_number (str): The phone number of the organization.

    Returns:
    - str: The UUID of the organization information
    """
    query = """
        UPDATE 
            organization_information
        SET 
            name = COALESCE(%s,name),
            website = COALESCE(%s,website),
            phone_number = COALESCE(%s,phone_number)
        WHERE 
            id = %s
        """
    cursor.execute(
        query,
        (
            name,
            website,
            phone_number,
            information_id,
        ),
    )
    return information_id


@handle_query_errors(OrganizationRetrievalError)
def get_organization(cursor: Cursor, organization_id):
    """
    This function get a organization from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - organization_id (str): The UUID of the organization.

    Returns:
    - dict: The organization
    """
    query = """
        SELECT 
            information_id,
            main_location_id 
        FROM 
            organization
        WHERE 
            id = %s
        """
    cursor.execute(query, (organization_id,))
    if result := cursor.fetchone():
        return result
    raise OrganizationNotFoundError(
        "Organization not found with organization_id: " + organization_id
    )


@handle_query_errors(OrganizationRetrievalError)
def get_full_organization(cursor: Cursor, org_id):
    """
    This function get the full organization details from the database.
    This includes the location, region and province info of the organization.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - org_id (str): The UUID of the organization.

    Returns:
    - dict: The organization
    """
    query = """
        SELECT 
            organization.id, 
            information.name, 
            information.website, 
            information.phone_number,
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
            organization_information as information
        ON
            organization.information_id = information.id
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


@handle_query_errors(LocationCreationError)
def new_location(cursor: Cursor, name, address, region_id, org_id=None):
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
    if result := cursor.fetchone():
        return result[0]
    raise LocationCreationError("Failed to create Location. No data returned.")


@handle_query_errors(LocationRetrievalError)
def get_location(cursor: Cursor, location_id):
    """
    This function get a location from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - location_id (str): The UUID of the location.

    Returns:
    - dict: The location
    """
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
    if result := cursor.fetchone():
        return result
    raise LocationNotFoundError("Location not found with location_id: " + location_id)


@handle_query_errors(LocationRetrievalError)
def get_full_location(cursor: Cursor, location_id):
    """
    This function get the full location details from the database.
    This includes the region and province info of the location.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - location_id (str): The UUID of the location.

    Returns:
    - dict: The location
    """
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


@handle_query_errors(LocationRetrievalError)
def get_location_by_region(cursor: Cursor, region_id):
    """
    This function get a location from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - region_id (str): The UUID of the region.

    Returns:
    - dict: The location
    """
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


@handle_query_errors(LocationRetrievalError)
def get_location_by_organization(cursor: Cursor, org_id):
    """
    This function get a location from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - org_id (str): The UUID of the organization.

    Returns:
    - dict: The location
    """
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


@handle_query_errors(RegionCreationError)
def new_region(cursor: Cursor, name, province_id):
    """
    This function create a new region in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - province_id (int): The id of the province.
    - name (str): The name of the region.

    Returns:
    - str: The UUID of the region
    """
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
    if result := cursor.fetchone():
        return result[0]
    raise RegionCreationError("Failed to create Region. No data returned.")


@handle_query_errors(RegionRetrievalError)
def get_region(cursor: Cursor, region_id):
    """
    This function get a region from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - region_id (int): The id of the region.

    Returns:
    - dict: The region
    """
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
    if result := cursor.fetchone():
        return result
    raise RegionNotFoundError("region not found with region_id: " + str(region_id))


@handle_query_errors(RegionRetrievalError)
def get_full_region(cursor: Cursor, region_id):
    """
    This function get the full region details from the database.
    This includes the province info of the region.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - region_id (str): The UUID of the region.

    Returns:
    - dict: The region
    """
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


@handle_query_errors(RegionRetrievalError)
def get_region_by_province(cursor: Cursor, province_id):
    """
    This function get a region from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - province_id (str): The UUID of the province.

    Returns:
    - dict: The region
    """
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


@handle_query_errors(ProvinceCreationError)
def new_province(cursor: Cursor, name):
    """
    This function create a new province in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - name (str): The name of the province.

    Returns:
    - str: The UUID of the province
    """
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
    if result := cursor.fetchone():
        return result[0]
    raise ProvinceCreationError("Failed to create Province. No data returned.")


@handle_query_errors(ProvinceRetrievalError)
def get_province(cursor: Cursor, province_id):
    """
    This function get a province from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - province_id (int): The UUID of the province.

    Returns:
    - dict: The province
    """
    query = """
        SELECT 
            name 
        FROM 
            province
        WHERE 
            id = %s
        """
    cursor.execute(query, (province_id,))
    if result := cursor.fetchone():
        return result
    raise ProvinceNotFoundError(
        "province not found with province_id: " + str(province_id)
    )


@handle_query_errors(ProvinceRetrievalError)
def get_all_province(cursor: Cursor):
    """
    This function get all province from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.

    Returns:
    - dict: The province
    """
    query = """
        SELECT 
            id, 
            name 
        FROM 
            province
        """
    cursor.execute(query)
    return cursor.fetchall()
