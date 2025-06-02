group_number = 1

import sys
import time

sys.path.append('/home/connex/library')
from SynapsisLibrary import packData, trigger, times
sys.path.append('/home/connex/project/database')
from query_project_db import SystemServiceDB, SensorGroupDB
from sensorLibrary import Environment
sys.path.append('/home/connex/project/function')
from sensorFunction import SensorFunction
from serviceProjectFunction import ServiceProjectFunction
sys.path.append("/home/connex/project/function/sensor")
from collectDataSensorFunction import CollectDataSensorFunction
from calibrationSensorFunction import CalibrateSensorFunction
from dbFunction import dbFunction

group_id = SensorGroupDB.selectIsNumber(group_number)[0]["id"]

datetimes = times.getDatetime()
print("Start : ", datetimes)
sensor_setting = CollectDataSensorFunction.getSensorSetting(group_id)
feature_setting = dbFunction.getFeatureSetting()
data_sensor = CollectDataSensorFunction.byGroupState(group_id)
alarm_data = SensorFunction.alarmSensorFunction.initiateAlarmSensor(data_sensor, sensor_setting, feature_setting)
global_variable = {'flag': 0, 'totalSensor': data_sensor['numSensor']}


def readSensor():
    environment = Environment(group_id, data_sensor)
    sensorResult = environment.main()
    return sensorResult


def main():
    global group_id, data_sensor, alarm_data, sensor_setting, feature_setting, global_variable

    ### GET DATA SENSOR ####
    sensor_setting = CollectDataSensorFunction.getSensorSetting(group_id)
    feature_setting = dbFunction.getFeatureSetting()
    data_sensor = CollectDataSensorFunction.byGroupState(group_id)
    if global_variable['totalSensor'] != data_sensor['numSensor']:
        alarm_data = SensorFunction.alarmSensorFunction.initiateAlarmSensor(data_sensor, sensor_setting, feature_setting)
        global_variable['totalSensor'] = data_sensor['numSensor']
    alarm_data['totalNormal'], alarm_data['totalMin'], alarm_data['totalMax'], alarm_data['totalSensorError'] = 0, 0, 0, 0
    alarm_data['totalNormalTolerance'], alarm_data['totalMinTolerance'], alarm_data['totalMaxTolerance'], alarm_data['totalErrorTolerance'] = 0, 0, 0, 0
    alarm_data['totalTolerance'], alarm_data['totalSensorInactive'], alarm_data['totalAlarmInactive'] = 0, 0, 0
    ########################

    global_variable['flag'] += 1
    timestamp = times.getDatetime()
    print(f"{timestamp}".center(34, '-'))
    print(f"Interval | Frekuensi : {str(sensor_setting['interval'])} Seconds | {str(sensor_setting['frekuensi'])}x")
    print("Sampling : ", str(global_variable['flag']))
    
    sensor_result = readSensor()
    calibration_value = CalibrateSensorFunction.calculateCalibration(data_sensor, sensor_result['value'])
    alarm_data, summary_sensor = SensorFunction.alarmSensorFunction.checkAlarm(data_sensor, calibration_value, sensor_result, alarm_data, 'Serial', timestamp)
    sensor_pack = packData.sensorPack(data_sensor['sensorId'], calibration_value, data_sensor['numSensor'])
    print("Sensor Data : ", sensor_pack)
    
    if 'Success' in sensor_result['message'] and 'Failed' not in sensor_result['message']:
        print("Status Read Sensor : \033[32m" + str(sensor_result['message']) + '\033[00m')
        print("Summary Sensor : " + str(summary_sensor['logColored']))
    else:
        if 'Success' in sensor_result['message'] and 'Failed' in sensor_result['message']:
            print("Status Read Sensor : \033[93m" + str(sensor_result['message']) + '\033[00m')
        else:
            print("Status Read Sensor : \033[31m" + str(sensor_result['message']) + '\033[00m')
        print("Summary Sensor : \033[93m" + str(summary_sensor['logColored']) + "\033[00m")
    
    SystemServiceDB.updateStatusByName(sensor_result['message'], timestamp, "sensor" + str(group_id))
    print("---------------------------------")
    ################################
    
    print("")
    global_variable['flag'] = 0
    time.sleep(sensor_setting['interval'])

while True:
    if __name__ == '__main__':        
        try:
            main()
        except Exception as e:
            ServiceProjectFunction.handlingServiceError("Sensor " + str(group_id), e)
