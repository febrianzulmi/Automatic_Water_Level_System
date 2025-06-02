path = "/home/connex"

import sys
import time

sys.path.append(f"{path}/library")
from SynapsisLibrary import times
sys.path.append(f"{path}/project/function")
from dbFunction import dbFunction
from logFunction import logFunction
from monitoringFunction import monitoringFunction
from serverFunction import serverFunction
from serviceProjectFunction import ServiceProjectFunction
sys.path.append(f"{path}/project/database")
from query_project_db import LogMonitoringDB, SystemServiceDB


datetimes = times.getDatetime()
service_name = "nearon_buffer"
global_variable = {}   
global_variable["logger"] = logFunction.setupLogger(service_name, stream=True)  
global_variable["serviceName"] = service_name
global_variable["mqttConnection"], global_variable["mqttClient"] = None, None
global_variable["countBuffer"] = 0
global_variable["logger"].debug(f"Start : {datetimes}")

def main():
    global global_variable

    timestamp = times.getDatetime()
    feature_setting = dbFunction.getFeatureSetting()
    buffer_state = feature_setting["bufferMonitor"]
    interval = feature_setting["bufferMonitorInterval"]
    unit = feature_setting["bufferMonitorUnit"]
    if int(unit) == 1: buffer_interval = int(interval)
    elif int(unit) == 2: buffer_interval = int(interval)*60
    elif int(unit) == 3: buffer_interval = int(interval)*3600
    else: buffer_interval = 5

    if int(buffer_state) == 1:
        buffer_data_list = LogMonitoringDB.selectBuffer()
        
        if len(buffer_data_list) > 0:
            server_config = serverFunction.getServerConfig()
            global_variable["countBuffer"] = 0
            global_variable["logger"].debug(f"Buffer : {len(buffer_data_list)} Data")
            break_state = 0

            for x in range(len(buffer_data_list)):
                result_buffer = monitoringFunction.runBuffer(x, buffer_data_list, server_config, global_variable)
                if int(result_buffer["state"]) == 0:
                    break_state = 1
                    break
            
            if break_state == 1:
                log_service = f"{len(buffer_data_list)} Buffer Data ({global_variable['countBuffer']} Success) | " \
                            f"{result_buffer['message']['log']} (Status Code {result_buffer['message']['state_code']})"
            else:      
                log_service = f"{len(buffer_data_list)} Buffer Data ({global_variable['countBuffer']} Success)"    
            
            color_log_service = f"\033[94mResult : {log_service} at {timestamp}\033[00m"
            SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            global_variable["logger"].debug(f"{color_log_service}\n")
        
        else:
            log_service = "No Buffer Data"
            color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
            SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            global_variable["logger"].debug(f"{color_log_service}\n")
    
    else:
        log_service = "Feature Buffer Monitoring Setting Inactive"
        color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
        SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
        global_variable["logger"].debug(f"{color_log_service}\n")
    
    time.sleep(buffer_interval)                


while True:
    if __name__ == "__main__": 
        try:
            main()
        except Exception as error:
            ServiceProjectFunction.handlingServiceError("Buffer Monitoring", error, global_variable)
