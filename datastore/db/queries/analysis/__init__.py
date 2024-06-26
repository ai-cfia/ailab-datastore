"""
This file contains the queries for the analysis table.
"""

def new_analysis(cursor, analysis_dict):
    """
    This function creates a new analysis in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - analysis_dict (dict): The dictionary containing the analysis information.

    Returns:
    - The id of the new analysis.
    """
    try:
        query = """
            INSERT INTO 
                analysis(
                    data
                    )
            VALUES 
                (%s)
            RETURNING id
            """
        cursor.execute(query, (analysis_dict,))
        return cursor.fetchone()[0]
    except Exception as e:
        print(e)
        raise Exception("Error: analysis could not be created")