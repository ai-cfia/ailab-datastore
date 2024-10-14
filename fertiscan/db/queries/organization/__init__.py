"""
This module represent the function for the table organization and its children tables: [location, region, province]


"""


class OrganizationCreationError(Exception):
    pass


class OrganizationNotFoundError(Exception):
    pass


class OrganizationUpdateError(Exception):
    pass


def new_organization(cursor, information_id, location_id=None):
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
        cursor.execute(
            query,
            (
                information_id,
                location_id,
            ),
        )
        return cursor.fetchone()[0]
    except Exception as e:
        raise OrganizationCreationError(
            "Datastore organization unhandeled error" + e.__str__()
        )


def new_organization_info_located(
    cursor, address: str, name: str, website: str, phone_number: str
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
    try:
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
        return cursor.fetchone()[0]
    except Exception as e:
        raise OrganizationCreationError(
            "Datastore organization unhandeled error: " + e.__str__()
        )


def new_organization_info(cursor, name, website, phone_number, location_id=None):
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
    try:
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
        return cursor.fetchone()[0]
    except Exception as e:
        raise OrganizationCreationError(
            "Datastore organization unhandeled error" + e.__str__()
        )


def get_organization_info(cursor, information_id):
    """
    This function get a organization information from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - information_id (str): The UUID of the organization information.

    Returns:
    - dict: The organization information
    """
    try:
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
        res = cursor.fetchone()
        if res is None:
            raise OrganizationNotFoundError
        return res
    except OrganizationNotFoundError:
        raise OrganizationNotFoundError(
            f"organization information not found with information_id: {information_id}"
        )
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())


def get_organizations_info_json(cursor, label_id) -> dict:
    """
    This function get a organization information from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - information_id (str): The UUID of the organization information.

    Returns:
    - dict: The organization information
    """
    try:
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
    except OrganizationNotFoundError:
        raise OrganizationNotFoundError(
            "organization information not found for the label_info_id " + str(label_id)
        )
    except Exception as e:
        raise Exception("Datastore organization unhandeled error: " + e.__str__())


def update_organization(cursor, organization_id, information_id, location_id):
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
    except Exception as e:
        raise OrganizationUpdateError(
            "Datastore organization unhandeled error" + e.__str__()
        )


def update_organization_info(cursor, information_id, name, website, phone_number):
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
    try:
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
    except Exception as e:
        raise OrganizationUpdateError(
            "Datastore organization unhandeled error" + e.__str__()
        )


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
                information_id,
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
    except OrganizationNotFoundError:
        raise OrganizationNotFoundError(
            "organization not found with organization_id: " + organization_id
        )
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
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())
