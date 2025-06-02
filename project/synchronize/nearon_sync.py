path = "/home/connex"

import sys
import time

sys.path.append(f"{path}/library")
from SynapsisLibrary import times
sys.path.append(f"{path}/project/database")
from query_project_db import SystemServiceDB
sys.path.append(f"{path}/project/function")
from dbFunction import dbFunction
from logFunction import logFunction
from serverFunction import serverFunction
from serviceProjectFunction import ServiceProjectFunction
from synchronizeFunction import synchronizeFunction


datetimes = times.getDatetime()
service_name = "nearon_sync"
global_variable = {}   
global_variable["logger"] = logFunction.setupLogger(service_name, stream=True)  
global_variable["serviceName"] = service_name
global_variable["mqttConnection"], global_variable["mqttClient"] = None, None
global_variable["flagRebootSync"] = 0
global_variable["updateReboot"] = 0
global_variable["topicSubscriptionState"] = {}
global_variable["topicSubscriptionState"]["node"] = {"topic": "node", "state": 0, "setting": ""}
global_variable["topicSubscriptionState"]["sensor"] = {"topic": "sensor", "state": 0, "setting": ""} 
global_variable["topicSubscriptionState"]["actuator"] = {"topic": "actuator", "state": 0, "setting": ""}


def main():
    global global_variable

    feature_setting = dbFunction.getFeatureSetting()
    for x in global_variable["topicSubscriptionState"]:
        parameter = x.capitalize()
        global_variable["topicSubscriptionState"][x]["setting"] = feature_setting[f"sync{parameter}"]
    synchronizeState = feature_setting["synchronize"]
    interval = feature_setting["synchronizeInterval"]
    unit = feature_setting["synchronizeUnit"]
    if int(unit) == 1:
        synchronizeInterval = int(interval)
    elif int(unit) == 2:
        synchronizeInterval = int(interval)*60
    elif int(unit) == 3:    
        synchronizeInterval = int(interval)*3600  
    else:
        synchronizeInterval = 5 

    if str(synchronizeState) == "1":
        deviceSetting = dbFunction.getDeviceSetting()
        serverConfig = serverFunction.getServerConfig()
        synchronizeFunction.runSync(deviceSetting, feature_setting, serverConfig, global_variable)
    else:
        timestamp = times.getDatetime()
        logService = "Feature Synchronize Setting Inactive"
        colorLogService = f"\033[31m{logService} at {timestamp}\033[00m"
        global_variable["logger"].debug(f"{colorLogService}\n")
        SystemServiceDB.updateStatusByName(logService, timestamp, global_variable["serviceName"])
      
    time.sleep(synchronizeInterval)


while True:
    if __name__ == "__main__": 
        try:
            main()
        except Exception as error:
            ServiceProjectFunction.handlingServiceError("Synchronize", error, global_variable)