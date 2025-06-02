import sys, time
sys.path.append('../../library')
from SynapsisLibrary import *
sys.path.append('../database')
from sql import *
from function import getSetting, getURL, getInterval, checkURL

now = times.now()
time1 = int((now.minute*60)+now.second)

def getToken(id_device, url_auth, key):
    URLCheck = checkURL(url_auth)
    if URLCheck == 0:
       print("URL : " + url_auth)
       return 'Failed Get Token'
    else:
       print('URL : ', url_auth)
       user = packData.userPack(id_device, key)
       auth = http.getToken(url_auth, user)
       return auth

def runAuth():
    timestamps = times.getDatetime()
    print("----- ", timestamps, " -----")
    id_device, name, ip, port, key, token = getSetting()
    url_auth = getURL(ip, port, "auth")
    if token == '' or token == None:
       if id_device == '' or id_device == None:
          print("ID Device : Undefined")
       else:
          print("ID Device : ", id_device)
          if key == '' or key == None:
             print("API Key : Undefined")
          else:
             print("API Key : ", key)
             result = getToken(id_device, url_auth, key)
             if result != 'Failed Get Token':
                update =  setting.updateToken(result)
             print("Token : ", result)                   
    else:
       print("Token : ", token)
    print("---------------------------------")
    
def main():
    global time1
    now2 = times.now()
    time2 = int((now2.minute*60)+now2.second)  
    interval = getInterval("auth")
    state1, state2, time_update = trigger.schedule(time1, time2, interval, 1)
    if state1 == 1 and state2 == 1:
       runAuth()
       time1 = time_update
       time.sleep(1)

while True:
      if __name__ == '__main__':
         main()

