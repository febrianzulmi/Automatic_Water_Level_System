# 🚰 Automatic Water Pump Control System

An automated water level and pump control system using an RS485 Modbus sensor and Raspberry Pi GPIO.
<img width="377" height="507" alt="image" src="https://github.com/user-attachments/assets/10ade186-8e01-46ad-8878-5db031a77223" />

## 📋 Features

- ✅ Real-time water level monitoring via RS485 Modbus
- ✅ Automated pump control based on configured thresholds
- ✅ Comprehensive activity logging
- ✅ Easily customizable configuration
- ✅ Test mode for sensors and pumps
- ✅ System status monitoring

## 🔧 Technical Specifications

### Water Level Sensor
- **Protocol**: RS485 Modbus RTU
- **Device ID**: 1
- **Function Code**: 03 (Read Holding Registers)
- **Register Address**: 4
- **Baud Rate**: 9600
- **Data Bits**: 8
- **Parity**: None
- **Stop Bit**: 1

### Pump Control
- **GPIO Pin**: 0 (configurable)
- **Logic**: 
  - Pump is **ACTIVE** when water level ≤ 0 cm
  - Pump is **OFF** when water level ≥ 10 cm

## 📁 File Structure

```text
├── water_level_pump_control.py   # Main program
├── pump_config.py                # Configuration file
├── water_level_rs485.py          # Simple version
├── water_level_rs485_config.py   # Configurable version
└── README.md                     # This documentation
```

## 🚀 Installation

### 1. Install Dependencies

```bash
# Install minimalmodbus for RS485
pip install minimalmodbus

# Install RPi.GPIO for GPIO control
pip install RPi.GPIO

# Install pyserial (usually installed automatically with minimalmodbus)
pip install pyserial
```

### 2. Hardware Connections

#### RS485 Water Level Sensor
```text
Raspberry Pi     RS485 Sensor
TX (GPIO 14) -> RX
RX (GPIO 15) -> TX
GND          -> GND
3.3V/5V      -> VCC
```

#### Water Pump (via Relay Module)
```text
Raspberry Pi     Relay Module    Water Pump
GPIO 0       -> IN1
GND          -> GND
5V           -> VCC
                 -> Water Pump
```

### 3. Configuration

Edit the `pump_config.py` file according to your needs:

```python
# Sensor Configuration
SERIAL_PORT = '/dev/ttyUSB0'  # Serial port
DEVICE_ID = 1                 # Modbus Device ID
BAUD_RATE = 9600              # Baud rate

# Pump Configuration
PUMP_GPIO_PIN = 0             # GPIO pin for the pump
PUMP_ON_THRESHOLD = 0         # Water level to activate pump (cm)
PUMP_OFF_THRESHOLD = 10       # Water level to deactivate pump (cm)

# Safety Features
SAFETY_TIMEOUT = 300          # Safety timeout (seconds)
MAX_PUMP_RUNTIME = 600        # Maximum pump runtime (seconds)
```

## 🎯 Usage

### Continuous Monitoring (Default)
```bash
python water_level_pump_control.py
```

### Test Sensor
```bash
python water_level_pump_control.py test
```

### Test Pump
```bash
python water_level_pump_control.py pump
```

### Check System Status
```bash
python water_level_pump_control.py status
```

### Help
```bash
python water_level_pump_control.py help
```

## 📊 Sample Output

```text
🚰 WATER LEVEL & PUMP CONTROL SYSTEM
============================================================
📡 Port: /dev/ttyUSB0
🆔 Device ID: 1
⚡ Baud rate: 9600
🔌 Pump GPIO Pin: 0
🟢 Pump ACTIVE: Level ≤ 0 cm
🔴 Pump OFF: Level ≥ 10 cm
⏱️ Interval: 5 seconds

============================================================
Press Ctrl+C to stop
------------------------------------------------------------
[2024-01-15 14:30:25] Level: 5.2 cm | Pump: 🔴 OFF
[2024-01-15 14:30:30] Level: 0.1 cm | Pump: 🟢 ACTIVE
[2024-01-15 14:30:35] Level: 0.0 cm | Pump: 🟢 ACTIVE (Runtime: 5.0s)
[2024-01-15 14:30:40] Level: 2.5 cm | Pump: 🟢 ACTIVE (Runtime: 10.0s)
[2024-01-15 14:30:45] Level: 10.1 cm | Pump: 🔴 OFF - Water level reached 10.1 cm (Runtime: 15.0s)
```

## 🔍 Troubleshooting

### "Permission denied" error on serial port
```bash
# Add user to the dialout group
sudo usermod -a -G dialout $USER

# Or run with sudo
sudo python water_level_pump_control.py
```

### Sensor not detected
1. Check RS485 wiring connections.
2. Ensure the correct serial port is used (`/dev/ttyUSB0`, `/dev/ttyS0`, etc.).
3. Test using the command `ls /dev/tty*`.
4. Verify the baud rate and device ID.

### Pump not working
1. Check GPIO-to-relay wiring connections.
2. Test the pump manually using the `pump` command.
3. Ensure the relay module receives an adequate power supply.
4. Check if your pump requires higher current capacity.

### Logging
All activities are recorded in `water_pump_control.log`:
```bash
tail -f water_pump_control.log
```

## ⚙️ Customization

### Changing Level Thresholds
Edit `pump_config.py`:
```python
PUMP_ON_THRESHOLD = 5    # Pump active when level ≤ 5 cm
PUMP_OFF_THRESHOLD = 15  # Pump off when level ≥ 15 cm
```

### Changing GPIO Pin
```python
PUMP_GPIO_PIN = 17  # Change to GPIO 17
```

### Changing Monitoring Interval
```python
READING_INTERVAL = 10  # Read every 10 seconds
```

## 🛡️ Safety Features

1. **Auto Cleanup**: GPIO states are cleaned up automatically when the program stops.
2. **Error Handling**: Graceful exception handling for runtime errors.

## 📝 Logs

The `water_pump_control.log` file records:
- Pump activities (ON/OFF)
- Sensor errors
- Pump runtimes
- Complete timestamps

## 🤝 Contributing

If you find any bugs or want to add new features, feel free to open an issue or submit a pull request.

## 📄 License

This program is created for educational and personal use purposes.

---

**⚠️ Warning**: Ensure your water system is secure and free of leaks before running this automation system.
