path = "/home/connex"

import sys
import time

sys.path.append(f"{path}/library")
from SynapsisLibrary import times
sys.path.append(f"{path}/project/database")
from query_project_db import LogMonitoringDB, SystemServiceDB
sys.path.append(f"{path}/project/function")
from dbFunction import dbFunction
from logFunction import logFunction
from monitoringFunction import monitoringFunction
from serviceProjectFunction import ServiceProjectFunction


datetimes = times.getDatetime()
service_name = "nearon_alarm"
global_variable = {}   
global_variable["logger"] = logFunction.setupLogger(service_name, stream=True)  
global_variable["serviceName"] = service_name
global_variable["mqttConnection"], global_variable["mqttClient"] = None, None
global_variable["countAlarm"] = 0
global_variable["toleranceConfig"] = 1
global_variable["logger"].debug(f"Start : {datetimes}")

def main():
    global global_variable

    timestamp = times.getDatetime()
    feature_setting = dbFunction.getFeatureSetting()
    alarm_monitor_state = feature_setting["alarmMonitor"]
    interval = feature_setting["alarmMonitorInterval"]
    unit = feature_setting["alarmMonitorUnit"]
    if int(unit) == 1: alarm_monitor_interval = int(interval)
    elif int(unit) == 2: alarm_monitor_interval = int(interval)*60
    elif int(unit) == 3: alarm_monitor_interval = int(interval)*3600  
    else: alarm_monitor_interval = 5 
    
    if str(alarm_monitor_state) == "1":
        alarm_data = LogMonitoringDB.selectAlarm()
        
        if len(alarm_data) > 0: 
            global_variable["countAlarm"] = 0
            global_variable["logger"].debug(f"Alarm Data : {len(alarm_data)} Data") 
            break_state = 0
            for x in range(len(alarm_data)):
                result_alarm = monitoringFunction.runAlarm(x, alarm_data, global_variable)  
                if int(result_alarm["state"]) == 0:
                    break_state = 1
                    break 
                
            if break_state == 1:
                log_service = f"{len(alarm_data)} Alarm Data ({global_variable['countAlarm']} Success) | " \
                            f"{result_alarm['message']['log']} (Status Code {result_alarm['message']['state_code']})"
            else:      
                log_service = f"{len(alarm_data)} Alarm Data ({global_variable['countAlarm']} Success)"
            color_log_service = f"\033[94mResult : {log_service} at {timestamp}\033[00m"
            global_variable["logger"].debug(f"{color_log_service}\n") 
        
        else:
            log_service = "No Alarm Data"
            color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
            SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            global_variable["logger"].debug(f"{color_log_service}\n")
    
    else:
        monitoringFunction.alarmMonitoringProcess.updateAlarmFlag() # --> Update Alarm Flag Menjadi 2 Ketika Alarm Monitoring Setting Inactive
        log_service = "Feature Alarm Monitoring Setting Inactive"
        color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
        SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
        global_variable["logger"].debug(f"{color_log_service}\n")
    
    monitoringFunction.alarmMonitoringProcess.clearAlarmData()  #--> Menghapus Alarm Data & Alarm Tolerance Date Ketika Flag Alarm Sudah 2 
    time.sleep(alarm_monitor_interval)       
    
    
while True:
    if __name__ == "__main__": 
        try:
            main()
        except Exception as error:
            ServiceProjectFunction.handlingServiceError("Alarm Monitoring", error, global_variable)
