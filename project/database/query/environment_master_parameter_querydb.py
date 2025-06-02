import json
import sys

sys.path.append('/home/connex/library')
from SynapsisLibrary import sql


def openDB():
    with open('/home/connex/project/database/dbNearonProject.json', 'r') as f:
        db = json.load(f)
        host = db['host']
        database = db['database']
        username = db['username']
        password = db['password']
    f.close()
    return host, database, username, password

host, database, username, password = openDB()

class EnvironmentMasterParameterDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentMasterParameterDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentMasterParameterDB WHERE id = %s"
        value = (id,)
        action = sql.selectWithInput(connection, query, value)
        return action

    def insert(id, name, parameterCode, createdAt):
        connection = sql.connect(host, database, username, password)
        query = """INSERT INTO environmentMasterParameterDB 
                    (id, name, parameterCode, createdAt) 
                    VALUES (%s, %s, %s, %s)"""
        value = (id, name, parameterCode, createdAt)
        action = sql.execute(connection, query, value)
        return action
    
    def update(id, name, parameterCode, updatedAt):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE environmentMasterParameterDB 
                   SET name=%s, parameterCode=%s, updatedAt=%s 
                   WHERE id=%s"""
        value = (name, parameterCode, updatedAt, id)
        action = sql.execute(connection, query, value) 
        return action
    
    def updateById(id, name, parameterCode):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE environmentMasterParameterDB 
                SET name=%s, parameterCode=%s, updatedAt=NOW() 
                WHERE id=%s"""
        value = (name, parameterCode, id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM environmentMasterParameterDB WHERE id = %s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action
