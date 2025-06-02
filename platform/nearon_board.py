import RPi.GPIO as GPIO
import os, time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, 1)
time.sleep(10)
#os.system("ntpdate -u id.pool.ntp.org")

