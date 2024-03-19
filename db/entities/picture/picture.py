import uuid
from datetime import date
from db.entities.tableEntity.tableEntity import TableEntity
from db.queries import queries

class Picture(TableEntity):
    picture_id: uuid
    picture: dict
    index_id: uuid
    owner_id: uuid
    
    nbSeed: int
    zoom: float
    
    uploadDate: date
    parent: bool
    source: str
    format: str
    height: int
    width: int
    
    def __init__(self, picture_id: uuid, picture: dict, index_id: uuid):
        self.picture_id = picture_id
        self.picture = picture
        self.index_id = index_id
        
    def update(self):
        con = queries.createConnection()
        cur = queries.createCursor(con)
        
        query = "SELECT EXISTS(SELECT 1 FROM pictures WHERE id = %s);"
        cur = queries.queryParameterizedDB(con,cur,query,self.index_id)
        if queries.getOneResult(cur):
            query = "UPDATE pictures SET pictures = %s WHERE id = %s;"
            cur = queries.queryParameterizedDB(con,cur,query,())
        else:
            query = "INSERT INTO pictures (id,picture, indexID) VALUES (%s,%s, %s);"
            cur = queries.queryParameterizedDB(con,cur,query,(self.index_id,self.index,self.owner_id))
        queries.endQuery(con,cur)