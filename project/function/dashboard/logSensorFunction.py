import json
import pandas as pd
import sys

sys.path.append('/home/connex/project/database')
from query_project_db import LogSensorDB, SensorListDB
sys.path.append('/home/connex/project/function')
from logFunction import logFunction


class logSensor():
    def upload(uploaded_file):
        try:
            data = pd.read_csv(uploaded_file, sep=';')
            if 'sensor_id' not in data.columns:
                result = {"state": "0", "message": f"Upload Failed! CSV file is missing 'sensor_id' column"}
                return json.dumps(result)
            for row in range(len(data)):
                sensor_id_col = data.loc[row, 'sensor_id']
                get = SensorListDB.selectOne(sensor_id_col)
                if get:
                    id = get[0]['id']
                    data_sensor = str(data.loc[row, 'data'])
                    type = data.loc[row, 'type']
                    if type == 'Normal':
                        type = 1
                    elif type == 'Routine':
                        type = 9
                    elif type == 'Daily':
                        type = 10
                    elif type == 'Alarm Error':
                        type = 4
                    elif type == 'Alarm Max':
                        type = 3
                    elif type == 'Alarm Min':
                        type = 2
                    timestamp = data.loc[row, 'timestamp']
                    inserts = LogSensorDB.insert(id, data_sensor, type, timestamp)
            result = {'state':'1', 'message': f'Upload {str(len(data))} Data Success!'}
        except Exception as e:
            result = {'state':'0', 'message': f'Upload Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)
    
    def deleteRange(sensor_id, sensor_name, datetime1, datetime2):
        try:
            if sensor_id == 'all' and datetime1 == ' ' and datetime2 == ' ':
                deletes = LogSensorDB.deleteAll()
                message = 'All Sensors Data'
            elif sensor_id != 'all' and datetime1 == ' ' and datetime2 == ' ':
                deletes = LogSensorDB.deleteBySensor(sensor_id)
                message = f'All Sensors {sensor_name} Data'
            else:
                deletes = LogSensorDB.deleteByTime(sensor_id, datetime1, datetime2)
                if sensor_id == 'all':
                    message = f'All Sensors Data between {datetime1} and {datetime2 }'
                else:
                    message = f'Sensors {sensor_name} Data between {datetime1} and {datetime2 }'  
            if int(deletes) == 1:
                result = {'state':'1', 'message': f'Delete {message} Success!'}
            else:
                result = {'state':'0', 'message': f'Delete {message} Failed!'}
        except Exception as e:
            result = {'state':'0', 'message': f'Delete Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)

    def deleteOne(idLog):
        try:
            delete = LogSensorDB.deleteOne(idLog)
            if int(delete) == 1:
                result = {'state':'1', 'message': 'Delete Successful!'}
            else:
                result = {'state':'0', 'message': 'Delete Failed!'}
        except Exception as e:
            result = {'state':'0', 'message':f'Update Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)
    
    def download(deviceSetting, sensor_id, datetime1, datetime2):
        try:
            nameFile = deviceSetting['name']
            if sensor_id == 'all' and datetime1 == ' ' and datetime2 == ' ':
                fetch = LogSensorDB.selectAll()
            elif sensor_id != 'all' and datetime1 == ' ' and datetime2 == ' ':
                fetch = LogSensorDB.selectBySensor(sensor_id)
            else:
                fetch = LogSensorDB.selectByTime(sensor_id, datetime1, datetime2)
            dataLog = logFunction.downloadLog.logSensor(fetch)
            filename = "Sensor Log (" + str(nameFile) + ").csv"
            message = {'state':'1', 'message': 'Download Success'}
            result = {'message': message, 'dataLog': dataLog, 'filename': filename} 
        except Exception as e:
            message = {'state':'0', 'message': f'Download Failed! Sorry, there was an issue updating - {str(e)}'}
            result = {'message': message, 'dataLog': [], 'filename':''} 
        return result
        
    