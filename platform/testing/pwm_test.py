import RPi.GPIO as GPIO
import argparse, time
 
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-p", "--Pin", help = "Show Output")
parser.add_argument("-f", "--Frekuensi", help = "Show Output")
parser.add_argument("-c", "--Cycle", help = "Show Output")
parser.add_argument("-t", "--Type", help = "Show Output")
 
# Read arguments from command line
args = parser.parse_args()
pin, frekuensi, tipe, cycle = None, None, None, None

if args.Pin != None:
    pin = args.Pin
if args.Frekuensi != None:
    frekuensi = args.Frekuensi
if args.Type != None:
    tipe = args.Type
if args.Cycle != None:
    cycle = args.Cycle

if pin != None and cycle != None and tipe != None and frekuensi != None:
   try:
      GPIO.setwarnings(False)
      if int(tipe) == 0:
         GPIO.setmode(GPIO.BCM)
         type = "BCM"
      else:
         GPIO.setmode(GPIO.BOARD)
         type = "Board"
      GPIO.setup(int(pin), GPIO.OUT) 
      pi_pwm = GPIO.PWM(int(pin),int(frekuensi))
      pi_pwm.start(0)
      for duty in range(0,int(cycle),1):
          pi_pwm.ChangeDutyCycle(int(cycle))
          time.sleep(0.01)
      time.sleep(0.05)     
      for duty in range(int(cycle),-1,-1):
          pi_pwm.ChangeDutyCycle(int(cycle))
          time.sleep(0.01)     
      print("Test PWM PIN(" + type + ") " + str(pin) + " with Frequency " + str(frekuensi) + " : " + str(cycle))          
   except Exception as e:
      print("Error PIN(" + type + ") " + str(pin) + " : " + str(e))   
else:
   print("Please Fill the Form before Run the Test")