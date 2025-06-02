import netifaces as ni
from netifaces import AF_INET, AF_INET6, AF_LINK, AF_PACKET, AF_BRIDGE
import subprocess, time, sys
sys.path.append('../library')
from SynapsisLibrary import *
sys.path.append('database/')
from sql import*

def getInterface(interface):
    state = subprocess.check_output("cat /sys/class/net/"+interface+"/operstate", shell=True);
    state = state.decode("utf-8")
    state = state.replace("\n","")
    if "eth" in interface:
       tipe = 0
    else:
       tipe = 1
    iface = ni.ifaddresses(interface)
    mac = iface[17][0]['addr']
    if len(iface) == 3:
       ip = ni.ifaddresses(interface)[AF_INET][0]['addr']
    else:
       ip = '-' 
    return tipe, state, mac, ip
   
#def find(db, iface):
 
while True:
    iface_db = interface.select()
    iface = ni.interfaces()
    iface.remove('lo')
    len_iface = len(iface)
    len_db = len(iface_db)
    #print("Now("len_iface") DB(",len_db,")")
    if len_iface > len_db:
       for i in range(len_iface):
           tipe, state, mac, ip = getInterface(iface[i])
           find = 0
           for x in range(len_db): 
               if iface_db[x][0] == iface[i]:
                  find = 1
                  break      
           if find == 1:
              interface.update(iface[i],tipe,mac,ip)	
              print("Update ", iface[i])	
           else:
              interface.insert(iface[i],tipe,mac,ip)
              print("Tambah ", iface[i]) 
    elif len_db > len_iface:
       for i in range(len_db):
           find = 0
           for x in range(len_iface): 
               if iface[x] == iface_db[i][0]:
                  find = 1
                  break      
           if find == 1:
              tipe, state, mac, ip = getInterface(iface[i])
              interface.update(iface[i],tipe,mac,ip)
              print("Update ", iface[i])	
           else:
              interface.delete(iface_db[i][0])
              print("Kurang ", iface_db[i][0])  
    else:
       for i in range(len_iface):
           print("Check ", iface[i])
       #print(iface_db)    
    print("")
    time.sleep(5)
      
