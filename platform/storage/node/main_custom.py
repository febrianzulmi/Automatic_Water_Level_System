import sys, time, json
sys.path.append('../../library')
from SynapsisLibrary import packData, trigger, times
sys.path.append('../database')
from sql import *
from function import getData, getSetting, getInterval, getURL, checkURL, getAllSensor, getValueSensor

w1 = times.getDatetime()
print("Start : ",w1)
now = times.now()
now1 = int((now.minute*60)+now.second)

def getDataSensor(id_device, timestamp):
    ### GET LIST SENSOR ###
    id, sensor_id, sensor_name, num_sensor = getAllSensor()
    sensor_value = []
    sensor_value = getValueSensor(id)
    #######################
    ### PACK DATA ###
    sensor_pack = packData.sensorPack(sensor_id,sensor_value,num_sensor)
    data_pack = packData.dataPack(id_device, sensor_id, sensor_value, num_sensor, timestamp)                
    #################
    return id, sensor_id, sensor_name, sensor_value, num_sensor, sensor_pack, data_pack

def main():
    global now1
    
    now2 = times.now()
    timestamp = now2.strftime("%Y-%m-%d %H:%M:%S")
    now2 = int((now2.minute*60)+now2.second)
    
    ### GET INTERVAL ###
    interval = getInterval("send")
    frekuensi = 1
    ####################

    ### GET DEVICE INFO ####
    id_device, name, ip, port, key, token = getSetting()   
    ########################

    if id_device == '' or id_device == None:
       print("----- ", timestamp, " -----")
       print("ID Device : Undefined")
       print("---------------------------------")
       print("")
       time.sleep(1)
          
    else:
       ### CUSTOM SCHEDULE SEND ###
       id, sensor_id, sensor_name, sensor_value, num_sensor, sensor_pack, data_pack = getDataSensor(id_device, timestamp)
       print("----- ", timestamp, " -----")       
       # DROP YOUR SCHEDULE HERE ###
       print("---------------------------------")
       print("")
       time.sleep(1)

       ############################

while True:
      if __name__ == '__main__': main()
