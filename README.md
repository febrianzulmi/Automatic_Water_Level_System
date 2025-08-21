# Water Level Sensor RS485 Modbus Reader

Program Python untuk membaca data sensor water level melalui komunikasi RS485 dengan protokol Modbus RTU.

## Konfigurasi Sensor

- **Device ID**: 1
- **Function Code**: 03 (Read Holding Registers)
- **Measuring Value Address**: 4
- **Baud Rate**: 9600
- **Data Bits**: 8
- **Parity**: None
- **Stop Bit**: 1

## Instalasi

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Atau install manual:
```bash
pip install minimalmodbus pyserial
```

### 2. Konfigurasi Port Serial

Edit file `config.py` dan sesuaikan port serial:

```python
SERIAL_PORT = '/dev/ttyUSB0'  # Ganti dengan port yang sesuai
```

**Port yang umum digunakan:**
- Linux: `/dev/ttyUSB0`, `/dev/ttyUSB1`, `/dev/ttyS0`, `/dev/ttyS1`
- Windows: `COM1`, `COM2`, `COM3`, dst.
- macOS: `/dev/tty.usbserial-*`, `/dev/tty.usbmodem*`

## Penggunaan

### 1. Program Dasar (`water_level_rs485.py`)

```bash
# Monitoring berkelanjutan
python water_level_rs485.py

# Test koneksi
python water_level_rs485.py test

# Baca sekali
python water_level_rs485.py single
```

### 2. Program dengan Konfigurasi (`water_level_rs485_config.py`)

```bash
# Monitoring berkelanjutan
python water_level_rs485_config.py

# Test koneksi
python water_level_rs485_config.py test

# Baca sekali
python water_level_rs485_config.py single

# Lihat port yang tersedia
python water_level_rs485_config.py ports

# Bantuan
python water_level_rs485_config.py help
```

## Troubleshooting

### 1. Permission Error (Linux)

Jika mendapat error permission, jalankan dengan sudo:

```bash
sudo python water_level_rs485_config.py test
```

Atau tambahkan user ke group dialout:

```bash
sudo usermod -a -G dialout $USER
# Logout dan login kembali
```

### 2. Port Tidak Ditemukan

Cek port yang tersedia:

```bash
python water_level_rs485_config.py ports
```

Atau di Linux:
```bash
ls /dev/ttyUSB*
ls /dev/ttyS*
```

### 3. Koneksi Gagal

1. Pastikan sensor terhubung dan mendapat power
2. Periksa kabel RS485 (A+ dan B-)
3. Pastikan Device ID sesuai
4. Cek baud rate dan setting komunikasi

## Struktur File

```
├── water_level_rs485.py          # Program dasar
├── water_level_rs485_config.py   # Program dengan konfigurasi
├── config.py                     # File konfigurasi
├── requirements.txt              # Dependencies
└── README.md                     # Dokumentasi ini
```

## Contoh Output

### Monitoring Berkelanjutan
```
============================================================
Water Level Sensor RS485 Modbus Reader
============================================================
Serial Port: /dev/ttyUSB0
Device ID: 1
Baud Rate: 9600
Register Address: 4
Function Code: 3
Reading Interval: 5 seconds
Unit: mm
============================================================
Press Ctrl+C to stop monitoring
------------------------------------------------------------
[2024-01-15 14:30:25] Water Level: 1250 mm
[2024-01-15 14:30:30] Water Level: 1252 mm
[2024-01-15 14:30:35] Water Level: 1248 mm
```

### Test Koneksi
```
Testing connection to /dev/ttyUSB0...
✓ Connection test successful!
✓ Read value: 1250 mm
```

## Integrasi dengan Sistem Lain

Program ini dapat diintegrasikan dengan sistem monitoring atau database dengan memodifikasi fungsi `read_water_level()` untuk mengembalikan data dalam format yang sesuai.

## Catatan Teknis

- Program menggunakan library `minimalmodbus` untuk komunikasi Modbus RTU
- Timeout default: 1 detik
- Buffer dibersihkan sebelum setiap transaksi
- Port ditutup setelah setiap panggilan untuk menghindari konflik

## Lisensi

Program ini dibuat untuk keperluan monitoring sensor water level. Silakan modifikasi sesuai kebutuhan.
     
