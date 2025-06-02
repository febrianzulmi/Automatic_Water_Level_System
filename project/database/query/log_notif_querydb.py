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
# print (host , database, username, password)
class LogNotifDB():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logNotifDB ORDER BY create_time DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logNotifDB WHERE create_time BETWEEN %s AND %s ORDER by create_time DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByState():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logNotifDB WHERE state != 'Success'"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def insertAll(tipe, sensor, condition, notif, subject, message, state, create_time, send_time):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO logNotifDB (type,sensor,conditions,notif,subject,message,state,create_time,send_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        value = (tipe, sensor, condition, notif, subject, message, state, create_time, send_time)
        action = sql.execute(connection, query, value)
        return action

    def insert(tipe, sensor, condition, notif, subject, message, state, create_time):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO logNotifDB (type,sensor,conditions,notif,subject,message,state,create_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        value = (tipe, sensor, condition, notif, subject, message, state, create_time)
        action = sql.execute(connection, query, value)
        return action

    def updateAll(tipe, notif, subject, message, state, create_time, send_time, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logNotifDB set type=%s, notif=%s, subject=%s, message=%s, state=%s, create_time=%s, send_time=%s WHERE id=%s"
        value = (tipe, notif, subject, message, state, create_time, send_time, id)
        action = sql.execute(connection, query, value)
        return action

    def updateNotif(id_log, state, send_time):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logNotifDB set state=%s, send_time=%s WHERE id=%s"
        value = (state, send_time,id_log)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logNotifDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

    def deleteByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logNotifDB WHERE create_time BETWEEN %s AND %s"
        value = (datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logNotifDB"
        action = sql.execute(connection, query)
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE logNotifDB"
        action = sql.executeOnly(connection, query)
        return action
    
