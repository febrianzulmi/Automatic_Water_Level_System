group_number = 5
path = "/home/connex"

import sys
import time

sys.path.append(f"{path}/library")
from SynapsisLibrary import packData, times
sys.path.append(f"{path}/project/database")
from query_project_db import SystemServiceDB, SensorGroupDB
from sensorLibrary import Power
sys.path.append(f"{path}/project/function")
from logFunction import logFunction
from sensorFunction import SensorFunction
from serviceProjectFunction import ServiceProjectFunction
sys.path.append(f"{path}/project/function/sensor")
from collectDataSensorFunction import CollectDataSensorFunction
from calibrationSensorFunction import CalibrateSensorFunction
from dbFunction import dbFunction

sensor_variable = {}
sensor_variable["groupNumber"] = group_number
sensor_variable["serviceName"] = f"sensor{group_number}"

group_id = SensorGroupDB.selectIsNumber(group_number)[0]["id"]

datetimes = times.getDatetime()
print("Start : ", datetimes)
sensor_setting = CollectDataSensorFunction.getSensorSetting(group_id)
feature_setting = dbFunction.getFeatureSetting()
data_sensor = CollectDataSensorFunction.byGroupState(group_id)
alarm_data = SensorFunction.alarmSensorFunction.initiateAlarmSensor(data_sensor, sensor_setting, feature_setting)


sensor_variable["flag"] = 0
sensor_variable["totalSensor"] = data_sensor["numSensor"]
sensor_variable["logger"] = logFunction.setupLogger(sensor_variable["serviceName"], stream=True) 
sensor_variable["calibratePort1"], sensor_variable["calibratePort2"], sensor_variable["calibratePort3"], sensor_variable["calibratePort4"]  = 0, 0, 0, 0
sensor_variable["acsPort1"], sensor_variable["acsPort2"], sensor_variable["acsPort3"], sensor_variable["acsPort4"] = None, None, None, None

def readSensor():
    power = Power(group_id, data_sensor)
    sensor_result = power.main(sensor_variable)
    return sensor_result


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
