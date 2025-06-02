import sys, time, json
sys.path.append('../../library')
from SynapsisLibrary import packData, trigger, times, http
sys.path.append('../database')
from sql import *
from function import getData, getSetting, getInterval, getURL, checkURL, getAllSensor, getValueSensor

now = times.now()
now1 = int((now.minute*60)+now.second)

def runHTTP(ip, port, token, sensor_pack, data_pack, timestamp):
    url_data = getURL(ip, port, "data")
    URLCheck = checkURL(url_data)
    print("URL : ", url_data)
    if URLCheck == 1:
       print("Sensor Data : ", sensor_pack)
       print("Data Pack : ", data_pack)
       ### SEND DATA HTTP ###
       status, payload = http.postHTTP(url_data, data_pack, token)
       print("Status Send : ", status)
       if status == 200:
          payload = json.loads(payload)
          message = payload['message']
          if message == 'Data created successfully!':
             print("Send Data Successfully")
          else:
             print("Error Send : ", message)
       else:
          print("Error Send : ", payload)
       ######################

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
       
       print('Protocol : HTTP')
       runHTTP(ip, port, token, sensor_pack, data_pack, timestamp)      
       #####################
    
    print("")        

if __name__ == '__main__': main()
