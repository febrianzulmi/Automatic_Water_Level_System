import sys, time
sys.path.append('../../library')
from SynapsisLibrary import *
sys.path.append('../database')
from sql import *
from function import getData, getSetting, getURL, getInterval, checkURL

now = times.now()
time1 = int((now.minute*60)+now.second)

def runHTTP(x, url_data, data_pack, token, sensor_pack, timestamp, id, node_id, tipe):
    status, payload = http.postHTTP(url_data, data_pack, token)
    if status == 200:
       payload = json.loads(payload)
       message = payload['message']
       if message == 'Data created successfully!':
          if tipe == 'node':
             delete = logBufferNode.deleteOne(id)
             update = logSendNode.updateLog(json.dumps(sensor_pack),timestamp)
          else:
             delete = logBufferGateway.deleteOne(id)
             update = logSendGateway.updateLog(node_id,timestamp)
          print(str(x) + ")", str(status), " - ", timestamp, " - ", sensor_pack)
       else:
          print(str(x) + ")", str(status) + "(" + message +") - ", timestamp, " - ", sensor_pack)
    else:
       print(str(x) + ")", str(status), " - ", timestamp, " - ", sensor_pack)

def runBuffer():
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    id_device, name, ip, port, key, token = getSetting()
    timestamps = times.getDatetime()
    print("----- ", timestamps, " -----")
    
    print("Protocol : HTTP")
    url_data = getURL(ip, port, "data")
    URLCheck = checkURL(url_data)
    print("URL : ", url_data)
    if URLCheck == 1:
       if int(project_gateway) == 1:
          cek_gateway = logBufferGateway.selectAll() 
          if len(cek_gateway) > 0:
             print("Check Buffer Gateway")
             x = 0
             for i in cek_gateway:
                 x += 1
                 id = i[0]
                 node_id = i[1]
                 sensor = i[2]
                 timestamp = i[3]
                 sensor_pack = json.loads(sensor)
                 data_pack = {}
                 data_pack['data'] = sensor_pack
                 data_pack['node_id'] = node_id
                 data_pack['date_time'] = str(timestamp)
                 runHTTP(x, url_data, data_pack, token, sensor_pack, timestamp, id, node_id, 'gateway')
          else:
             print("Check Buffer Gateway : No Buffer Data")
       if int(project_node) == 1:
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
                 runHTTP(x, url_data, data_pack, token, sensor_pack, timestamp, id, id_device, 'node')
          else:
             print("Check Buffer Node : No Buffer Data")
  
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

