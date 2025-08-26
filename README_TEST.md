# 🚰 Water Pump Test - Versi Sederhana

File sederhana untuk tes kontrol pompa air berdasarkan level air sensor RS485.

## 📋 Fitur

- ✅ Monitoring level air real-time via RS485 Modbus
- ✅ Safety OFF otomatis saat level tinggi (10 cm)
- ✅ Kontrol ON manual via dashboard
- ✅ Tanpa logging file
- ✅ Tanpa fitur keamanan kompleks
- ✅ Hanya untuk tes

## 🔧 Konfigurasi

Edit langsung di dalam file `water_pump_test.py`:

```python
# Konfigurasi
SERIAL_PORT = '/dev/ttyUSB0'    # Port serial
DEVICE_ID = 1                   # ID device Modbus
BAUD_RATE = 9600                # Baud rate
READING_INTERVAL = 5            # Interval baca (detik)
PUMP_GPIO_PIN = 0               # GPIO pin untuk pompa
PUMP_OFF_THRESHOLD = 10         # Level untuk matikan pompa (cm) - Safety OFF
WATER_LEVEL_UNIT = 'cm'         # Unit sensor (mm atau cm)
```

## 🚀 Penggunaan

### Install Dependencies
```bash
pip install minimalmodbus RPi.GPIO pyserial
```

### Test Sensor
```bash
python3 water_pump_test.py test
```

### Test Pompa
```bash
python3 water_pump_test.py pump
```

### Monitoring Kontinyu
```bash
python3 water_pump_test.py
```

### Bantuan
```bash
python3 water_pump_test.py help
```

## 📊 Output Contoh

```
🚰 SISTEM KONTROL LEVEL AIR & POMPA - VERSI TEST
============================================================
📡 Port: /dev/ttyUSB0
🆔 Device ID: 1
⚡ Baud rate: 9600
🔌 Pump GPIO Pin: 0
🔴 Pompa MATI: Level ≥ 10 cm (Safety OFF)
🟢 Pompa ON: Manual control via dashboard
⏱️  Interval: 5 detik
============================================================
Tekan Ctrl+C untuk menghentikan
------------------------------------------------------------
[2024-01-15 14:30:25] Level: 5.2 cm | Pompa: 🔴 MATI
[2024-01-15 14:30:30] Level: 0.1 cm | Pompa: 🔴 MATI (Manual control)
[2024-01-15 14:30:35] Level: 10.1 cm | Pompa: 🔴 MATI (Safety OFF)
```

## ⚠️ Troubleshooting

### Permission Error
```bash
sudo python3 water_pump_test.py
```

### Port Serial Tidak Ditemukan
```bash
ls /dev/tty*
# Edit SERIAL_PORT di dalam file
```

### Pompa Tidak Berfungsi
```bash
python3 water_pump_test.py pump
```

## 📝 Catatan

- File ini hanya untuk tes, tidak ada logging ke file
- Tidak ada fitur keamanan kompleks
- Pastikan hardware terhubung dengan benar
- Gunakan Ctrl+C untuk menghentikan program

---

**�� Siap untuk tes!**
