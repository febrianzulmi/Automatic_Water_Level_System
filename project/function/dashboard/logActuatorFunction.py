import json
import pandas as pd
import sys


sys.path.append('/home/connex/project/database')
from query_project_db import LogActuatorDB, ActuatorListDB
sys.path.append('/home/connex/project/function')
from logFunction import logFunction


class logActuatorSystem():
    def deleteRange(datetime1, datetime2):
        try:
            if datetime1 == ' ' and datetime2 == ' ':
                deletes = LogActuatorDB.deleteAll()
                message = 'All Actuators Data'
            else:
                deletes = LogActuatorDB.deleteByTime(datetime1, datetime2)
                message = f'Actuator Data between {datetime1} and {datetime2}'
        
            if int(deletes) == 1:
                result = {'state':'1', 'message': f'Delete {message} Success!'}
            else:
                result = {'state':'0', 'message': f'Delete {message} Failed!'}
        except Exception as e:
            result = {'state':'0', 'message': f'Delete Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)
    
    def deleteOne(id):
        try:
            deletes = LogActuatorDB.deleteOne(id)
            if int(deletes) == 1:
                result  = {'state':'1', 'message': 'Delete Success!'}
            else:
                result = {'state':'0', 'message': 'Delete Failed'}
        
        except Exception as e:
            result = {'state':'0', 'message':f'Update Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)
    
    def download(deviceSetting, datetimes1, datetimes2):
        try:
            nameFile = deviceSetting['name']
            if datetimes1 == ' ' and datetimes2 == ' ':
                fetch = LogActuatorDB.selectAll()
            else:
                fetch = LogActuatorDB.selectByTime(datetimes1, datetimes2)
            dataLog = logFunction.downloadLog.logActuator(fetch)
            filename = f"Actuator Log (Node {nameFile}).csv"
            message = {'state':'1', 'message': 'Download Success'}
            result = {'message': message, 'dataLog': dataLog, 'filename': filename} 
        except Exception as e:
            message = {'state':'0', 'message': f'Download Failed! Sorry, there was an issue updating - {str(e)}'}
            result = {'message': message, 'dataLog': [], 'filename':''} 
        return result
    
    def uploadFile(uploaded_file):
        try:
            data = pd.read_csv(uploaded_file, sep=';')
            if 'actuator_name' not in data.columns:
                result = {"state": "0", "message": f"Upload Failed! CSV file is missing 'actuator_name' column"}
                return json.dumps(result)
            for row in range(len(data)):
                actuator_name = data.loc[row, 'actuator_name']
                get_actuator = ActuatorListDB.selectByName(actuator_name)
                if get_actuator:  # Pastikan hasil query tidak kosong
                    id_actuator = get_actuator[0]['id']  # Ambil nilai 'id' dari hasil query
                    value = str(data.loc[row, 'value'])
                    action = data.loc[row, 'action']
                    if action == 'Boot':
                        action = 0
                    elif action == 'Server Remote':
                        action = 1
                    elif action == 'Schedule':
                        action = 2
                    else:
                        action = 3
                timestamp = data.loc[row, 'timestamp']
                inserts = LogActuatorDB.insert(id_actuator, value, action, timestamp)
            result = {'state':'1', 'message': f'Upload {str(len(data))} Data Success!'}
        except Exception as e:
            result = {'state':'0', 'message':f'Update Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)


