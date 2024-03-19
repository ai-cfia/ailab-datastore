import uuid
from entities.tableEntity.tableEntity import TableEntity
from queries import queries

class Index(TableEntity):
    index_id: uuid
    index: dict
    owner_id: uuid
    
    seed_id: uuid
    nbImages: int
    
    def __init__(self, index_id: uuid, index: dict, owner_id: uuid):
        self.index_id = index_id
        self.index = index
        self.owner_id = owner_id
        
    def update(self):
        con = queries.createConnection()
        cur = queries.createCursor(con)
        
        query = "SELECT EXISTS(SELECT 1 FROM indexes WHERE id = %s);"
        cur = queries.queryParameterizedDB(con,cur,query,self.index_id)
        if queries.getOneResult(cur):
            query = "UPDATE indexes SET index = %s WHERE id = %s;"
            cur = queries.queryParameterizedDB(con,cur,query,(self.index,self.index_id))
        else:
            query = "INSERT INTO indexes (id, index, ownerID) VALUES (%s, %s, %s);"
            cur = queries.queryParameterizedDB(con,cur,query,(self.index_id,self.index,self.owner_id))
        queries.endQuery(con,cur)
        
