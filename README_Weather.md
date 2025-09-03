# Weather Station Sensor

Sistem sensor weather station yang terintegrasi dengan `sensorLibrary.py` dan dapat dijalankan melalui `sensor4.py`.

## Struktur File

- `sensorLibrary.py` - Library utama yang berisi class `Weather`
- `weather_sensor.py` - Main function untuk menjalankan weather station sensor
- `weather_config.py` - File konfigurasi untuk weather station
- `tes_weather.py` - File asli yang sudah diintegrasikan

## Fitur

### Sensor yang Didukung

1. **Wind Speed** - Kecepatan angin (m/s)
2. **Wind Strength** - Kekuatan angin
3. **Wind Direction 1** - Arah angin (0-7)
4. **Wind Direction 2** - Arah angin (0-360°)
5. **Humidity** - Kelembaban (%)
6. **Temperature** - Suhu (°C)
7. **PM2.5** - Partikel udara 2.5μm (μg/m³)
8. **PM1.0** - Partikel udara 1.0μm (μg/m³)
9. **Atmospheric Pressure** - Tekanan atmosfer (kPa)
10. **Illuminance Low** - Pencahayaan rendah (Lux)
11. **Illuminance High** - Pencahayaan tinggi (Lux)
12. **Illuminance** - Pencahayaan (Lux)
13. **Rainfall** - Curah hujan (mm)

### Konfigurasi Hardware

- **Port**: `/dev/ttyUSB0` (default)
- **Baudrate**: 4800
- **Slave ID**: 2
- **Timeout**: 2 detik
- **Retries**: 3 kali

## Cara Penggunaan

### 1. Menjalankan weather_sensor.py

```bash
python3 weather_sensor.py
```

### 2. Menggunakan class Weather di script lain

```python
from sensorLibrary import Weather

# Inisialisasi weather station
weather = Weather(groupId=1, dataSensor={
    "numSensor": 3,
    "sensorId": ["temperature", "humidity", "windSpeed"],
    "sensorDatatype": [0, 0, 0]
})

# Baca sensor
result = weather.main()
print(result)
```

### 3. Konfigurasi Custom

```python
from weather_config import WEATHER_CONFIG, SENSOR_CONFIG

# Ubah konfigurasi
WEATHER_CONFIG["port"] = "/dev/ttyUSB1"
WEATHER_CONFIG["baudrate"] = 9600
```

## Struktur Data Sensor

### Input Data Sensor

```python
dataSensor = {
    "numSensor": 8,  # Jumlah sensor
    "sensorId": [    # Daftar ID sensor
        "windSpeed",
        "humidity",
        "temperature",
        # ... sensor lainnya
    ],
    "sensorDatatype": [  # Tipe data sensor (0=numeric, 1=string)
        0, 0, 0,  # ... sesuai jumlah sensor
    ]
}
```

### Output Result

```python
{
    "value": [25.5, 60.2, 2.1, ...],  # Nilai sensor
    "message": "8 Sensors Success Sampling",  # Status message
    "state": [True, True, True, ...]  # Status setiap sensor
}
```

## Error Handling

Sistem memiliki error handling yang robust:

1. **Koneksi Error** - Otomatis retry koneksi
2. **Register Error** - Return nilai default jika gagal baca
3. **Timeout Error** - Handle timeout komunikasi serial
4. **Reconnection** - Otomatis reconnect jika koneksi terputus

## Integrasi dengan Database

Class Weather dapat diintegrasikan dengan sistem database yang ada:

```python
# Contoh integrasi dengan database
from sensorLibrary import Weather
from query_project_db import SensorListDB

weather = Weather(groupId, dataSensor)
result = weather.main()

# Simpan ke database
for i, sensor_id in enumerate(dataSensor["sensorId"]):
    SensorListDB.updateValue(
        result["value"][i], 
        times.now(), 
        sensor_id
    )
```

## Troubleshooting

### 1. Port tidak ditemukan

```bash
# Cek port yang tersedia
ls /dev/ttyUSB*
ls /dev/ttyACM*

# Pastikan permission port
sudo chmod 666 /dev/ttyUSB0
```

### 2. Koneksi gagal

- Periksa kabel USB
- Pastikan weather station menyala
- Cek baudrate dan slave ID
- Restart weather station

### 3. Data tidak akurat

- Kalibrasi sensor
- Periksa multiplier dan offset
- Pastikan register address benar

## Development

### Menambah Sensor Baru

1. Tambah register address di `weather_config.py`
2. Update mapping di class `Weather`
3. Test dengan sensor baru

### Modifikasi Konfigurasi

1. Edit `weather_config.py`
2. Restart aplikasi
3. Monitor log untuk perubahan

## Dependencies

- `pymodbus` - Modbus communication
- `pyserial` - Serial communication
- `numpy` - Numeric operations
- Database libraries sesuai sistem

## License

Sesuai dengan license project utama.

## Support

Untuk bantuan teknis, hubungi tim development atau buat issue di repository project.
