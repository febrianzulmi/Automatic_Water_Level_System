id_act = 6

import sys, time, json, requests
sys.path.append('../../library')
from SynapsisLibrary import trigger, times
sys.path.append('../database')
from sql import *
from function import getInterval

w1 = times.getDatetime()
print("Start : ",w1)
now = times.now()
now1 = int((now.minute*60)+now.second)
last_value = None
last_time = None                

def actionActuator():
    print("Do Action")   

def main():
    global id_act, w1, now1, last_value, last_time
    
    now2 = times.now()
    timestamp = now2.strftime("%Y-%m-%d %H:%M:%S")
    now2 = int((now2.minute*60)+now2.second)
    
    ### GET INTERVAL ###
    interval = getInterval("control")
    frekuensi = 1
    ####################
        
    state, state2, nows = trigger.schedule(now1, now2, interval, frekuensi)
    if state == 1 and state2 == 1:
       now1 = nows
       
       print("----- ", timestamp, " -----")
       get = actuator.selectById(id_act)
       for i in get:
           act_id = i[1]
           act_name = i[2]   
           value = i[3]
           value_time = i[4]
       print("Actuator ID : " + str(act_id))
       print("Actuator Name : " + str(act_name))
       print("Last Value : " + str(last_value) + " - " + str(last_time)) 
       print("Value : " + str(value) + " - " + str(value_time))
       if str(value) != str(last_value):
          actionActuator()
          last_value = value
          last_time = value_time          
       print("---------------------------------")
       
       print("")
       time.sleep(1)
    
while True:
      if __name__ == '__main__': main()
