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

class LogMonitoringDB():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logMonitoringDB ORDER by timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectRoutineByTimeOnly(datetimes):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logMonitoringDB WHERE tipe=9 and timestamp=%s"
        value = (datetimes,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectMonitorAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logMonitoringDB where state!='-' ORDER by timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectMonitorByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logMonitoringDB WHERE state!='-' AND (timestamp BETWEEN %s AND %s) ORDER by timestamp DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectMonitorWithoutBufferByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logMonitoringDB WHERE state!='-' AND  AND buffer!=0 and (timestamp BETWEEN %s AND %s) ORDER by timestamp DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectBuffer():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logMonitoringDB where buffer=0"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectBufferAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logMonitoringDB where buffer=0 ORDER by timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectBufferByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logMonitoringDB WHERE buffer=0 AND (timestamp BETWEEN %s AND %s) ORDER by timestamp DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectAlarm():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logMonitoringDB where state='-'"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def insert(data, state, buffer, timestamp, tipe, attempt):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO logMonitoringDB (data, state, buffer, timestamp, tipe, attempt) VALUES (%s, %s, %s, %s, %s, %s)"
        value = (data, state, buffer, timestamp, tipe, attempt)
        action = sql.execute(connection, query, value)
        return action

    def updateAll(data,state,buffer,timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logMonitoringDB set data=%s, state=%s, buffer=%s, timestamp=%s WHERE id=%s"
        value = (data,state,buffer,timestamp,id)
        action = sql.execute(connection, query, value)
        return action

    def updateRoutine(state, buffer, attempt, data, timestamp):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logMonitoringDB set state=%s, buffer=%s, attempt=%s WHERE data=%s and timestamp=%s"
        value = (state, buffer, attempt, data, timestamp)
        action = sql.execute(connection, query, value)
        return action

    def updateBuffer(attempt, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logMonitoringDB set buffer=2, attempt=%s WHERE id=%s"
        value = (attempt,id)
        action = sql.execute(connection, query, value)
        return action

    def updateAttempt(attempt, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logMonitoringDB set attempt=%s WHERE id=%s"
        value = (attempt,id)
        action = sql.execute(connection, query, value)
        return action

    def updateAlarm(statusCode, buffer, attempt, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logMonitoringDB set state=%s, buffer=%s, attempt=%s WHERE id=%s"
        value = (statusCode, buffer, attempt, id)
        action = sql.execute(connection, query, value)
        return action

    def updateTimestamp(timestamp, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logMonitoringDB set timestamp=%s WHERE id=%s"
        value = (timestamp, id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logMonitoringDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

    def deleteMonitorByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logMonitoringDB WHERE state != '-' AND (timestamp BETWEEN %s AND %s)"
        value = (datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteMonitorWithoutBufferByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logMonitoringDB WHERE state!='-' and  and buffer!=0 AND (timestamp BETWEEN %s AND %s)"
        value = (datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteMonitorAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logMonitoringDB WHERE state!='-' "
        action = sql.execute(connection, query)
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE logMonitoringDB"
        action = sql.executeOnly(connection, query)
        return action

    def deleteBufferByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logMonitoringDB WHERE buffer=0 AND (timestamp BETWEEN %s AND %s)"
        value = (datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteBufferAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logMonitoringDB WHERE buffer=0"
        action = sql.execute(connection, query)
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE logMonitoringDB"
        action = sql.executeOnly(connection, query)
        return action
