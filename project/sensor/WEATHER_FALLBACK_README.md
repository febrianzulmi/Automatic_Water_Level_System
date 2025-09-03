# Weather Sensor Fallback Data System

## Overview
Sistem fallback data untuk weather sensor yang memungkinkan pengambilan data terakhir yang valid dari database log monitoring ketika sensor gagal terbaca atau weather station tidak dapat diakses.

## Fitur Utama

### 1. Automatic Fallback
- Ketika sensor gagal terbaca, sistem otomatis mengambil data terakhir yang valid dari database
- Data fallback dibatasi maksimal 24 jam untuk memastikan kualitas data
- Fallback mode khusus ketika weather station tidak dapat diakses sama sekali
- **Data fallback TIDAK diupdate ke log monitoring** - hanya data fresh yang diupdate

### 2. Data Health Monitoring
- Pengecekan umur data untuk memastikan data yang digunakan masih relevan
- Warning dan rekomendasi berdasarkan status kesehatan data
- Logging detail untuk tracking dan debugging

### 3. Smart Error Handling
- Reconnection otomatis ke weather station
- Graceful degradation ketika hardware bermasalah
- Informasi error yang informatif dan actionable

### 4. **Database Update Control**
- Data hanya diupdate ke log monitoring ketika semua sensor berhasil sampling
- Fallback data tidak diupdate ke database untuk menghindari data lama
- Flag `can_update_log` untuk kontrol update database

## Cara Kerja

### Flow Normal
```
1. Weather station terhubung
2. Baca semua sensor
3. Update database dengan data baru
4. Return success message
```

### Flow dengan Fallback
```
1. Weather station terhubung
2. Beberapa sensor gagal terbaca
3. Ambil data terakhir dari database untuk sensor yang gagal
4. Update database dengan data campuran (baru + lama)
5. Return warning message dengan detail fallback
```

### Flow Fallback Total
```
1. Weather station tidak dapat diakses
2. Ambil semua data terakhir dari database
3. Update database dengan data lama
4. Return fallback mode message
```

## Implementasi

### Class Weather yang Dimodifikasi

#### Method Baru
- `get_last_valid_data(sensor_id, max_age_hours=24)`: Ambil data terakhir dari database
- `_fallback_to_last_data()`: Fallback total ketika weather station tidak dapat diakses
- `_check_data_health()`: Cek kesehatan data dan berikan rekomendasi

#### Flag Baru
- `can_update_log`: Flag boolean yang menentukan apakah data bisa diupdate ke log monitoring
  - `True`: Semua sensor berhasil, data bisa diupdate ke database
  - `False`: Ada sensor yang failed, gunakan fallback data tanpa update database

#### Method yang Dimodifikasi
- `main()`: Tambahan logic fallback dan health check
- `connect()`: Tambahan reconnection logic

### Database Integration
```python
# Import yang diperlukan
from query_project_db import LogSensorDB, SensorListDB

# Query data terakhir
last_data = LogSensorDB.selectLastOne(sensor_db_id)
```

## Konfigurasi

### Parameter Fallback
- `max_age_hours`: Maksimal umur data yang diizinkan (default: 24 jam)
- `fallback_max_age_hours`: Maksimal umur data untuk fallback total (default: 48 jam)

### Database Mapping
```python
# Mapping sensor ID ke database ID
self.sensor_list = SensorListDB.selectByGroupFull(self.groupId)
self.sensor_id_map = {sensor['sensor_id']: sensor['id'] for sensor in self.sensor_list}
```

## Output dan Logging

### Success Message
```
"5 Sensors Success Sampling"
can_update_log: True
```

### Partial Fallback Message
```
"3 of 5 Sensors Success Sampling | Wind Speed Error - Using last valid data: 15.2, Temperature Error - Using last valid data: 25.6"
can_update_log: False
```

### Fallback Mode Message
```
"5 Sensors Success Sampling (Fallback Mode - Using Last Valid Data)"
can_update_log: False
```

### Health Information
```
"INFO: 2/5 sensor menggunakan data lama"
"WARNING: 4/5 sensor menggunakan data lama"
"WARNING: Semua sensor menggunakan data lama (lebih dari 24 jam)"
```

### Database Update Control
```
can_update_log: True   → Database diupdate
can_update_log: False  → Database tidak diupdate (Fallback Mode)
```

## Monitoring dan Maintenance

### Metrics yang Dimonitor
- Jumlah sensor yang menggunakan data fallback
- Umur data fallback
- Status koneksi weather station
- Kualitas data yang dikembalikan

### Rekomendasi Maintenance
- Periksa koneksi weather station ketika ada banyak fallback
- Monitor umur data fallback untuk deteksi masalah hardware
- Review log error untuk troubleshooting

## Testing

### File Test
```bash
python3 project/sensor/weather_example.py
```

### Test Cases
1. **Normal Operation**: Semua sensor berfungsi normal
2. **Partial Fallback**: Beberapa sensor gagal, gunakan data lama
3. **Total Fallback**: Weather station tidak dapat diakses
4. **Data Aging**: Test dengan data yang sudah lama
5. **Database Error**: Test ketika database tidak dapat diakses

## Troubleshooting

### Common Issues

#### 1. Sensor Selalu Menggunakan Data Lama
- Cek koneksi weather station
- Periksa konfigurasi port dan baudrate
- Test koneksi Modbus secara manual

#### 2. Data Fallback Tidak Tersedia
- Cek apakah sensor sudah pernah menyimpan data
- Periksa struktur database dan mapping
- Verifikasi query LogSensorDB

#### 3. Performance Issues
- Monitor query database performance
- Cek indexing pada tabel log monitoring
- Optimasi query jika diperlukan

### Debug Commands
```python
# Enable debug logging
weather = Weather(group_id, data_sensor)
weather.weatherObject.debug = True

# Test koneksi
print(f"Connected: {weather.weatherObject.is_socket_open()}")

# Test fallback data
value, success = weather.get_last_valid_data("windSpeed")
print(f"Fallback result: {value}, Success: {success}")
```

## Dependencies

### Database
- `SensorListDB`: Untuk mapping sensor
- `LogSensorDB`: Untuk data fallback
- `SensorGroupDB`: Untuk konfigurasi group

### Hardware
- Modbus RTU connection
- Weather station device
- Serial port access

### Python Libraries
- `pymodbus`: Modbus communication
- `datetime`: Time handling
- `sys`, `os`: System operations

## Security Considerations

### Data Validation
- Validasi format data sebelum digunakan
- Sanitasi input dari database
- Error handling untuk data corrupt

### Access Control
- Database connection security
- Port access restrictions
- Logging untuk audit trail

## Performance Optimization

### Database Queries
- Gunakan `selectLastOne` untuk efisiensi
- Index pada timestamp dan sensor_id
- Connection pooling jika diperlukan

### Memory Management
- Cleanup koneksi Modbus
- Garbage collection untuk object besar
- Monitoring memory usage

## Future Enhancements

### Planned Features
1. **Predictive Fallback**: Prediksi nilai berdasarkan trend data
2. **Data Quality Scoring**: Scoring kualitas data fallback
3. **Multi-Source Fallback**: Fallback dari multiple weather stations
4. **Real-time Monitoring**: Dashboard monitoring real-time

### Scalability
- Support untuk multiple weather station groups
- Distributed database support
- Load balancing untuk multiple instances

## Support dan Maintenance

### Contact
- Developer: [Nama Developer]
- System Admin: [Nama Admin]
- Documentation: [Link Dokumentasi]

### Update Schedule
- Code review: Setiap implementasi fitur baru
- Performance review: Bulanan
- Security audit: Triwulanan
- Hardware maintenance: Sesuai jadwal

---

**Catatan**: Sistem ini dirancang untuk memberikan continuity of service ketika ada masalah hardware, namun tetap memberikan warning yang jelas kepada operator tentang status data yang digunakan.
