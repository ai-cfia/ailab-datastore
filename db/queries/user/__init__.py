import uuid

def is_user_registered(cursor,email: str) -> bool:
    query = """
        SELECT EXISTS(
            SELECT 
                1 
            FROM 
                users
            WHERE 
                email = %s
        )
            """
    cursor.execute(query, (email,))
    return cursor.fetchone() is not None

def get_user_id(cursor,email: str) -> str:
    query = """
        SELECT 
            id 
        FROM 
            users
        WHERE 
            email = %s
            """
    cursor.execute(query, (email,))
    return cursor.fetchone()[0]

def register_user(cursor, email:str)->None:
    query = """
        INSERT INTO 
            users(email)
        VALUES
            (%s)
            """
    cursor.execute(query, (email,))