import mysql.connector, json, sys
sys.path.append('../library')
from SynapsisLibrary import *

def openDB():
    with open('/home/connex/platform/database/db.json', 'r') as f:
        db = json.load(f)
        host = db['host']
        database = 'synapsis_project'
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

class setting():
    def reset():
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE setting"
        action = sql.executeOnly(connection, query)
        return action
        
class attributes():
    def selectOne(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM attributes where name = %s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
            
    def reset():
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE attributes"
        action = sql.executeOnly(connection, query)
        return action
    
class intervals():
    def reset():
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE intervals"
        action = sql.executeOnly(connection, query)
        return action
        
class gateway():
    def reset():
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE gateway"
        action = sql.executeOnly(connection, query)
        return action
        
class sensor():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
        
    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM sensor"
        action = sql.executeOnly(connection, query)   
    
    def reset():
        connection = sql.connect(host, database, username, password)
        query = "ALTER TABLE sensor AUTO_INCREMENT=1"
        action = sql.executeOnly(connection, query)
        return action

class params():
   def reset():
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE sensor_param"
        action = sql.executeOnly(connection, query)
        return action

class groups():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor_group"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
            
    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM sensor_group"
        action = sql.executeOnly(connection, query)
        return action
        
    def reset():
        connection = sql.connect(host, database, username, password)
        query = "ALTER TABLE sensor_group AUTO_INCREMENT=1"
        action = sql.executeOnly(connection, query)
        return action

class logSendNode():
    def reset():
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE log_sendNode"
        action = sql.executeOnly(connection, query)
        return action

class logSendGateway():
    def reset():
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE log_sendGateway"
        action = sql.executeOnly(connection, query)
        return action

class logBufferNode():
    def reset():
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE log_bufferNode"
        action = sql.executeOnly(connection, query)
        return action

class logBufferGateway():
    def reset():
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE log_bufferGateway"
        action = sql.executeOnly(connection, query)
        return action

class logSensor():
    def selectLastOne(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sensor where sensor_id=%s ORDER BY timestamp DESC LIMIT 1"
        value=(sensor_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
            
    def reset():
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE log_sensor"
        action = sql.executeOnly(connection, query)
        return action

class logError():
    def reset():
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE log_error"
        action = sql.executeOnly(connection, query)
        return action

class system():
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM system where name = %s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def insert(name,service,enable,last_run,since):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO system (name,service,enable,state,last_run,since) VALUES (%s, %s, %s, %s, %s, %s)"
        value = (name,service,enable,'-',last_run,since)
        action = sql.execute(connection, query, value)
        return action
    
    def updateServiceByName(service,enable,last_run,since,name):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE system set service=%s, enable=%s, last_run=%s, since=%s WHERE name=%s"
        value = (service,enable,last_run,since,name)
        action = sql.execute(connection, query, value)
        return action