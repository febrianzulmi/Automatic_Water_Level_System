import mysql.connector
import json
import sys
import random
import string

sys.path.append('/home/connex/library')
from SynapsisLibrary import *


def openDB():
    with open('/home/connex/project/database/dbNearonProject.json', 'r') as f:
        db = json.load(f)
        host = db['host']
        database = "synapsis_project"
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

class resetDatabaseProject():
    def deleteTable(table_name):
        try:
            connection = sql.connect(host, database, username, password)
            query = f"DROP TABLE IF EXISTS {table_name}"
            action = sql.execute(connection, query)
            connection.close()
            return True
        except Exception as e:
            print(f"Error deleting table {table_name}: {e}")
            return False

class powerMasterSensorDB():
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
    

class powerMasterParameterDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM powerMasterParameterDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM powerMasterParameterDB WHERE id = %s"
        value = (id,)
        action = sql.selectWithInput(connection, query, value)
        return action

    def insert(id, name, parameterCode, createdAt):
        connection = sql.connect(host, database, username, password)
        query = """INSERT INTO powerMasterParameterDB 
                    (id, name, parameterCode, createdAt) 
                    VALUES (%s, %s, %s, %s)"""
        value = (id, name, parameterCode, createdAt)
        action = sql.execute(connection, query, value)
        return action
    
    def update(id, name, parameterCode, updatedAt):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE powerMasterParameterDB 
                   SET name=%s, parameterCode=%s, updatedAt=%s 
                   WHERE id=%s"""
        value = (name, parameterCode, updatedAt, id)
        action = sql.execute(connection, query, value) 
        return action
    
    def updateById(id, name, parameterCode):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE powerMasterParameterDB 
                SET name=%s, parameterCode=%s, updatedAt=NOW() 
                WHERE id=%s"""
        value = (name, parameterCode, id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM powerMasterParameterDB WHERE id = %s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

class powerDeviceDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM powerDeviceDB"
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


# Environment database
class environmentMasterSensorDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentMasterSensorDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentMasterSensorDB WHERE id = %s"
        value = (id,)
        action = sql.selectWithInput(connection, query, value)
        return action

    def insert(id, name, sensorId, createdAt):
        connection = sql.connect(host, database, username, password)
        query = """INSERT INTO environmentMasterSensorDB 
                    (id, name, sensorId, createdAt) 
                    VALUES (%s, %s, %s, %s)"""
        value = (id, name, sensorId, createdAt)
        action = sql.execute(connection, query, value)
        return action
    
    def update(id, name, sensorId, updatedAt):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE environmentMasterSensorDB 
                   SET name=%s, sensorId=%s, updatedAt=%s 
                   WHERE id=%s"""
        value = (name, sensorId, updatedAt, id)
        action = sql.execute(connection, query, value) 
        return action
    
    def updateById(id, name, sensorId):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE environmentMasterSensorDB 
                SET name=%s, sensorId=%s, updatedAt=NOW() 
                WHERE id=%s"""
        value = (name, sensorId, id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM environmentMasterSensorDB WHERE id = %s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action
    

class environmentMasterParameterDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentMasterParameterDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentMasterParameterDB WHERE id = %s"
        value = (id,)
        action = sql.selectWithInput(connection, query, value)
        return action

    def insert(id, name, parameterCode, createdAt):
        connection = sql.connect(host, database, username, password)
        query = """INSERT INTO environmentMasterParameterDB 
                    (id, name, parameterCode, createdAt) 
                    VALUES (%s, %s, %s, %s)"""
        value = (id, name, parameterCode, createdAt)
        action = sql.execute(connection, query, value)
        return action
    
    def update(id, name, parameterCode, updatedAt):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE environmentMasterParameterDB 
                   SET name=%s, parameterCode=%s, updatedAt=%s 
                   WHERE id=%s"""
        value = (name, parameterCode, updatedAt, id)
        action = sql.execute(connection, query, value) 
        return action
    
    def updateById(id, name, parameterCode):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE environmentMasterParameterDB 
                SET name=%s, parameterCode=%s, updatedAt=NOW() 
                WHERE id=%s"""
        value = (name, parameterCode, id)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM environmentMasterParameterDB WHERE id = %s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

class environmentDeviceDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM environmentDeviceDB"
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


    def insert(number, id, name, ip, connectionStatus, state, createdAt):
        connection = sql.connect(host, database, username, password)
        query = """INSERT INTO environmentDeviceDB 
                    (id, number, name, ip, connection, state, createdAt) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        value = (id, number, name, ip, connectionStatus, state, createdAt)
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
    
    def updateById(number, id, name, ip, state):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE environmentDeviceDB 
                SET number=%s, name=%s, ip=%s, state=%s, updatedAt=NOW() 
                WHERE id=%s"""
        value = (number, name, ip, state, id)
        action = sql.execute(connection, query, value)
        return action


    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM environmentDeviceDB WHERE id = %s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

# New Setting
class deviceSettingDB():       
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM deviceSettingDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def insert(deviceUID, deviceName, deviceVersion):
        data = [deviceUID, deviceName, deviceVersion]
        column = ['uid', 'name', 'version']
        for i in range(3):
            connection = sql.connect(host, database, username, password)
            query = "INSERT INTO deviceSettingDB (name, value) VALUES (%s, %s)"
            value = (column[(i)], data[(i)])
            action = sql.execute(connection, query, value)
        return action

    def update(deviceUID, deviceName, deviceVersion):
        data = [deviceUID, deviceName, deviceVersion]
        for i in range(1,4):
            connection = sql.connect(host, database, username, password)
            query = "UPDATE deviceSettingDB SET value = %s WHERE id = %s"
            value = (data[(i-1)], i)
            action = sql.execute(connection, query, value)
        return action
    
    def updateByName(name, value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE deviceSettingDB SET value=%s WHERE name=%s"
        value = (value, name)
        action = sql.execute(connection, query, value)
        return action

class serverSettingDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverSettingDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    def selectByServer(server):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverSettingDB WHERE server = %s"
        value = (server,)
        action = sql.selectWithInput(connection, query, value)
        return action
    def updateByName(domainAddress, ipAddress, port, user, passw, server):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE serverSettingDB SET domainAddress=%s, ipAddress=%s, port=%s, username=%s, password=%s WHERE server=%s"
        value = (domainAddress, ipAddress, port, user, passw, server)
        action = sql.execute(connection, query, value)
        return action

class serverHttpDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverHttpDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    def selectByParameter(parameter):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverHttpDB WHERE parameter = %s"
        value = (parameter,)
        action = sql.selectWithInput(connection, query, value)
        return action
    def insert(name, parameter, type, api):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO serverHttpDB (name, parameter, type, data) VALUES (%s, %s, %s, %s)"
        value = (name, parameter, type, api)
        action = sql.execute(connection, query, value)
        return action
    def update(name, parameter, type, api, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE serverHttpDB SET name=%s, parameter=%s, type=%s, data=%s WHERE id=%s"
        value = (name, parameter, type, api, id)
        action = sql.execute(connection, query, value)
        return action
    def delete(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM serverHttpDB WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

class serverMqttDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverMqttDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    def selectByParameter(parameter):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverMqttDB WHERE parameter = %s"
        value = (parameter,)
        action = sql.selectWithInput(connection, query, value)
        return action
    def insert(name, parameter, api):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO serverMqttDB (name, parameter, data) VALUES (%s, %s, %s)"
        value = (name, parameter, api)
        action = sql.execute(connection, query, value)
        return action
    def update(name, parameter, topic, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE serverMqttDB SET name=%s, parameter=%s, data=%s WHERE id=%s"
        value = (name, parameter, topic, id)
        action = sql.execute(connection, query, value)
        return action
    def delete(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM serverMqttDB WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

class serverHttpAuthDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverHttpAuthDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverHttpAuthDB where name = %s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def updateValueByName(value, name):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE serverHttpAuthDB set value=%s WHERE name=%s"
        value = (value,name)
        action = sql.execute(connection, query, value)
        return action

    def deleteValueByName(name):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE serverHttpAuthDB SET value = '' WHERE name = %s"
        value = (name,)
        action = sql.execute(connection, query, value)
        return action

class connexSettingDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT name, value FROM connexSettingDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    def toggle():
        connection = sql.connect(host, database, username, password)
        query = "SELECT value FROM connexSettingDB WHERE name = 'log'"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    def updateByName(name, value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE connexSettingDB SET value=%s WHERE name=%s"
        value = (value, name)
        action = sql.execute(connection, query, value)
        return action

class intervalRoutineLogDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM intervalRoutineLogDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    def selectByIntervalAndUnit(interval, unit):
        connection = sql.connect(host, database, username, password)
        query = "SELECT `interval`, unit FROM intervalRoutineLogDB WHERE `interval`=%s AND unit=%s"
        value = (interval, unit)
        action = sql.selectWithInput(connection, query, value)
        return action
    def insert(interval, unit):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO intervalRoutineLogDB (`interval`, unit) VALUES (%s, %s)"
        value = (interval, unit)
        action = sql.execute(connection, query, value)
        return action
    def deleteOne(idVal):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM intervalRoutineLogDB WHERE id=%s"
        value = (idVal,)
        action = sql.execute(connection, query, value)
        return action
    def update(interval, unit, idVal):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE intervalRoutineLogDB SET `interval`=%s, unit=%s WHERE id=%s"
        value = (interval, unit, idVal)
        action = sql.execute(connection, query, value)
        return action

class intervalRoutineMonitorDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM intervalRoutineMonitorDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    def selectByIntervalAndUnit(interval, unit):
        connection = sql.connect(host, database, username, password)
        query = "SELECT `interval`, unit FROM intervalRoutineMonitorDB WHERE `interval`=%s AND unit=%s"
        value = (interval, unit)
        action = sql.selectWithInput(connection, query, value)
        return action
    def insert(interval, unit, state):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO intervalRoutineMonitorDB (`interval`, unit, state) VALUES (%s, %s, %s)"
        value = (interval, unit, state)
        action = sql.execute(connection, query, value)
        return action
    def deleteOne(idVal):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM intervalRoutineMonitorDB WHERE id=%s"
        value = (idVal,)
        action = sql.execute(connection, query, value)
        return action
    def update(interval, unit, state, idVal):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE intervalRoutineMonitorDB SET `interval`=%s, unit=%s, state=%s WHERE id=%s"
        value = (interval, unit, state, idVal)
        action = sql.execute(connection, query, value)
        return action

class sensor():
    # function yang baru menghilangkan kolom id di sensor_group
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor.*, sensor_group.id AS idGroup,sensor_group.name AS name_group, sensor_group.intervals, sensor_group.unit, sensor_group.frekuensi, sensor_group.service_id, sensor_group.enterAlarm, sensor_group.exitAlarm, sensor_group.errorAlarm FROM sensor join sensor_group on sensor.group_id=sensor_group.id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByGroupFull(group_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor.*, sensor_group.name AS name_group, sensor_group.intervals, sensor_group.unit as unitInterval, sensor_group.frekuensi, sensor_group.service_id, sensor_group.enterAlarm, sensor_group.exitAlarm, sensor_group.errorAlarm FROM sensor join sensor_group on sensor.group_id=sensor_group.id WHERE sensor.group_id=%s"
        value = (group_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectPriorityLog():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor.*, sensor_group.* FROM sensor join sensor_group on sensor.group_id=sensor_group.id where sensor.log=1"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectPriorityMonitor():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor.*, sensor_group.* FROM sensor join sensor_group on sensor.group_id=sensor_group.id where sensor.monitor=1"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectDailyLog():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor.*, sensor_group.* FROM sensor join sensor_group on sensor.group_id=sensor_group.id where sensor.log=2"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectDailyMonitor():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor.*, sensor_group.* FROM sensor join sensor_group on sensor.group_id=sensor_group.id where sensor.monitor=2"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectOne(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor where sensor_id = %s"
        value = (sensor_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectValue(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT value, timestamp FROM sensor where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByAlarmId(alarmId):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor where alarmId1=%s or alarmId2=%s"
        value = (alarmId,alarmId)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectCalibrateById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT calibrate, formula FROM sensor where id=%s"
        value=(id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByGroup(id_group):
        connection = sql.connect(host, database, username, password)
        query = "SELECT id, sensor_id, name, oid_tipe FROM sensor where group_id=%s"
        value=(id_group,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByGroupOID(group, oid):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor where group_id = %s and oid = %s"
        value = (group, oid)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByRoutineMonitorInterval(routineMonitorIntervalId):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor where monitor = %s"
        value = (routineMonitorIntervalId,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByLogInterval(logIntervalId):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor where log = %s"
        value = (logIntervalId,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO sensor (sensor_id,oid,group_id,name,calibrate,formula,oid_tipe,monitor,log) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        value = (sensor_id,oid,group_id,name,calibrate,formula,oid_tipe,monitor,log)
        action = sql.execute(connection, query, value)
        return action

    def update(sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log, alarm, min, max, alarm_type, stateSensorList, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor set sensor_id=%s, oid=%s, group_id=%s, name=%s, calibrate=%s, formula=%s, oid_tipe=%s, monitor=%s, log=%s, alarm=%s, min=%s, max=%s, alarm_type=%s ,state=%s WHERE id=%s"
        value = (sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log, alarm, min, max, alarm_type, stateSensorList, id)
        action = sql.execute(connection, query, value)
        return action

    def updateParam(name, alarm, sensor_max, sensor_min, unit, alarm_type, last_sync, sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor set name=%s, alarm=%s, max=%s, min=%s, unit=%s, alarm_type=%s, last_sync=%s WHERE sensor_id=%s"
        value = (name, alarm, sensor_max, sensor_min, unit, alarm_type, last_sync, sensor_id)
        action = sql.execute(connection, query, value)
        return action

    def updateValue(value,timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor set value=%s, timestamp=%s WHERE id=%s"
        value = (value,timestamp,id)
        action = sql.execute(connection, query, value)
        return action

    def updateAlarmId(alarmId, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor set alarmId1=%s WHERE sensor_id=%s"
        value = (alarmId, id)
        action = sql.execute(connection, query, value)
        return action

    def updateLastAlarmId(alarmId, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor set alarmId2=%s WHERE sensor_id=%s"
        value = (alarmId, id)
        action = sql.execute(connection, query, value)
        return action

    def updateCondition(condition, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor set conditions=%s WHERE sensor_id=%s"
        value = (condition,id)
        action = sql.execute(connection, query, value)
        return action

    def updateNotifState(notif_state, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor set notif_state=%s WHERE sensor_id=%s"
        value = (notif_state,id)
        action = sql.execute(connection, query, value)
        return action

    def updateNotifCount(notif_count, notif_time, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor set notif_count=%s, notif_time=%s WHERE sensor_id=%s"
        value = (notif_count, notif_time, id)
        action = sql.execute(connection, query, value)
        return action

    def updateResetAlarm(id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor set notif_state=0, notif_count= 0, notif_time=0, conditions='Alarm Inactive', alarmId1='', alarmId2='' WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM sensor WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

class actuator():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuator"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectOne(actuator_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor where actuator_id = %s"
        value = (actuator_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByActId(actuator_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuator where actuator_id = %s"
        value = (actuator_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuator where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(actuator_id,name):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO actuator (actuator_id,name) VALUES (%s, %s)"
        value = (actuator_id,name)
        action = sql.execute(connection, query, value)
        return action

    def update(actuator_id,name,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuator set actuator_id=%s, name=%s WHERE id=%s"
        value = (actuator_id,name,id)
        action = sql.execute(connection, query, value)
        return action

    def updateService(service_id,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuator set service_id=%s WHERE id=%s"
        value = (service_id,id)
        action = sql.execute(connection, query, value)
        return action

    def updateParam(name, value, timestamp, schedule, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuator set name=%s, value=%s, timestamp=%s, schedule=%s WHERE id=%s"
        value = (name, value, timestamp, schedule, id)
        action = sql.execute(connection, query, value)
        return action

    def updateStatus(status,times,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuator set status=%s, last_time=%s WHERE id=%s"
        value = (status,times,id)
        action = sql.execute(connection, query, value)
        return action

    def updateAction(value,times,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuator set last_value=%s, last_update=%s WHERE id=%s"
        value = (value,times,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM actuator WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

class actuator_param():
    # New Query
    def checkExistingParam(actuatorID, name, param, value):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuator_param WHERE actuator_id=%s AND name=%s AND parameter=%s AND value=%s"
        value = (actuatorID, name, param, value)
        fetchall = sql.selectWithInput(connection, query, value)
        isExist = len(fetchall)
        return isExist
    
    def selectFull():
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuator_param.id, actuator_param.actuator_id as actuatorID, actuator_param.name as name_parameter, actuator_param.parameter, 
                actuator_param.value, actuator.actuator_id, actuator.name, actuator.value as value_actuator, actuator.timestamp, actuator.service_id, 
                actuator.last_value, actuator.last_update, actuator.schedule FROM actuator_param join actuator on actuator_param.actuator_id=actuator.id"""
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectOne(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuator_param where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByActuatorIdFull(id):
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuator_param.id, actuator_param.actuator_id as actuatorID, actuator_param.name as name_parameter, actuator_param.parameter, actuator_param.value, 
                actuator.actuator_id, actuator.name, actuator.value as value_actuator, actuator.timestamp, actuator.service_id, actuator.last_value, 
                actuator.last_update, actuator.schedule FROM actuator_param join actuator on actuator_param.actuator_id=actuator.id where actuator_param.actuator_id=%s"""
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(actuator_id,name,param,value):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO actuator_param (actuator_id,name,parameter,value) VALUES (%s, %s, %s, %s)"
        value = (actuator_id,name,param, value)
        action = sql.execute(connection, query, value)
        return action

    def update(actuator_id,name,param,value,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuator_param set actuator_id=%s, name=%s, parameter=%s, value=%s WHERE id=%s"
        value = (actuator_id,name,param,value,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM actuator_param WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

class actuator_schedule():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT actuator_schedule.*, actuator.* FROM actuator_schedule join actuator on actuator_schedule.actuator_id=actuator.id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByActuatorIdFull(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT actuator_schedule.*, actuator.name FROM actuator_schedule JOIN actuator ON actuator_schedule.actuator_id = actuator.id WHERE actuator_schedule.actuator_id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuator_schedule where actuator_id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectBySchedule(id, day, time, value):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuator_schedule where actuator_id=%s and day=%s and time=%s and value=%s"
        value = (id, day, time, value)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(id, actuator_id, day, time, value):
        connection = sql.connect(host, database, username, password)
        query = "INSERT actuator_schedule (id, actuator_id, day, time, value) VALUES (%s, %s, %s, %s, %s)"
        value = (id, actuator_id, day, time, value)
        action = sql.execute(connection, query, value)
        return action

    def updateSchedule(id, day, time, value, id_sch):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuator_schedule set actuator_id=%s, day=%s, time=%s, value=%s WHERE id=%s"
        value = (id, day, time, value, id_sch)
        action = sql.execute(connection, query, value)
        return action

    def updateState(state, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuator_schedule set state=%s WHERE id=%s"
        value = (state,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM actuator_schedule WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

    def deleteByActId(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM actuator_schedule WHERE actuator_id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

class calibrateFormula():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM calibrate_formula"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM calibrate_formula where id=%s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(name,sample):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO calibrate_formula (name,sample) VALUES (%s,%s)"
        value = (name,sample)
        action = sql.execute(connection, query, value)
        return action

    def updateNameByFormula(name,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE calibrate_formula set name=%s WHERE id=%s"
        value = (name,id)
        action = sql.execute(connection, query, value)
        return action

    def updateSampleByFormula(sample,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE calibrate_formula set sample=%s WHERE id=%s"
        value = (sample,id)
        action = sql.execute(connection, query, value)
        return action

    def updateCoefByFormula(koef_a,koef_b,datetime,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE calibrate_formula set koef_a=%s, koef_b=%s, calculate_time=%s WHERE id=%s"
        value = (koef_a,koef_b,datetime,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM calibrate_formula WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

class calibrateSample():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT calibrate_sample.*, calibrate_formula.id as formulaId, calibrate_formula.name as formulaName FROM calibrate_sample join calibrate_formula on calibrate_sample.formula_id=calibrate_formula.id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByFormula(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT calibrate_sample.*, calibrate_formula.id as formulaId, calibrate_formula.name FROM calibrate_sample join calibrate_formula on calibrate_sample.formula_id=calibrate_formula.id where calibrate_sample.formula_id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(formula,value_sample,value_reference):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO calibrate_sample(formula_id,value_sample,value_reference) VALUES (%s,%s,%s)"
        value = (formula,value_sample,value_reference)
        action = sql.execute(connection, query, value)
        return action

    def update(formula_id,sample,reference,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE calibrate_sample set formula_id=%s, value_sample=%s, value_reference=%s WHERE id=%s"
        value = (formula_id,sample,reference,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM calibrate_sample WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

class paramList():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor_paramList.id as id_param_value, sensor_paramList.sensor_id, sensor_paramList.name as name_param_list, sensor_paramList.parameter, sensor_paramList.value as value_param_list, sensor.* FROM sensor_paramList join sensor on sensor_paramList.sensor_id=sensor.id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByGroupFull(group_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor_paramList.id as id_param_value, sensor_paramList.sensor_id, sensor_paramList.name as name_param_list, sensor_paramList.parameter, sensor_paramList.value as value_param_list, sensor.* FROM sensor_paramList join sensor on sensor_paramList.sensor_id=sensor.id where sensor.group_id = %s"
        value = (group_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectBySensorParameter(id,parameter):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor_paramList where sensor_id = %s and parameter=%s"
        value = (id,parameter)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectParameterListSensor(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor.sensor_id,sensor_paramList.parameter,sensor_paramList.value  FROM sensor_paramList JOIN sensor ON sensor_paramList.sensor_id=sensor.id WHERE sensor.group_id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectBySensorList(groupId):
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor.sensor_id, sensor_paramList.value FROM sensor JOIN sensor_paramList ON sensor.id=sensor_paramList.sensor_id WHERE sensor.group_id=%s"
        value = (groupId,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(sensor_id,name,parameter,value):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO sensor_paramList (sensor_id,name,parameter,value) VALUES (%s, %s, %s, %s)"
        value = (sensor_id,name,parameter,value)
        action = sql.execute(connection, query, value)
        return action

    def update(sensor_id,name,parameter,value,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor_paramList set sensor_id=%s, name=%s, parameter=%s, value=%s WHERE id=%s"
        value = (sensor_id,name,parameter,value,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM sensor_paramList WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

class params():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor_param.id as id_param, sensor_param.group_id, sensor_param.name as name_param,sensor_param.parameter,sensor_param.value, sensor_group.* FROM sensor_param join sensor_group on sensor_param.group_id=sensor_group.id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByGroupFull(group_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor_param.id as id_param, sensor_param.group_id, sensor_param.name as name_param,sensor_param.parameter,sensor_param.value, sensor_group.* FROM sensor_param join sensor_group on sensor_param.group_id=sensor_group.id WHERE sensor_param.group_id=%s"
        value = (group_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectOne(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor_param where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByGroupParameter(id,parameter):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensor_param where group_id = %s and parameter=%s"
        value = (id,parameter)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByGroupSensor(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensor_param.parameter, sensor_param.value FROM sensor_param JOIN sensor_group ON sensor_param.group_id = sensor_group.id WHERE sensor_group.id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(group_id,name,parameter,value):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO sensor_param (group_id,name,parameter,value) VALUES (%s, %s, %s, %s)"
        value = (group_id,name,parameter,value)
        action = sql.execute(connection, query, value)
        return action

    def update(group_id,name,parameter,value,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor_param set group_id=%s, name=%s, parameter=%s, value=%s WHERE id=%s"
        value = (group_id,name,parameter,value,id)
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

    def insert(name, intervals, unit, frekuensi, service_id, enterAlarm, exitAlarm, errorAlarm):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO sensor_group (name,intervals,unit,frekuensi,service_id,enterAlarm,exitAlarm,errorAlarm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        value = (name,intervals,unit,frekuensi,service_id,enterAlarm,exitAlarm,errorAlarm)
        action = sql.execute(connection, query, value)
        return action

    def update(name, interval, unit, frekuensi, service_id, id, enterAlarm, exitAlarm, errorAlarm, stateSensor):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensor_group set name=%s, intervals=%s, unit=%s, frekuensi=%s, service_id=%s, enterAlarm=%s, exitAlarm=%s, errorAlarm=%s , state=%s WHERE id=%s"
        value = (name,interval,unit,frekuensi,service_id,enterAlarm,exitAlarm,errorAlarm, stateSensor,id)
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

    def selectRoutineByTimeOnly(datetimes):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendNode WHERE tipe=9 and timestamp=%s"
        value = (datetimes,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectMonitorAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendNode where state!='-' ORDER by timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectMonitorByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendNode WHERE state!='-' AND (timestamp BETWEEN %s AND %s) ORDER by timestamp DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectMonitorWithoutBufferByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendNode WHERE state!='-' AND  AND buffer!=0 and (timestamp BETWEEN %s AND %s) ORDER by timestamp DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectBuffer():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendNode where buffer=0"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectBufferAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendNode where buffer=0 ORDER by timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectBufferByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendNode WHERE buffer=0 AND (timestamp BETWEEN %s AND %s) ORDER by timestamp DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectAlarm():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_sendNode where state='-'"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def insert(data, state, buffer, timestamp, tipe, attempt):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_sendNode (data, state, buffer, timestamp, tipe, attempt) VALUES (%s, %s, %s, %s, %s, %s)"
        value = (data, state, buffer, timestamp, tipe, attempt)
        action = sql.execute(connection, query, value)
        return action

    def updateAll(data,state,buffer,timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sendNode set data=%s, state=%s, buffer=%s, timestamp=%s WHERE id=%s"
        value = (data,state,buffer,timestamp,id)
        action = sql.execute(connection, query, value)
        return action

    def updateRoutine(state, buffer, attempt, data, timestamp):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sendNode set state=%s, buffer=%s, attempt=%s WHERE data=%s and timestamp=%s"
        value = (state, buffer, attempt, data, timestamp)
        action = sql.execute(connection, query, value)
        return action

    def updateBuffer(attempt, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sendNode set buffer=2, attempt=%s WHERE id=%s"
        value = (attempt,id)
        action = sql.execute(connection, query, value)
        return action

    def updateAttempt(attempt, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sendNode set attempt=%s WHERE id=%s"
        value = (attempt,id)
        action = sql.execute(connection, query, value)
        return action

    def updateAlarm(statusCode, buffer, attempt, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sendNode set state=%s, buffer=%s, attempt=%s WHERE id=%s"
        value = (statusCode, buffer, attempt, id)
        action = sql.execute(connection, query, value)
        return action

    def updateTimestamp(timestamp, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sendNode set timestamp=%s WHERE id=%s"
        value = (timestamp, id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sendNode WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

    def deleteMonitorByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sendNode WHERE state!='-' and  AND (timestamp BETWEEN %s AND %s)"
        value = (datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteMonitorWithoutBufferByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sendNode WHERE state!='-' and  and buffer!=0 AND (timestamp BETWEEN %s AND %s)"
        value = (datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteMonitorAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sendNode WHERE state!='-' "
        action = sql.execute(connection, query)
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE log_sendNode"
        action = sql.executeOnly(connection, query)
        return action

    def deleteBufferByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sendNode WHERE buffer=0 AND (timestamp BETWEEN %s AND %s)"
        value = (datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteBufferAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_sendNode WHERE buffer=0"
        action = sql.execute(connection, query)
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE log_sendNode"
        action = sql.executeOnly(connection, query)
        return action

class logSensor():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT log_sensor.*, sensor.sensor_id, sensor.name FROM log_sensor join sensor on log_sensor.sensor_id=sensor.id ORDER BY timestamp DESC"
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

    def selectRoutineBySensorTime(sensor_id, timestamp):
        connection = sql.connect(host, database, username, password)
        query = "SELECT log_sensor.*, sensor.sensor_id FROM log_sensor join sensor on log_sensor.sensor_id=sensor.id WHERE log_sensor.tipe=9 and sensor.sensor_id=%s and log_sensor.timestamp=%s"
        value = (sensor_id, timestamp)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByAlarmSensorTime(sensor_id, typeAlarm, timestamp):
        connection = sql.connect(host, database, username, password)
        query = "SELECT log_sensor.*, sensor.sensor_id FROM log_sensor join sensor on log_sensor.sensor_id=sensor.id WHERE sensor.sensor_id=%s and log_sensor.tipe=%s and log_sensor.timestamp=%s"
        value = (sensor_id, typeAlarm, timestamp)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectBySensor(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT log_sensor.*, sensor.sensor_id, sensor.name FROM log_sensor join sensor on sensor.id=log_sensor.sensor_id WHERE log_sensor.sensor_id=%s ORDER by log_sensor.timestamp DESC"
        value = (sensor_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByTime(sensor_id, datetime1, datetime2):
        connection = sql.connect(host, database, username, password)
        if sensor_id == 'all':
           query = "SELECT log_sensor.*, sensor.sensor_id, sensor.name FROM log_sensor join sensor on sensor.id=log_sensor.sensor_id WHERE log_sensor.timestamp BETWEEN %s AND %s ORDER by log_sensor.timestamp DESC"
           value = (datetime1,datetime2)
        else:
           query = "SELECT log_sensor.*, sensor.sensor_id, sensor.name FROM log_sensor join sensor on sensor.id=log_sensor.sensor_id  WHERE log_sensor.sensor_id=%s AND log_sensor.timestamp BETWEEN %s AND %s ORDER by log_sensor.timestamp DESC"
           value = (sensor_id,datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(sensor_id,data,tipe,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_sensor (sensor_id,data,tipe,timestamp) VALUES (%s, %s, %s, %s)"
        value = (sensor_id,data,tipe,timestamp)
        action = sql.execute(connection, query, value)
        return action

    def updateAll(sensor_id, data, timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sensor set sensor_id=%s, data=%s, timestamp=%s WHERE id=%s"
        value = (sensor_id, data, timestamp,id)
        action = sql.execute(connection, query, value)
        return action

    def updateValue(value, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sensor set data=%s WHERE id=%s"
        value = (value, id)
        action = sql.execute(connection, query, value)
        return action

    def updateTimestamp(timestamp, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_sensor set timestamp=%s WHERE id=%s"
        value = (timestamp, id)
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

    def deleteByTime(sensor_id, datetime1, datetime2):
        connection = sql.connect(host, database, username, password)
        if sensor_id == 'all':
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
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE log_sensor"
        action = sql.executeOnly(connection, query)
        return action

class logActuator():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT log_actuator.*, actuator.actuator_id, actuator.name FROM log_actuator JOIN actuator ON log_actuator.actuator_id=actuator.id ORDER BY log_actuator.timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT log_actuator.*, actuator.actuator_id, actuator.name FROM log_actuator JOIN actuator ON log_actuator.actuator_id=actuator.id WHERE log_actuator.timestamp BETWEEN %s AND %s ORDER by log_actuator.timestamp DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(actuator_id,value,action,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_actuator (actuator_id,value,action,timestamp) VALUES (%s, %s, %s, %s)"
        value = (actuator_id,value,action,timestamp)
        action = sql.execute(connection, query, value)
        return action

    def updateAll(actuator_id,value,action,timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_actuator set actuator_id=%s, value=%s, action=%s, timestamp=%s WHERE id=%s"
        value = (actuator_id,value,action,timestamp,id)
        action = sql.execute(connection, query, value)
        return action

    def updateNotifWhatsapp(id_log):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_actuator set notif_wa=1 WHERE id=%s"
        value = (id_log,)
        action = sql.execute(connection, query, value)
        return action

    def updateNotifEmail(id_log):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_actuator set notif_email=1 WHERE id=%s"
        value = (id_log,)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_actuator WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

    def deleteByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_actuator WHERE timestamp BETWEEN %s AND %s"
        value = (datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_actuator"
        action = sql.execute(connection, query)
        return action

class logAlarm():
    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * from log_alarm where id=%s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByFlag(flag):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * from log_alarm where flag=%s"
        value = (flag,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectAlarmToleranceById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * from log_alarm where count_time<tolerance and id=%s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByIdType(type, id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * from log_alarm where tipe=%s and id=%s"
        value = (type, id)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByIdFlag(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * from log_alarm where id=%s and flag=2"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectBySensorFirstAlarmTime(id, firstAlarm):
        connection = sql.connect(host, database, username, password)
        query = "SELECT log_alarm.*, sensor.id as idSensor from log_alarm join sensor on log_alarm.sensor_id=sensor.id where sensor.sensor_id=%s and log_alarm.first_alarm=%s"
        value = (id, firstAlarm)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(id, sensor_id, value, tipe, count, count_time, tolerance, firstAlarm):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_alarm (id, sensor_id, value, tipe, count, count_time, tolerance, first_alarm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        value = (id, sensor_id, value, tipe, count, count_time, tolerance, firstAlarm)
        action = sql.execute(connection, query, value)
        return action

    def updateCountAlarm(count, count_time,  tolerance, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_alarm set count=%s, count_time=%s, tolerance=%s WHERE id=%s"
        value = (count, count_time, tolerance, id)
        action = sql.execute(connection, query, value)
        return action

    def updateAlarm(count, count_time, tolerance, lastAlarm, flag, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_alarm set count=%s, count_time=%s, tolerance=%s, last_alarm=%s, flag=%s WHERE id=%s"
        value = (count, count_time, tolerance, lastAlarm, flag, id)
        action = sql.execute(connection, query, value)
        return action

    def updateFlag(flag, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_alarm set flag=%s WHERE id=%s"
        value = (flag, id)
        action = sql.execute(connection, query, value)
        return action

    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_alarm WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_alarm"
        action = sql.execute(connection, query)
        return action

class logTolerance():
    def selectByAlarm(alarmId):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * from log_tolerance where alarmId=%s"
        value = (alarmId,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(value, timestamp, alarmId):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_tolerance (value, timestamp, alarmId) VALUES (%s, %s, %s)"
        value = (value, timestamp, alarmId)
        action = sql.execute(connection, query, value)
        return action

    def deleteByAlarmId(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_tolerance WHERE alarmId=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_tolerance"
        action = sql.execute(connection, query)
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE log_tolerance"
        action = sql.executeOnly(connection, query)
        return action

class logNotif():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_notif ORDER BY create_time DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_notif WHERE create_time BETWEEN %s AND %s ORDER by create_time DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByState():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_notif WHERE state != 'Success'"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def insertAll(tipe, sensor, condition, notif, subject, message, state, create_time, send_time):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_notif (type,sensor,conditions,notif,subject,message,state,create_time,send_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        value = (tipe, sensor, condition, notif, subject, message, state, create_time, send_time)
        action = sql.execute(connection, query, value)
        return action

    def insert(tipe, sensor, condition, notif, subject, message, state, create_time):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_notif (type,sensor,conditions,notif,subject,message,state,create_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        value = (tipe, sensor, condition, notif, subject, message, state, create_time)
        action = sql.execute(connection, query, value)
        return action

    def updateAll(tipe, notif, subject, message, state, create_time, send_time, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_notif set type=%s, notif=%s, subject=%s, message=%s, state=%s, create_time=%s, send_time=%s WHERE id=%s"
        value = (tipe, notif, subject, message, state, create_time, send_time, id)
        action = sql.execute(connection, query, value)
        return action

    def updateNotif(id_log, state, send_time):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE log_notif set state=%s, send_time=%s WHERE id=%s"
        value = (state, send_time,id_log)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_notif WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

    def deleteByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_notif WHERE create_time BETWEEN %s AND %s"
        value = (datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_notif"
        action = sql.execute(connection, query)
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE log_notif"
        action = sql.executeOnly(connection, query)
        return action

class logError():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_error ORDER BY timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectOne(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_error where id=%s ORDER BY timestamp DESC"
        value=(id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM log_error WHERE timestamp BETWEEN %s AND %s ORDER by timestamp DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(service,error,file,line,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO log_error (service,error,file,line,timestamp) VALUES (%s, %s, %s, %s, %s)"
        value = (service,error,file,line,timestamp)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_error WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

    def deleteByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_error WHERE timestamp BETWEEN %s AND %s"
        value = (datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM log_error"
        action = sql.execute(connection, query)
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE log_error"
        action = sql.executeOnly(connection, query)
        return action

class system():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM system"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def insert(name,service,enable,last_run,since):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO system (name,service,enable,state,last_run,since) VALUES (%s, %s, %s, %s, %s, %s)"
        value = (name,service,enable,'-',last_run,since)
        action = sql.execute(connection, query, value)
        return action
    
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM system where name = %s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def updateStatusByName(state,times,name):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE system set state=%s, last_update=%s WHERE name=%s"
        value = (state,times,name)
        action = sql.execute(connection, query, value)
        return action
    
    def updateServiceStateById(state, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE system set state=%s WHERE id=%s"
        value = (state, id)
        action = sql.execute(connection, query, value)
        return action
    
    def updateServiceBootById(boot, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE system set enable=%s WHERE id=%s"
        value = (boot, id)
        action = sql.execute(connection, query, value)
        return action

    def updateStatusByName(state,times,name):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE system set state=%s, last_update=%s WHERE name=%s"
        value = (state,times,name)
        action = sql.execute(connection, query, value)
        return action
    
    def updateServiceByName(service,enable,last_run,since,name):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE system set service=%s, enable=%s, last_run=%s, since=%s WHERE name=%s"
        value = (service,enable,last_run,since,name)
        action = sql.execute(connection, query, value)
        return action