from uuid import UUID

from psycopg import Cursor
from psycopg.rows import dict_row, tuple_row
from psycopg.sql import SQL

from fertiscan.db.models import GuaranteedAnalysis


def create_guaranteed(
    cursor: Cursor,
    read_name: str | None = None,
    value: float | None = None,
    unit: str | None = None,
    language: str | None = None,
    element_id: int | None = None,
    label_id: str | UUID | None = None,
    edited: bool | None = False,
):
    """
    Inserts a new guaranteed record into the database.

    Args:
        cursor (Cursor): The database cursor used to execute the query.
        read_name (str | None): Name of the read (optional).
        value (float | None): Value associated with the record (optional).
        unit (str | None): Measurement unit (optional).
        language (str | None): Language identifier (optional).
        element_id (int | None): Foreign key referencing element_compound table (optional).
        label_id (str | UUID | None): Foreign key referencing label_information table (optional).
        edited (bool | None): Whether the record was edited (default is False).

    Returns:
        dict | None: The inserted guaranteed record as a dictionary, or None if insertion failed.
    """
    if all(v is None for v in (read_name, value, unit)):
        raise ValueError("At least one of read_name, value, or unit must be provided")

    query = SQL("""
        INSERT INTO guaranteed 
        (read_name, value, unit, language, element_id, label_id, edited)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(
            query, (read_name, value, unit, language, element_id, label_id, edited)
        )
        return new_cur.fetchone()


def read_guaranteed(cursor: Cursor, id: str | UUID):
    """
    Retrieves a guaranteed record by its ID.

    Args:
        cursor (Cursor): The database cursor used to execute the query.
        id (str | UUID): The UUID or string ID of the guaranteed record.

    Returns:
        dict | None: The guaranteed record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Guaranteed ID must be provided")

    query = SQL("SELECT * FROM guaranteed WHERE id = %s;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


def update_guaranteed(
    cursor: Cursor,
    id: str | UUID,
    read_name: str | None = None,
    value: float | None = None,
    unit: str | None = None,
    language: str | None = None,
    element_id: int | None = None,
    label_id: str | UUID | None = None,
    edited: bool | None = None,
):
    """
    Updates an existing guaranteed record by its ID.

    Args:
        cursor (Cursor): The database cursor used to execute the query.
        id (str | UUID): The UUID or string ID of the guaranteed record.
        read_name (str | None): Updated read name (optional).
        value (float | None): Updated value (optional).
        unit (str | None): Updated measurement unit (optional).
        language (str | None): Updated language identifier (optional).
        element_id (int | None): Updated element ID (optional).
        label_id (str | UUID | None): Updated label ID (optional).
        edited (bool | None): Updated edited flag (optional).

    Returns:
        dict | None: The updated guaranteed record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Guaranteed ID must be provided")

    if all(v is None for v in (read_name, value, unit)):
        raise ValueError("At least one of read_name, value, or unit must be provided")

    query = SQL("""
        UPDATE guaranteed
        SET read_name = COALESCE(%s, read_name),
            value = COALESCE(%s, value),
            unit = COALESCE(%s, unit),
            language = COALESCE(%s, language),
            element_id = COALESCE(%s, element_id),
            label_id = COALESCE(%s, label_id),
            edited = COALESCE(%s, edited)
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(
            query,
            (
                read_name,
                value,
                unit,
                language,
                element_id,
                label_id,
                edited,
                id,
            ),
        )
        return new_cur.fetchone()


def delete_guaranteed(cursor: Cursor, id: str | UUID):
    """
    Deletes a guaranteed record by its ID.

    Args:
        cursor (Cursor): The database cursor used to execute the query.
        id (str | UUID): The UUID or string ID of the guaranteed record.

    Returns:
        dict | None: The deleted guaranteed record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Guaranteed ID must be provided")

    query = SQL("""
        DELETE FROM guaranteed
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


def read_all_guaranteed(cursor: Cursor):
    """
    Retrieves all guaranteed records from the database.

    Args:
        cursor (Cursor): The database cursor used to execute the query.

    Returns:
        list[dict]: A list of all guaranteed records as dictionaries.
    """
    query = SQL("SELECT * FROM guaranteed;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query)
        return new_cur.fetchall()


def query_guaranteed(
    cursor: Cursor,
    read_name: str | None = None,
    value: float | None = None,
    unit: str | None = None,
    language: str | None = None,
    element_id: int | None = None,
    label_id: str | UUID | None = None,
    edited: bool | None = None,
) -> list[dict]:
    """
    Queries guaranteed records based on optional filter criteria.

    Args:
        cursor (Cursor): The database cursor used to execute the query.
        read_name (str | None): Filter by read name (optional).
        value (float | None): Filter by value (optional).
        unit (str | None): Filter by unit (optional).
        language (str | None): Filter by language (optional).
        element_id (int | None): Filter by element ID (optional).
        label_id (str | UUID | None): Filter by label ID (optional).
        edited (bool | None): Filter by edited flag (optional).

    Returns:
        list[dict]: A list of guaranteed records matching the criteria.
    """
    conditions = []
    parameters = []

    if read_name is not None:
        conditions.append("read_name = %s")
        parameters.append(read_name)
    if value is not None:
        conditions.append("value = %s")
        parameters.append(value)
    if unit is not None:
        conditions.append("unit = %s")
        parameters.append(unit)
    if language is not None:
        conditions.append("language = %s")
        parameters.append(language)
    if element_id is not None:
        conditions.append("element_id = %s")
        parameters.append(element_id)
    if label_id is not None:
        conditions.append("label_id = %s")
        parameters.append(label_id)
    if edited is not None:
        conditions.append("edited = %s")
        parameters.append(edited)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = SQL(f"SELECT * FROM guaranteed{where_clause};")

    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, parameters)
        return new_cur.fetchall()


def read_full_guaranteed(cursor: Cursor, id: str | UUID):
    """
    Retrieves full guaranteed details from the database using the guaranteed view.

    Args:
        cursor (Cursor): The database cursor used to execute the query.
        id (str | UUID): The UUID or string ID of the guaranteed record.

    Returns:
        dict | None: The guaranteed record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Guaranteed ID must be provided")

    query = SQL("SELECT * FROM full_guaranteed_view WHERE id = %s;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


def get_guaranteed_analysis_json(cursor: Cursor, label_id: str | UUID):
    """
    Retrieves the guaranteed analysis JSON for a specific label from the database.

    Args:
        cursor (Cursor): The database cursor used to execute the query.
        label_id (str | UUID): The UUID or string ID of the label.

    Returns:
        dict: The guaranteed analysis JSON as a dictionary. If no data is found,
        returns a default dictionary with keys "title", "is_minimal", "en", and "fr".
    """
    query = """
        SELECT get_guaranteed_analysis_json(%s);
    """
    cursor.row_factory = tuple_row
    cursor.execute(query, (label_id,))
    data = cursor.fetchone()[0]
    if data is None:
        data = {"title": None, "is_minimal": False, "en": [], "fr": []}
    return data


def update_guaranteed_analysis(
    cursor: Cursor, label_id: str | UUID, guaranteed_analysis: dict | GuaranteedAnalysis
):
    """
    Updates the guaranteed analysis for a specific label in the database.

    Args:
        cursor (Cursor): The database cursor used to execute the query.
        label_id (str | UUID): The UUID or string ID of the label.
        guaranteed_analysis (dict | GuaranteedAnalysis): The guaranteed analysis
        data, either as a dictionary or a GuaranteedAnalysis instance.

    Returns:
        None
    """
    if not isinstance(guaranteed_analysis, GuaranteedAnalysis):
        guaranteed_analysis = GuaranteedAnalysis.model_validate(guaranteed_analysis)

    cursor.row_factory = tuple_row
    cursor.execute(
        "SELECT update_guaranteed_analysis(%s, %s);",
        (label_id, guaranteed_analysis.model_dump_json()),
    )
