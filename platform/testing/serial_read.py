import serial, argparse

parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-p", "--Pin", help = "Show Output")
parser.add_argument("-r", "--Rate", help = "Show Output")
parser.add_argument("-t", "--Timeout", help = "Show Output")
 
# Read arguments from command line
args = parser.parse_args()
pin, timeout, rate = None, None, None

if args.Pin != None:
    pin = args.Pin
if args.Timeout != None:
    timeout = args.Timeout    
if args.Rate != None:
    rate = args.Rate    
    
if pin != None and timeout != None and rate != None:
   try:
      if int(timeout) == 0:
         ser = serial.Serial(pin, int(rate))
      else:
         ser = serial.Serial(pin, int(rate), timeout=int(timeout))
      line = ser.readline()
      data = line.decode().strip()
      if data == '':
         print("No Received Data from Serial Port " + pin)
      else:
         print("Received Data from Serial Port " + pin + " : ")
         print(data)
   except Exception as e:
      print("Error Read Data from Serial Port " + pin)
else:
   print("Please Fill the Form before Run the Test")
