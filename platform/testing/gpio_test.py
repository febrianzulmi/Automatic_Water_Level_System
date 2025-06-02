import RPi.GPIO as GPIO
import argparse
import time
 
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-p", "--Pin", help = "Show Output")
parser.add_argument("-m", "--Mode", help = "Show Output")
parser.add_argument("-t", "--Type", help = "Show Output")
parser.add_argument("-a", "--Action", help = "Show Output")
 
# Read arguments from command line
args = parser.parse_args()
pin, mode, tipe, action= None, None, None, None

if args.Pin != None:
    pin = args.Pin
if args.Mode != None:
    mode = args.Mode
if args.Type != None:
    tipe = args.Type
if args.Action != None:
    action = args.Action

if pin != None and mode != None and tipe != None:
   try:
      GPIO.setwarnings(False)
      if int(tipe) == 0:
         GPIO.setmode(GPIO.BCM)
         type = "BCM"
      else:
         GPIO.setmode(GPIO.BOARD)
         type = "Board"
      if int(mode) == 0:
         GPIO.setup(int(pin), GPIO.IN)
         result = GPIO.input(int(pin))
         print("Input PIN(" + type + ") " + str(pin) + " : " + str(result))
      else:
         GPIO.setup(int(pin), GPIO.OUT) 
         result = GPIO.output(int(pin),int(action))   
         print("Output PIN(" + type + ") " + str(pin) + " : " + str(action)) 
                    
   except Exception as e:
      print("Error PIN(" + type + ") " + str(pin) + " : " + str(e))      
else:
   print("Please Fill the Form before Run the Test")