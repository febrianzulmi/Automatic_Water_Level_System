import random, subprocess, psutil, os, datetime, time
import netifaces as ni
from netifaces import AF_INET, AF_INET6, AF_LINK, AF_PACKET, AF_BRIDGE

def getTemp():
    temp = subprocess.check_output("vcgencmd measure_temp", shell=True);
    temp = temp.decode("utf-8")
    temp = temp.replace("temp=","")
    temp = temp.replace("'C","")
    temp = temp.replace("\n","")
    return temp    

def getUptime():
    boot = psutil.boot_time()
    boot_time = datetime.datetime.fromtimestamp(boot)
    boot_time = boot_time.strftime("%d/%m/%y %H:%M:%S")
    now = time.time()
    diff = now-boot
    converted_time = datetime.timedelta(seconds=int(diff))
    uptime = str(converted_time).split(":")
    if "day" in uptime[0]:
       new = uptime[0].split(",")
       day = new[0]
       hour = new[1]
       minute = uptime[1]
       second = uptime[2]
       state = 1
    else:
       hour = uptime[0]
       minute = uptime[1]
       second = uptime[2]
       state = 2
    if int(hour) > 1:
       str_hour = 'hours '
    else:
       str_hour = 'hour '
    if int(minute) > 1:
       str_minute = 'minutes '
    else:
       str_minute = 'minute '
    if int(second) > 1:
       str_second = 'seconds'
    else:
       str_second = 'second'
    if state == 1:
       uptimes = f"{day} {hour} {str_hour} {minute} {str_minute} {second} {str_second}" 
    else:   
       uptimes = f"{hour} {str_hour} {minute} {str_minute} {second} {str_second}"
    return uptimes, boot_time  

def getInterface(interface):
    state = subprocess.check_output("cat /sys/class/net/"+interface+"/operstate", shell=True)
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
    return ip
    
def getSSID(interface):
    #ssid = os.popen("iw dev " + interface + " link | grep SSID | awk '{print $2}'").read()
    ssid = os.popen("iw dev " + interface + " link | grep SSID").read()
    ssid = ssid.replace('SSID:','')
    ssid = ssid.replace('\n','')
    ssid = ssid.replace('\t ','')
    if ssid == '':
       ssid = '-'
    return ssid
    
def getUsage():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    mem_total = round(float(memory.total/(2**20)))
    mem_used = round(float(memory.used/(2**20)))
    percent = round(float(mem_used/mem_total * 100))
    result = str(percent) + "% (" + str(mem_used) + "/" + str(mem_total) + " MB)"
    cpu = str(cpu) + " %"
    return cpu 
