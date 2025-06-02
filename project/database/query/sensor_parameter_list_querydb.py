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

class SensorParameterListDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensorParameterListDB.id as id_param_value, sensorParameterListDB.sensor_id, sensorParameterListDB.name as name_param_list, sensorParameterListDB.parameter, sensorParameterListDB.value as value_param_list, sensorListDB.* FROM sensorParameterListDB join sensorListDB on sensorParameterListDB.sensor_id=sensorListDB.id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByGroupFull(group_id):
        connection = sql.connect(host, database, username, password)
        query = """SELECT sensorParameterListDB.id as id_param_value, sensorParameterListDB.sensor_id, sensorParameterListDB.name as name_param_list, 
                sensorParameterListDB.parameter, sensorParameterListDB.value as value_param_list, sensorListDB.* FROM sensorParameterListDB join sensorListDB on 
                sensorParameterListDB.sensor_id=sensorListDB.id where sensorListDB.group_id = %s"""
        value = (group_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectBySensorParameter(id,parameter):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorParameterListDB where sensor_id = %s and parameter=%s"
        value = (id,parameter)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectParameterListSensor(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensorListDB.sensor_id,sensorParameterListDB.parameter,sensorParameterListDB.value  FROM sensorParameterListDB JOIN sensorListDB ON sensorParameterListDB.sensor_id=sensorListDB.id WHERE sensorListDB.group_id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectBySensorList(groupId):
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensorListDB.sensor_id, sensorParameterListDB.value FROM sensorListDB JOIN sensorParameterListDB ON sensorListDB.id=sensorParameterListDB.sensor_id WHERE sensorListDB.group_id=%s"
        value = (groupId,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorParameterListDB where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(id, sensor_id, name, parameter,value):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO sensorParameterListDB (id, sensor_id, name, parameter, value) VALUES (%s, %s, %s, %s, %s)"
        value = (id, sensor_id,name,parameter,value)
        action = sql.execute(connection, query, value)
        return action

    def update(sensor_id,name,parameter,value,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorParameterListDB set sensor_id=%s, name=%s, parameter=%s, value=%s WHERE id=%s"
        value = (sensor_id,name,parameter,value,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM sensorParameterListDB WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action
    
