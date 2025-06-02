path = "/home/connex"

import sys
import time

sys.path.append(f"{path}/library")
from SynapsisLibrary import times
sys.path.append(f"{path}/project/function")
from httpProtocolFunction import httpProtocolFunction
from logFunction import logFunction
from serviceProjectFunction import ServiceProjectFunction
sys.path.append(f"{path}/project/databse")
from query_project_db import SystemServiceDB


datetimes = times.getDatetime()
service_name = "nearon_auth"
global_variable = {}   
global_variable["logger"] = logFunction.setupLogger(service_name, stream=True)  
global_variable["serviceName"] = service_name
global_variable["logger"].debug(f"Start : {datetimes}")


def main():
    global global_variable

    timestamp = times.getDatetime()
    logService = httpProtocolFunction.getAuthentication(timestamp, global_variable)
    SystemServiceDB.updateStatusByName(logService, timestamp, global_variable["serviceName"])
    if "Device Already Authentication" in logService or "Success Authentication" in logService:
        time.sleep(60)
    else:
        time.sleep(10)


while True:
    if __name__ == "__main__": 
        try:
            main()
        except Exception as error:
            ServiceProjectFunction.handlingServiceError("Authentication", error, global_variable)