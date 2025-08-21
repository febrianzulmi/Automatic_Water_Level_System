#!/usr/bin/env python3
"""
Water Level Sensor RS485 Modbus Reader with Configuration File
Configuration:
- Device ID = 1
- Function = 03 (Read Holding Registers)
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
import os

# Import configuration
try:
    from config import *
except ImportError:
    print("Warning: config.py not found. Using default settings.")
    # Default configuration
    SERIAL_PORT = '/dev/ttyUSB0'
    DEVICE_ID = 1
    FUNCTION_CODE = 3
    MEASURING_VALUE_ADDRESS = 4
    BAUD_RATE = 9600
    DATA_BITS = 8
    PARITY = 'N'
    STOP_BITS = 1
    READING_INTERVAL = 5
    TIMEOUT = 1.0
    WATER_LEVEL_UNIT = 'mm'

class WaterLevelSensor:
    def __init__(self, port=SERIAL_PORT, device_id=DEVICE_ID, baudrate=BAUD_RATE):
        """
        Initialize the water level sensor
        
        Args:
            port (str): Serial port
            device_id (int): Modbus device ID
            baudrate (int): Baud rate
        """
        self.port = port
        self.device_id = device_id
        self.baudrate = baudrate
        
        # Initialize the Modbus instrument
        self.instrument = minimalmodbus.Instrument(port, device_id)
        
        # Configure Modbus settings
        self.instrument.mode = minimalmodbus.MODE_RTU
        self.instrument.serial.baudrate = baudrate
        self.instrument.serial.bytesize = DATA_BITS
        self.instrument.serial.parity = serial.PARITY_NONE
        self.instrument.serial.stopbits = STOP_BITS
        self.instrument.serial.timeout = TIMEOUT
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
            result = self.instrument.read_registers(MEASURING_VALUE_ADDRESS, 1, FUNCTION_CODE)
            water_level = result[0]
            
            return {
                "success": True,
                "water_level": water_level,
                "unit": WATER_LEVEL_UNIT,
                "message": f"Successfully read water level: {water_level} {WATER_LEVEL_UNIT}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "water_level": None,
                "unit": None,
                "message": f"Error reading water level: {str(e)}"
            }
    
    def read_water_level_continuous(self, interval=READING_INTERVAL):
        """
        Continuously read water level data
        
        Args:
            interval (int): Reading interval in seconds
        """
        print("=" * 60)
        print("Water Level Sensor RS485 Modbus Reader")
        print("=" * 60)
        print(f"Serial Port: {self.port}")
        print(f"Device ID: {self.device_id}")
        print(f"Baud Rate: {self.baudrate}")
        print(f"Register Address: {MEASURING_VALUE_ADDRESS}")
        print(f"Function Code: {FUNCTION_CODE}")
        print(f"Reading Interval: {interval} seconds")
        print(f"Unit: {WATER_LEVEL_UNIT}")
        print("=" * 60)
        print("Press Ctrl+C to stop monitoring")
        print("-" * 60)
        
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
            print(f"Testing connection to {self.port}...")
            result = self.instrument.read_registers(MEASURING_VALUE_ADDRESS, 1, FUNCTION_CODE)
            print(f"✓ Connection test successful!")
            print(f"✓ Read value: {result[0]} {WATER_LEVEL_UNIT}")
            return True
        except Exception as e:
            print(f"✗ Connection test failed: {str(e)}")
            print("\nTroubleshooting tips:")
            print("1. Check if the serial port is correct")
            print("2. Verify the device is connected and powered")
            print("3. Check if you have permission to access the port")
            print("4. Try running with sudo if on Linux")
            return False

def list_available_ports():
    """List available serial ports"""
    import glob
    
    print("Available serial ports:")
    
    # Linux
    for port in glob.glob('/dev/ttyUSB*'):
        print(f"  {port}")
    for port in glob.glob('/dev/ttyS*'):
        print(f"  {port}")
    
    # Windows
    for i in range(10):
        port = f'COM{i}'
        try:
            import serial
            s = serial.Serial(port)
            s.close()
            print(f"  {port}")
        except:
            pass

def main():
    """Main function to run the water level sensor reader"""
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            # Test connection
            sensor = WaterLevelSensor()
            sensor.test_connection()
        elif sys.argv[1] == 'single':
            # Single reading
            sensor = WaterLevelSensor()
            result = sensor.read_water_level()
            if result["success"]:
                print(f"Water Level: {result['water_level']} {result['unit']}")
            else:
                print(f"Error: {result['message']}")
        elif sys.argv[1] == 'ports':
            # List available ports
            list_available_ports()
        elif sys.argv[1] == 'help':
            print("Water Level Sensor RS485 Modbus Reader")
            print("\nUsage:")
            print("  python water_level_rs485_config.py          # Continuous monitoring")
            print("  python water_level_rs485_config.py test     # Test connection")
            print("  python water_level_rs485_config.py single   # Single reading")
            print("  python water_level_rs485_config.py ports    # List available ports")
            print("  python water_level_rs485_config.py help     # Show this help")
            print("\nConfiguration:")
            print("  Edit config.py to adjust settings")
        else:
            print("Unknown command. Use 'help' for usage information.")
    else:
        # Continuous monitoring (default)
        sensor = WaterLevelSensor()
        sensor.read_water_level_continuous()

if __name__ == "__main__":
    main()
