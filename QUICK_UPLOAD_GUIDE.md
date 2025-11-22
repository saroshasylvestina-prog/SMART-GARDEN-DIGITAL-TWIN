# Quick Upload Guide - Fix 2-Second Delay

## The Problem
Your Arduino has old code with a 2-second delay. We need to upload clean code.

## Quick Upload (3 Steps)

### Step 1: Open Arduino IDE
**Option A: Use the batch script**
- Double-click `UPLOAD_ARDUINO_CODE.bat`
- Arduino IDE will open with the code ready

**Option B: Manual**
- Open Arduino IDE
- File → Open → Select `arduino_pump_control_clean.ino`

### Step 2: Select Board and Port
1. **Tools → Board → Arduino Uno** (or your board)
2. **Tools → Port → COM5** (or your Arduino's COM port)

### Step 3: Upload
1. Click **Upload** button (→ arrow icon) or press **Ctrl+U**
2. Wait for **"Done uploading"** message
3. **Close Serial Monitor** if it opens
4. **Close Arduino IDE**

## Verify Upload

1. **Open Serial Monitor** (Tools → Serial Monitor)
2. **Set baudrate to 9600**
3. **Press Arduino reset button**
4. You should see:
   ```
   Arduino Pump Control Ready - NO AUTO DELAYS
   Initial state: OFF (Pin 8 = HIGH)
   ```
5. **Pump should NOT turn on** when you reset
6. **Close Serial Monitor**

## Test After Upload

1. **Close Arduino Serial Monitor**
2. **Restart Flask app:**
   ```bash
   python app.py
   ```
3. **Test pump** - should now run for exactly 1 second

## What Changed

**Old code (WRONG):**
- Had `delay(2000)` in loop
- Pump ran automatically for 2 seconds

**New code (CORRECT):**
- No delays
- Only responds to Python "ON"/"OFF" commands
- Duration controlled by Python (1 second)

## Still Running for 2 Seconds?

1. **Re-upload** the clean code
2. **Check Serial Monitor** - verify Arduino shows "NO AUTO DELAYS"
3. **Check Python console** - see when ON/OFF commands are sent
4. **Verify** the uploaded code matches `arduino_pump_control_clean.ino`

