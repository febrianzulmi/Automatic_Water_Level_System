path = "/home/connex"

import sys
import time

sys.path.append(f"{path}/library")
from SynapsisLibrary import times, Scheduler
sys.path.append(f"{path}/project/database")
from query_project_db import IntervalRoutineMonitorDB, SystemServiceDB
sys.path.append(f"{path}/project/function")
from dbFunction import dbFunction
from logFunction import logFunction
from monitoringFunction import monitoringFunction
from serviceProjectFunction import ServiceProjectFunction

from icecream import ic

datetimes = times.getDatetime()
service_name = "nearon_routine"
global_variable = {}   
global_variable["logger"] = logFunction.setupLogger(service_name, stream=True)  
global_variable["serviceName"] = service_name
global_variable["mqttConnection"], global_variable["mqttClient"] = None, None
global_variable["logger"].debug(f"Start : {datetimes}")


def main():
    global global_variable

    ### Get Configuration ###
    feature_setting = dbFunction.getFeatureSetting()
    ####################

    if str(feature_setting["routineMonitor"]) == "1":
        routineMonitorData = IntervalRoutineMonitorDB.selectEnable()
        intervalData, intervalId = [], []
        for x in range(len(routineMonitorData)):
            intervalId.append(routineMonitorData[x]["id"])
            intervalDB = routineMonitorData[x]["interval"]
            unitDB = routineMonitorData[x]["unit"]
            intervalMonitor = 1
            if str(unitDB) == "1":
               intervalMonitor = int(intervalDB)
            elif str(unitDB) == "2":
               intervalMonitor = int(intervalDB) * 60
            elif str(unitDB) == "3":
               intervalMonitor = int(intervalDB) * 60 * 60
            intervalData.append(intervalMonitor)  
        Scheduler.check(intervalData, monitoringFunction.runMonitoring, args=(intervalId, intervalData, global_variable), thread=True)    
    else:
        timestamp = times.getDatetime()
        logService = "Feature Routine Monitoring Setting Inactive"
        colorLogService = f"\033[31m{logService} at {timestamp}\033[00m"
        SystemServiceDB.updateStatusByName(logService, timestamp, global_variable["serviceName"])
        global_variable["logger"].debug(f"{colorLogService}\n")
        time.sleep(2)


while True:
      if __name__ == "__main__":
        try:
            main()
        except Exception as error:
            ServiceProjectFunction.handlingServiceError("Routine Monitoring", error, global_variable)
