import smbus

bus = smbus.SMBus(1) # 1 indicates /dev/i2c-1
count = 0
addr = []
for device in range(128):
      try:
         bus.read_byte(device)
         addr.append(hex(device))
         count+=1
      except: # exception if read_byte fails
         pass
if count > 0:
   print(str(count) + " I2C Address Detected ")
   for i in range(count):
       print("Address " + str(i+1) + " : " + str(addr[i]))
else:
   print("No I2C Address Detected")
    