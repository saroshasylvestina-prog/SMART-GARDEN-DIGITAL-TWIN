"""
Test script to verify GPIO pin 8 is working correctly
Run this to diagnose pump/relay issues
"""
import time

print("="*60)
print("PUMP GPIO TEST SCRIPT")
print("="*60)
print()

try:
    import RPi.GPIO as GPIO
    print("✅ RPi.GPIO library found")
except ImportError:
    print("❌ RPi.GPIO library NOT found")
    print("   Install with: pip install RPi.GPIO")
    exit(1)

# Test configuration
PIN = 8
ACTIVE_LOW = True  # Change to False if needed

print(f"Testing GPIO Pin {PIN} (BCM numbering)")
print(f"Relay type: {'Active-LOW' if ACTIVE_LOW else 'Active-HIGH'}")
print()

try:
    # Setup
    GPIO.setwarnings(False)
    try:
        GPIO.cleanup()
        print("✅ GPIO cleanup completed")
    except:
        print("⚠️  GPIO cleanup skipped (no previous setup)")
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)
    print(f"✅ Pin {PIN} configured as OUTPUT")
    
    # Test 1: Set to OFF state
    print("\n" + "-"*60)
    print("TEST 1: Setting pump to OFF state")
    print("-"*60)
    off_state = GPIO.HIGH if ACTIVE_LOW else GPIO.LOW
    GPIO.output(PIN, off_state)
    time.sleep(0.5)
    actual = GPIO.input(PIN)
    print(f"Set pin to: {'HIGH' if off_state == GPIO.HIGH else 'LOW'}")
    print(f"Actual pin state: {actual} (0=LOW, 1=HIGH)")
    print(f"Expected: {1 if ACTIVE_LOW else 0}")
    if actual == (1 if ACTIVE_LOW else 0):
        print("✅ OFF state correct - Pump should be OFF")
    else:
        print("❌ OFF state incorrect!")
    print("\n⏸️  Waiting 3 seconds... Check if pump is OFF")
    time.sleep(3)
    
    # Test 2: Set to ON state
    print("\n" + "-"*60)
    print("TEST 2: Setting pump to ON state")
    print("-"*60)
    on_state = GPIO.LOW if ACTIVE_LOW else GPIO.HIGH
    GPIO.output(PIN, on_state)
    time.sleep(0.5)
    actual = GPIO.input(PIN)
    print(f"Set pin to: {'LOW' if on_state == GPIO.LOW else 'HIGH'}")
    print(f"Actual pin state: {actual} (0=LOW, 1=HIGH)")
    print(f"Expected: {0 if ACTIVE_LOW else 1}")
    if actual == (0 if ACTIVE_LOW else 1):
        print("✅ ON state correct - Pump should be ON")
    else:
        print("❌ ON state incorrect!")
    print("\n▶️  Waiting 3 seconds... Check if pump is ON")
    time.sleep(3)
    
    # Test 3: Return to OFF
    print("\n" + "-"*60)
    print("TEST 3: Returning pump to OFF state")
    print("-"*60)
    GPIO.output(PIN, off_state)
    time.sleep(0.5)
    actual = GPIO.input(PIN)
    print(f"Set pin to: {'HIGH' if off_state == GPIO.HIGH else 'LOW'}")
    print(f"Actual pin state: {actual} (0=LOW, 1=HIGH)")
    print(f"Expected: {1 if ACTIVE_LOW else 0}")
    if actual == (1 if ACTIVE_LOW else 0):
        print("✅ OFF state correct - Pump should be OFF")
    else:
        print("❌ OFF state incorrect!")
    print("\n⏸️  Waiting 3 seconds... Check if pump is OFF")
    time.sleep(3)
    
    # Cleanup
    GPIO.output(PIN, off_state)  # Ensure OFF before cleanup
    GPIO.cleanup()
    print("\n✅ Test completed. GPIO cleaned up.")
    
except Exception as e:
    print(f"\n❌ ERROR during test: {e}")
    import traceback
    traceback.print_exc()
    try:
        GPIO.cleanup()
    except:
        pass

print("\n" + "="*60)
print("DIAGNOSIS:")
print("="*60)
print("If pump was ON during TEST 1 (OFF state):")
print("  → Relay might be active-HIGH, try ACTIVE_LOW = False")
print()
print("If pump was OFF during TEST 2 (ON state):")
print("  → Relay might be active-LOW, try ACTIVE_LOW = True")
print()
print("If pump didn't respond at all:")
print("  → Check wiring connections")
print("  → Verify pin number (BCM 8 = Physical 24)")
print("  → Check relay power supply")
print("="*60)

