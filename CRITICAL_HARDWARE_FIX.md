# CRITICAL: Pump Runs Without Control - Hardware Fix

## ⚠️ URGENT ISSUE

If the pump runs even when:
- USB cable is removed
- Arduino is reset
- No code is running

**This means the pump is NOT going through the relay/Arduino at all!**

## The Problem

The pump has a **direct connection** to the battery, bypassing all control.

## Root Causes

### Cause 1: Pump Connected to NC Terminal (Most Common)
```
Battery (+) → Relay COM
Pump (+) → Relay NC  ← WRONG! This bypasses control
```

**NC (Normally Closed)** = Always connected when relay is OFF
- When relay OFF → NC is connected → Pump runs
- When relay ON → NC disconnects → Pump stops (opposite of what you want!)

**Fix:** Move pump wire from **NC** to **NO** terminal

### Cause 2: Direct Battery Connection
```
Battery (+) → Pump (+)  ← Direct connection, bypassing relay!
```

**Fix:** Remove direct connection. Pump must go through relay.

### Cause 3: Relay Stuck/Defective
- Relay contacts welded together
- Relay mechanical failure
- Relay module defective

**Fix:** Replace relay module

## Step-by-Step Fix

### Step 1: Disconnect Everything

**STOP! Disconnect all power first!**

1. **Disconnect battery/power supply**
2. **Disconnect USB cable**
3. **Remove all connections**

### Step 2: Check Current Wiring

**Look at your relay module terminals:**

```
Relay Module:
├── VCC (power for relay)
├── GND (ground)
├── IN/IN1 (control signal)
├── COM (common terminal)
├── NO (Normally Open) ← USE THIS!
└── NC (Normally Closed) ← DO NOT USE!
```

### Step 3: Correct Wiring

**Battery Connection:**
```
Battery (+) → Relay COM terminal ONLY
Battery (-) → Ground (GND)
```

**Pump Connection:**
```
Pump (+) → Relay NO terminal (NOT NC!)
Pump (-) → Battery (-) or Ground
```

**Control Connection:**
```
Arduino/GPIO Pin 8 → Relay IN/IN1
5V → Relay VCC
GND → Relay GND
```

### Step 4: Verify NO Terminal

**Test without any control:**
1. Connect battery ONLY (no Arduino, no GPIO)
2. **Pump should NOT run** ✅
3. If pump runs → Still using NC or direct connection ❌

## Visual Wiring Check

### ❌ WRONG Wiring (Pump Always ON):
```
Battery (+) ──> Relay COM
                │
                ├──> NC ──> Pump (+)  ← WRONG TERMINAL!
                │
                └──> NO ──> (nothing)
```

### ✅ CORRECT Wiring (Pump Controlled):
```
Battery (+) ──> Relay COM
                │
                ├──> NC ──> (nothing)  ← Leave empty
                │
                └──> NO ──> Pump (+)  ← CORRECT TERMINAL!
```

## Testing Procedure

### Test 1: No Control Connected
1. **Disconnect Arduino/GPIO completely**
2. **Connect ONLY battery**
3. **Pump should be OFF** ✅
4. If pump is ON → Wrong terminal or direct connection ❌

### Test 2: Manual Relay Test
1. **Disconnect all control signals**
2. **Manually connect relay IN to 5V** → Pump should turn ON
3. **Manually connect relay IN to GND** → Pump should turn OFF
4. If pump doesn't respond → Relay defective

### Test 3: Multimeter Test
1. **Set multimeter to continuity/beep mode**
2. **Relay OFF (no signal):**
   - COM to NO → Should be **open** (no beep) ✅
   - COM to NC → Will beep (this is why pump runs!) ❌
3. **Relay ON (signal applied):**
   - COM to NO → Should **beep** (connected) ✅
   - COM to NC → Should be open (disconnected) ✅

## Common Mistakes

### Mistake 1: Using NC Instead of NO
**Symptom:** Pump runs without any control
**Fix:** Move wire from NC to NO terminal

### Mistake 2: Multiple Connections
**Symptom:** Pump has multiple wires
**Fix:** Ensure only ONE path: Battery → COM → NO → Pump

### Mistake 3: Relay Module Jumper
Some relay modules have jumpers:
- **H** (High) = Active-high
- **L** (Low) = Active-low
- **NC/NO** = Terminal selection

**Check:** Look for jumpers on relay module

## Quick Fix Checklist

1. ✅ **Disconnect all power**
2. ✅ **Check which terminal pump is on:**
   - If on **NC** → Move to **NO**
   - If on **NO** → Check for direct connection
3. ✅ **Remove any direct battery-to-pump wires**
4. ✅ **Verify wiring:**
   - Battery (+) → COM
   - Pump (+) → NO (NOT NC!)
   - Pump (-) → Battery (-)
5. ✅ **Test without control:**
   - Connect battery only
   - Pump should be OFF
6. ✅ **Reconnect control:**
   - Arduino/GPIO → Relay IN
   - Power → Relay VCC/GND

## If Still Not Working

### Option 1: Replace Relay Module
- Relay might be defective
- Contacts might be welded
- Try a different relay module

### Option 2: Check Relay Type
- Some relays have different terminal layouts
- Check relay module documentation
- Verify COM, NO, NC labels

### Option 3: Use Different Relay
- Try a different relay module
- Test with known working relay
- Verify relay is functioning

## Safety Reminder

⚠️ **ALWAYS disconnect power before:**
- Changing wiring
- Moving connections
- Testing continuity
- Troubleshooting

## Summary

**The pump is running because:**
1. It's connected to **NC** (Normally Closed) terminal, OR
2. There's a **direct connection** bypassing the relay, OR
3. The **relay is defective/stuck**

**The fix:**
1. Move pump wire from **NC to NO** terminal
2. Remove any direct battery-to-pump connections
3. Ensure pump ONLY goes through: Battery → COM → NO → Pump

Once fixed, the pump will:
- ✅ Be OFF when no control signal
- ✅ Turn ON when relay activates
- ✅ Be controlled by your code

