number = 1

import sys
import time

sys.path.append('/home/connex/library')
from SynapsisLibrary import times
sys.path.append('/home/connex/project/database')
from query_project_db import ActuatorDB, SystemServiceDB
sys.path.append('/home/connex/project/function')
from actuatorFunction import actuatorFunction
from actuatorLibrary import actuatorAC
from serviceProjectFunction import ServiceProjectFunction
from logFunction import logFunction

global_variable = {}
global_variable["Number"] = number
global_variable["serviceName"] = f"actuator{number}"
global_variable["flag"] = 0
global_variable["logger"] = logFunction.setupLogger(global_variable["serviceName"], stream=True)

timestamp = times.getDatetime()
global_variable["logger"].debug(f"Start : {timestamp}")
first = 0

def actionActuator(actuator_custom_id, value):
    status = actuatorAC(actuator_custom_id, value)
    return status

def main():
    global first

    now2 = times.now()
    timestamp = now2.strftime("%Y-%m-%d %H:%M:%S")
    now2 = int((now2.minute*60)+now2.second)

    actuatorData = ActuatorDB.selectByNumber(number)
    actuator_list_id = actuatorData[0]["id"]
    if len(actuatorData) == 1:
        for i in actuatorData:
            actuator_custom_id = i['actuator_custom_id']
            actuator_name = i['name']
            server_value = i['server_value']
            server_sync_at = i['server_sync_at']
            last_server_value = i['last_server_value']
            last_server_sync_at = i['last_server_sync_at']
        global_variable["logger"].debug(f"Actuator : {actuator_name} ( {actuator_custom_id} )")
        global_variable["logger"].debug(f"{timestamp}".center(34, '-'))

        if first == 0:
            status_actuator = actuatorFunction.checkSyncValueFunction(actuator_list_id, number, actuator_custom_id, timestamp, actionActuator)
            if "Action Success" in status_actuator:
                first = 1
        else:
            status_actuator = actuatorFunction.checkServerValueFunction(actuator_list_id, actuator_custom_id, server_value, server_sync_at, last_server_value, last_server_sync_at, timestamp, actionActuator)
        status_schedule = actuatorFunction.checkScheduleFunction(actuator_list_id, actuator_custom_id, timestamp, actionActuator)
        status = status_actuator + " | " + status_schedule
        SystemServiceDB.updateStatusByName(status, timestamp, "actuator" + str(number))
        global_variable["logger"].debug("---------------------------------")
    else:
        global_variable["logger"].debug("No Actuator Found with Number" + str(number))

    global_variable["logger"].debug("")
    time.sleep(1)

while True:
    if __name__ == '__main__':        
        try:
            main()
        except Exception as e:
            ServiceProjectFunction.handlingServiceError("Actuator " + str(number), e, global_variable)
