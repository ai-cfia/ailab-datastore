import uuid
from db.entities.tableEntity.tableEntity import TableEntity
from db.queries import queries

class User(TableEntity):
    user_id: uuid
    email: str
    
    def __init__(self, user_id: uuid, email:str):
        self.user_id = user_id
        self.email = email
         
    def update(self):
        """
        Updates the current user object with the user in the Database.
        If the user does not exist, it creates a new user with the current user's id and email.
        """ 
        con = queries.createConnection()
        cur = queries.createCursor(con)
        
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE id = %s);"
        cur = queries.queryParameterizedDB(con,cur,query,self.user_id)
        if queries.getOneResult(cur):
            query = "UPDATE users SET email = %s WHERE id = %s;"
            cur = queries.queryParameterizedDB(con,cur,query,(self.email,self.user_id))
        else:
            query = "INSERT INTO users (id, email) VALUES (%s, %s);"
            cur = queries.queryParameterizedDB(con,cur,query,(self.user_id,self.email))
        queries.endQuery(con,cur)
        