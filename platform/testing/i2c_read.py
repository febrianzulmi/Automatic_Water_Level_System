import argparse, smbus

parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-a", "--Address", help = "Show Output")
parser.add_argument("-s", "--Start", help = "Show Output")
parser.add_argument("-b", "--Block", help = "Show Output")
 
# Read arguments from command line
args = parser.parse_args()
address = None
start = None
block = None

if args.Address != None:
    address = args.Address 
if args.Start != None:
    start = args.Start 
if args.Block != None:
    block = args.Block   
  
if address != None and start != None and block != None:
   try:
      bus = smbus.SMBus(1)
      addr = int(address,16)
      start_addr = int(start,16)
      if int(block) > 0:
         read = bus.read_i2c_block_data(addr, start_addr, int(block))
      else:
         read = bus.read_byte_data(addr,start_addr)
      print("Received Data from Address " + address + " : ")
      print(str(read))
   except Exception as e:
      print("Error Read I2C Address " + address + " : " + str(e))
else:
   print("Please Fill the Form before Run the Test")