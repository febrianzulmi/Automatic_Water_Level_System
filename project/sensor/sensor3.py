group_id = 3
path = "/home/connex"

import sys
import time
import numpy as np

# Add ADS1115 import for ACLoadOutput
try:
    import Adafruit_ADS1x15
    ADS1115_AVAILABLE = True
except ImportError:
    ADS1115_AVAILABLE = False
    print("Warning: Adafruit_ADS1x15 not available. ACLoadOutput sensors will not work.")

sys.path.append(f"{path}/library")
from SynapsisLibrary import packData, times
sys.path.append(f"{path}/project/database")
from query_project_db import SystemServiceDB, SensorGroupDB
from sensorLibrary import ACLoadOutput
sys.path.append(f"{path}/project/function")
from dbFunction import dbFunction
from logFunction import logFunction
from sensorFunction import SensorFunction
from serviceProjectFunction import ServiceProjectFunction
sys.path.append(f"{path}/project/function/sensor")
from collectDataSensorFunction import CollectDataSensorFunction
from calibrationSensorFunction import CalibrateSensorFunction

sensor_variable = {}
sensor_variable["groupNumber"] = group_id
sensor_variable["serviceName"] = f"sensor{group_id}"

# Get group ID from database
group_result = SensorGroupDB.selectIsNumber(group_id)
if not group_result:
    print(f"Error: Group {group_id} not found in database")
    exit(1)
group_id = group_result[0]["id"]

datetimes = times.getDatetime()
print("Start : ", datetimes)
sensor_setting = CollectDataSensorFunction.getSensorSetting(group_id)
feature_setting = dbFunction.getFeatureSetting()
data_sensor = CollectDataSensorFunction.byGroupState(group_id)

# Check if data_sensor is valid
if not data_sensor or data_sensor["numSensor"] == 0:
    print(f"Error: No sensors found for group {group_id}")
    exit(1)

alarm_data = SensorFunction.alarmSensorFunction.initiateAlarmSensor(data_sensor, sensor_setting, feature_setting)

sensor_variable["flag"] = 0
sensor_variable["totalSensor"] = data_sensor["numSensor"]
sensor_variable["logger"] = logFunction.setupLogger(sensor_variable["serviceName"], stream=True) 


def readSensor():
    try:
        sensor_result = ACLoadOutput.main(group_id, data_sensor)
        return sensor_result
    except Exception as e:
        print(f"Error in readSensor(): {str(e)}")
        # Return default result if error occurs
        return {
            "value": [0.00] * data_sensor["numSensor"],
            "message": f"Error reading sensors: {str(e)}",
            "state": [False] * data_sensor["numSensor"]
        }


def main():
    global group_id, data_sensor, alarm_data, sensor_setting, feature_setting, sensor_variable

    sensor_setting = CollectDataSensorFunction.getSensorSetting(group_id)
    feature_setting = dbFunction.getFeatureSetting()
    data_sensor = CollectDataSensorFunction.byGroupState(group_id)
    if sensor_variable["totalSensor"] != data_sensor["numSensor"]:
        alarm_data = SensorFunction.alarmSensorFunction.initiateAlarmSensor(data_sensor, sensor_setting, feature_setting)
        sensor_variable["totalSensor"] = data_sensor["numSensor"]
    alarm_data["totalNormal"], alarm_data["totalMin"], alarm_data["totalMax"], alarm_data["totalSensorError"] = 0, 0, 0, 0
    alarm_data["totalNormalTolerance"], alarm_data["totalMinTolerance"], alarm_data["totalMaxTolerance"], alarm_data["totalErrorTolerance"] = 0, 0, 0, 0
    alarm_data["totalTolerance"], alarm_data["totalSensorInactive"], alarm_data["totalAlarmInactive"] = 0, 0, 0

    sensor_variable["flag"] += 1
    timestamp = times.getDatetime()
    sensor_variable["logger"].debug(f"------ {str(timestamp)} ------") 
    sensor_variable["logger"].debug(f"Interval & Frequency Sampling : {str(sensor_setting['frekuensi'])}x in {str(sensor_setting['interval'])} Seconds ({sensor_variable['flag']}x)")
    
    sensor_result = readSensor()
    calibration_value = CalibrateSensorFunction.calculateCalibration(data_sensor, sensor_result["value"])
    alarm_data, summary_sensor = SensorFunction.alarmSensorFunction.checkAlarm(data_sensor, calibration_value, sensor_result, alarm_data, "Serial", timestamp)
    sensor_pack = packData.sensorPack(data_sensor["sensorId"], calibration_value, data_sensor["numSensor"])
    sensor_variable["logger"].debug(f"Sensor Data : {sensor_pack}")
    
    if "Success" in sensor_result["message"] and "Failed" not in sensor_result["message"] and "Error" not in sensor_result["message"]:
        sensor_variable["logger"].debug(f"Status Read Sensor : \033[32m{sensor_result['message']}\033[00m")
        sensor_variable["logger"].debug(f"Summary Sensor : {summary_sensor['logColored']}")
    else:
        if "Success" in sensor_result["message"] and "Failed" in sensor_result["message"] or "Error" in sensor_result["message"]:
            sensor_variable["logger"].debug(f"Status Read Sensor : \033[93m{str(sensor_result['message'])}\033[00m")
        else:
            sensor_variable["logger"].debug(f"Status Read Sensor : \033[31m{str(sensor_result['message'])}\033[00m")
        sensor_variable["logger"].debug(f"Summary Sensor : \033[93m{summary_sensor['logColored']}\033[00m")
    
    SystemServiceDB.updateStatusByName(sensor_result["message"], timestamp, sensor_variable["serviceName"])
    sensor_variable["logger"].debug(f"---------------------------------\n")
    sensor_variable["flag"] = 0
    time.sleep(sensor_setting["interval"])
    

while True:
    if __name__ == "__main__":        
        try:
            main()
        except Exception as error:
            ServiceProjectFunction.handlingServiceError(f"Sensor {sensor_variable['groupNumber']}", error, sensor_variable)
