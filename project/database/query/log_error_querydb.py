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

class LogErrorDB():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logErrorDB ORDER BY timestamp DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectOne(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logErrorDB where id=%s ORDER BY timestamp DESC"
        value=(id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM logErrorDB WHERE timestamp BETWEEN %s AND %s ORDER by timestamp DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(service,error,file,line,timestamp):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO logErrorDB (service,error,file,line,timestamp) VALUES (%s, %s, %s, %s, %s)"
        value = (service,error,file,line,timestamp)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logErrorDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

    def deleteByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logErrorDB WHERE timestamp BETWEEN %s AND %s"
        value = (datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logErrorDB"
        action = sql.execute(connection, query)
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE logErrorDB"
        action = sql.executeOnly(connection, query)
        return action
