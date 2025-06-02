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

class CalibrateSampleDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT calibrateSampleDB.*, calibrateFormulaDB.id as formulaId, calibrateFormulaDB.name as formulaName FROM calibrateSampleDB join calibrateFormulaDB on calibrateSampleDB.formula_id=calibrateFormulaDB.id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByFormula(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT calibrateSampleDB.*, calibrateFormulaDB.id as formulaId, calibrateFormulaDB.name FROM calibrateSampleDB join calibrateFormulaDB on calibrateSampleDB.formula_id=calibrateFormulaDB.id where calibrateSampleDB.formula_id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(formula,value_sample,value_reference):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO calibrateSampleDB(formula_id,value_sample,value_reference) VALUES (%s,%s,%s)"
        value = (formula,value_sample,value_reference)
        action = sql.execute(connection, query, value)
        return action

    def update(formula_id,sample,reference,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE calibrateSampleDB set formula_id=%s, value_sample=%s, value_reference=%s WHERE id=%s"
        value = (formula_id,sample,reference,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM calibrateSampleDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
    