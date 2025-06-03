import sys
import time
import RPi.GPIO as GPIO
from PIL import ImageFont

sys.path.append('/home/connex/library')
from SynapsisLibrary import times
sys.path.append('/home/connex/project/database')
from query_project_db import SystemServiceDB
sys.path.append('/home/connex/project/function')
from displayFunction import displayFunction
from serviceProjectFunction import ServiceProjectFunction


# GPIO pin configuration for the buttons
BTN_UP_PIN = 26        
BTN_DOWN_PIN = 1   
BTN_SELECT_PIN = 0     
BTN_BACK_PIN = 7        

# Set GPIO mode to BCM
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Setup button pins as inputs with pull-up resistors
GPIO.setup(BTN_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_SELECT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_BACK_PIN, GPIO.IN, GPIO.PUD_UP)

# Initialize the OLED display
OLED_RESET_PIN = None  # Set to GPIO pin if your display has a reset pin
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED = None

# Load default font
FONT = ImageFont.load_default()
wifiIcon = ImageFont.truetype('font/fontawesome-webfont.ttf', 18)
ethernetIcon = ImageFont.truetype('font/fa-solid-900.ttf', 18)
fontNavbar = ImageFont.truetype('font/ArialCE.ttf', 9)
FONT_SMALL = ImageFont.truetype('font/ArialCE.ttf', 9)
FONT_SELECT = ImageFont.truetype('font/ArialCE.ttf', 17)

globalVariable = {"font": {}, "oled": {}, "button": {}, "service": {}, "logo": 'logo/logoSynapsisPutih.png', "splashState": 0}
globalVariable["font"] = {"ethernet": ethernetIcon, "wifi": wifiIcon, "navbar": fontNavbar, "small": FONT_SMALL, "select": FONT_SELECT, "default": FONT}
globalVariable["oled"] = {"oled": OLED, "oled_reset": OLED_RESET_PIN, "oled_width": OLED_WIDTH, "oled_height": OLED_HEIGHT}
globalVariable["button"] = {"down": BTN_DOWN_PIN, "up": BTN_UP_PIN, "select": BTN_SELECT_PIN, "back": BTN_BACK_PIN}
globalVariable['service'] = {"service_name": "connex_display", "service_message": "N/A"}

try:
    while globalVariable["oled"]["oled"] == None:
        timestamp = times.getDatetime()
        globalVariable= displayFunction.setup(globalVariable)
        if globalVariable["oled"]["oled"] == None:
            print(f"{timestamp} - Hardware Display N/A")
            SystemServiceDB.updateStatusByName("Hardware Display N/A", timestamp, globalVariable['service']['service_name'])  
            time.sleep(5)
        else:
            break
    displayFunction.mainFunction.main(globalVariable)
except Exception as e:
    ServiceProjectFunction.handlingServiceError('Display', str(e))
