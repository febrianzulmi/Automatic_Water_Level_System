number = 9

import sys, time, json, argparse
sys.path.append('../../library')
from SynapsisLibrary import packData, times
sys.path.append('../database')
from sql import *
from function import getSensorSetting, getSensorByGroup, calibrateSensor
from sensorIBMS import *

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--Type", help = "Show Output")
args = parser.parse_args()
tipe = None
if args.Type != None:
   tipe = args.Type
   
sensor_id = []
sensor_name = []
sensor_value = []
num_sensor = 0

def readSensor():
    global group_id
    #value, status = '', [0] 
    return value, status    

def main():
    global group_id, sensor_id, sensor_name, sensor_value, num_sensor, tipe
    
    timestamp = times.getDatetime()    
    print("Timestamp : " + timestamp)
    
    group = groups.selectOne(group_id)
    if len(group) > 0:
       for i in group:
           print("Group Sensor : " + i[1] + " (ID " + str(i[0]) + ")")
    else:
       print("Group Sensor : -")
    id, sensor_id, sensor_name, num_sensor = getSensorByGroup(group_id)
    if num_sensor > 0:
       # DROP YOUR READ SENSOR FUNCTION HERE
       sensor_value, status_read = readSensor()
       if 'Success' in status_read:
           print("Status Read Sensor : " + str(status_read))
           print("Value Sensor : ")
           for i in range(num_sensor):
               if str(tipe) == '1':
                  calibrate_value, calibrate_flag = calibrateSensor(id, sensor_value)
                  if str(calibrate_flag[i]) == '1':
                     print(str(i+1) + ") " + sensor_name[i] + " : " + str(sensor_value[i]) + " (Raw) | " + str(calibrate_value[i]) + " (Calibrate)" )
                  else:    
                     print(str(i+1) + ") " + sensor_name[i] + " : " + str(sensor_value[i]) + " (Raw)" )
               elif str(tipe) == '0':
                  print(str(i+1) + ") " + sensor_name[i] + " : " + str(sensor_value[i]) )
       else:
          print("Status Read Sensor : Error - " + str(status_read))       
    else:
       print("Value Sensor : -")
       
if __name__ == '__main__': main()
