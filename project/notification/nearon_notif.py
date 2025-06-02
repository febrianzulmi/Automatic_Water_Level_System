path = "/home/connex"

import sys
import time

sys.path.append(f"{path}/library")
from SynapsisLibrary import times
sys.path.append(f"{path}/project/function")
from dbFunction import dbFunction
from logFunction import logFunction
from notificationFunction import notificationFunction
from serverFunction import serverFunction
from serviceProjectFunction import ServiceProjectFunction
sys.path.append(f"{path}/project/database")
from query_project_db import SystemServiceDB, LogNotifDB


datetimes = times.getDatetime()
service_name = "nearon_notif"
global_variable = {}   
global_variable["logger"] = logFunction.setupLogger(service_name, stream=True)  
global_variable["serviceName"] = service_name
global_variable["mqttConnection"], global_variable["mqttClient"] = None, None
global_variable["countNotification"] = 0

def main():
    global global_variable
    
    timestamp = times.getDatetime()
    feature_setting = dbFunction.getFeatureSetting()
    notification_state = feature_setting["notification"]
    interval = feature_setting["notificationInterval"]
    unit = feature_setting["notificationUnit"]
    if int(unit) == 1: notification_interval = int(interval)
    elif int(unit) == 2: notification_interval = int(interval)*60
    elif int(unit) == 3: notification_interval = int(interval)*3600  
    else: notification_interval = 5 
    
    if int(notification_state) == 1:
        notification_data = LogNotifDB.selectByState()
    
        if len(notification_data) > 0:
            server_config = serverFunction.getServerConfig()
            global_variable["countNotification"] = 0
            global_variable["logger"].debug(f"Notification : {len(notification_data)} Data")
            break_state = 0
            
            for x in range(len(notification_data)):
                result_notification = notificationFunction.runNotification(x, notification_data, server_config, global_variable)  
                if int(result_notification["state"]) == 0:
                    break_state = 1
                    break
                
            if break_state == 1:
                log_service = f"{len(notification_data)} Notification Data ({global_variable['countNotification']} Success) | " \
                            f"{result_notification['message']['log']} (Status Code {result_notification['message']['state_code']})"
            else:      
                log_service = f"{len(notification_data)} Notification Data ({global_variable['countNotification']} Success)"    
            
            color_log_service = f"\033[94mResult : {log_service} at {timestamp}\033[00m"
            SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            global_variable["logger"].debug(f"{color_log_service}\n")
    
        else:
            log_service = "No Notification Data"
            color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
            global_variable["logger"].debug(f"{color_log_service}\n")
            SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
    
    else:
        log_service = "Feature Notification Setting Inactive"
        color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
        global_variable["logger"].debug(f"{color_log_service}\n")
        SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])       
    
    time.sleep(notification_interval)   


while True:
    if __name__ == "__main__": 
        try:
            main()
        except Exception as error:
            ServiceProjectFunction.handlingServiceError("Notification", error, global_variable)
