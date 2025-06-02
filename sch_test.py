from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import random

c = ModbusClient(method="rtu", port='/dev/ttyUSB0', baudrate=9600, parity='N', stopbits=1, bytesize=8)
c.connect()

#result = c.read_input_registers(address=10414-10001, count=1, unit=1)
#print(result.registers)

#result = c.read_holding_registers(address=40195-40001, count=1, unit=1)
#print(result.registers)

#result =  c.write_register(address=40194-40001, value=50, unit=1)
#print(result.value)

#result = c.read_holding_registers(address=40194-40001, count=1, unit=1)
#print(result.registers)

#result = c.read_discrete_inputs(address=10413-10001, count=1, unit=1)
#print(result.should_respond)    

def writeHolding(addresses, unit, value):
    result = c.write_register(address=addresses-40001, value=value, unit=unit)
    print("Uniconn", unit, "Write Address:",addresses,"=>", result.value)
def writeCoil(addresses, unit, value):
    result = c.write_coil(address=addresses, value=value, unit=unit)
    print("Uniconn", unit, "Write Address:", addresses, "=>", result.value)

print("=============== UNICONN 1 ===============")
diskrit = [10413,10414,10415,10416,10432,10289]
diskrit_string = ["UniConn Locked Out?", "Controller Mode", "Controller Mode", "Controller Mode", "Motor Running Status", "Digital Input 1"]
inputs = [32041,32042,32043,32044,32049,32050,32051,32052,32065,32081,32083,32104,32077,32078,32079,32080]
inputs_string = ["Latched Alarms 0", "Latched Alarms 1", "Latched Alarms 2", "Latched Alarms 3", "Alarms 0", "Alarms 1", "Alarms 2", "Alarms 3", 
                 "Total Starts", "Total Run Time", "Total Off Time", "UniConn Supply voltage", "Current Run Time 1", "Current Run Time 2", "Current Off Time 1", 
                 "Current Off Time 2"]
holding = [40194,40195,40196,40188,40194]
holding_string = ["Low Supply Trip Setpoint", "Low Supply Trip Time", "Low Supply Trip Action", "High Supply Trip Setpoint", "Low Supply Trip Setpoint"]
for x in range(len(diskrit)):
    result = c.read_discrete_inputs(address=diskrit[x]-10001, count=1, unit=1)
    print(f"Read Address {diskrit_string[x]} ({diskrit[x]}) : {result.bits[0]}")
for x in range(len(inputs)):
    result = c.read_input_registers(address=inputs[x]-30001, count=1, unit=1)
    print(f"Read Address {inputs_string[x]} ({inputs[x]}) = {result.registers[0]}")
for x in range(len(holding)):
    result = c.read_holding_registers(address=holding[x]-40001, count=1, unit=1)
    print(f"Read Address {holding_string[x]} ({inputs[x]}) = {result.registers[0]}")
# result = c.read_holding_registers(address=32083-30001, count=1, unit=1)
# print(f"Read Address  (32083) = {result.registers[0]}")
# result = c.read_input_registers(address=32084-30001, count=1, unit=1)
# print(f"Read Address  (32084) = {result.registers[0]}")
# writeHolding(40188, 1, 250)
#writeHolding(40194, 1, random.randint(50,250))
#writeHolding(40195, 1, random.randint(1,10000))
#writeHolding(40196, 1, random.randint(0,3))
# writeCoil(0,1,1) # motor stop
# writeCoil(1,1,1) # clear port
# writeCoil(2,1,0) # motor start
# writeCoil(3,1,1) # clear latch
# writeCoil(4,1,1) # clear lockout

# print("=============== UNICONN 2 ===============")
# diskrit = [10413,10414,10415,10416,10432,10289]
# inputs = [32041,32042,32043,32044,32049,32050,32051,32052,32065,32081,32083,32104]
# holding = [40194,40195,40196]
# for x in range(len(diskrit)):
#     result = c.read_discrete_inputs(address=diskrit[x]-10001, count=1, unit=2                                    )
#     print("Read Address:",diskrit[x],"=>",result.should_respond)
# for x in range(len(inputs)):
#     result = c.read_input_registers(address=inputs[x]-30001, count=1, unit=2)
#     print("Read Address:",inputs[x],"=>",result.registers[0])
# for x in range(len(holding)):
#     result = c.read_holding_registers(address=holding[x]-40001, count=1, unit=2)
#     print("Read Address:",holding[x],"=>",result.registers[0])
#writeHolding(40194, 2, random.randint(50,250))
#writeHolding(40195, 2, random.randint(1,10000))
#writeHolding(40196, 2, random.randint(0,3))
#writeCoil(1,2,0)
#writeCoil(2,2,0)
#writeCoil(3,2,0)
#writeCoil(4,2,0)
#writeCoil(5,2,0)
