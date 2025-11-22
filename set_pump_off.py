"""
Quick script to immediately set pump to OFF state
Run this if pump/relay doesn't turn off on startup
"""
import time

print("Setting pump to OFF state...")

try:
    import RPi.GPIO as GPIO
    
    GPIO.setwarnings(False)
    try:
        GPIO.cleanup()
    except:
        pass
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(8, GPIO.OUT)
    
    # Set to HIGH for active-low relay (OFF state)
    GPIO.output(8, GPIO.HIGH)
    
    # Verify
    time.sleep(0.2)
    state = GPIO.input(8)
    
    print(f"✅ Pin 8 set to HIGH (state: {state})")
    print(f"✅ Relay should be OFF (green LED should be OFF)")
    print(f"✅ Pump should be stopped")
    
    # Keep it set (don't cleanup immediately)
    print("\nPin will stay HIGH. Press Ctrl+C to exit.")
    print("The pin state will persist until changed by the application.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        GPIO.cleanup()
        
except ImportError:
    print("❌ RPi.GPIO not available - not running on Raspberry Pi")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

