import argparse, smbus

def convertByte(data):
    if len(data) > 1:
       datas = []
       for i in data:
           datas.append(ord(i))
    else:
       datas = ord(data)       
    return datas

parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-a", "--Address", help = "Show Output")
parser.add_argument("-r", "--Register", help = "Show Output")
parser.add_argument("-d", "--Data", help = "Show Output")
 
# Read arguments from command line
args = parser.parse_args()
address = None
register = None
data = None

if args.Address != None:
    address = args.Address 
if args.Register != None:
    register = args.Register 
if args.Data != None:
    data = args.Data   
  
if address != None and register != None and data != None:
   try:
      bus = smbus.SMBus(1)
      addr = int(address,16)
      reg = int(register,16)
      datas = convertByte(data)
      if type(datas) == list:
         bus.write_i2c_block_data(addr, reg, datas)
      else:
         bus.write_byte_data(addr, reg, datas)
      print("Write Data Address " + address + " : ")
      print("String => " + str(data))
      print("Byte => " + str(datas))
   except Exception as e:
      print("Error Write I2C Address " + address + " : " + str(e))
else:
   print("Please Fill the Form before Run the Test")