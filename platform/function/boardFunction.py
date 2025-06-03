import adafruit_dht
import board
import datetime
import psutil
import RPi.GPIO as GPIO
import subprocess
import sys
import time
sys.path.append('/home/connex/platform/')
from function import getFanSetting


class boardFunction():
    def initDevice():
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(18, GPIO.OUT)
        fan = GPIO.PWM(18,50)
        fan.start(0)
        for proc in psutil.process_iter():
            if proc.name() == 'libgpiod_pulsein' or proc.name() == 'libgpiod_pulsei':
                proc.kill()
        try:
            dht = adafruit_dht.DHT11(board.D24, use_pulseio=True)
        except:
            dht= None
        device = {'fan': fan, 'dht': dht}
        return device
    
    def readDHT11(dhtDevice):
        if dhtDevice != None:
            try:
                temperature = dhtDevice.temperature
                humidity = dhtDevice.humidity
                status = True
            except Exception as e:
                temperature, humidity, status = 0.00, 0.00, False
        else:
            temperature, humidity, status = 'N/A', 'N/A', False
        result = {"temperature": temperature, "humidity": humidity, "status": status}
        return result

    def controlFanSpeed(fanDevice, temperature):
        temp = int(temperature)
        min_temp, max_temp, min_fan, max_fan = getFanSetting()
        speed = int((temp - min_temp) * (max_fan - min_fan) / (max_temp - min_temp) + min_fan)
        if speed < 0:
            speed = 0
        elif speed > 100:
            speed = 100     
        fanDevice.ChangeDutyCycle(speed)
        return speed
    
    def readUptime():
        boot = psutil.boot_time()
        boot_time = datetime.datetime.fromtimestamp(boot)
        boot_time = boot_time.strftime("%Y-%m-%d %H:%M:%S")
        #boot = datetime.datetime(2020,7,25,8,10,23)
        #boot = datetime.datetime.timestamp(boot)
        now = time.time()
        diff = now-boot
        converted_time = datetime.timedelta(seconds=int(diff))
        uptime = str(converted_time).split(":")
        state = 0
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
        systemTime = {"uptime": uptimes, "bootTime": boot_time}
        return systemTime

    def readCPUTemp():
        temp = subprocess.check_output("vcgencmd measure_temp", shell=True)
        temp = temp.decode("utf-8")
        temp = temp.replace("temp=","")
        temp = temp.replace("'C","")
        return temp

    def readStorage():
        hdd = psutil.disk_usage('/')
        hdd_total = round(float(hdd.total/(2**30)))
        hdd_used = round(float(hdd.used/(2**30)),1)
        percent = round(float(hdd_used/hdd_total * 100))
        result = str(percent) + "% (" + str("{:.1f}".format(hdd_used)) + "/" + str(hdd_total) + " GB)"
        return result

    def readCpuAndMemory():
        cpuUsage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        mem_total = round(float(memory.total/(2**20)))
        mem_used = round(float(memory.used/(2**20)))
        percent = round(float(mem_used/mem_total * 100))
        memoryUsage = str(percent) + "% (" + str(mem_used) + "/" + str(mem_total) + " MB)"
        usageData = {'cpu': cpuUsage, 'memory': memoryUsage}
        return usageData
