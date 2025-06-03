group_number = 9
path = "/home/connex"

import argparse
import sys
import time

sys.path.append(f"{path}/library")
from SynapsisLibrary import times
sys.path.append(f"{path}/project/database")
from query_project_db import SensorGroupDB
sys.path.append(f"{path}/project/function")
from sensorFunction import SensorFunction
from sensorLibrary import Network

group_id = SensorGroupDB.selectIsNumber(group_number)[0]["id"]

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--Type", help = "Show Output")
args = parser.parse_args()
tipe = None
if args.Type != None:
    tipe = args.Type
data_sensor = SensorFunction.CollectDataSensorFunction.byGroupState(group_id)
sensor_variable = {'lastTime': {}, 'lastValue': {}}


def readSensor():
    global sensor_variable
    network = Network(group_id, data_sensor, sensor_variable)
    sensor_result, sensor_variable = network.main()
    return sensor_result


def main():
    global group_id, data_sensor, tipe, sensor_variable

    timestamp = times.getDatetime()
    print(f"Timestamp : {timestamp}")
    
    for x in range(data_sensor['numSensor']):
        sensor_variable['lastTime'][data_sensor['sensorId'][x]] = 0
        sensor_variable['lastValue'][data_sensor['sensorId'][x]] = 0

    group = SensorGroupDB.selectOne(group_id)
    if len(group) > 0:
        for i in group:
            print(f"Group Sensor : {i['name']} (ID {str(i['id'])})")
    else:
        print("Group Sensor : -")

    if data_sensor["numSensor"] > 0:
        sensor_result = readSensor()
        print(f"Status Read Sensor : {sensor_result['message']}")
        print("Value Sensor : ")
        for i in range(data_sensor["numSensor"]):
            calibrate_value = SensorFunction.CalibrateSensorFunction.calculateCalibration(data_sensor, sensor_result["value"])
            
            if str(tipe) == "1":
                if str(data_sensor["sensorCalibration"][i]) == "1":
                    if sensor_result["state"][i] == True:
                        print(f"{str(i+1)}) {data_sensor['sensorName'][i]} : {str(calibrate_value[i])} (Raw) | {str(calibrate_value[i])} (Calibration)")
                    else:
                        print(f"{str(i+1)}) {data_sensor['sensorName'][i]} : {str(calibrate_value[i])} (Raw) | {str(calibrate_value[i])} (Calibration) -> Failed Sampling")
                else:
                    if sensor_result["state"][i] == True:
                        print(f"{str(i+1)}) {data_sensor['sensorName'][i]} : {str(calibrate_value[i])} (Raw)")
                    else:
                        print(f"{str(i+1)}) {data_sensor['sensorName'][i]} : {str(calibrate_value[i])} (Raw) -> Failed Sampling")
            
            elif str(tipe) == "0":
                if sensor_result["state"][i] == True:
                    print(f"{str(i+1)}) {data_sensor['sensorName'][i]} : {str(calibrate_value[i])}")
                else:
                    print(f"{str(i+1)}) {data_sensor['sensorName'][i]} : {str(calibrate_value[i])} -> Failed Sampling")
    
    else:
        print("Value Sensor : -")


if __name__ == "__main__": main()
