# Quick Fix: Arduino Not Connecting

## Current Status
Your Flask app is in **SIMULATION MODE** - Arduino connection failed!

## Quick Fix (3 Steps)

### Step 1: Close Arduino Serial Monitor
1. Open **Arduino IDE**
2. If **Serial Monitor** window is open → **Close it** (click X)
3. **Close Arduino IDE completely** (optional but recommended)

### Step 2: Upload Arduino Code (If Not Done)
1. Open **Arduino IDE**
2. Open `arduino_pump_control.ino`
3. **Tools → Board → Arduino Uno** (or your board)
4. **Tools → Port → COM5**
5. **Upload** (Ctrl+U)
6. Wait for "Done uploading"
7. **Close Serial Monitor if it opened**
8. **Close Arduino IDE**

### Step 3: Restart Flask App
**Option A: Use the batch script**
```bash
restart_with_arduino.bat
```

**Option B: Manual restart**
1. **Stop Flask app** (in the terminal where it's running, press **Ctrl+C**)
2. **Wait 3 seconds**
3. **Start Flask app:**
   ```bash
   python app.py
   ```

## What to Look For

When Flask app starts, you should see:
```
[ARDUINO] Found potential Arduino: COM5 - Arduino Uno (COM5)
[ARDUINO] Connected to COM5 at 9600 baud
[ARDUINO] Pump control initialized on pin 8
[ARDUINO] Relay type: active-low
[ARDUINO] Startup message: Arduino Pump Control Ready
[PUMP] Turned OFF via Arduino
```

**If you see:**
```
[ARDUINO] No Arduino found - using simulation mode
```
or
```
[ARDUINO ERROR] Serial port error: ...
```

**Then:**
- Arduino Serial Monitor is still open → Close it
- Wrong COM port → Check Device Manager
- Arduino code not uploaded → Upload it

## Test It

After restarting, test the connection:
```bash
python test_flask_arduino.py
```

Should show:
```
Mode: Arduino Serial
Connected: True
Port: COM5
```

## Still Not Working?

1. **Check Device Manager:**
   - Windows Key + X → Device Manager
   - Ports (COM & LPT) → Find Arduino
   - Note the COM port number

2. **Manually specify COM port:**
   Edit `pump_control.py` line ~280:
   ```python
   pump = PumpControlArduino(port='COM5', active_low=True)  # Change COM5 to your port
   ```

3. **Unplug and replug Arduino USB**
   - Sometimes Windows needs a refresh

4. **Restart your computer**
   - Last resort if ports are locked

