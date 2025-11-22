# Fix: COM Port Access Denied

## Problem
```
[ERROR] Failed to connect: could not open port 'COM5': PermissionError(13, 'Access is denied.')
```

This means **something else is using COM5**.

## Quick Fix Steps

### Step 1: Close Arduino Serial Monitor
1. Open **Arduino IDE**
2. If **Serial Monitor** is open → **Close it** (X button)
3. This is the #1 cause of this error!

### Step 2: Close Any Running Python Apps
If your Flask app (`python app.py`) is running:
1. Go to the terminal where it's running
2. Press **Ctrl+C** to stop it
3. Wait a few seconds

### Step 3: Check What's Using COM5
Run this command:
```bash
python -c "import serial.tools.list_ports; ports = serial.tools.list_ports.comports(); print('Available ports:'); [print(f'  {p.device}: {p.description} - In use: {p.device == \"COM5\"}') for p in ports]"
```

### Step 4: Restart Everything
1. **Close Arduino IDE completely**
2. **Close all Python terminals**
3. **Unplug and replug Arduino USB** (optional, but helps)
4. **Wait 5 seconds**
5. **Start fresh:**
   ```bash
   python app.py
   ```

## Alternative: Use Different COM Port

If COM5 is permanently blocked, check Device Manager:
1. **Windows Key + X** → **Device Manager**
2. **Ports (COM & LPT)** → Find your Arduino
3. Note the COM port number
4. Update code to use that port:
   ```python
   pump = PumpControlArduino(port='COM3', active_low=True)  # Change COM3 to your port
   ```

## Test After Fixing

Once you've closed everything:
```bash
python test_arduino_connection.py
```

Should show:
```
[OK] Connected to COM5 at 9600 baud
[ARDUINO] Response: PUMP:ON
```

## Still Not Working?

1. **Restart your computer** (sometimes Windows locks ports)
2. **Check Device Manager** - Is Arduino showing as COM5?
3. **Try a different USB port** on your computer
4. **Reinstall Arduino drivers** if needed

