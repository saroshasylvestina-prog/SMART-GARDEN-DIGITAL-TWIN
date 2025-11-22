# Fix: Green LED Always ON - Relay Stuck ON

## Understanding the Green LED

**Green LED ON** = Relay is activated (ON)
- Relay contacts are closed
- COM and NO are connected
- Pump receives power

**Green LED OFF** = Relay is deactivated (OFF)
- Relay contacts are open
- COM and NO are disconnected
- Pump has no power

## Your Problem

**Green LED is ON from the start** = Relay is activated immediately

This means:
- GPIO Pin 8 is sending **LOW signal** (0V)
- For active-low relay: LOW = ON
- Relay thinks it should be ON all the time

## Why This Happens

### For Active-LOW Relay:
- **LOW (0V)** → Relay ON → Green LED ON → Pump ON
- **HIGH (3.3V)** → Relay OFF → Green LED OFF → Pump OFF

### The Issue:
When Arduino/Raspberry Pi starts:
- GPIO pins might default to **LOW** (0V)
- Or pin is **floating** (undefined state)
- This immediately activates the relay

## The Solution

The code must **immediately set pin to HIGH** on startup to turn relay OFF.

### What Should Happen:

**At Power On:**
1. Code starts
2. Pin 8 set to **HIGH** (3.3V)
3. Green LED turns **OFF** ✅
4. Relay turns **OFF** ✅
5. Pump stops ✅

**When You Click "Turn ON":**
1. Code sets Pin 8 to **LOW** (0V)
2. Green LED turns **ON** ✅
3. Relay turns **ON** ✅
4. Pump starts ✅

## Quick Test

### Test 1: Check LED at Startup
1. **Power on Arduino/Raspberry Pi**
2. **Start application:** `python app.py`
3. **Check console output:**
   ```
   [REAL] Pump control initialized on GPIO pin 8 (active-low)
   [REAL] Initial state: OFF (Pin set to HIGH)
   [REAL] Verified pin state: 1 (0=LOW, 1=HIGH)
   ```
4. **Check green LED:**
   - Should be **OFF** ✅
   - If still **ON** → Pin not set correctly ❌

### Test 2: Manual Pin Test
```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(8, GPIO.OUT)

# Set HIGH (should turn LED OFF)
GPIO.output(8, GPIO.HIGH)
print("Pin HIGH - Green LED should be OFF")
time.sleep(3)

# Set LOW (should turn LED ON)
GPIO.output(8, GPIO.LOW)
print("Pin LOW - Green LED should be ON")
time.sleep(3)

# Back to HIGH
GPIO.output(8, GPIO.HIGH)
print("Pin HIGH - Green LED should be OFF")
time.sleep(3)

GPIO.cleanup()
```

## If LED Still Stays ON

### Problem 1: Code Not Running
- Application might not have started
- Code might be in simulation mode
- Check console for `[REAL]` messages

### Problem 2: Pin Not Responding
- GPIO pin might be defective
- Try different pin (18 or 23)
- Check wiring connection

### Problem 3: Wrong Relay Type
- Relay might actually be active-HIGH
- Try: `active_low=False` in code

### Problem 4: Another Process
- Another program might be controlling the pin
- Check: `ps aux | grep python`
- Kill other processes

## Expected Behavior

### Startup:
- ✅ Green LED: **OFF**
- ✅ Relay: **OFF**
- ✅ Pump: **OFF**

### When Code Turns ON:
- ✅ Green LED: **ON**
- ✅ Relay: **ON**
- ✅ Pump: **ON**

### When Code Turns OFF:
- ✅ Green LED: **OFF**
- ✅ Relay: **OFF**
- ✅ Pump: **OFF**

## Summary

**Green LED ON** = Relay activated = Pump should run

**Your issue:** LED ON from start = Pin is LOW (activating relay)

**The fix:** Code now ensures pin starts HIGH (LED OFF) immediately

**After restart:**
1. Green LED should turn **OFF**
2. Pump should stop
3. Code will control it properly

