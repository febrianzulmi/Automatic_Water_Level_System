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

class SensorGroupDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorGroupDB ORDER BY number ASC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectGroupOrderedByNumber():
        connection = sql.connect(host, database, username, password)
        query = "SELECT id, oid, number, name FROM sensorGroupDB ORDER BY number ASC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectOne(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorGroupDB where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectOneOid(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT oid FROM sensorGroupDB where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectIsOid(oid):
        connection = sql.connect(host, database, username, password)
        query = "SELECT id FROM sensorGroupDB where oid = %s"
        value = (oid,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectOneByState(id, state):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorGroupDB where id = %s and  state = %s"
        value = (id, state)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorGroupDB where name = %s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectIsNumber(number):
        connection = sql.connect(host, database, username, password)
        query = "SELECT id FROM sensorGroupDB where number = %s"
        value = (number,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByState(state):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorGroupDB where state = %s ORDER BY number ASC"
        value = (state,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(id, number, oid, name, intervals, unit, frekuensi, service_id, enterAlarm, exitAlarm, errorAlarm):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO sensorGroupDB (id, number, oid, name, intervals, unit, frekuensi, service_id, enterAlarm, exitAlarm, errorAlarm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        value = (id, number, oid, name, intervals, unit, frekuensi, service_id, enterAlarm, exitAlarm, errorAlarm)
        action = sql.execute(connection, query, value)
        return action

    def update(number, oid, name, interval, unit, frekuensi, service_id, id, enterAlarm, exitAlarm, errorAlarm, stateSensor):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorGroupDB set number=%s, oid=%s, name=%s, intervals=%s, unit=%s, frekuensi=%s, service_id=%s, enterAlarm=%s, exitAlarm=%s, errorAlarm=%s , state=%s WHERE id=%s"
        value = (number, oid, name, interval, unit, frekuensi, service_id, enterAlarm, exitAlarm, errorAlarm, stateSensor,id)
        action = sql.execute(connection, query, value)
        return action
    
    def updateService(service_id, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorGroupDB set service_id=%s WHERE id=%s"
        value = (service_id, id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM sensorGroupDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
