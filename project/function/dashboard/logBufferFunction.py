import json
import pandas as pd
import sys

sys.path.append('/home/connex/project/database')
from query_project_db import LogMonitoringDB


class logBuffer():
    def deleteRange(datetime1, datetime2):
        try:
            if datetime1 == ' ' and datetime2 == ' ':
                deletes = LogMonitoringDB.deleteBufferAll()
                message = 'All Buffer Data'
            else:
                deletes = LogMonitoringDB.deleteBufferByTime(datetime1, datetime2)
                message = f'Buffer Data between {datetime1} and {datetime2}'
            
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
                fetch = LogMonitoringDB.selectBufferAll()
            else:
                fetch = LogMonitoringDB.selectBufferByTime(datetimes1, datetimes2)
        
            dataLog = []
            header = ['data', 'state', 'buffer', 'type', 'attempt', 'timestamp']
            dataLog.append(header)
            for row in range(len(fetch)):
                data = []
                data.append(fetch[row]['data'])
                data.append(fetch[row]['state'])
                if int(fetch[row]['buffer']) == 0:
                    buffer = "Yes"
                elif int(fetch[row]['buffer']) == 1:
                    buffer = "No"
                else:
                    buffer = "Done"
                data.append(buffer)
                typeData = fetch[row]['tipe']
                if typeData == 1:
                    data.append("Normal")
                elif typeData == 9:
                    data.append("Routine")
                elif typeData == 10:
                    data.append("Daily")
                elif typeData == 11:
                    data.append("Replace")
                elif typeData == 4:
                    data.append("Alarm Error")
                elif typeData == 3:
                    data.append("Alarm Max")
                elif typeData == 2:
                    data.append("Alarm Min")
                data.append(fetch[row]['attempt'])
                data.append(fetch[row]['timestamp'])
                dataLog.append(data)
            filename = "Buffer Log (" + str(nameFile) + ").csv"
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
                attempt = data['attempt'][row]
                attempt = int(attempt)
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
                elif type == 'Replace':
                    type = 11
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