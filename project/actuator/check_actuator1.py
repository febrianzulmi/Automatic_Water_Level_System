number = 1

import argparse
import sys

sys.path.append('/home/connex/library')
from SynapsisLibrary import times
sys.path.append('/home/connex/project/database')
from query_project_db import ActuatorDB, LogActuatorDB
from actuatorLibrary import actuatorAC
sys.path.append("/home/connex/project/function")
from actuatorFunction import actuatorFunction
from notificationFunction import notificationFunction
from dbFunction import dbFunction



parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("-a", "--action", help = "Show Output")

# Read arguments from command line
args = parser.parse_args()
action = None

if args.action != None:
   action = args.action

def actionActuator(actuator_custom_id):
    status = actuatorAC(actuator_custom_id, action)
    return status

def main():
    global number, action

    timestamp = times.getDatetime()
    print("Timestamp : " + timestamp)

    feature_setting = dbFunction.getFeatureSetting()
    get = ActuatorDB.selectByNumber(number)
    actuator_list_id = get[0]['id']
    for i in get:
        actuator_custom_id = i['actuator_custom_id']
        actuator_name = i['name']

    print("Actuator Name : " + str(actuator_name))
    if action == '1':
       print("Action Actuator : ON")
       parameterActuator = actuatorFunction.getParameterActuator(number)
       print("Parameter Mode Swing : ", str(parameterActuator['swing']))
       print("Parameter Temperature : ", str(parameterActuator['temperature']))

    else:
       print("Action Actuator : OFF")

    status_actuator = actionActuator(actuator_custom_id)
    if "Action Success" in status_actuator:
       ActuatorDB.updateAction(action, 3, timestamp, actuator_list_id)
       LogActuatorDB.insert(actuator_list_id, action, 3, timestamp)
       control = status_actuator.replace("Action Success | ", "")
       if str(feature_setting['notification']) == "1":
          notificationFunction.generateNotificationActuator(actuator_list_id, 3, action, timestamp, control)

    print("State Action : " + status_actuator)

if __name__ == '__main__': main()
