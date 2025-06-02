import serial, argparse

parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-p", "--Pin", help = "Show Output")
parser.add_argument("-r", "--Rate", help = "Show Output")
parser.add_argument("-t", "--Timeout", help = "Show Output")
parser.add_argument("-v", "--Value", help = "Show Output")
 
# Read arguments from command line
args = parser.parse_args()
pin, timeout, rate, value = None, None, None, None

if args.Pin != None:
    pin = args.Pin
if args.Timeout != None:
    timeout = args.Timeout    
if args.Rate != None:
    rate = args.Rate
if args.Value != None:
    value = args.Value    
    
if pin != None and timeout != None and rate != None and value != None:
   try:
      if int(timeout) == 0:
         ser = serial.Serial(pin, int(rate))
      else:
         ser = serial.Serial(pin, int(rate), timeout=int(timeout))
      values = value.encode()
      ser.write(values)
      print("Write Data from Serial Port " + pin + " : " + value)
   except Exception as e:
      print("Error Write Data from Serial Port " + pin)
else:
   print("Please Fill the Form before Run the Test")