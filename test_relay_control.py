"""
Test script to manually control relay and verify it's working
Run this to test if relay responds to GPIO signals
"""
import time

print("="*60)
print("RELAY CONTROL TEST")
print("="*60)
print()

try:
    import RPi.GPIO as GPIO
    print("✅ RPi.GPIO library found")
except ImportError:
    print("❌ RPi.GPIO library NOT found")
    print("   This script requires Raspberry Pi with RPi.GPIO")
    exit(1)

# Configuration
PIN = 8
ACTIVE_LOW = True  # Change if needed

print(f"Testing GPIO Pin {PIN} (BCM numbering)")
print(f"Relay type: {'Active-LOW' if ACTIVE_LOW else 'Active-HIGH'}")
print()
print("Instructions:")
print("1. Watch the relay LED (if it has one)")
print("2. Listen for relay click sound")
print("3. Check if pump starts/stops")
print()

try:
    # Setup
    GPIO.setwarnings(False)
    try:
        GPIO.cleanup()
    except:
        pass
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)
    
    # Initial state: OFF
    initial_state = GPIO.HIGH if ACTIVE_LOW else GPIO.LOW
    GPIO.output(PIN, initial_state)
    print(f"✅ Initialized - Pin set to {'HIGH' if ACTIVE_LOW else 'LOW'} (OFF)")
    print()
    
    # Test sequence
    for i in range(3):
        print(f"\n{'='*60}")
        print(f"TEST CYCLE {i+1}/3")
        print('='*60)
        
        # Turn ON
        print("\n▶️  TURNING PUMP ON...")
        on_state = GPIO.LOW if ACTIVE_LOW else GPIO.HIGH
        GPIO.output(PIN, on_state)
        time.sleep(0.2)
        actual = GPIO.input(PIN)
        print(f"   Pin set to: {'LOW' if ACTIVE_LOW else 'HIGH'}")
        print(f"   Actual pin state: {actual}")
        print(f"   Expected: {0 if ACTIVE_LOW else 1}")
        
        if actual == (0 if ACTIVE_LOW else 1):
            print("   ✅ Pin state CORRECT")
        else:
            print("   ❌ Pin state INCORRECT!")
        
        print("\n   👀 CHECK NOW:")
        print("   - Relay LED should be ON")
        print("   - You should hear relay click")
        print("   - Pump should be RUNNING")
        print("\n   ⏱️  Waiting 5 seconds...")
        time.sleep(5)
        
        # Turn OFF
        print("\n⏸️  TURNING PUMP OFF...")
        off_state = GPIO.HIGH if ACTIVE_LOW else GPIO.LOW
        GPIO.output(PIN, off_state)
        time.sleep(0.2)
        actual = GPIO.input(PIN)
        print(f"   Pin set to: {'HIGH' if ACTIVE_LOW else 'LOW'}")
        print(f"   Actual pin state: {actual}")
        print(f"   Expected: {1 if ACTIVE_LOW else 0}")
        
        if actual == (1 if ACTIVE_LOW else 0):
            print("   ✅ Pin state CORRECT")
        else:
            print("   ❌ Pin state INCORRECT!")
        
        print("\n   👀 CHECK NOW:")
        print("   - Relay LED should be OFF")
        print("   - You should hear relay click")
        print("   - Pump should be STOPPED")
        print("\n   ⏱️  Waiting 5 seconds...")
        time.sleep(5)
    
    # Final state: OFF
    GPIO.output(PIN, initial_state)
    GPIO.cleanup()
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)
    print("\nDIAGNOSIS:")
    print("-"*60)
    print("If pump did NOT turn ON during test:")
    print("  1. Check relay power (VCC and GND connected?)")
    print("  2. Check GPIO Pin 8 connection to relay IN")
    print("  3. Check relay LED - does it light up?")
    print("  4. Try different pin (test with pin 18)")
    print("  5. Check if relay module is working (test with multimeter)")
    print()
    print("If pump turned ON but code doesn't work:")
    print("  1. Check if application is in simulation mode")
    print("  2. Restart the application")
    print("  3. Check console output for errors")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ ERROR during test: {e}")
    import traceback
    traceback.print_exc()
    try:
        GPIO.cleanup()
    except:
        pass

