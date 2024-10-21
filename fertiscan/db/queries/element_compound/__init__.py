from psycopg import Cursor
from psycopg.rows import dict_row
from psycopg.sql import SQL


def create_element_compound(
    cursor: Cursor, number: int, name_fr: str, name_en: str, symbol: str
):
    """
    Inserts a new element_compound record into the database.

    Args:
        cursor: Database cursor object.
        number: Atomic number of the element/compound.
        name_fr: French name of the element/compound.
        name_en: English name of the element/compound.
        symbol: Symbol of the element/compound.

    Returns:
        The inserted element_compound record as a dictionary, or None if failed.
    """
    if any(value is None for value in [number, name_fr, name_en, symbol]):
        raise ValueError("All fields must be provided and cannot be None.")

    query = SQL("""
        INSERT INTO element_compound (number, name_fr, name_en, symbol)
        VALUES (%s, %s, %s, %s)
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (number, name_fr, name_en, symbol))
        return new_cur.fetchone()


def read_element_compound(cursor: Cursor, id: int):
    """
    Retrieves an element_compound record by ID.

    Args:
        cursor: Database cursor object.
        id: ID of the element_compound.

    Returns:
        The element_compound record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Element_compound ID must be provided.")

    query = SQL("SELECT * FROM element_compound WHERE id = %s;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


def read_all_element_compounds(cursor: Cursor):
    """
    Retrieves all element_compound records from the database.

    Args:
        cursor: Database cursor object.

    Returns:
        A list of all element_compound records as dictionaries.
    """
    query = SQL("SELECT * FROM element_compound;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query)
        return new_cur.fetchall()


def update_element_compound(
    cursor: Cursor, id: int, number: int, name_fr: str, name_en: str, symbol: str
):
    """
    Updates an existing element_compound record by ID.

    Args:
        cursor: Database cursor object.
        id: ID of the element_compound.
        number: New atomic number of the element/compound.
        name_fr: New French name of the element/compound.
        name_en: New English name of the element/compound.
        symbol: New symbol of the element/compound.

    Returns:
        The updated element_compound record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Element_compound ID must be provided.")

    if any(value is None for value in [number, name_fr, name_en, symbol]):
        raise ValueError("All fields must be provided and cannot be None.")

    query = SQL("""
        UPDATE element_compound
        SET number = %s, name_fr = %s, name_en = %s, symbol = %s
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (number, name_fr, name_en, symbol, id))
        return new_cur.fetchone()


def delete_element_compound(cursor: Cursor, id: int):
    """
    Deletes an element_compound record by ID.

    Args:
        cursor: Database cursor object.
        id: ID of the element_compound.

    Returns:
        The deleted element_compound record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Element_compound ID must be provided.")

    query = SQL("""
        DELETE FROM element_compound
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


def query_element_compounds(
    cursor: Cursor,
    number: int | None = None,
    name_fr: str | None = None,
    name_en: str | None = None,
    symbol: str | None = None,
):
    """
    Queries element_compounds based on optional filter criteria.

    Args:
        cursor: Database cursor object.
        number: Optional atomic number to filter element_compounds.
        name_fr: Optional French name to filter element_compounds.
        name_en: Optional English name to filter element_compounds.
        symbol: Optional symbol to filter element_compounds.

    Returns:
        A list of element_compound records matching the filter criteria as dictionaries.
    """
    conditions = []
    parameters = []

    if number is not None:
        conditions.append("number = %s")
        parameters.append(number)

    if name_fr is not None:
        conditions.append("name_fr = %s")
        parameters.append(name_fr)

    if name_en is not None:
        conditions.append("name_en = %s")
        parameters.append(name_en)

    if symbol is not None:
        conditions.append("symbol = %s")
        parameters.append(symbol)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = SQL(f"SELECT * FROM element_compound{where_clause};")

    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, parameters)
        return new_cur.fetchall()
