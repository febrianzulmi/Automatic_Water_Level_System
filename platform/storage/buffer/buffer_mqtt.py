import sys, time
sys.path.append('../../library')
from SynapsisLibrary import *
sys.path.append('../database')
from sql import *
from function import getData, getSetting, getInterval, getTopic

now = times.now()
time1 = int((now.minute*60)+now.second)
initial_state, client = None, None #For MQTT

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
    
def runMQTT(x, topic_send, data_pack, sensor_pack timestamp, id, node_id):
    global client
    publish = mqtt.publishMessage(client, topic_send, data_pack)
    if publish != None:
       publish_state = publish.rc
       if publish_state == 0:
          print(str(x) + ") ", str(publish_state), " (Success) - ", timestamp, " - ", sensor_pack )
          delete = logBufferNode.deleteOne(id)
          update = logSendNode.updateLog(json.dumps(sensor_pack),timestamp)
       else:
          print(str(x) + ") ", str(publish_state), " (Failed) - ", timestamp, " - ", sensor_pack )
    else:
       print(str(x) + ") ", str(publish_state), " (Failed) - ", timestamp, " - ", sensor_pack )

def runBuffer():
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    id_device, name, ip, port, key, token = getSetting()
    timestamps = times.getDatetime()
    print("----- ", timestamps, " -----")
    
    print("Protocol : MQTT")
    print("Broker : ", ip + ":" + str(port))
    topic_send = conMQTT(id_device, key, ip, port)
    print("Topic : ", topic_send)
    state = mqtt.checkConnection()
    print("Connection : ", state)
    cek_node = logBufferNode.selectAll()
    if len(cek_node) > 0:
       print("Check Buffer Node")
       x = 0
       for i in cek_node:
           x += 1
           id = i[0]
           sensor = i[1]
           timestamp = i[2]
           sensor_pack = json.loads(sensor)
           data_pack = {}
           data_pack['data'] = sensor_pack
           data_pack['node_id'] = id_device
           data_pack['date_time'] = str(timestamp)
           runMQTT(x, topic_send, data_pack, sensor_pack, timestamp, id, id_device)
    
    print("---------------------------------")

def main():
    global time1
    now2 = times.now()
    time2 = int((now2.minute*60)+now2.second)  
    interval = getInterval("buffer")
    state1, state2, time_update = trigger.schedule(time1, time2, interval, 1)
    if state1 == 1 and state2 == 1:
       runBuffer()
       time1 = time_update
       time.sleep(1)
    
while True:
      if __name__ == '__main__':
         main()

