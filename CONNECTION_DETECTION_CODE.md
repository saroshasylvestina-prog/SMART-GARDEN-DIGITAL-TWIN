# Connection Detection Code - CONNECTED vs DISCONNECTED

This document shows the exact code that determines when to show "CONNECTED" vs "DISCONNECTED".

---

## 🔑 Key Code Sections

### 1. **Initialization - Sets Initial Connection Status**

**File:** `sensor.py` - `_initialize_sensor()` method

#### DHT Sensor (Lines 41-60):
```python
def _initialize_sensor(self):
    """Initialize the sensor connection"""
    if self.use_simulation:
        # ❌ SIMULATION MODE = DISCONNECTED
        print(f"[SIMULATION] DHT{self.sensor_type} sensor initialized on pin {self.pin}")
        self.connected = False  # ← No real hardware = DISCONNECTED
    else:
        # ✅ REAL MODE = Try to detect hardware
        try:
            # Test sensor connection
            humidity, temperature = Adafruit_DHT.read_retry(
                self.sensor_type, self.pin
            )
            if humidity is not None and temperature is not None:
                # ✅ HARDWARE DETECTED = CONNECTED
                self.connected = True
                print(f"[REAL] DHT{self.sensor_type} sensor connected on pin {self.pin}")
            else:
                # ❌ NO HARDWARE = DISCONNECTED
                self.connected = False
                print(f"[ERROR] Failed to read from DHT{self.sensor_type} sensor on pin {self.pin}")
        except Exception as e:
            # ❌ ERROR = DISCONNECTED
            self.connected = False
            print(f"[ERROR] Sensor initialization failed: {e}")
```

---

### 2. **Dynamic Detection - Updates Status During Runtime**

**File:** `sensor.py` - `read_sensor()` method

#### DHT Sensor (Lines 62-98):
```python
def read_sensor(self):
    """Read temperature and humidity from sensor"""
    # Allow reading even if not connected (to test connection)
    if self.use_simulation:
        # Simulation mode - generate fake data
        # Connection status stays False (doesn't change)
        self.temperature = round(random.uniform(18.0, 26.0), 1)
        self.humidity = round(random.uniform(45.0, 75.0), 1)
    else:
        # REAL MODE - Try to read from hardware
        try:
            humidity, temperature = Adafruit_DHT.read_retry(
                self.sensor_type, self.pin
            )
            if humidity is not None and temperature is not None:
                # ✅ SUCCESSFUL READ = CONNECTED
                if not self.connected:
                    self.connected = True  # ← Update to CONNECTED
                    print(f"[REAL] DHT{self.sensor_type} sensor connected on pin {self.pin}")
                self.temperature = round(temperature, 1)
                self.humidity = round(humidity, 1)
            else:
                # ❌ FAILED READ = DISCONNECTED
                if self.connected:
                    self.connected = False  # ← Update to DISCONNECTED
                    print(f"[WARNING] DHT{self.sensor_type} sensor disconnected")
                return None, None
        except Exception as e:
            # ❌ ERROR = DISCONNECTED
            print(f"[ERROR] Sensor read failed: {e}")
            if self.connected:
                self.connected = False  # ← Update to DISCONNECTED
                print(f"[WARNING] DHT{self.sensor_type} sensor disconnected due to error")
            return None, None
    
    self.last_reading_time = datetime.now()
    return self.temperature, self.humidity
```

---

### 3. **Status Retrieval - Returns Connection Status**

**File:** `sensor.py` - `get_status()` method (Lines 100-111):
```python
def get_status(self):
    """Get sensor connection status and last reading"""
    return {
        'connected': self.connected,  # ← True = CONNECTED, False = DISCONNECTED
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

**File:** `app.py` - `/api/sensor/read` route (Lines 65-83):
```python
@app.route("/api/sensor/read")
def sensor_read():
    """Force a new sensor reading"""
    temp, humidity = sensor.read_sensor()  # ← This checks/updates connection
    status = sensor.get_status()  # ← Gets current connection status
    if temp is not None and humidity is not None:
        return jsonify({
            'success': True,
            'temperature': temp,
            'humidity': humidity,
            'connected': status['connected'],  # ← True/False sent to frontend
            'timestamp': sensor.last_reading_time.strftime('%Y-%m-%d %H:%M:%S') if sensor.last_reading_time else None
        })
    else:
        return jsonify({
            'success': False,
            'connected': status['connected'],  # ← Still sends connection status
            'error': 'Failed to read sensor'
        }), 500
```

---

### 5. **Frontend HTML - Displays Status Badge**

**File:** `templates/index.html` (Lines 375-381):
```html
<div id="dht-status" class="sensor-status {% if sensor_status.connected %}status-connected{% else %}status-disconnected{% endif %}">
    {% if sensor_status.connected %}
        ✓ CONNECTED    <!-- ← Shows when connected = True -->
    {% else %}
        ✗ DISCONNECTED  <!-- ← Shows when connected = False -->
    {% endif %}
</div>
```

---

### 6. **Frontend JavaScript - Updates Badge Dynamically**

**File:** `templates/index.html` (Lines 1167-1176):
```javascript
// Update connection status badge
const statusBadge = document.getElementById('dht-status');
if (statusBadge) {
    if (data.connected) {  // ← Check JSON response
        // ✅ CONNECTED
        statusBadge.textContent = '✓ CONNECTED';
        statusBadge.className = 'sensor-status status-connected';  // Green
    } else {
        // ❌ DISCONNECTED
        statusBadge.textContent = '✗ DISCONNECTED';
        statusBadge.className = 'sensor-status status-disconnected';  // Red
    }
}
```

---

## 📋 Complete Logic Flow

```
┌─────────────────────────────────────────┐
│ 1. INITIALIZATION                       │
│    if use_simulation:                   │
│        connected = False  ❌            │
│    else:                                │
│        Try to read hardware             │
│        if success:                       │
│            connected = True  ✅          │
│        else:                             │
│            connected = False  ❌         │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. RUNTIME (read_sensor called)         │
│    if use_simulation:                   │
│        Generate fake data                │
│        (connected stays False)          │
│    else:                                │
│        Try to read hardware             │
│        if successful read:              │
│            if not connected:            │
│                connected = True  ✅      │
│        if failed read:                  │
│            if connected:                │
│                connected = False  ❌    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. get_status() returns                 │
│    {'connected': True/False, ...}       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 4. API returns JSON                     │
│    {'connected': True/False, ...}       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 5. Frontend displays                    │
│    if connected = True:  ✓ CONNECTED    │
│    if connected = False: ✗ DISCONNECTED │
└─────────────────────────────────────────┘
```

---

## 🎯 Decision Points

### **When `connected = True` (CONNECTED):**
1. ✅ Real hardware mode AND successful sensor read
2. ✅ Hardware detected during initialization
3. ✅ Hardware detected during runtime `read_sensor()` call

### **When `connected = False` (DISCONNECTED):**
1. ❌ Simulation mode (always)
2. ❌ Real mode but hardware not detected
3. ❌ Real mode but sensor read fails
4. ❌ Real mode but sensor read throws error

---

## 📝 Summary

**Key Variable:** `self.connected` (True/False)

**Set to True when:**
- Hardware is successfully detected and read

**Set to False when:**
- Simulation mode
- Hardware not detected
- Sensor read fails
- Sensor read throws error

**Updated dynamically:**
- Every time `read_sensor()` is called
- Automatically changes based on hardware detection

---

This is the complete code that determines CONNECTED vs DISCONNECTED status!

