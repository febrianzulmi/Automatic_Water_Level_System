import sys, time, json
sys.path.append('../../library')
from SynapsisLibrary import packData, trigger, times, http
sys.path.append('../database')
from sql import *
from function import getData, getSetting, getInterval, getURL, checkURL, getAllSensor, getValueSensor

w1 = times.getDatetime()
print("Start : ",w1)
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
             log = logSendNode.insert(json.dumps(sensor_pack), status, 1, timestamp)
          else:
             log = logSendNode.insert(json.dumps(sensor_pack), 400, 1, timestamp)
             buffer = logBufferNode.insert(json.dumps(sensor_pack), timestamp)
             print("Error Send : ", message)
       else:
          log = logSendNode.insert(json.dumps(sensor_pack), status, 0, timestamp)
          buffer = logBufferNode.insert(json.dumps(sensor_pack), timestamp) 
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
       ### SCHEDULE SEND ###
       state, state2, nows = trigger.schedule(now1, now2, interval, frekuensi)
       if state == 1 and state2 == 1:
          now1 = nows
          id, sensor_id, sensor_name, sensor_value, num_sensor, sensor_pack, data_pack = getDataSensor(id_device, timestamp)
          print("----- ", timestamp, " -----")       
          
          print('Protocol : HTTP')
          runHTTP(ip, port, token, sensor_pack, data_pack, timestamp)  
          
          print("---------------------------------")
          print("")
          time.sleep(1)
       #####################

while True:
      if __name__ == '__main__': main()
