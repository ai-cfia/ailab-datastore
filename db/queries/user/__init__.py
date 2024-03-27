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
    res =cursor.fetchone()[0]
    return res

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
    res = cursor.fetchone()[0]
    return res

def register_user(cursor, email:str)->None:
    #TODO : remove ID creation from here
    user_id = uuid.uuid4()
    query = """
        INSERT INTO 
            users(id,email)
        VALUES
            (%s,%s)
            """
    cursor.execute(query, (user_id,email,))