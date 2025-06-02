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


class PowerDeviceDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM powerDeviceDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectByNumberOrderd():
        connection = sql.connect(host, database, username, password)
        query = "SELECT id, number, name, ip, state FROM powerDeviceDB ORDER BY number ASC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM powerDeviceDB WHERE name = %s"
        value = (name,)
        action = sql.selectWithInput(connection, query, value)
        return action
    
    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM powerDeviceDB WHERE id = %s"
        value = (id,)
        action = sql.selectWithInput(connection, query, value)
        return action

    
    def checkNumber(number):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM powerDeviceDB WHERE number = %s"
        value = (number,)
        action = sql.selectWithInput(connection, query, value)
        return action
    
    def checkName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM powerDeviceDB WHERE name = %s"
        value = (name,)
        action = sql.selectWithInput(connection, query, value)
        return action
    
    def checkIp(ip):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM powerDeviceDB WHERE ip = %s"
        value = (ip,)
        action = sql.selectWithInput(connection, query, value)
        return action


    def insert(number, id, name, ip, connectionStatus, state, createdAt):
        connection = sql.connect(host, database, username, password)
        query = """INSERT INTO powerDeviceDB 
                    (id, number, name, ip, connection, state, createdAt) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        value = (id, number, name, ip, connectionStatus, state, createdAt)
        action = sql.execute(connection, query, value)
        return action
    

    def update(id, number, name, ip, connectionStatus, state, updatedAt):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE powerDeviceDB 
                   SET number=%s, name=%s, ip=%s, connection=%s, state=%s, updatedAt=%s 
                   WHERE id=%s"""
        value = (number, name, ip, connectionStatus, state, updatedAt, id)
        action = sql.execute(connection, query, value)
        return action
    
    def updateById(number, id, name, ip, state):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE powerDeviceDB 
                SET number=%s, name=%s, ip=%s, state=%s, updatedAt=NOW() 
                WHERE id=%s"""
        value = (number, name, ip, state, id)
        action = sql.execute(connection, query, value)
        return action


    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM powerDeviceDB WHERE id = %s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action