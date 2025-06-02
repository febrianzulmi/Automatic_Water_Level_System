import json
import pandas as pd
import sys

sys.path.append('/home/connex/project/database')
from query_project_db import LogErrorDB
sys.path.append('/home/connex/project/function')
from logFunction import logFunction


class logErrorSystem():
    def deleteRange(datetime1, datetime2):
        try:
            if datetime1 == ' ' and datetime2 == ' ':
                deletes = LogErrorDB.deleteAll()
                message = 'All Error Data'
            else:
                deletes = LogErrorDB.deleteByTime(datetime1,datetime2)
                message = f'Error Data between {datetime1} and {datetime2}'
            if int(deletes) == 1:
                result = {'state':'1', 'message': f'Delete {message} Success!'}
            else:
                result = {'state':'0', 'message': f'Delete {message} Failed!'}

        except Exception as e:
            result = {'state':'0', 'message': f'Delete Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)

    def deleteOne(idLog):
        try:
            delete = LogErrorDB.deleteOne(idLog)
            if int(delete) == 1:
                result  = {'state':'1', 'message': 'Delete Success!'}
            else:
                result = {'state':'0', 'message': 'Delete Failed!'}
        except Exception as e:
            result =  {'state':'0', 'message': f'Delete Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)
    
    def download(deviceSetting, datetimes1, datetimes2):
        try:
            nameFile = deviceSetting['name']
            if datetimes1 == ' ' and datetimes2 == ' ':
                fetch = LogErrorDB.selectAll()
            else:
                fetch = LogErrorDB.selectByTime(datetimes1,datetimes2)
            dataLog = logFunction.downloadLog.logError(fetch)
            filename = "Error Log (Node " + str(nameFile) + ").csv"
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
                service = data['service'][row]
                error = data['error'][row]
                file = data['filename'][row]
                line = data['line'][row]
                timestamp = data['timestamp'][row]
                inserts = LogErrorDB.insert(str(service), str(error), str(file), str(line), timestamp)
            result = {'state':'1', 'message': f'Upload {str(len(data))} Data Success!'}
        except Exception as e:
            result = {'state':'0', 'message':f'Upload Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)