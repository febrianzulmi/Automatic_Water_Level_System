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

class PowerMasterSensorDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM powerMasterSensorDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM powerMasterSensorDB WHERE id = %s"
        value = (id,)
        action = sql.selectWithInput(connection, query, value)
        return action

    def insert(id, name, sensorId, createdAt):
        connection = sql.connect(host, database, username, password)
        query = """INSERT INTO powerMasterSensorDB 
                    (id, name, sensorId, createdAt) 
                    VALUES (%s, %s, %s, %s)"""
        value = (id, name, sensorId, createdAt)
        action = sql.execute(connection, query, value)
        return action
    
    def update(id, name, sensorId, updatedAt):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE powerMasterSensorDB 
                   SET name=%s, sensorId=%s, updatedAt=%s 
                   WHERE id=%s"""
        value = (name, sensorId, updatedAt, id)
        action = sql.execute(connection, query, value) 
        return action
    
    def updateById(id, name, sensorId):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE powerMasterSensorDB 
                SET name=%s, sensorId=%s, updatedAt=NOW() 
                WHERE id=%s"""
        value = (name, sensorId, id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM powerMasterSensorDB WHERE id = %s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action
    