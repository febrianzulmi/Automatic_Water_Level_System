#!/usr/bin/env python3
"""
Water Level Sensor RS485 Modbus Reader
Configuration:
- Device ID: 1
- Function: 03 (Read Holding Registers)
- Measuring Value Address: 4
- Baud rate: 9600
- Data Bits: 8
- Parity: None
- Stop Bit: 1
"""

import minimalmodbus
import serial
import time
import sys

class WaterLevelSensor:
    def __init__(self, port='/dev/ttyUSB0', device_id=1, baudrate=9600):
        """
        Initialize the water level sensor
        
        Args:
            port (str): Serial port (e.g., '/dev/ttyUSB0', '/dev/ttyS0', 'COM1')
            device_id (int): Modbus device ID
            baudrate (int): Baud rate (default: 9600)
        """
        self.port = port
        self.device_id = device_id
        self.baudrate = baudrate
        
        # Initialize the Modbus instrument
        self.instrument = minimalmodbus.Instrument(port, device_id)
        
        # Configure Modbus settings
        self.instrument.mode = minimalmodbus.MODE_RTU
        self.instrument.serial.baudrate = baudrate
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = serial.PARITY_NONE
        self.instrument.serial.stopbits = 1
        self.instrument.serial.timeout = 1.0
        self.instrument.close_port_after_each_call = True
        self.instrument.clear_buffers_before_each_transaction = True
        
    def read_water_level(self):
        """
        Read water level from register address 4 using function code 03
        
        Returns:
            dict: Dictionary containing water level value and status
        """
        try:
            # Read register 4 (measuring value address) with function code 03
            # Function code 03 is automatically used by read_registers method
            result = self.instrument.read_registers(4, 1, 3)
            water_level = result[0]
            
            return {
                "success": True,
                "water_level": water_level,
                "unit": "mm",  # Assuming millimeters, adjust as needed
                "message": f"Successfully read water level: {water_level}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "water_level": None,
                "unit": None,
                "message": f"Error reading water level: {str(e)}"
            }
    
    def read_water_level_continuous(self, interval=5):
        """
        Continuously read water level data
        
        Args:
            interval (int): Reading interval in seconds
        """
        print(f"Starting continuous water level monitoring...")
        print(f"Port: {self.port}")
        print(f"Device ID: {self.device_id}")
        print(f"Baud rate: {self.baudrate}")
        print(f"Register address: 4")
        print(f"Function code: 03")
        print(f"Reading interval: {interval} seconds")
        print("-" * 50)
        
        try:
            while True:
                result = self.read_water_level()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                
                if result["success"]:
                    print(f"[{timestamp}] Water Level: {result['water_level']} {result['unit']}")
                else:
                    print(f"[{timestamp}] ERROR: {result['message']}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
    
    def test_connection(self):
        """
        Test the Modbus connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Try to read a register to test connection
            result = self.instrument.read_registers(4, 1, 3)
            print(f"Connection test successful! Read value: {result[0]}")
            return True
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False

def main():
    """Main function to run the water level sensor reader"""
    
    # Configuration
    PORT = '/dev/ttyUSB0'  # Change this to your actual port
    DEVICE_ID = 1
    BAUD_RATE = 9600
    
    # Create sensor instance
    sensor = WaterLevelSensor(port=PORT, device_id=DEVICE_ID, baudrate=BAUD_RATE)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            # Test connection
            sensor.test_connection()
        elif sys.argv[1] == 'single':
            # Single reading
            result = sensor.read_water_level()
            if result["success"]:
                print(f"Water Level: {result['water_level']} {result['unit']}")
            else:
                print(f"Error: {result['message']}")
        else:
            print("Usage:")
            print("  python water_level_rs485.py          # Continuous monitoring")
            print("  python water_level_rs485.py test     # Test connection")
            print("  python water_level_rs485.py single   # Single reading")
    else:
        # Continuous monitoring (default)
        sensor.read_water_level_continuous()

if __name__ == "__main__":
    main()
