# Hardware Wiring Fix - Pump Runs When Battery Connected

## ⚠️ CRITICAL ISSUE IDENTIFIED

If the pump runs when you **simply connect the battery** (without any code), this means:

**The pump is NOT going through the relay properly!**

## The Problem

The pump should **ONLY** run when:
- ✅ Relay is activated (GPIO pin controls it)
- ✅ Code sends signal to relay

If it runs with **just battery connection**, it means:
- ❌ Pump is connected directly to battery (bypassing relay)
- ❌ Pump is connected to relay's NC (Normally Closed) terminal
- ❌ Relay is not in the circuit properly

## Correct Wiring Diagram

```
Battery (+) ──┐
              │
              ├──> Relay COM (Common)
              │
              │    When Relay OFF: COM ──> NC ──> (nothing/disconnected)
              │    When Relay ON:  COM ──> NO ──> Pump (+)
              │
Pump (+) <────┘    (Connected to NO terminal)
              │
              │
Pump (-) ────────> Battery (-) / Ground
```

## Step-by-Step Fix

### Step 1: Check Relay Terminals

Your relay module has these terminals:
- **VCC** - Power for relay (connect to 5V or 3.3V)
- **GND** - Ground (connect to GND)
- **IN/IN1** - Control signal (connect to GPIO Pin 8)
- **COM** - Common terminal
- **NO** - Normally Open (pump should connect here)
- **NC** - Normally Closed (DO NOT use this!)

### Step 2: Correct Wiring

**Battery Connection:**
```
Battery (+) → Relay COM terminal
Battery (-) → Ground (GND)
```

**Pump Connection:**
```
Pump (+) → Relay NO (Normally Open) terminal
Pump (-) → Battery (-) / Ground
```

**Relay Control:**
```
GPIO Pin 8 → Relay IN/IN1
5V → Relay VCC
GND → Relay GND
```

### Step 3: Verify Relay State

**When Relay is OFF (Pin HIGH for active-low):**
- COM and NO should be **disconnected** (open circuit)
- Pump should **NOT** run
- Battery current should **NOT** flow to pump

**When Relay is ON (Pin LOW for active-low):**
- COM and NO should be **connected** (closed circuit)
- Pump should **run**
- Battery current flows: Battery → COM → NO → Pump

## Common Mistakes

### ❌ Mistake 1: Using NC Terminal
```
Battery (+) → COM
Pump (+) → NC  ← WRONG! This makes pump always ON
```
**Fix:** Use **NO** terminal instead of **NC**

### ❌ Mistake 2: Direct Connection
```
Battery (+) → Pump (+)  ← Bypassing relay completely!
```
**Fix:** Pump must go through relay COM → NO

### ❌ Mistake 3: Wrong Terminal
```
Pump connected to wrong relay terminal
```
**Fix:** Use **NO** (Normally Open) terminal

## Testing Your Wiring

### Test 1: Disconnect GPIO
1. **Disconnect GPIO Pin 8** from relay IN
2. **Connect battery only**
3. **Pump should NOT run** ✅
4. If pump runs → Wiring is wrong (using NC or direct connection)

### Test 2: Check Relay LED
Most relay modules have an LED:
- **LED OFF** = Relay OFF = Pump should be OFF
- **LED ON** = Relay ON = Pump should be ON

### Test 3: Multimeter Test
1. Set multimeter to continuity/beep mode
2. **Relay OFF:** COM and NO should be **open** (no beep)
3. **Relay ON:** COM and NO should be **closed** (beep)

## Correct Wiring Checklist

- [ ] Battery (+) connected to **Relay COM**
- [ ] Battery (-) connected to **Ground**
- [ ] Pump (+) connected to **Relay NO** (NOT NC!)
- [ ] Pump (-) connected to **Battery (-)** or Ground
- [ ] GPIO Pin 8 connected to **Relay IN/IN1**
- [ ] 5V connected to **Relay VCC**
- [ ] GND connected to **Relay GND**
- [ ] **NO direct connection** between battery and pump

## Visual Guide

```
┌─────────────────┐
│   Battery       │
│   +  ───────────┼──> Relay COM
│   -  ───────────┼──> GND
└─────────────────┘
                    │
                    │  (When relay ON)
                    ▼
              ┌─────────┐
              │  Relay  │
              │  COM    │──> NO ──> Pump (+)
              │  IN ────┼──> GPIO Pin 8
              │  VCC ───┼──> 5V
              │  GND ───┼──> GND
              └─────────┘
                    │
                    │
              Pump (-) ──> Battery (-) / GND
```

## If Pump Still Runs

### Option 1: Check Relay Module
- Some relay modules have a **jumper** to change NO/NC behavior
- Check relay module documentation
- Try a different relay module

### Option 2: Use Different Relay Terminal
- If using NO doesn't work, try:
  - Check if relay is working (LED indicator)
  - Test relay with multimeter
  - Try a different relay module

### Option 3: Verify Relay is Working
```python
# Quick test script
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(8, GPIO.OUT)

# Turn relay ON
GPIO.output(8, GPIO.LOW)  # For active-low
print("Relay ON - Check if LED lights up")
time.sleep(2)

# Turn relay OFF
GPIO.output(8, GPIO.HIGH)  # For active-low
print("Relay OFF - Check if LED turns off")
time.sleep(2)

GPIO.cleanup()
```

## Safety Warning

⚠️ **Before making any wiring changes:**
1. **Disconnect battery/power**
2. **Double-check all connections**
3. **Verify with multimeter** (no continuity when relay OFF)
4. **Reconnect power** only after verification

## Summary

**The issue is NOT in the code** - it's in the **hardware wiring**.

**Fix:**
1. Ensure pump is connected to **NO** (Normally Open) terminal
2. Ensure battery goes through relay **COM → NO → Pump**
3. **NO direct connection** between battery and pump
4. Test: Disconnect GPIO - pump should NOT run

Once wiring is correct, the code will work properly!

