import mysql.connector, json, sys
sys.path.append('../../library')
from SynapsisLibrary import *

def openDB():
    with open('../database/db.json', 'r') as f:
        db = json.load(f)
        host = db['host']
        database = db['database']
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
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM setting where id = 1"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def insert(node_id,name,ip,port,api_key):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO setting (id,id_device,name,ip,port,api_key,token) VALUES (1, %s, %s, %s, %s, %s, '')"
        value = (node_id,name,ip,port,api_key)
        action = sql.execute(connection, query, value)
        return action

    def update(node_id,name,ip,port,api_key):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE setting set id_device=%s, name=%s, ip=%s, port=%s, api_key=%s where id = 1"
        value = (node_id,name,ip,port,api_key)
        action = sql.execute(connection, query, value)
        return action

    def updateToken(token):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE setting set token=%s where id = 1"
        value = (token,)
        action = sql.execute(connection, query, value)
        return action

class attributes():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM attributes"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
        
    def selectOne(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM attributes where name = %s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
        
    def insert(name,value):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO attributes (name,value) VALUES (%s, %s)"
        value = (name,value)
        action = sql.execute(connection, query, value)
        return action
        
    def update(name,value,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE attributes set name=%s, value=%s WHERE id=%s"
        value = (name,value,id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM attributes WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

class intervals():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM intervals"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
        
    def selectOne(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM intervals where name = %s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
        
    def insert(name,intervals,unit):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO intervals (name,intervals,unit) VALUES (%s, %s, %s)"
        value = (name,intervals,unit)
        action = sql.execute(connection, query, value)
        return action
        
    def update(name,intervals,unit,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE intervals set name=%s, intervals=%s, unit=%s WHERE id=%s"
        value = (name,intervals,unit,id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM intervals WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
        
class gateway():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM gateway where id = 1"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
        
    def insert(values):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO gateway (id, value) VALUES (1, %s)"
        value = (values,)
        action = sql.execute(connection, query, value)
        return action
        
    def update(values):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE gateway set value=%s where id = 1"
        value = (values,)
        action = sql.execute(connection, query, value)
        return action
        
class sensor():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor.*, sensor_group.* FROM sensor join sensor_group on sensor.group_id=sensor_group.id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectOne(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor where sensor_id = %s"
        value = (sensor_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall    
        
    def selectByGroup(id_group):
        connection = sql.connect(host, database, username, password)
        query = "SELECT id, sensor_id, name FROM sensor where group_id=%s"
        value=(id_group,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
            
    def insert(sensor_id,group_id,name):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO sensor (sensor_id,group_id,name) VALUES (%s, %s, %s)"
        value = (sensor_id,group_id,name)
        action = sql.execute(connection, query, value)
        return action
        
    def update(sensor_id,group_id,name,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor set sensor_id=%s, group_id=%s, name=%s WHERE id=%s"
        value = (sensor_id,group_id,name,id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM sensor WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

class params():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor_param.*, sensor_group.* FROM sensor_param join sensor_group on sensor_param.group_id=sensor_group.id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectOne(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor_param where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
            
    def insert(group_id,name,param):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO sensor_param (group_id,name,param) VALUES (%s, %s, %s)"
        value = (group_id,name,param)
        action = sql.execute(connection, query, value)
        return action
        
    def update(group_id,name,param,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor_param set group_id=%s, name=%s, param=%s WHERE id=%s"
        value = (group_id,name,param,id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM sensor_param WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

class groups():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor_group"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectOne(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor_group where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor_group where name = %s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
            
    def insert(name,intervals,unit,frekuensi,service_id):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO sensor_group (name,intervals,unit,frekuensi,service_id) VALUES (%s, %s, %s, %s, %s)"
        value = (name,intervals,unit,frekuensi,service_id)
        action = sql.execute(connection, query, value)
        return action
        
    def update(name,intervals,unit,frekuensi,service_id,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor_group set name=%s, intervals=%s, unit=%s, frekuensi=%s, service_id=%s WHERE id=%s"
        value = (name,intervals,unit,frekuensi,service_id,id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM sensor_group WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

class logSendNode():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendNode ORDER by timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
        
    def selectByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendNode WHERE timestamp BETWEEN %s AND %s ORDER by timestamp DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(data,state,buffer,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_sendNode (data,state,buffer,timestamp) VALUES (%s, %s, %s, %s)"
        value = (data,state,buffer,timestamp)
        action = sql.execute(connection, query, value)
        return action
    
    def updateAll(data,state,buffer,timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sendNode set data=%s, state=%s, buffer=%s, timestamp=%s WHERE id=%s"
        value = (data,state,buffer,timestamp,id)
        action = sql.execute(connection, query, value)
        return action
    
    def updateLog(data,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sendNode set buffer=2 WHERE data=%s AND timestamp=%s"
        value = (data,timestamp)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sendNode WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
        
    def deleteByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sendNode WHERE timestamp BETWEEN %s AND %s"
        value = (datetime1,datetime2) 
        action = sql.execute(connection, query, value)
        return action
    
    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sendNode"
        action = sql.execute(connection, query)
        return action

class logSendGateway():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendGateway ORDER by timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectLastOne():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendGateway ORDER by timestamp DESC LIMIT 1"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectNode():
        connection = sql.connect(host, database, username, password)
        query = "SELECT node_id FROM log_sendGateway GROUP BY node_id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectByNode(node_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendGateway WHERE node_id=%s ORDER by timestamp DESC"
        value = (node_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByTime(node_id,datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        if node_id == '':
           query = "SELECT * FROM log_sendGateway WHERE timestamp BETWEEN %s AND %s ORDER by timestamp DESC"
           value = (datetime1,datetime2)
        else:
           query = "SELECT * FROM log_sendGateway WHERE node_id=%s AND timestamp BETWEEN %s AND %s ORDER by timestamp DESC"
           value = (node_id,datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(node_id,sensor,state,buffer,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_sendGateway (node_id,data,state,buffer,timestamp) VALUES (%s, %s, %s, %s, %s)"
        value = (node_id,sensor,state,buffer,timestamp)
        action = sql.execute(connection, query, value)
        return action
    
    def updateAll(node_id,sensor,state,buffer,timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sendGateway set node_id=%s, data=%s, state=%s, buffer=%s, timestamp=%s WHERE id=%s"
        value = (node_id,sensor,state,buffer,timestamp,id)
        action = sql.execute(connection, query, value)
        return action
    
    def updateLog(node_id,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sendGateway set buffer=2 WHERE node_id=%s and timestamp=%s"
        value = (node_id,timestamp)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sendGateway WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteByNode(node_id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sendGateway WHERE node_id=%s"
        value = (node_id,)
        action = sql.execute(connection, query, value)
        return action
        
    def deleteByTime(node_id,datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        if node_id == '':
           query = "DELETE FROM log_sendGateway WHERE timestamp BETWEEN %s AND %s"
           value = (datetime1,datetime2) 
        else:
           query = "DELETE FROM log_sendGateway WHERE node_id=%s AND timestamp BETWEEN %s AND %s"
           value = (node_id,datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sendGateway"
        action = sql.execute(connection, query)
        return action

class logBufferNode():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_bufferNode ORDER by timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectBuffer():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_bufferNode"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall    
    
    def selectByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_bufferNode WHERE timestamp BETWEEN %s AND %s ORDER by timestamp DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(data,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_bufferNode (data,timestamp) VALUES (%s, %s)"
        value = (data,timestamp)
        action = sql.execute(connection, query, value)
        return action
    
    def updateAll(data,timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_bufferNode set data=%s, timestamp=%s WHERE id=%s"
        value = (data,timestamp,id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_bufferNode WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
        
    def deleteByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_bufferNode WHERE timestamp BETWEEN %s AND %s"
        value = (datetime1,datetime2) 
        action = sql.execute(connection, query, value)
        return action
    
    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_bufferNode"
        action = sql.execute(connection, query)
        return action

class logBufferGateway():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_bufferGateway ORDER BY timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectBuffer():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_bufferGateway"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectNode():
        connection = sql.connect(host, database, username, password)
        query = "SELECT node_id FROM log_bufferGateway GROUP BY node_id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectByNode(node_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_bufferGateway WHERE node_id=%s ORDER by timestamp DESC"
        value = (node_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByTime(node_id,datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        if node_id == '':
           query = "SELECT * FROM log_bufferGateway WHERE timestamp BETWEEN %s AND %s ORDER by timestamp DESC"
           value = (datetime1,datetime2)
        else:
           query = "SELECT * FROM log_bufferGateway WHERE node_id=%s AND timestamp BETWEEN %s AND %s ORDER by timestamp DESC"
           value = (node_id,datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(node_id,data,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_bufferGateway (node_id,data,timestamp) VALUES (%s, %s, %s)"
        value = (node_id,data,timestamp)
        action = sql.execute(connection, query, value)
        return action

    def updateAll(node_id, data, timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_bufferGateway set node_id=%s, data=%s, timestamp=%s WHERE id=%s"
        value = (node_id, data, timestamp,id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_bufferGateway WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteByNode(node_id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_bufferGateway WHERE node_id=%s"
        value = (node_id,)
        action = sql.execute(connection, query, value)
        return action
        
    def deleteByTime(node_id,datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        if node_id == '':
           query = "DELETE FROM log_bufferGateway WHERE timestamp BETWEEN %s AND %s"
           value = (datetime1,datetime2) 
        else:
           query = "DELETE FROM log_bufferGateway WHERE node_id=%s AND timestamp BETWEEN %s AND %s"
           value = (node_id,datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_bufferGateway"
        action = sql.execute(connection, query)
        return action

class logSensor():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT log_sensor.*, sensor.sensor_id FROM log_sensor join sensor on log_sensor.sensor_id=sensor.id ORDER BY timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectOne(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sensor where sensor_id=%s ORDER BY timestamp DESC"
        value=(sensor_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
        
    def selectLastOne(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sensor where sensor_id=%s ORDER BY timestamp DESC LIMIT 1"
        value=(sensor_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectBySensor(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT log_sensor.*, sensor.sensor_id FROM log_sensor join sensor on sensor.id=log_sensor.sensor_id WHERE log_sensor.sensor_id=%s ORDER by log_sensor.timestamp DESC"
        value = (sensor_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByTime(sensor_id,datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        if sensor_id == '':
           query = "SELECT log_sensor.*, sensor.sensor_id FROM log_sensor join sensor on sensor.id=log_sensor.sensor_id WHERE log_sensor.timestamp BETWEEN %s AND %s ORDER by log_sensor.timestamp DESC"
           value = (datetime1,datetime2)
        else:
           query = "SELECT log_sensor.*, sensor.sensor_id FROM log_sensor join sensor on sensor.id=log_sensor.sensor_id  WHERE log_sensor.sensor_id=%s AND log_sensor.timestamp BETWEEN %s AND %s ORDER by log_sensor.timestamp DESC"
           value = (sensor_id,datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(sensor_id,data,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_sensor (sensor_id,data,timestamp) VALUES (%s, %s, %s)"
        value = (sensor_id,data,timestamp)
        action = sql.execute(connection, query, value)
        return action

    def updateAll(sensor_id, data, timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sensor set sensor_id=%s, data=%s, timestamp=%s WHERE id=%s"
        value = (sensor_id, data, timestamp,id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sensor WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteBySensor(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sensor WHERE sensor_id=%s"
        value = (sensor_id,)
        action = sql.execute(connection, query, value)
        return action
        
    def deleteByTime(sensor_id,datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        if sensor_id == '':
           query = "DELETE FROM log_sensor WHERE timestamp BETWEEN %s AND %s"
           value = (datetime1,datetime2) 
        else:
           query = "DELETE FROM log_sensor WHERE sensor_id=%s AND timestamp BETWEEN %s AND %s"
           value = (sensor_id,datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sensor"
        action = sql.execute(connection, query)
        return action

class logError():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_error ORDER BY timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectNode():
        connection = sql.connect(host, database, username, password)
        query = "SELECT node_id FROM log_error GROUP BY node_id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_error WHERE timestamp BETWEEN %s AND %s ORDER by timestamp DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(datas,error,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_error (data,errors,timestamp) VALUES (%s, %s, %s)"
        value = (datas,error,timestamp)
        action = sql.execute(connection, query, value)
        return action

    def updateAll(data, error, timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_error set data=%s, errors=%s, timestamp=%s WHERE id=%s"
        value = (data, error, timestamp, id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_error WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
        
    def deleteByTime(node_id,datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_error WHERE timestamp BETWEEN %s AND %s"
        value = (datetime1,datetime2) 
        action = sql.execute(connection, query, value)
        return action
    
    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_error"
        action = sql.execute(connection, query)
        return action
