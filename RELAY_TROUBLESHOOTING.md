# Relay Troubleshooting Guide

## Problem: Pump Runs Continuously

If your pump runs continuously when connected to GPIO pin 8, this is usually due to **relay polarity** (active-low vs active-high).

## Relay Types

### Active-Low Relay (Most Common)
- **LOW signal (0V)** = Relay ON (pump runs)
- **HIGH signal (3.3V)** = Relay OFF (pump stops)
- **Default state**: Pin should be HIGH to keep pump OFF

### Active-High Relay
- **HIGH signal (3.3V)** = Relay ON (pump runs)
- **LOW signal (0V)** = Relay OFF (pump stops)
- **Default state**: Pin should be LOW to keep pump OFF

## Solution

### Step 1: Check Your Relay Type

Most relays are **active-low**. If your pump runs continuously, try:

1. **Edit `pump_control.py`** (line 143):
   ```python
   pump = PumpControl(pin=8, use_simulation=False, active_low=True)
   ```

2. **If that doesn't work**, try:
   ```python
   pump = PumpControl(pin=8, use_simulation=False, active_low=False)
   ```

### Step 2: Verify Pin Configuration

Make sure:
- ✅ Pin 8 is connected to relay IN/IN1
- ✅ Relay VCC to 5V (or 3.3V depending on relay)
- ✅ Relay GND to Ground
- ✅ Pump connected to relay NO/COM terminals

### Step 3: Test the Configuration

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Check initialization message**:
   - Should show: `[REAL] Pump control initialized on GPIO pin 8 (active-low)`
   - Should show: `[REAL] Initial state: OFF (Pin set to HIGH)`

3. **Test pump control**:
   - Click "Turn ON" - pump should run for configured duration
   - Click "Turn OFF" - pump should stop immediately

## Common Issues

### Issue 1: Pump Always ON
**Cause**: Relay is active-low but code uses active-high (or vice versa)

**Fix**: Change `active_low=True` in `pump_control.py`

### Issue 2: Pump Never Turns ON
**Cause**: Wrong relay type or pin not connected

**Fix**: 
- Check wiring
- Try switching `active_low` value
- Verify pin number (BCM pin 8 = physical pin 24)

### Issue 3: Pin Already in Use
**Cause**: Pin was used by another process

**Fix**: 
```bash
# Check what's using the pin
gpio readall

# Or restart Raspberry Pi
sudo reboot
```

## Pin Configuration

### BCM Pin 8 (Physical Pin 24)
- GPIO 8 (BCM numbering)
- Physical pin 24 on Raspberry Pi
- Can be used for PWM or digital output

### Alternative Pins
If pin 8 doesn't work, try:
- Pin 18 (GPIO 18) - PWM capable
- Pin 23 (GPIO 23)
- Pin 24 (GPIO 24)

Change in `pump_control.py`:
```python
pump = PumpControl(pin=18, use_simulation=False, active_low=True)
```

## Testing Commands

### Test GPIO Pin Directly
```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(8, GPIO.OUT)

# Test active-low (LOW = ON)
GPIO.output(8, GPIO.LOW)  # Pump should turn ON
GPIO.output(8, GPIO.HIGH)  # Pump should turn OFF

# Test active-high (HIGH = ON)
GPIO.output(8, GPIO.HIGH)  # Pump should turn ON
GPIO.output(8, GPIO.LOW)   # Pump should turn OFF
```

## Configuration Options

In `pump_control.py`, you can configure:

```python
pump = PumpControl(
    pin=8,              # GPIO pin number (BCM)
    use_simulation=False, # Set False to use real GPIO
    active_low=True      # True for active-low, False for active-high
)
```

## Verification Checklist

- [ ] Relay type identified (active-low or active-high)
- [ ] `active_low` parameter set correctly
- [ ] `use_simulation=False` in pump_control.py
- [ ] Pin 8 properly connected to relay
- [ ] Relay power connected (VCC and GND)
- [ ] Pump connected to relay NO/COM terminals
- [ ] Initial state shows "OFF" in console
- [ ] Test "Turn ON" button works
- [ ] Test "Turn OFF" button works

## Still Having Issues?

1. **Check relay module**: Some relays have jumpers to change active-low/active-high
2. **Check wiring**: Ensure all connections are secure
3. **Test with multimeter**: Verify pin output voltage
4. **Check relay LED**: Most relays have an LED that shows state
5. **Try different pin**: Test with GPIO 18 or 23

## Safety Notes

⚠️ **Always disconnect power** when making wiring changes
⚠️ **Double-check connections** before applying power
⚠️ **Use appropriate relay** for your pump's voltage/current requirements
⚠️ **Test with low voltage first** before connecting pump

