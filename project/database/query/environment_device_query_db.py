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

class EnvironmentDeviceDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentDeviceDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectByNumberOrderd():
        connection = sql.connect(host, database, username, password)
        query = "SELECT id, number, name, method, ip, modbus_id, state FROM environmentDeviceDB ORDER BY number ASC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentDeviceDB WHERE name = %s"
        value = (name,)
        action = sql.selectWithInput(connection, query, value)
        return action
    
    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentDeviceDB WHERE id = %s"
        value = (id,)
        action = sql.selectWithInput(connection, query, value)
        return action

    
    def checkNumber(number):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentDeviceDB WHERE number = %s"
        value = (number,)
        action = sql.selectWithInput(connection, query, value)
        return action
    
    def checkName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentDeviceDB WHERE name = %s"
        value = (name,)
        action = sql.selectWithInput(connection, query, value)
        return action
    
    def checkIp(ip):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentDeviceDB WHERE ip = %s"
        value = (ip,)
        action = sql.selectWithInput(connection, query, value)
        return action
    
    def checkModbusId(modbus_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentDeviceDB WHERE modbus_id = %s"
        value = (modbus_id,)
        action = sql.selectWithInput(connection, query, value)
        return action
    
    def checkPort(number, port):
        column_name = f"port{port}"
        connection = sql.connect(host, database, username, password)
        query =  f"SELECT {column_name} FROM environmentDeviceDB WHERE number = %s AND {column_name}"
        value = (number,)
        action = sql.selectWithInput(connection, query, value)
        return action


    def insertNetwork(number, id, name, ip, method, state, createdAt, ports):
        connection = sql.connect(host, database, username, password)
        query = """INSERT INTO environmentDeviceDB 
                    (id, number, name, ip, method, state, createdAt, port1, port2, port3, port4, port5, port6, port7, port8) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        value = (id, number, name, ip, method, state, createdAt, ports[0], ports[1], ports[2], ports[3], ports[4], ports[5], ports[6], ports[7])
        action = sql.execute(connection, query, value)
        return action
    
    def insertModbus(number, id, name, modbus_id, method, state, createdAt, ports):
        connection = sql.connect(host, database, username, password)
        query = """INSERT INTO environmentDeviceDB 
                    (id, number, name, modbus_id, method, state, createdAt, port1, port2, port3, port4, port5, port6, port7, port8) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        value = (id, number, name, modbus_id, method, state, createdAt, ports[0], ports[1], ports[2], ports[3], ports[4], ports[5], ports[6], ports[7])
        action = sql.execute(connection, query, value)
        return action
    

    def update(id, number, name, ip, connectionStatus, state, updatedAt):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE environmentDeviceDB 
                   SET number=%s, name=%s, ip=%s, connection=%s, state=%s, updatedAt=%s 
                   WHERE id=%s"""
        value = (number, name, ip, connectionStatus, state, updatedAt, id)
        action = sql.execute(connection, query, value)
        return action
    
    def updateNetworkById(number, id, name, ip, method, state, ports):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE environmentDeviceDB 
                SET number=%s, name=%s, ip=%s, modbus_id= "0", method=%s, state=%s, port1=%s, port2=%s, port3=%s, port4=%s, port5=%s, port6=%s, port7=%s, port8=%s, updatedAt=NOW() 
                WHERE id=%s"""
        value = (number, name, ip, method, state, ports[0], ports[1], ports[2], ports[3], ports[4], ports[5], ports[6], ports[7], id)
        action = sql.execute(connection, query, value)
        return action
    

    def updateModbusById(number, id, name, modbus_id, method, state, ports):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE environmentDeviceDB 
                SET number=%s, name=%s,  ip="0", modbus_id=%s, method=%s, state=%s, port1=%s, port2=%s, port3=%s, port4=%s, port5=%s, port6=%s, port7=%s, port8=%s, updatedAt=NOW() 
                WHERE id=%s"""
        value = (number, name, modbus_id, method, state, ports[0], ports[1], ports[2], ports[3], ports[4], ports[5], ports[6], ports[7], id)
        action = sql.execute(connection, query, value)
        return action


    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM environmentDeviceDB WHERE id = %s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action
    
    