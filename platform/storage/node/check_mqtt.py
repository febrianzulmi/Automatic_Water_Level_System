import sys, time, json
sys.path.append('../../library')
from SynapsisLibrary import packData, trigger, times, mqtt
sys.path.append('../database')
from sql import *
from function import getData, getSetting, getInterval, getAllSensor, getValueSensor, getTopic

now = times.now()
now1 = int((now.minute*60)+now.second)

def runMQTT(node_id, key, ip, port, sensor_pack, data_pack, timestamp):
    broker = ip
    print("Broker : ", ip + ":" + str(port))
    topic_send = getTopic("data")
    if topic_send != '':
       topic_send = topic_send + str(node_id)
    print("Topic : ", topic_send)   
    client, initial_state = mqtt.connect(broker, port, node_id, key, alive=5, timeout=3)
    print("Initial Connection : ", initial_state)
    state = mqtt.checkConnection()
    print("Connection : ", state)
    print("Sensor Data : ", sensor_pack)
    print("Data Pack : ", data_pack)
    publish = mqtt.publishMessage(client, topic_send, data_pack)
    if publish != None:
       publish = publish.rc
    if publish == 0:
       print("Publish State : ", str(publish) + " (Success)")
    else:      
       print("Publish State : ", str(publish) + " (Failed)")   

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
       print('ID Device : ', id_device)    
       
       print('Protocol : MQTT')
       runMQTT(id_device, key, ip, port, sensor_pack, data_pack, timestamp)      
       #####################
    
    print("")        

if __name__ == '__main__': main()
