import Adafruit_ADS1x15
import argparse
 
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-p", "--Pin", help = "Show Output")
parser.add_argument("-g", "--Gain", help = "Show Output")
 
# Read arguments from command line
args = parser.parse_args()
pin, gain = None, None

if args.Pin != None:
    pin = args.Pin
if args.Gain != None:
    gain = args.Gain
if pin != None and gain != None:
   try:
     if int(gain) == 0:
        gain = 2/3
     else:
        gain = int(gain)   
     adc = Adafruit_ADS1x15.ADS1115()
     value = adc.read_adc(int(pin), gain=gain)
     print("Value Analog " + str(pin) + " with Gain " + str(gain) + " : " + str(value))
   except Exception as e:
     print(e)
else:
   print("Please Fill the Form before Run the Test")