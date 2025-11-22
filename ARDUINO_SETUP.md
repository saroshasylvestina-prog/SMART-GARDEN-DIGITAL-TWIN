# Arduino Setup Guide for Pump Control

## Problem
You're using **Arduino** (not Raspberry Pi), but the code is trying to use `RPi.GPIO` which only works on Raspberry Pi.

## Solution: Use Serial Communication

Python will send commands to Arduino via **Serial (USB)**, and Arduino will control the relay.

## Step 1: Upload Arduino Code

1. **Open Arduino IDE**
2. **Open** `arduino_pump_control.ino`
3. **Select your board:**
   - Tools → Board → Select your Arduino (Uno, Nano, etc.)
4. **Select COM port:**
   - Tools → Port → Select your Arduino COM port (e.g., COM3)
5. **Upload** the code (Ctrl+U or Upload button)

## Step 2: Find Your COM Port

### On Windows:
1. Open **Device Manager**
2. Look under **Ports (COM & LPT)**
3. Find your Arduino (e.g., "Arduino Uno (COM3)")

### Or use Python:
```bash
python -c "import serial.tools.list_ports; [print(f'{p.device}: {p.description}') for p in serial.tools.list_ports.comports()]"
```

## Step 3: Update Python Code

You have two options:

### Option A: Use Arduino Serial Control (Recommended)

1. **Install PySerial:**
   ```bash
   pip install pyserial
   ```

2. **Update `pump_control.py`** to use Arduino serial communication:
   - Replace the `PumpControl` class with `PumpControlArduino`
   - Or modify `app.py` to use `pump_control_arduino.py`

### Option B: Keep Current Code (If Arduino has RPi.GPIO library)

If your Arduino is actually a Raspberry Pi or you have GPIO library on Arduino, keep current code.

## Step 4: Test Connection

Run this test script:
```bash
python test_arduino_connection.py
```

This will:
- Find your Arduino
- Test serial communication
- Test pump ON/OFF commands

## Step 5: Update app.py

Change this line in `app.py`:
```python
from pump_control import pump
```

To:
```python
from pump_control_arduino import PumpControlArduino
pump = PumpControlArduino(port='COM3', active_low=True)  # Change COM3 to your port
```

Or let it auto-detect:
```python
from pump_control_arduino import PumpControlArduino
pump = PumpControlArduino(active_low=True)  # Will auto-detect COM port
```

## Arduino Code Commands

The Arduino code listens for these serial commands:
- `ON` or `1` → Turn pump ON
- `OFF` or `0` → Turn pump OFF  
- `STATUS` → Get current status

## Troubleshooting

### "No module named 'serial'"
```bash
pip install pyserial
```

### "Arduino not found"
- Check USB cable connection
- Check COM port in Device Manager
- Try manually specifying port: `PumpControlArduino(port='COM3')`

### "Serial port already in use"
- Close Arduino IDE Serial Monitor
- Close any other programs using the port
- Restart Python application

### "Pump doesn't respond"
- Check Arduino Serial Monitor (Tools → Serial Monitor)
- Should see: "Arduino Pump Control Ready"
- Send "ON" manually to test
- Check relay wiring (VCC, GND, IN, NO/COM)

## Quick Test

1. **Upload Arduino code**
2. **Open Serial Monitor** (Arduino IDE → Tools → Serial Monitor)
3. **Set baudrate to 9600**
4. **Type "ON" and press Enter** → Pump should turn ON
5. **Type "OFF" and press Enter** → Pump should turn OFF

If this works, Python communication should work too!

