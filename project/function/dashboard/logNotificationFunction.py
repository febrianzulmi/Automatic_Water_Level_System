import json
import pandas as pd
import sys

sys.path.append('/home/connex/project/database')
from query_project_db import LogNotifDB
sys.path.append('/home/connex/project/function')
from logFunction import logFunction


class logNotification():
    def deleteRange(datetime1, datetime2):
        try:
            if datetime1 == ' ' and datetime2 == ' ':
                deletes = LogNotifDB.deleteAll()
                message = 'All Notification Data'
            else:
                deletes = LogNotifDB.deleteByTime(datetime1,datetime2)
                message = f'Notification Data between {datetime1} and {datetime2}'
            
            if int(deletes) == 1:
                result = {'state':'1', 'message': f'Delete {message} Success!'}
            else:
                result = {'state':'0', 'message': f'Delete {message} Failed!'}
        except Exception as e:
            result = {'state':'0', 'message': f'Delete Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)

    def deleteOne(idLog):
        try:
            delete = LogNotifDB.deleteOne(idLog)
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
                fetch = LogNotifDB.selectAll()
            else:
                fetch = LogNotifDB.selectByTime(datetimes1,datetimes2)
            dataLog = logFunction.downloadLog.logNotification(fetch)
            filename = "Notificaton Log (Node " + str(nameFile) + ").csv"
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
                types = data['type'][row]
                sensorData = data['sensor'][row]
                conditionData = data['condition'][row]
                notif = data['notif'][row]
                subject = data['subject'][row]
                message = data['message'][row]
                state = data['state'][row]
                create_time = data['create_time'][row]
                send_time = data['send_time'][row]
                if pd.isna(send_time) or send_time == "-":
                    inserts = LogNotifDB.insert(types, sensorData, conditionData, notif, subject, message, state, create_time)
                else:
                    inserts = LogNotifDB.insertAll(types, sensorData, conditionData, notif, subject, message, state, create_time, send_time)
            result = {'state':'1', 'message': f'Upload {str(len(data))} Data Success!'}
        except Exception as e:
            result = {'state':'0', 'message':f'Update Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)