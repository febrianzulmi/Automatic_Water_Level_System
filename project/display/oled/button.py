import RPi.GPIO as GPIO
import time

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
GPIO.setup(BTN_BACK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_buttons():
    while True:
        if not GPIO.input(BTN_UP_PIN):  # Button pressed
            print("UP button pressed")
        if not GPIO.input(BTN_DOWN_PIN):
            print("DOWN button pressed")
        if not GPIO.input(BTN_SELECT_PIN):
            print("SELECT button pressed")
        if not GPIO.input(BTN_BACK_PIN):
            print("BACK button pressed")
        time.sleep(0.1)  # Debounce delay

try:
    print("Press buttons to see their status. Press Ctrl+C to exit.")
    read_buttons()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()  # Reset GPIO configuration
