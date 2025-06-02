import sys, time, json
sys.path.append('../../library')
from SynapsisLibrary import packData, trigger, times, mqtt
sys.path.append('../database')
from sql import *
from function import getData, getSetting, getInterval, getAllSensor, getValueSensor, getTopic

w1 = times.getDatetime()
print("Start : ",w1)
now = times.now()
now1 = int((now.minute*60)+now.second)
initial_state, client = None, None #For MQTT

def publishData(topic_send, data_pack, sensor_pack, timestamp):
    global client
    state = mqtt.checkConnection()
    print("Connection : ", state)
    publish = mqtt.publishMessage(client, topic_send, data_pack)
    if publish != None:
       publish_state = publish.rc
       if publish_state == 0:
          print("Publish State : ", str(publish_state) + " (Success)")
          log = logSendNode.insert(json.dumps(sensor_pack), publish_state, 1, timestamp)
       else:
          print("Publish State : ", str(publish_state) + " (Failed)")
          log = logSendNode.insert(json.dumps(sensor_pack), publish_state, 0, timestamp)
          buffer = logBufferNode.insert(json.dumps(sensor_pack), timestamp)
    else:
       print("Publish State : ", str(publish) + " (Failed)")
       log = logSendNode.insert(json.dumps(sensor_pack), 0, 0, timestamp)
       buffer = logBufferNode.insert(json.dumps(sensor_pack), timestamp)     

def conMQTT(node_id, key, ip, port):
    global initial_state, client
    broker = ip
    topic_send = getTopic("data")
    if topic_send == '':
       topic_send = ''
    else:
       topic_send = topic_send + str(node_id)
    if initial_state == None:
       client, initial_state = mqtt.connect(broker, port, node_id, key, alive=5, timeout=3)
    return topic_send

def runMQTT(node_id, key, ip, port, sensor_pack, data_pack, timestamp):
    global initial_state, client
    topic_send = conMQTT(node_id, key, ip, port)
    print("Broker : ", ip + ":" + str(port))
    if topic_send != '':
       print("Topic : ", topic_send)
       print("Sensor Data : ", sensor_pack)
       print("Data Pack : ", data_pack)         
       if initial_state == True:
          publishData(topic_send, data_pack, sensor_pack, timestamp)
       else:
          publishData(topic_send, data_pack, sensor_pack, timestamp)          
    else:
       print("Topic : Undefined")
       print("Sensor Data : ", sensor_pack)
       print("Data Pack : ", data_pack)

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
    global now1, initial_state, client
    
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
          
          print('Protocol : MQTT')
          runMQTT(id_device, key, ip, port, sensor_pack, data_pack, timestamp)  
          
          print("---------------------------------")
          print("")
          time.sleep(1)
       #####################

while True:
      if __name__ == '__main__': main()
