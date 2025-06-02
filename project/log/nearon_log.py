path = "/home/connex"

import sys 
import time

sys.path.append(f"{path}/library")
from SynapsisLibrary import times, Scheduler
sys.path.append(f"{path}/project/database")
from query_project_db import IntervalRoutineLogDB, SystemServiceDB
sys.path.append(f"{path}/project/function")
from dbFunction import dbFunction
from logFunction import logFunction
from serviceProjectFunction import ServiceProjectFunction

datetimes = times.getDatetime()
service_name = "nearon_log"
global_variable = {}   
global_variable["logger"] = logFunction.setupLogger(service_name, stream=True)  
global_variable["serviceName"] = service_name
global_variable["logger"].debug(f"Start : {datetimes}")


def main():
    global global_variable

    featureSetting = dbFunction.getFeatureSetting()
    if str(featureSetting["log"]) == "1": 
        routineLogData = IntervalRoutineLogDB.selectEnable()
        intervalData, intervalId = [], []
        for x in range(len(routineLogData)):
            intervalId.append(routineLogData[x]["id"])
            intervalDB = routineLogData[x]["interval"]
            unitDB = routineLogData[x]["unit"]
            intervalLog = 1
            if int(unitDB) == 1:
                intervalLog = int(intervalDB)
            elif int(unitDB) == 2:
                intervalLog = int(intervalDB) * 60
            elif int(unitDB) == 3:
                intervalLog = int(intervalDB) * 60 * 60
            intervalData.append(intervalLog)
        Scheduler.check(intervalData, logFunction.runInternalLog, args=(intervalId, intervalData, global_variable), thread=True)

    else:
        timestamp = times.getDatetime()
        logService = "Feature Routine Internal Log Setting Inactive"
        colorLogService = f"\033[31m{logService}\033[00m"
        SystemServiceDB.updateStatusByName(logService, timestamp, global_variable["serviceName"])
        global_variable["logger"].debug(f"{colorLogService}\n")
        time.sleep(2)


while True:
    if __name__ == "__main__":
        try:
            main()
        except Exception as error:
            ServiceProjectFunction.handlingServiceError("Routine Internal Log", error, global_variable)
