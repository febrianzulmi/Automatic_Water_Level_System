import sys, time, json
sys.path.append('../../library')
from SynapsisLibrary import packData, trigger, times
sys.path.append('../database')
from sql import *
from function import getData, getSetting, getInterval, getAllSensor, getValueSensor, getOID

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
    timestamp = times.getDatetime()
    
    ### GET DEVICE INFO ####
    id_device, name, ip, port, key, token = getSetting()   
    ########################
       
    if id_device == '' or id_device == None:
       print("ID Device : Undefined")
          
    else:
       ### SEND FUNCTION ###
       id, sensor_id, sensor_name, sensor_value, num_sensor, sensor_pack, data_pack = getDataSensor(id_device, timestamp)
       print('Timestamp : ', timestamp)
       print('ID Device : ', id_device)    
       
       print('Protocol : SNMP')
       base_oid = getOID("base")
       for i in range(num_sensor):
           oid = str(base_oid) + "." + str(sensor_id[i])
           oid_file = "/tmp/" + str(oid)
           f = open(str(oid_file), "w")
           f.write("." + str(oid))
           f.write("\n")
           f.write("integer")
           f.write("\n")
           f.write(str(sensor_value[i]))
           f.write("\n")
           f.close()
           print("Sensor ID " + str(sensor_id[i]) + " (" + str(oid) + ") Updated with Value " + str(sensor_value[i]))
               
       #####################
    
    print("")        

if __name__ == '__main__': main()
