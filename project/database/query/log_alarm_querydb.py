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

class LogAlarmDB():
    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * from logAlarmDB where id=%s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByFlag(flag):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * from logAlarmDB where flag=%s"
        value = (flag,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectAlarmToleranceById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * from logAlarmDB where count_time<tolerance and id=%s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByIdType(type, id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * from logAlarmDB where tipe=%s and id=%s"
        value = (type, id)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByIdFlag(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * from logAlarmDB where id=%s and flag=2"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectBySensorFirstAlarmTime(id, firstAlarm):
        connection = sql.connect(host, database, username, password)
        query = "SELECT logAlarmDB.*, sensorListDB.id as idSensor from logAlarmDB join sensorListDB on logAlarmDB.sensor_id=sensorListDB.id where sensorListDB.sensor_id=%s and logAlarmDB.first_alarm=%s"
        value = (id, firstAlarm)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(id, sensor_id, value, tipe, count, count_time, tolerance, firstAlarm):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO logAlarmDB (id, sensor_id, value, tipe, count, count_time, tolerance, first_alarm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        value = (id, sensor_id, value, tipe, count, count_time, tolerance, firstAlarm)
        action = sql.execute(connection, query, value)
        return action

    def updateCountAlarm(count, count_time,  tolerance, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logAlarmDB set count=%s, count_time=%s, tolerance=%s WHERE id=%s"
        value = (count, count_time, tolerance, id)
        action = sql.execute(connection, query, value)
        return action

    def updateAlarm(count, count_time, tolerance, lastAlarm, flag, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logAlarmDB set count=%s, count_time=%s, tolerance=%s, last_alarm=%s, flag=%s WHERE id=%s"
        value = (count, count_time, tolerance, lastAlarm, flag, id)
        action = sql.execute(connection, query, value)
        return action

    def updateFlag(flag, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logAlarmDB set flag=%s WHERE id=%s"
        value = (flag, id)
        action = sql.execute(connection, query, value)
        return action

    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logAlarmDB WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logAlarmDB"
        action = sql.execute(connection, query)
        return action
