import json
import pandas as pd
import sys

sys.path.append('/home/connex/project/database')
from query_project_db import LogMonitoringDB
sys.path.append('/home/connex/project/function')
from logFunction import logFunction


class logMonitoring():
    def deleteRange(datetime1, datetime2):
        try:
            if datetime1 == ' ' and datetime2 == ' ':
                deletes = LogMonitoringDB.deleteMonitorAll()
                message = 'All Monitoring Data'
            else:
                deletes = LogMonitoringDB.deleteMonitorByTime(datetime1, datetime2)
                print(deletes)
                message = f'Monitoring Data between {datetime1} and {datetime2}'
            
            if int(deletes) == 1:
                result = {'state':'1', 'message': f'Delete {message} Success!'}
            else:
                result = {'state':'0', 'message': f'Delete {message} Failed!'}
        except Exception as e:
            result = {'state':'0', 'message': f'Delete Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)

    def deleteOne(idLog):
        try:
            delete = LogMonitoringDB.deleteOne(idLog)
            if int(delete) == 1:
                result  = {'state':'1', 'message': 'Delete Success!'}
            else:
                result = {'state':'0', 'message': 'Delete Failed!'}
        except Exception as e:
            result = {'state':'0', 'message': f'Delete Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)

    def download(deviceSetting, datetimes1, datetimes2):
        try:
            nameFile = deviceSetting['name']
            if datetimes1 == ' ' and datetimes2 == ' ':
                fetch = LogMonitoringDB.selectMonitorAll()
            else:
                fetch = LogMonitoringDB.selectMonitorByTime(datetimes1, datetimes2)
            dataLog = logFunction.downloadLog.logMonitoring(fetch)
            filename = "Monitoring Log (" + str(nameFile) + ").csv"
            message = {'state':'1', 'message': 'Download Success'}
            result = {'message': message, 'dataLog': dataLog, 'filename': filename} 
        except Exception as e:
            message = {'state':'0', 'message': f'Download Failed! Sorry, there was an issue updating - {str(e)}'}
            result = {'message': message, 'dataLog': [], 'filename':''} 
        return result

    def uploadFile(uploaded_file):
        try:
            data = pd.read_csv(uploaded_file, sep=';')
            for row in range(len(data)):
                datas = data['data'][row]
                datas = datas.replace("'","\"")
                buffer = data['buffer'][row]
                attempt = int(data['attempt'][row])
                state = data['state'][row]
                state = int(state)
                if buffer == 'Yes':
                    buffer = 0
                elif buffer == 'No':
                    buffer = 1
                else:
                    buffer = 2
                type = data['type'][row]
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
                timestamp = data['timestamp'][row]
                inserts = LogMonitoringDB.insert(datas,state,buffer,timestamp,type,attempt)
            result = {'state':'1', 'message': f'Upload {str(len(data))} Data Success!'}
        except Exception as e:
            result = {'state':'0', 'message': f'Update Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)
