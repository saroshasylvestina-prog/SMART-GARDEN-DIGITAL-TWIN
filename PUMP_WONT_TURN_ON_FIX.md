# Pump Won't Turn ON - Troubleshooting Guide

## Problem: Pump Doesn't Run When Code Tries to Turn It ON

The pump is correctly wired (doesn't run continuously), but it won't activate when the code sends the signal.

## Quick Diagnostic Steps

### Step 1: Check Console Output

When you click "Turn ON", check the console for:

**Good output:**
```
[PUMP] Turned ON (Pin 8 = LOW)
[PUMP] Verified pin state: 0 (Expected: 0)
[PUMP] Pin state correct - Relay should be ON
```

**Bad output (simulation mode):**
```
[PUMP] SIMULATION MODE - No actual GPIO control
```
→ **Fix:** Change `use_simulation=False` in pump_control.py

**Bad output (pin mismatch):**
```
[PUMP] Turned ON (Pin 8 = LOW)
[PUMP] Verified pin state: 1 (Expected: 0)
[WARNING] Pin state mismatch!
```
→ **Fix:** GPIO pin not responding - check wiring

### Step 2: Test Relay Directly

Run this test script:
```bash
python test_relay_control.py
```

This will:
- Manually control the relay
- Show pin states
- Help identify if it's a code or hardware issue

### Step 3: Check Relay Power

**Most Common Issue!**

The relay module needs power to work:
- ✅ **VCC** connected to **5V** (or 3.3V depending on relay)
- ✅ **GND** connected to **Ground**
- ✅ Relay LED should light up when activated

**Test:**
1. Disconnect GPIO Pin 8
2. Manually connect relay IN to 5V → Relay should activate
3. Manually connect relay IN to GND → Relay should deactivate

### Step 4: Verify GPIO Pin is Working

```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(8, GPIO.OUT)

# Test 1: Set LOW (should activate relay for active-low)
GPIO.output(8, GPIO.LOW)
print("Pin set to LOW - Check relay LED and pump")
time.sleep(3)

# Test 2: Set HIGH (should deactivate relay)
GPIO.output(8, GPIO.HIGH)
print("Pin set to HIGH - Check relay LED and pump")
time.sleep(3)

GPIO.cleanup()
```

## Common Issues & Fixes

### Issue 1: Relay Not Powered

**Symptoms:**
- Pump doesn't respond
- Relay LED doesn't light up
- No relay click sound

**Fix:**
- Connect relay VCC to 5V (or 3.3V)
- Connect relay GND to Ground
- Check power supply is working

### Issue 2: Wrong GPIO Pin

**Symptoms:**
- Code runs but nothing happens
- No relay response

**Fix:**
- Verify pin 8 is connected to relay IN/IN1
- Check BCM pin 8 = Physical pin 24
- Try a different pin (18 or 23) to test

### Issue 3: Code in Simulation Mode

**Symptoms:**
- Console shows `[SIMULATION]`
- No actual GPIO control

**Fix:**
- Check `pump_control.py` line 163:
  ```python
  pump = PumpControl(pin=8, use_simulation=False, active_low=True)
  ```
- Ensure `use_simulation=False`

### Issue 4: Relay Needs Higher Voltage

**Symptoms:**
- Relay LED dim or doesn't light
- Relay clicks but doesn't stay on

**Fix:**
- Some relays need 5V, not 3.3V
- Check relay module specifications
- Try connecting VCC to 5V instead of 3.3V

### Issue 5: GPIO Pin Not Strong Enough

**Symptoms:**
- Pin state changes but relay doesn't activate
- Works with manual connection but not GPIO

**Fix:**
- Use a transistor or optocoupler to boost signal
- Or use a relay module with built-in driver

## Step-by-Step Diagnosis

### Test 1: Manual Relay Test
1. **Disconnect GPIO Pin 8** from relay
2. **Connect relay IN directly to 5V** → Pump should turn ON
3. **Connect relay IN directly to GND** → Pump should turn OFF

**Result:**
- ✅ Works → Relay is fine, issue is with GPIO
- ❌ Doesn't work → Relay wiring/power issue

### Test 2: GPIO Pin Test
```bash
python test_relay_control.py
```

**Watch for:**
- Relay LED lighting up
- Relay click sound
- Pump starting/stopping

**Result:**
- ✅ Works → GPIO is fine, issue is with application code
- ❌ Doesn't work → GPIO pin or wiring issue

### Test 3: Application Test
1. Start application: `python app.py`
2. Check console for `[REAL]` not `[SIMULATION]`
3. Click "Turn ON" button
4. Watch console output

**Check console for:**
```
[PUMP] Turned ON (Pin 8 = LOW)
[PUMP] Verified pin state: 0 (Expected: 0)
[PUMP] Pin state correct - Relay should be ON
```

## Quick Fixes

### Fix 1: Ensure Real GPIO Mode
```python
# In pump_control.py line 163
pump = PumpControl(pin=8, use_simulation=False, active_low=True)
```

### Fix 2: Check Relay Power
- VCC → 5V (or 3.3V)
- GND → Ground
- Verify with multimeter

### Fix 3: Verify Pin Connection
- GPIO Pin 8 (BCM) = Physical Pin 24
- Connected to relay IN/IN1
- Connection is secure

### Fix 4: Test with Different Pin
```python
# Try pin 18 instead
pump = PumpControl(pin=18, use_simulation=False, active_low=True)
```

## What to Check

### Hardware Checklist
- [ ] Relay VCC connected to power (5V or 3.3V)
- [ ] Relay GND connected to ground
- [ ] GPIO Pin 8 connected to relay IN/IN1
- [ ] All connections are secure
- [ ] Relay LED works (if relay has one)
- [ ] Battery/power supply is adequate

### Software Checklist
- [ ] `use_simulation=False` in pump_control.py
- [ ] `active_low=True` (or False if needed)
- [ ] Application restarted after code changes
- [ ] Console shows `[REAL]` not `[SIMULATION]`
- [ ] No errors in console output

## Debugging Output

The code now shows detailed debugging. When you click "Turn ON", look for:

```
[PUMP] Turned ON (Pin 8 = LOW)
[PUMP] Verified pin state: 0 (Expected: 0)
[PUMP] Pin state correct - Relay should be ON
```

If you see warnings or mismatches, that's the issue!

## Still Not Working?

1. **Run test script:**
   ```bash
   python test_relay_control.py
   ```

2. **Check relay module:**
   - Does it have a jumper for active-low/active-high?
   - What voltage does it need?
   - Is it a 1-channel or multi-channel module?

3. **Try different pin:**
   - Test with GPIO 18 or 23
   - Some pins have special functions

4. **Check Raspberry Pi:**
   - Is it a real Raspberry Pi?
   - Is RPi.GPIO library installed?
   - Are you running as root or with GPIO permissions?

## Expected Behavior

When you click "Turn ON":
1. Console shows: `[PUMP] Turned ON (Pin 8 = LOW)`
2. Pin 8 goes LOW (0V)
3. Relay activates (LED on, click sound)
4. Pump starts running
5. After duration, pump turns OFF automatically

If any step fails, that's where the problem is!

