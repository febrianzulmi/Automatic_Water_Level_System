path = "/home/connex"

import asyncio
import sys

import serial

sys.path.append(f"{path}/project/function")
from displayFunction import DisplayFunction
from serviceProjectFunction import ServiceProjectFunction
from logFunction import logFunction


ser = serial.Serial('/dev/ttyS0', 9600, timeout=3)
loop = asyncio.get_event_loop()
global_variable = {}
global_variable["serviceName"] = "nearon_display"
global_variable["logger"] = logFunction.setupLogger(global_variable["serviceName"], stream=True) 

async def main(loop, ser):
    await DisplayFunction.MainFunction.send_command(loop, ser, ["page 0"], global_variable)
    await DisplayFunction.update_page(loop, ser, 1, global_variable)
    await asyncio.gather(
        DisplayFunction.MainFunction.update_values_periodically(loop, ser, global_variable),
        DisplayFunction.MainFunction.read_serial(loop, ser, global_variable)
    )

try:
    loop.run_until_complete(main(loop, ser))
except KeyboardInterrupt:
    print("Interrupted By User.")
except Exception as e:
    print(f"Error: {e}")
    ServiceProjectFunction.handlingServiceError('Display', str(e), global_variable)
finally:
    ser.close()
