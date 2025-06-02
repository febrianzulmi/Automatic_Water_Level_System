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

class SensorParameterGroupDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensorParameterGroupDB.id as id_param, sensorParameterGroupDB.group_id, sensorParameterGroupDB.name as name_param,sensorParameterGroupDB.parameter,sensorParameterGroupDB.value, sensorGroupDB.* FROM sensorParameterGroupDB join sensorGroupDB on sensorParameterGroupDB.group_id=sensorGroupDB.id ORDER BY sensorGroupDB.number ASC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByGroupFull(group_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensorParameterGroupDB.id as id_param, sensorParameterGroupDB.group_id, sensorParameterGroupDB.name as name_param,sensorParameterGroupDB.parameter,sensorParameterGroupDB.value, sensorGroupDB.* FROM sensorParameterGroupDB join sensorGroupDB on sensorParameterGroupDB.group_id=sensorGroupDB.id WHERE sensorParameterGroupDB.group_id=%s"
        value = (group_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectOne(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorParameterGroupDB where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByGroupParameter(id,parameter):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorParameterGroupDB where group_id = %s and parameter=%s"
        value = (id,parameter)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByGroupSensor(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensorParameterGroupDB.parameter, sensorParameterGroupDB.value FROM sensorParameterGroupDB JOIN sensorGroupDB ON sensorParameterGroupDB.group_id = sensorGroupDB.id WHERE sensorGroupDB.id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(id, group_id,name,parameter,value):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO sensorParameterGroupDB (id, group_id, name, parameter, value) VALUES (%s, %s, %s, %s, %s)"
        value = (id, group_id,name,parameter,value)
        action = sql.execute(connection, query, value)
        return action

    def update(group_id,name,parameter,value,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorParameterGroupDB set group_id=%s, name=%s, parameter=%s, value=%s WHERE id=%s"
        value = (group_id,name,parameter,value,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM sensorParameterGroupDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
