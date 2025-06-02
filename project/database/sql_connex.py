import mysql.connector
import json
import sys

sys.path.append('/home/connex/library')
from SynapsisLibrary import *


def openDB():
    with open('/home/connex/project/database/dbNearonProject.json', 'r') as f:
        db = json.load(f)
        host = db['host']
        database = 'synapsis_control'
        username = db['username']
        password = db['password']
    f.close()
    return host, database, username, password

host, database, username, password = openDB()

class mydb():
    global host, database, username, password

    def mysql_connect():
        connect = sql.connect(host, database, username, password)
        return connect

    def mysql_cursor(mysql_connect):
        return sql.cursor(mysql_connect)

class info():
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT value FROM info where name=%s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
        
    def updateByName(name,value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE info set value=%s WHERE name=%s"
        value = (value,name)
        action = sql.execute(connection, query, value)
        return action      

class snmp():
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT value FROM snmp where name=%s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
        
    def updateByName(name,value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE snmp set value=%s WHERE name=%s"
        value = (value,name)
        action = sql.execute(connection, query, value)
        return action 

class services():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM services"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

class wireless():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM wireless"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

class info():
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT value FROM info where name=%s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
        
    def updateByName(name,value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE info set value=%s WHERE name=%s"
        value = (value,name)
        action = sql.execute(connection, query, value)
        return action
