import requests, json, os, shutil
from sql import *

def getPort():
    try:
       f = open("../../platform/ports.conf","r")
       port = f.read()
       f.close()
       port = port.replace("\n","")
    except:
       port = '80'
    return port

def checkSession():
    port = getPort()
    try:
       sess = requests.get('http://localhost:' + port + '/api/project/session')
       sess = sess.text
       sess = json.loads(sess)
       id = sess['id']
       username = sess['username']
       state = sess['state']
       level = sess['level']
    except Exception as e:
       id = 0
       username = ''
       level = 0
       state = 0
    return id, username, state, level

def getData():
    port = getPort()
    try:
       project = requests.get('http://localhost:' + port + '/api/project')
       project = project.text
       project = json.loads(project)
       name = project['name']
       port = project['port']
       gateway = project['gateway']
       node = project['node']
       protocol = project['protocol']
    except Exception as e:
       print(e)
       name = ''
       port = None
       gateway = 0
       node = 0
       protocol = 0
    return name, port, gateway, node, protocol

def getSetting():
    cek = setting.select()
    if len(cek) > 0:
       for i in cek:
           id_device = i[1]
           name= i[2]
           if int(id_device) == 0:
              id_device = ''
           ip = i[3]
           port = i[4]
           key = i[5]
           token = i[6]
    else:	
        id_device = ''
        name = ''
        ip = ''
        port = ''
        key = ''
        token = ''
    return id_device, name, ip, port, key, token
    
def getTopic(name):
    cek = attributes.selectOne(name)
    if len(cek) > 0:
       for i in cek:
           param = i[2]
    else:
       param = ''
    return param

def getOID(name):
    cek = attributes.selectOne(name)
    if len(cek) > 0:
       for i in cek:
           param = i[2]
    else:
       param = ''
    return param
    
def getURL(ip, port, name):
    cek = attributes.selectOne(name)
    if len(cek) > 0:
       for i in cek:
           param = i[2]
    else:
       param = ''
    if ip == '' and port == '':
       urls = 'Undefined IP and Port'
    elif ip == '' and port != '':
       urls = 'Undefined IP'
    elif ip != '' and port == '':
       urls = 'Undefined Port'
    else:
       if param == '':
          urls = 'Undefined Parameter'
       else:
          urls = 'http://'+ str(ip) +':'+ str(port) + str(param)
    return urls

def checkURL(url):
    if url == 'Undefined Parameter' or url == 'Undefined IP' or url == 'Undefined Port' or url == 'Undefined IP and Port':
       state = 0
    else:
       state = 1
    return state

def getInterval(name):
    default = 60
    cek = intervals.selectOne(name)
    if len(cek) > 0:
       for i in cek:
           interval = i[2]
           unit = i[3]
       if int(unit) == 1:
          interval = interval 
       elif int(unit) == 2:
          interval = int(interval) * 60
       elif int(unit) == 3:
          interval = int(interval) * 3600
       else:
          interval = default
    else:
       interval = default
    return interval 

def getSensorSetting(group_id):
    try:
      get = groups.selectOne(group_id)
      if len(get) > 0:
         for i in get:
             interval = i[2]
             unit = i[3]
             if unit == 1:
                interval = interval
             elif unit == 2:
                interval = interval * 60
             else:
                interval = interval * 3600
             frekuensi = i[4]
      else:
         interval = 60 #in Seconds
         frekuensi = 1
    except:
      interval = 60 #in Seconds
      frekuensi = 1
    return interval, frekuensi

def getSensorByGroup(group_id):
    id = []
    sensor_id = []
    sensor_name = []
    sensors  = sensor.selectByGroup(group_id)
    if len(sensors) > 0:
       for i in range(len(sensors)):
           id.append(sensors[i][0])
           sensor_id.append(sensors[i][1])
           sensor_name.append(sensors[i][3])
    num_sensor = len(sensors)       
    return id, sensor_id, sensor_name, num_sensor

def getAllSensor():
    id = []
    sensor_id = []
    sensor_name = []
    sensors  = sensor.select()
    if len(sensors) > 0:
       for i in range(len(sensors)):
           id.append(sensors[i][0])
           sensor_id.append(sensors[i][1])
           sensor_name.append(sensors[i][2])
    num_sensor = len(sensors)       
    return id, sensor_id, sensor_name, num_sensor
    
def getValueSensor(id):
    sensor_value = []
    for i in range(len(id)):
        values = logSensor.selectLastOne(id[i])
        value = '-'
        for i in values:
            value = i[2]        
        sensor_value.append(value)
    return sensor_value
    
def getGatewayHTTP():
    ports = gateway.select()
    for i in ports:
        port = i[1]

def createOID():
    base = "/home/pi"
    path_snmp =  base + "/project/sensor/oid"
    os.system("sudo rm -r " + path_snmp)
    cek = os.path.exists(path_snmp)
    if cek == False:
       os.system("sudo mkdir " + path_snmp)
    base_oid = getOID('base')
    if base != '':
       sensors  = sensor.select()
       if len(sensors) > 0:
          shutil.copy(base + '/platform/storage/snmpd.conf.master', '/etc/snmp/snmpd.conf')
          files = open("/etc/snmp/snmpd.conf", "a")
          files.write("\n")
          for i in range(len(sensors)):
              id = sensors[i][0]
              id_sensor = sensors[i][1] 
              oid = base_oid + "." + str(id_sensor)
              oid_script = path_snmp + "/" + oid + ".sh"
              cek_script = os.path.exists(oid_script)
              if cek_script == False:
                 f = open(oid_script, "w") 
                 f.write("#!/bin/bash\n")
                 f.write("cat /tmp/" + oid)
                 f.close()
              values = logSensor.selectLastOne(id)
              if len(values) > 0:
                 for i in values:
                     value = i[2]
              else:
                 value = 0 
              f = open("/tmp/" + oid, "w")
              f.write("." + str(oid))
              f.write("\n")
              f.write("integer")
              f.write("\n")
              f.write(str(value))
              f.write("\n")
              f.close()            
              files.write("pass ." + oid + " /bin/sh " + oid_script + "\n")
          files.close()    
          os.system("sudo service snmpd restart")
