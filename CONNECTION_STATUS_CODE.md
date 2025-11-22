# Connection Status Code Explanation

This document shows the code responsible for handling the **CONNECTED/DISCONNECTED** status of sensors.

## Key Components

### 1. **Initialization - Sets Initial Connection Status**

#### DHT Sensor (Lines 41-60 in `sensor.py`):
```python
def _initialize_sensor(self):
    """Initialize the sensor connection"""
    if self.use_simulation:
        print(f"[SIMULATION] DHT{self.sensor_type} sensor initialized on pin {self.pin}")
        self.connected = False  # Simulation mode = no real hardware connected
    else:
        try:
            # Test sensor connection
            humidity, temperature = Adafruit_DHT.read_retry(
                self.sensor_type, self.pin
            )
            if humidity is not None and temperature is not None:
                self.connected = True  # ✅ Hardware detected = CONNECTED
                print(f"[REAL] DHT{self.sensor_type} sensor connected on pin {self.pin}")
            else:
                self.connected = False  # ❌ No hardware = DISCONNECTED
                print(f"[ERROR] Failed to read from DHT{self.sensor_type} sensor on pin {self.pin}")
        except Exception as e:
            self.connected = False  # ❌ Error = DISCONNECTED
            print(f"[ERROR] Sensor initialization failed: {e}")
```

#### MQ135, LDR, Moisture Sensors (Similar pattern):
```python
def _initialize_sensor(self):
    if self.use_simulation:
        self.connected = False  # Simulation = DISCONNECTED
    else:
        try:
            # Try to connect to hardware
            import RPi.GPIO as GPIO
            import spidev
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)
            self.connected = True  # ✅ Hardware detected = CONNECTED
        except:
            self.connected = False  # ❌ No hardware = DISCONNECTED
```

---

### 2. **Dynamic Connection Detection - Updates Status During Runtime**

#### DHT Sensor `read_sensor()` method (Lines 62-98):
```python
def read_sensor(self):
    """Read temperature and humidity from sensor"""
    # Allow reading even if not connected (to test connection)
    if self.use_simulation:
        # Generate simulated data (doesn't change connection status)
        self.temperature = round(random.uniform(18.0, 26.0), 1)
        self.humidity = round(random.uniform(45.0, 75.0), 1)
    else:
        try:
            humidity, temperature = Adafruit_DHT.read_retry(
                self.sensor_type, self.pin
            )
            if humidity is not None and temperature is not None:
                # ✅ Successful read = Update to CONNECTED
                if not self.connected:
                    self.connected = True
                    print(f"[REAL] DHT{self.sensor_type} sensor connected on pin {self.pin}")
                self.temperature = round(temperature, 1)
                self.humidity = round(humidity, 1)
            else:
                # ❌ Failed read = Update to DISCONNECTED
                if self.connected:
                    self.connected = False
                    print(f"[WARNING] DHT{self.sensor_type} sensor disconnected")
                return None, None
        except Exception as e:
            # ❌ Error = Update to DISCONNECTED
            if self.connected:
                self.connected = False
                print(f"[WARNING] DHT{self.sensor_type} sensor disconnected due to error")
            return None, None
```

#### MQ135 Sensor `read_sensor()` method (Lines 172-210):
```python
def read_sensor(self):
    if self.use_simulation:
        # Generate simulated data
        self.air_quality = round(random.uniform(20.0, 80.0), 1)
        # ... (doesn't change connection status)
    else:
        try:
            analog_value = self._read_analog(self.analog_pin)
            if analog_value is None:
                # ❌ Failed read = DISCONNECTED
                if self.connected:
                    self.connected = False
                    print(f"[WARNING] MQ135 sensor disconnected")
                return None, None, None
            
            # ✅ Successful read = CONNECTED
            if not self.connected:
                self.connected = True
                print(f"[REAL] MQ135 sensor connected on analog pin A{self.analog_pin}")
            # ... process data
```

#### LDR Sensor `read_sensor()` method (Lines 303-340):
```python
def read_sensor(self):
    if self.use_simulation:
        # Generate simulated data
        # ... (doesn't change connection status)
    else:
        try:
            analog_value = self._read_analog(self.analog_pin)
            if analog_value is None:
                # ❌ Failed = DISCONNECTED
                if self.connected:
                    self.connected = False
                    print(f"[WARNING] LDR sensor disconnected")
                return None, None
            
            # ✅ Successful = CONNECTED
            if not self.connected:
                self.connected = True
                print(f"[REAL] LDR sensor connected on analog pin A{self.analog_pin}")
            # ... process data
```

#### Moisture Sensor `read_sensor()` method (Lines 427-460):
```python
def read_sensor(self):
    if self.use_simulation:
        # Generate simulated data
        # ... (doesn't change connection status)
    else:
        try:
            analog_value = self._read_analog(self.analog_pin)
            if analog_value is None:
                # ❌ Failed = DISCONNECTED
                if self.connected:
                    self.connected = False
                    print(f"[WARNING] Moisture sensor disconnected")
                return None, None
            
            # ✅ Successful = CONNECTED
            if not self.connected:
                self.connected = True
                print(f"[REAL] Moisture sensor connected on analog pin A{self.analog_pin}")
            # ... process data
```

---

### 3. **Status Retrieval - Returns Connection Status to Frontend**

#### `get_status()` method (Lines 100-110 for DHT, similar for others):
```python
def get_status(self):
    """Get sensor connection status and last reading"""
    return {
        'connected': self.connected,  # ← This is what frontend reads
        'sensor_type': f'DHT{self.sensor_type}',
        'pin': self.pin,
        'mode': 'Simulation' if self.use_simulation else 'Real Sensor',
        'temperature': self.temperature,
        'humidity': self.humidity,
        'last_reading': self.last_reading_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_reading_time else 'Never'
    }
```

---

### 4. **API Endpoint - Sends Status to Frontend**

#### In `app.py` (Lines 65-80):
```python
@app.route("/api/sensor/read")
def sensor_read():
    """Force a new sensor reading"""
    temp, humidity = sensor.read_sensor()  # ← This triggers connection check
    status = sensor.get_status()  # ← Gets updated connection status
    if temp is not None and humidity is not None:
        return jsonify({
            'success': True,
            'temperature': temp,
            'humidity': humidity,
            'connected': status['connected'],  # ← Frontend reads this
            'timestamp': sensor.last_reading_time.strftime('%Y-%m-%d %H:%M:%S') if sensor.last_reading_time else None
        })
```

---

### 5. **Frontend Update - Displays Connection Status**

#### In `templates/index.html` (Lines 1162-1188):
```javascript
function refreshSensor() {
    fetch('/api/sensor/read')
        .then(response => response.json())
        .then(data => {
            // Update connection status badge
            const statusBadge = document.querySelector('.sensor-section:first-of-type .sensor-status');
            if (statusBadge) {
                if (data.connected) {  // ← Check connection status from API
                    statusBadge.textContent = '✓ CONNECTED';
                    statusBadge.className = 'sensor-status status-connected';  // Green
                } else {
                    statusBadge.textContent = '✗ DISCONNECTED';
                    statusBadge.className = 'sensor-status status-disconnected';  // Red
                }
            }
            // ... update sensor values
        });
}
```

---

## Connection Status Logic Summary

### **Simulation Mode:**
- `self.connected = False` (always)
- Status: **DISCONNECTED** (red badge)
- Still generates data for testing

### **Real Mode:**
- **Initialization:**
  - Tries to connect to hardware
  - `connected = True` if hardware detected
  - `connected = False` if hardware not found

- **Runtime (during `read_sensor()`):**
  - If successful read → `connected = True` (CONNECTED)
  - If failed read → `connected = False` (DISCONNECTED)
  - Updates automatically when hardware is connected/disconnected

### **Key Points:**
1. **Simulation mode** = Always `False` (DISCONNECTED)
2. **Real mode** = `True` only when hardware is actually detected
3. **Status updates dynamically** during `read_sensor()` calls
4. **Frontend refreshes** status every 5 seconds automatically
5. **Manual refresh** buttons also update status immediately

---

## Files Involved

1. **`sensor.py`** - Connection logic (initialization + dynamic detection)
2. **`app.py`** - API endpoints that return connection status
3. **`templates/index.html`** - Frontend JavaScript that displays status

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│ 1. Sensor Initialization                                │
│    - Simulation mode → connected = False                │
│    - Real mode → Try hardware → connected = True/False  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. read_sensor() called (every 5 seconds or manual)      │
│    - Simulation: Generate fake data (status unchanged)   │
│    - Real: Try to read hardware                         │
│      • Success → connected = True  ✅                     │
│      • Failure → connected = False ❌                    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. get_status() returns connection status               │
│    - Returns: {'connected': True/False, ...}            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. API endpoint sends status to frontend                │
│    - JSON: {'connected': True/False, ...}               │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Frontend JavaScript updates badge                    │
│    - True → "✓ CONNECTED" (green)                      │
│    - False → "✗ DISCONNECTED" (red)                     │
└─────────────────────────────────────────────────────────┘
```

---

This is the complete flow of how connection status is determined and displayed!

