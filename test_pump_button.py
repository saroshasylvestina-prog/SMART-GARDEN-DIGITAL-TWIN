#!/usr/bin/env python3
"""
Test script to diagnose why pump button doesn't work
This will test GPIO pin control directly
"""

import time
import sys

print("="*60)
print("PUMP BUTTON DIAGNOSTIC TEST")
print("="*60)

# Test 1: Check if RPi.GPIO is available
print("\n[TEST 1] Checking RPi.GPIO availability...")
try:
    import RPi.GPIO as GPIO
    print("[OK] RPi.GPIO is available")
except ImportError:
    print("[ERROR] RPi.GPIO is NOT available")
    print("\nYou are on Windows using Arduino, not Raspberry Pi!")
    print("You need to use Serial communication instead.")
    print("\nPlease:")
    print("1. Upload arduino_pump_control.ino to your Arduino")
    print("2. Run: python test_arduino_connection.py")
    print("3. Update app.py to use PumpControlArduino")
    print("\nSee ARDUINO_SETUP.md for detailed instructions")
    sys.exit(1)

# Test 2: Initialize GPIO
print("\n[TEST 2] Initializing GPIO...")
try:
    GPIO.setwarnings(False)
    try:
        GPIO.cleanup()
    except:
        pass
    GPIO.setmode(GPIO.BCM)
    print("[OK] GPIO initialized (BCM mode)")
except Exception as e:
    print(f"[ERROR] GPIO initialization failed: {e}")
    sys.exit(1)

# Test 3: Setup pin 8
print("\n[TEST 3] Setting up pin 8...")
pin = 8
active_low = True  # Change to False if your relay is active-high

try:
    # Set initial state to OFF (HIGH for active-low)
    initial_state = GPIO.HIGH if active_low else GPIO.LOW
    GPIO.setup(pin, GPIO.OUT, initial=initial_state)
    GPIO.output(pin, initial_state)
    print(f"[OK] Pin {pin} set up as OUTPUT")
    print(f"   Initial state: {'HIGH (OFF for active-low)' if active_low else 'LOW (OFF for active-high)'}")
    time.sleep(0.5)
    
    # Check current state
    current_state = GPIO.input(pin)
    print(f"   Current pin state: {current_state} (0=LOW, 1=HIGH)")
except Exception as e:
    print(f"❌ Pin setup failed: {e}")
    import traceback
    traceback.print_exc()
    GPIO.cleanup()
    sys.exit(1)

# Test 4: Turn ON (LOW for active-low, HIGH for active-high)
print("\n[TEST 4] Turning pump ON...")
try:
    on_state = GPIO.LOW if active_low else GPIO.HIGH
    GPIO.output(pin, on_state)
    time.sleep(0.2)  # Wait for state to settle
    
    actual_state = GPIO.input(pin)
    expected_state = 0 if active_low else 1
    
    print(f"   Set pin to: {'LOW' if active_low else 'HIGH'}")
    print(f"   Actual pin state: {actual_state} (Expected: {expected_state})")
    
    if actual_state == expected_state:
        print("[OK] Pin state correct - Relay should be ON")
        print("   -> Check if green LED is ON and pump is running")
    else:
        print("[ERROR] Pin state mismatch!")
        print("   → GPIO pin might not be responding correctly")
        print("   → Check wiring and relay power supply")
    
    # Keep ON for 2 seconds
    print("\n   Pump should be ON now... (check LED and pump)")
    time.sleep(2)
    
except Exception as e:
    print(f"❌ Failed to turn ON: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Turn OFF
print("\n[TEST 5] Turning pump OFF...")
try:
    off_state = GPIO.HIGH if active_low else GPIO.LOW
    GPIO.output(pin, off_state)
    time.sleep(0.2)  # Wait for state to settle
    
    actual_state = GPIO.input(pin)
    expected_state = 1 if active_low else 0
    
    print(f"   Set pin to: {'HIGH' if active_low else 'LOW'}")
    print(f"   Actual pin state: {actual_state} (Expected: {expected_state})")
    
    if actual_state == expected_state:
        print("✅ Pin state correct - Relay should be OFF")
        print("   → Check if green LED is OFF and pump stopped")
    else:
        print("❌ Pin state mismatch!")
    
    time.sleep(1)
    
except Exception as e:
    print(f"❌ Failed to turn OFF: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Toggle test (ON/OFF/ON/OFF)
print("\n[TEST 6] Toggle test (ON → OFF → ON → OFF)...")
try:
    for i in range(2):
        print(f"\n   Cycle {i+1}:")
        
        # ON
        GPIO.output(pin, GPIO.LOW if active_low else GPIO.HIGH)
        time.sleep(0.2)
        state = GPIO.input(pin)
        print(f"      ON:  Pin = {state} (Expected: {0 if active_low else 1})")
        time.sleep(1)
        
        # OFF
        GPIO.output(pin, GPIO.HIGH if active_low else GPIO.LOW)
        time.sleep(0.2)
        state = GPIO.input(pin)
        print(f"      OFF: Pin = {state} (Expected: {1 if active_low else 0})")
        time.sleep(1)
    
    print("[OK] Toggle test completed")
    
except Exception as e:
    print(f"[ERROR] Toggle test failed: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
print("\n[TEST 7] Cleaning up...")
try:
    # Set to OFF before cleanup
    GPIO.output(pin, GPIO.HIGH if active_low else GPIO.LOW)
    time.sleep(0.1)
    GPIO.cleanup()
    print("[OK] GPIO cleaned up")
except Exception as e:
    print(f"[WARNING] Cleanup warning: {e}")

print("\n" + "="*60)
print("DIAGNOSTIC TEST COMPLETE")
print("="*60)
print("\nIf the pump didn't respond during tests:")
print("1. Check relay power (VCC to 5V, GND to Ground)")
print("2. Check wiring (Pin 8 to relay IN)")
print("3. Try changing active_low=True to active_low=False in this script")
print("4. Check if relay LED responds to pin changes")
print("="*60)

