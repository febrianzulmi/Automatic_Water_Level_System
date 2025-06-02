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

class LogSensorDB():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT logSensorDB.*, sensorListDB.sensor_id, sensorListDB.name FROM logSensorDB join sensorListDB on logSensorDB.sensor_id=sensorListDB.id ORDER BY timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectOne(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logSensorDB where sensor_id=%s ORDER BY timestamp DESC"
        value=(sensor_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectLastOne(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logSensorDB where sensor_id=%s ORDER BY timestamp DESC LIMIT 1"
        value=(sensor_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectRoutineBySensorTime(sensor_id, timestamp):
        connection = sql.connect(host, database, username, password)
        query = "SELECT logSensorDB.*, sensorListDB.sensor_id FROM logSensorDB join sensorListDB on logSensorDB.sensor_id=sensorListDB.id WHERE logSensorDB.tipe=9 and sensorListDB.sensor_id=%s and logSensorDB.timestamp=%s"
        value = (sensor_id, timestamp)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByAlarmSensorTime(sensor_id, typeAlarm, timestamp):
        connection = sql.connect(host, database, username, password)
        query = "SELECT logSensorDB.*, sensorListDB.sensor_id FROM logSensorDB join sensorListDB on logSensorDB.sensor_id=sensorListDB.id WHERE sensorListDB.sensor_id=%s and logSensorDB.tipe=%s and logSensorDB.timestamp=%s"
        value = (sensor_id, typeAlarm, timestamp)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectBySensor(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT logSensorDB.*, sensorListDB.sensor_id, sensorListDB.name FROM logSensorDB join sensorListDB on sensorListDB.id=logSensorDB.sensor_id WHERE logSensorDB.sensor_id=%s ORDER by logSensorDB.timestamp DESC"
        value = (sensor_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByTime(sensor_id, datetime1, datetime2):
        connection = sql.connect(host, database, username, password)
        if sensor_id == 'all':
           query = "SELECT logSensorDB.*, sensorListDB.sensor_id, sensorListDB.name FROM logSensorDB join sensorListDB on sensorListDB.id=logSensorDB.sensor_id WHERE logSensorDB.timestamp BETWEEN %s AND %s ORDER by logSensorDB.timestamp DESC"
           value = (datetime1,datetime2)
        else:
           query = "SELECT logSensorDB.*, sensorListDB.sensor_id, sensorListDB.name FROM logSensorDB join sensorListDB on sensorListDB.id=logSensorDB.sensor_id  WHERE logSensorDB.sensor_id=%s AND logSensorDB.timestamp BETWEEN %s AND %s ORDER by logSensorDB.timestamp DESC"
           value = (sensor_id,datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(sensor_id,data,tipe,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO logSensorDB (sensor_id,data,tipe,timestamp) VALUES (%s, %s, %s, %s)"
        value = (sensor_id,data,tipe,timestamp)
        action = sql.execute(connection, query, value)
        return action

    def updateAll(sensor_id, data, timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logSensorDB set sensor_id=%s, data=%s, timestamp=%s WHERE id=%s"
        value = (sensor_id, data, timestamp,id)
        action = sql.execute(connection, query, value)
        return action

    def updateValue(value, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logSensorDB set data=%s WHERE id=%s"
        value = (value, id)
        action = sql.execute(connection, query, value)
        return action

    def updateTimestamp(timestamp, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logSensorDB set timestamp=%s WHERE id=%s"
        value = (timestamp, id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logSensorDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

    def deleteBySensor(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logSensorDB WHERE sensor_id=%s"
        value = (sensor_id,)
        action = sql.execute(connection, query, value)
        return action

    def deleteByTime(sensor_id, datetime1, datetime2):
        connection = sql.connect(host, database, username, password)
        if sensor_id == 'all':
           query = "DELETE FROM logSensorDB WHERE timestamp BETWEEN %s AND %s"
           value = (datetime1,datetime2)
        else:
           query = "DELETE FROM logSensorDB WHERE sensor_id=%s AND timestamp BETWEEN %s AND %s"
           value = (sensor_id,datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logSensorDB"
        action = sql.execute(connection, query)
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE logSensorDB"
        action = sql.executeOnly(connection, query)
        return action
    
