import serial, time, datetime
from function import *

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=3)

def write(command):
    end = b'\xff\xff\xff'
    #print(command)
    encodes = command.encode('ascii')
    commands  = encodes + end
    ser.write(commands)

def read():
    if ser.in_waiting:
        rec = ser.read_until(b'\xff\xff\xff')
        data = rec.hex()
        data = data.replace('ffffff','')
        array, text, count = [], '', 0
        for i in range(len(data)):
            text = text + data[i]
            count += 1
            if count == 2:
               array.append(text)
               count, text = 0, ''
        if array[0] == '66':
           array.pop(0)
           data = int(array[0])
           return data
        elif array[0] == '70' or array[0] == '71':
           array.pop(0)
           for i in range(len(array)):
               text = text + array[i]
           text = bytes.fromhex(text)
           text = text.decode('ascii')
           if array[0] == '70':
              return str(text)
           elif array[0] == '71':
              return int(text)
        else:
           text = bytes.fromhex(text)
           text = text.decode('ascii') 
           return text        
    return 'Kosong'    

def command_set(command):
    write(command)
    print(command)
    
def command_read(command):
    write(command)
    data = read()
    print(command, data)
    return data
    
command_set('page 0')

while  True:
    print("Start")

    now = datetime.datetime.now()
    times = now.strftime("%H:%M:%S")
    days = now.strftime("%d/%m/%y")

    number = random.randint(0, 100)
    temp = getTemp()
    uptime, boot_time = getUptime()
    ipwlan = getInterface('wlan0')
    ssid = getSSID('wlan0')
    ipeth = getInterface('eth0')
    cpu = getUsage()
    
    #data = command_read('sendme')
    #print("Page : ", data)
    
    command_set('name.txt=\"Connex Device\"')
    command_set('date.txt=\"' + days + '\"')
    command_set('time.txt=\"' + times + '\"')
    command_set('suhu.txt=\"' + str(temp) + ' C\"')
    if float(temp) > 70.0:
       command_set('suhu.pco=63488')
    else:
       command_set('suhu.pco=65535')    
    
    #if data == 0:
    if ssid == "-":
          command_set('page0.ipwlan.txt=\"IP Undefined\"') 
          command_set('page0.ssid.txt=\"SSID Undefined\"')
    else:
          command_set('page0.ssid.txt=\"' + str(ssid) + '\"')
          command_set('page0.ipwlan.txt=\"' + ipwlan + '\"')
               
    command_set('page0.ipeth.txt=\"' + str(ipeth) + '\"')
    command_set('page0.uptime.txt=\"'+ uptime + '\"')
    command_set('page0.lastboot.txt=\"'+ boot_time + '\"')
    command_set('page0.cpu.txt=\"'+ cpu + '\"')
       
    #elif data == 1:
    command_set('page1.sensor.txt=\"' + str(number) + '\"') 
    #time.sleep(1)    
    print("")
    

    
