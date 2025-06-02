import datetime
import logging
import pyexcel as pe
import sys

sys.path.append('/home/connex/library')
from SynapsisLibrary import times
sys.path.append('/home/connex/project/database')
from query_project_db import LogSensorDB, LogActuatorDB, LogNotifDB, LogErrorDB, LogMonitoringDB, SystemServiceDB, ActuatorListDB
sys.path.append("/home/connex/project/function/sensor")
from collectDataSensorFunction import CollectDataSensorFunction
sys.path.append('/home/connex/project/function')
from dbFunction import dbFunction


class logFunction():
    def runInternalLog(num, intervalId, intervalData, globalVariable):
        timestamp = times.getDatetime()
        sensorData = CollectDataSensorFunction.byLogInterval(intervalId[num]) 
        if sensorData['numSensor'] > 0:
            countLog = 0
            for x in range(sensorData['numSensor']):
                sensorID = sensorData['id'][x]
                sensorValue = sensorData['sensorValue'][x]
                insertLog = LogSensorDB.insert(sensorID, sensorValue, "9", timestamp)
                if int(insertLog) == 1:
                    countLog += 1
            logService = "{} of {} Sensors Success Routine Internal Log Interval ({} Seconds)".format(sensorData['numSensor'], countLog, intervalData[num])
            if int(sensorData['numSensor']) ==  int(countLog):
                colorLogService = "\033[92m{} at {}\033[00m".format(logService, timestamp)
            elif int(sensorData['numSensor']) >  int(countLog):
                colorLogService = "\033[93m{} at {}\033[00m".format(logService, timestamp)
            else:
                colorLogService = "\033[92m{} at {}\033[00m".format(logService, timestamp)    
            print("{}\n".format(colorLogService))   
        else:
            logService = "No Sensor with Routine Internal Log Interval {} Seconds".format(intervalData[num])
            colorLogService = "\033[31m{}\033[00m".format(logService)
            print("{}\n".format(colorLogService))
        SystemServiceDB.updateStatusByName(logService, timestamp, globalVariable['serviceName'])
        return  sensorData #1
    
    def setupLogger(name, stream=False):
        formatter = logging.Formatter("%(asctime)s | {} | %(levelname)s | %(message)s".format(name))
        file_handler = logging.FileHandler(f"/home/connex/log/system/{name}.log", mode='a')
        file_handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        if stream == True: 
            console_handler = logging.StreamHandler()
            logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        return logger
    
    class backupFunction():
        def runBackup():
            datetimes = times.now()
            day = datetimes.day
            months = datetimes.month
            
            if int(months) == 1:
                month = 12
            else:
                month = months - 1

            year = datetimes.year
            date1 = datetime.datetime(year, month, 1, 0, 0, 0)
            periode = date1.strftime("%B %Y")
            date1 = times.convertTimeToString(date1)
            date2 = datetime.datetime(year, months, 1, 0, 0, 0)
            date2 = times.convertTimeToString(date2)

            if int(day) == 1:
                print("==== " + times.getDatetime() + " ====")
                print("Backup Sensor Log Periode", periode)
                logFunction.backupFunction.backupLog("sensor", periode, date1, date2)
                print("Backup Actuator Log Periode", periode)
                logFunction.backupFunction.backupLog("actuator", periode, date1, date2)
                print("Backup Notif Log Periode", periode)
                logFunction.backupFunction.backupLog("notif", periode, date1, date2)
                print("Backup Error Log Periode", periode)
                logFunction.backupFunction.backupLog("error", periode, date1, date2)
                print("Backup Monitoring Log Periode", periode)
                logFunction.backupFunction.backupLog("monitoring", periode, date1, date2)
                print("============================")
                print("")
    
        def backupLog(log, periode, date1, date2):
            deviceSetting = dbFunction.getDeviceSetting()
            if log == 'sensor':
                fetch = LogSensorDB.selectByTime("all", date1, date2)
                filename = "Sensor Log (" + str(deviceSetting['name']) + ") - " + periode + ".csv"
                datas = logFunction.downloadLog.logSensor(fetch)
                pe.save_as(array=datas, dest_file_name="/home/connex/log/backup/sensor/"+filename, dest_delimiter=';')
                LogSensorDB.deleteByTime('', date1, date2)
            elif log == 'actuator':
                fetch = LogActuatorDB.selectByTime(date1, date2)
                filename = "Actuator Log (" + str(deviceSetting['name']) + ") - " + periode + ".csv"
                datas = logFunction.downloadLog.logActuator(fetch)
                pe.save_as(array=datas, dest_file_name="/home/connex/log/backup/actuator/"+filename, dest_delimiter=';')
                LogActuatorDB.deleteByTime(date1, date2)
            elif log == 'notif':
                fetch = LogNotifDB.selectByTime(date1, date2)
                filename = "Notification Log (" + str(deviceSetting['name']) + ") - " + periode + ".csv"
                datas = logFunction.downloadLog.logNotification(fetch)
                pe.save_as(array=datas, dest_file_name="/home/connex/log/backup/notification/"+filename, dest_delimiter=';')
                LogNotifDB.deleteByTime(date1, date2)
            elif log == 'error':
                fetch = LogErrorDB.selectByTime(date1, date2)
                filename = "Error Log (" + str(deviceSetting['name']) + ") - " + periode + ".csv"
                datas = logFunction.downloadLog.logError(fetch)
                pe.save_as(array=datas, dest_file_name="/home/connex/log/backup/error/"+filename, dest_delimiter=';')
                LogErrorDB.deleteByTime(date1, date2)
            elif log == 'monitoring':
                fetch = LogMonitoringDB.selectMonitorWithoutBufferByTime(date1, date2)
                filename = "Monitoring Log (" + str(deviceSetting['name']) + ") - " + periode + ".csv"
                datas = logFunction.downloadLog.logMonitoring(fetch)
                pe.save_as(array=datas, dest_file_name="/home/connex/log/backup/monitoring/"+filename, dest_delimiter=';')
                LogMonitoringDB.deleteMonitorWithoutBufferByTime(date1, date2)
        
    class downloadLog():
        def logSensor(log):
            dataLog = []
            header = ['sensor_id', 'data', 'type', 'timestamp']
            dataLog.append(header)
            for row in log:
                data = []
                sensor_id = row['sensor_id']
                data.append(sensor_id)
                data_sensor = row['data']
                data.append(data_sensor)
                typeDataSensor = row['tipe']
                if str(typeDataSensor) == "1":
                    typeDataSensor = "Normal"
                elif str(typeDataSensor) == "9":
                    typeDataSensor = "Routine"
                elif str(typeDataSensor) == "10":
                    typeDataSensor = "Daily"
                elif str(typeDataSensor) == "4":
                    typeDataSensor = "Alarm Error"
                elif str(typeDataSensor) == "3":
                    typeDataSensor = "Alarm Max"
                elif str(typeDataSensor) == "2":
                    typeDataSensor = "Alarm Min"
                data.append(typeDataSensor)
                data.append(row['timestamp'])
                dataLog.append(data) 
            return dataLog
        
        def logMonitoring(log):
            dataLog = []
            header = ['data', 'state', 'buffer', 'type', 'attempt', 'timestamp']
            dataLog.append(header)
            for row in range(len(log)):
                data = []
                data.append(log[row]['data'])
                data.append(log[row]['state'])
                if str(log[row]['buffer']) == "0":
                    buffer = "Yes"
                elif str(log[row]['buffer']) == "1":
                    buffer = "No"
                else:
                    buffer = "Done"
                data.append(buffer)
                typeData = log[row]['tipe']
                if str(typeData) == "1":
                    typeData = "Normal"
                elif str(typeData) == "9":
                    typeData = "Routine"
                elif str(typeData) == "10":
                    typeData = "Daily"
                elif str(typeData) == "4":
                    typeData = "Alarm Error"
                elif str(typeData) == "3":
                    typeData = "Alarm Max"
                elif str(typeData) == "2":
                    typeData = "Alarm Min"
                data.append(typeData)
                data.append(log[row]['attempt'])
                data.append(log[row]['timestamp'])
                dataLog.append(data)
            return dataLog
        
        def logActuator(log):
            dataLog = []
            header = ['actuator_name', 'value', 'action', 'timestamp']
            dataLog.append(header)
            for row in log:
                data = []
                actuator_list_id = row['actuator_list_id']
                actuator_name = ActuatorListDB.selectById(actuator_list_id)[0]['name']
                data.append(actuator_name)
                data.append(row['value'])
                action = row['action']
        
                if str(action) == "0":
                    action = "Boot"
                elif str(action) == "1":
                    action = "Server Remote"
                elif str(action) == "2":
                    action = "Schedule"
                else:
                    action = "Local Remote"
        
                data.append(action)
                data.append(row['action_at'])
                dataLog.append(data)
            return dataLog
        
        def logNotification(log):
            dataLog = []
            header = ['type', 'sensor', 'condition', 'notif', 'subject', 'message', 'state', 'create_time', 'send_time']
            dataLog.append(header)
            for row in range(len(log)):
                data = []
                data.append(log[row]['type'])
                data.append(log[row]['sensor'])
                data.append(log[row]['conditions'])
                data.append(log[row]['notif'])
                data.append(log[row]['subject'])
                data.append(log[row]['message'])
                data.append(log[row]['state'])
                data.append(log[row]['create_time'])
                data.append(log[row]['send_time'])
                dataLog.append(data)
            return dataLog
        
        def logError(log):
            dataLog = []
            header = ['service', 'error', 'filename', 'line', 'timestamp']
            dataLog.append(header)
            for row in range(len(log)):
                data = []
                data.append(log[row]['service'])
                data.append(log[row]['error'])
                data.append(log[row]['file'])
                data.append(log[row]['line'])
                data.append(log[row]['timestamp'])
                dataLog.append(data)
            return dataLog