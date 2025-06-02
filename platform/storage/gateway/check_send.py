import sys, time, json
sys.path.append('../../library')
from SynapsisLibrary import packData, trigger, times
sys.path.append('../database')
from sql import *
from function import getData, getSetting, getInterval, getURL, checkURL, getAllSensor, getValueSensor

def runHTTP(ip, port, token, data_pack, timestamp):
    url_data = getURL(ip, port, "data")
    URLCheck = checkURL(url_data)
    print("URL : ", url_data)
    if URLCheck == 1:
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

def getDataSend(timestamp):
    ### GET LAST SEND DATA ###
    fetch = logSendGateway.selectLastOne()
    if len(fetch) > 0:
       for i in fetch:
           lastNode = json.loads(i[1])
           lastData = i[2]
    else:
       lastNode = ''
       lastData = ''
    ##########################
    ### PACK DATA ###
    lastPack = {}
    lastPack['node_id'] = lastNode
    lastPack['data'] = lastData
    lastPack['date_time'] = timestamp           
    #################
    return lastPack

def main():    
    timestamp = times.getDatetime()
    
    ### GET DEVICE INFO ####
    id_device, name, ip, port, key, token = getSetting()   
    ########################
       
    if id_device == '' or id_device == None:
       print("ID Device : Undefined")
          
    else:
       ### SEND FUNCTION ###
       project_name, project_port, project_gateway, project_node, project_protocol = getData()
       data_pack = getDataSend(timestamp)
       print('ID Device : ', id_device)    
       
       if project_protocol == 1:
          print('Protocol : HTTP')
          runHTTP(ip, port, token, data_pack, timestamp)  
               
       elif project_protocol == 2:
          print('Protocol : MQTT')
          print('Coming Soon')
             
       elif project_protocol == 3:
          print('Protocol : SNMP')
          print('Coming Soon')
           
       else:
          print('Protocol : Undefined')       
       #####################
    
    print("")        

if __name__ == '__main__': main()