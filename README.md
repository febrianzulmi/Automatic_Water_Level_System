# 🚰 Sistem Kontrol Pompa Air Otomatis

Sistem kontrol pompa air otomatis berdasarkan level air menggunakan sensor RS485 Modbus dan Raspberry Pi GPIO.

## 📋 Fitur

- ✅ Monitoring level air real-time via RS485 Modbus
- ✅ Kontrol pompa otomatis berdasarkan threshold

- ✅ Logging aktivitas lengkap
- ✅ Konfigurasi yang mudah disesuaikan
- ✅ Test mode untuk sensor dan pompa
- ✅ Status monitoring sistem

## 🔧 Spesifikasi Teknis

### Sensor Water Level
- **Protocol**: RS485 Modbus RTU
- **Device ID**: 1
- **Function Code**: 03 (Read Holding Registers)
- **Register Address**: 4
- **Baud Rate**: 9600
- **Data Bits**: 8
- **Parity**: None
- **Stop Bit**: 1

### Kontrol Pompa
- **GPIO Pin**: 0 (dapat diubah di config)
- **Logic**: 
  - Pompa AKTIF saat level air ≤ 0 cm
  - Pompa MATI saat level air ≥ 10 cm



## 📁 Struktur File

```
├── water_level_pump_control.py  # Program utama
├── pump_config.py              # File konfigurasi
├── water_level_rs485.py        # Versi sederhana
├── water_level_rs485_config.py # Versi dengan config
└── README.md                   # Dokumentasi ini
```

## 🚀 Instalasi

### 1. Install Dependencies

```bash
# Install minimalmodbus untuk RS485
pip install minimalmodbus

# Install RPi.GPIO untuk kontrol GPIO
pip install RPi.GPIO

# Install pyserial (biasanya sudah terinstall dengan minimalmodbus)
pip install pyserial
```

### 2. Koneksi Hardware

#### Sensor Water Level RS485
```
Raspberry Pi    Sensor RS485
TX (GPIO 14) -> RX
RX (GPIO 15) -> TX
GND         -> GND
3.3V/5V     -> VCC
```

#### Pompa Air
```
Raspberry Pi    Relay Module    Pompa Air
GPIO 0      -> IN1
GND         -> GND
5V          -> VCC
                    -> Pompa Air
```

### 3. Konfigurasi

Edit file `pump_config.py` sesuai kebutuhan:

```python
# Konfigurasi Sensor
SERIAL_PORT = '/dev/ttyUSB0'  # Port serial
DEVICE_ID = 1                 # ID device Modbus
BAUD_RATE = 9600              # Baud rate

# Konfigurasi Pompa
PUMP_GPIO_PIN = 0             # GPIO pin untuk pompa
PUMP_ON_THRESHOLD = 0         # Level untuk aktifkan pompa (cm)
PUMP_OFF_THRESHOLD = 10       # Level untuk matikan pompa (cm)

# Fitur Keamanan
SAFETY_TIMEOUT = 300          # Timeout keamanan (detik)
MAX_PUMP_RUNTIME = 600        # Maksimal runtime pompa (detik)
```

## 🎯 Penggunaan

### Monitoring Kontinyu (Default)
```bash
python water_level_pump_control.py
```

### Test Sensor
```bash
python water_level_pump_control.py test
```

### Test Pompa
```bash
python water_level_pump_control.py pump
```

### Cek Status Sistem
```bash
python water_level_pump_control.py status
```

### Bantuan
```bash
python water_level_pump_control.py help
```

## 📊 Output Contoh

```
🚰 SISTEM KONTROL LEVEL AIR & POMPA
============================================================
📡 Port: /dev/ttyUSB0
🆔 Device ID: 1
⚡ Baud rate: 9600
🔌 Pump GPIO Pin: 0
🟢 Pompa AKTIF: Level ≤ 0 cm
🔴 Pompa MATI: Level ≥ 10 cm
⏱️  Interval: 5 detik


============================================================
Tekan Ctrl+C untuk menghentikan
------------------------------------------------------------
[2024-01-15 14:30:25] Level: 5.2 cm | Pompa: 🔴 MATI
[2024-01-15 14:30:30] Level: 0.1 cm | Pompa: 🟢 AKTIF
[2024-01-15 14:30:35] Level: 0.0 cm | Pompa: 🟢 AKTIF (Runtime: 5.0s)
[2024-01-15 14:30:40] Level: 2.5 cm | Pompa: 🟢 AKTIF (Runtime: 10.0s)
[2024-01-15 14:30:45] Level: 10.1 cm | Pompa: 🔴 MATI - Level air mencapai 10.1 cm (Runtime: 15.0s)
```

## 🔍 Troubleshooting

### Error "Permission denied" pada port serial
```bash
# Tambahkan user ke group dialout
sudo usermod -a -G dialout $USER

# Atau jalankan dengan sudo
sudo python water_level_pump_control.py
```

### Sensor tidak terdeteksi
1. Cek koneksi kabel RS485
2. Pastikan port serial benar (`/dev/ttyUSB0`, `/dev/ttyS0`, dll)
3. Test dengan command `ls /dev/tty*`
4. Cek baud rate dan device ID

### Pompa tidak berfungsi
1. Cek koneksi GPIO ke relay
2. Test pompa manual dengan command `pump`
3. Pastikan relay module mendapat power supply yang cukup
4. Cek apakah pompa memerlukan arus yang lebih besar

### Logging
Semua aktivitas dicatat di file `water_pump_control.log`:
```bash
tail -f water_pump_control.log
```

## ⚙️ Kustomisasi

### Mengubah Threshold Level
Edit `pump_config.py`:
```python
PUMP_ON_THRESHOLD = 5    # Pompa aktif saat level ≤ 5 cm
PUMP_OFF_THRESHOLD = 15  # Pompa mati saat level ≥ 15 cm
```

### Mengubah GPIO Pin
```python
PUMP_GPIO_PIN = 17  # Ganti ke GPIO 17
```

### Mengubah Interval Monitoring
```python
READING_INTERVAL = 10  # Baca setiap 10 detik
```

## 🛡️ Fitur Keamanan

1. **Auto Cleanup**: GPIO akan dibersihkan saat program berhenti
2. **Error Handling**: Sistem akan menangani error dengan graceful

## 📝 Log

File log `water_pump_control.log` berisi:
- Aktivitas pompa (ON/OFF)
- Error sensor
- Runtime pompa
- Timestamp lengkap

## 🤝 Kontribusi

Jika menemukan bug atau ingin menambah fitur, silakan buat issue atau pull request.

## 📄 Lisensi

Program ini dibuat untuk keperluan edukasi dan penggunaan pribadi.

---

**⚠️ Peringatan**: Pastikan sistem air Anda aman dan tidak ada kebocoran sebelum menggunakan sistem otomatis ini.
     
