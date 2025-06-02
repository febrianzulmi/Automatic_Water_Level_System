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

class SensorPortConfigDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorPortConfigDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorPortConfigDB WHERE name = %s"
        value = (name,)
        action = sql.selectWithInput(connection, query, value)
        return action
    
    def selectByActivePort():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorPortConfigDB WHERE type !=0"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def updateById(type, modbus_id, digital_pin, id):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE sensorPortConfigDB 
                SET type=%s, modbus_id=%s, digital_pin=%s
                WHERE id=%s"""
        value = (type, modbus_id, digital_pin, id)
        action = sql.execute(connection, query, value)
        return action
    
    def checkModbusId(modbus_id, id):
        connection = sql.connect(host, database, username, password)
        query = """
            SELECT * 
            FROM sensorPortConfigDB 
            WHERE modbus_id = %s AND id != %s
        """
        value = (modbus_id, id)
        action = sql.selectWithInput(connection, query, value)
        return action

    def checkDigitalPin(digital_pin, id):
        connection = sql.connect(host, database, username, password)
        query = """
            SELECT * 
            FROM sensorPortConfigDB 
            WHERE digital_pin = %s AND id != %s
        """
        value = (digital_pin, id)
        action = sql.selectWithInput(connection, query, value)
        return action