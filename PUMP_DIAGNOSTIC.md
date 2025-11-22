# Pump Running Continuously - Diagnostic Guide

## Exact Problem Analysis

If your pump runs continuously even after setting `active_low=True`, here are the **exact issues** to check:

## Issue 1: Application Not Restarted ⚠️

**Most Common Problem!**

The code changes won't take effect until you **restart the application**.

### Solution:
1. **Stop the current application** (Ctrl+C in terminal)
2. **Restart it**:
   ```bash
   python app.py
   ```
3. **Check console output** - Should see:
   ```
   [REAL] Pump control initialized on GPIO pin 8 (active-low)
   [REAL] Initial state: OFF (Pin set to HIGH)
   [REAL] Verified pin state: 1 (0=LOW, 1=HIGH)
   ```

## Issue 2: Pin Already in Use

Another process might be controlling pin 8.

### Check:
```bash
# Check if pin is in use
gpio readall

# Or check running Python processes
ps aux | grep python
```

### Solution:
```bash
# Kill any processes using GPIO
sudo killall python3

# Or restart Raspberry Pi
sudo reboot
```

## Issue 3: GPIO Not Initialized Correctly

The pin might not be set to HIGH on startup.

### Test with Diagnostic Script:
```bash
python test_pump_gpio.py
```

This will:
- Test pin 8 directly
- Show actual pin states
- Verify relay behavior
- Help identify the exact issue

## Issue 4: Hardware Wiring Problem

### Check Connections:
- ✅ **GPIO Pin 8** → **Relay IN/IN1**
- ✅ **Relay VCC** → **5V** (or 3.3V)
- ✅ **Relay GND** → **Ground (GND)**
- ✅ **Pump** → **Relay NO/COM terminals**

### Common Wiring Mistakes:
- ❌ Pin connected to wrong relay terminal
- ❌ Relay not powered (no VCC/GND)
- ❌ Loose connections
- ❌ Wrong pin number (BCM 8 = Physical pin 24)

## Issue 5: Relay Module Jumper Settings

Some relay modules have jumpers to change active-low/active-high.

### Check:
- Look for jumpers labeled "H" (High) or "L" (Low)
- Check relay module documentation
- Try moving jumper to opposite position

## Issue 6: Pin State Verification

The code now verifies the pin state. Check console for:

```
[REAL] Verified pin state: 1 (0=LOW, 1=HIGH)
```

- If shows `1` and pump is ON → Wrong relay type (try `active_low=False`)
- If shows `0` and pump is OFF → Correct! But pump might be wired wrong
- If shows wrong value → GPIO initialization issue

## Step-by-Step Diagnostic

### Step 1: Verify Code is Running
```bash
# Check if app is running
ps aux | grep "python app.py"

# Check console output when starting
python app.py
# Look for: [REAL] Pump control initialized...
```

### Step 2: Test Pin Directly
```bash
python test_pump_gpio.py
```

Watch the output and observe pump behavior during each test.

### Step 3: Manual GPIO Test
```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(8, GPIO.OUT)

# Test 1: Set HIGH (should be OFF for active-low)
GPIO.output(8, GPIO.HIGH)
print("Pin set to HIGH - Pump should be OFF")
time.sleep(5)

# Test 2: Set LOW (should be ON for active-low)
GPIO.output(8, GPIO.LOW)
print("Pin set to LOW - Pump should be ON")
time.sleep(5)

# Test 3: Back to HIGH
GPIO.output(8, GPIO.HIGH)
print("Pin set to HIGH - Pump should be OFF")
time.sleep(5)

GPIO.cleanup()
```

### Step 4: Check Current Pin State
```python
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(8, GPIO.IN)  # Read current state
state = GPIO.input(8)
print(f"Current pin 8 state: {state} (0=LOW, 1=HIGH)")
GPIO.cleanup()
```

## Expected Behavior

### For Active-LOW Relay:
- **Pin HIGH (1)** = Relay OFF = Pump OFF ✅
- **Pin LOW (0)** = Relay ON = Pump ON ✅

### At Startup:
- Pin should be set to **HIGH**
- Pump should be **OFF**
- Console should show: `Initial state: OFF (Pin set to HIGH)`

## Quick Fix Checklist

1. ✅ **Restarted application?** (Most important!)
2. ✅ **Checked console output?** (Should show [REAL] not [SIMULATION])
3. ✅ **Verified pin state?** (Run test_pump_gpio.py)
4. ✅ **Checked wiring?** (All connections secure)
5. ✅ **Tested with manual GPIO?** (See Step 3 above)
6. ✅ **Tried different pin?** (Test with pin 18 or 23)

## If Still Not Working

1. **Run diagnostic script**:
   ```bash
   python test_pump_gpio.py
   ```

2. **Check relay module documentation** - Some modules have special requirements

3. **Test with multimeter** - Verify pin output voltage:
   - HIGH should be ~3.3V
   - LOW should be ~0V

4. **Try different pin** - Test with GPIO 18:
   ```python
   pump = PumpControl(pin=18, use_simulation=False, active_low=True)
   ```

5. **Check relay LED** - Most relays have an LED indicator showing state

## Console Output to Look For

**Correct initialization:**
```
==================================================
INITIALIZING PUMP CONTROL
==================================================
[REAL] Pump control initialized on GPIO pin 8 (active-low)
[REAL] Initial state: OFF (Pin set to HIGH)
[REAL] Verified pin state: 1 (0=LOW, 1=HIGH)
==================================================
```

**If you see [SIMULATION] instead:**
- RPi.GPIO library not installed
- Or running on non-Raspberry Pi
- Code won't control real hardware

## Still Having Issues?

Share the console output from:
1. Starting the application
2. Running `test_pump_gpio.py`
3. Any error messages

This will help identify the exact problem!

