#!/usr/bin/env python3
"""
Auto-fix Arduino connection issues
This script will:
1. Check if COM port is available
2. Try to release the port if needed
3. Test the connection
4. Provide instructions if manual intervention is needed
"""
import time
import serial
import serial.tools.list_ports
import sys

print("="*60)
print("AUTO-FIX ARDUINO CONNECTION")
print("="*60)

# Step 1: Find Arduino
print("\n[STEP 1] Looking for Arduino...")
ports = serial.tools.list_ports.comports()
arduino_port = None

for port in ports:
    print(f"  Found: {port.device} - {port.description}")
    if any(keyword in port.description.upper() for keyword in 
           ['ARDUINO', 'USB SERIAL', 'CH340', 'CP210', 'FTDI']):
        arduino_port = port.device
        print(f"  [OK] This looks like an Arduino!")

if not arduino_port:
    print("\n[ERROR] No Arduino found!")
    print("  - Check USB cable connection")
    print("  - Check Device Manager")
    sys.exit(1)

print(f"\n[OK] Arduino found on: {arduino_port}")

# Step 2: Check if port is available
print(f"\n[STEP 2] Checking if {arduino_port} is available...")
try:
    # Try to open the port briefly to see if it's available
    test_ser = serial.Serial(arduino_port, 9600, timeout=0.1)
    test_ser.close()
    print(f"[OK] Port {arduino_port} is available!")
    port_available = True
except serial.SerialException as e:
    error_msg = str(e)
    if "Access is denied" in error_msg or "PermissionError" in error_msg:
        print(f"[ERROR] Port {arduino_port} is BUSY!")
        print(f"  Error: {e}")
        print(f"\n[SOLUTION]")
        print(f"  1. Close Arduino IDE Serial Monitor")
        print(f"  2. Close any Python scripts using the port")
        print(f"  3. Wait 5 seconds")
        print(f"  4. Run this script again")
        port_available = False
    else:
        print(f"[ERROR] Port error: {e}")
        port_available = False

if not port_available:
    print("\n" + "="*60)
    print("MANUAL ACTION REQUIRED")
    print("="*60)
    print("\nPlease:")
    print("1. Close Arduino Serial Monitor")
    print("2. Close any running Flask app (Ctrl+C)")
    print("3. Wait 5 seconds")
    print("4. Run: python app.py")
    print("\n" + "="*60)
    sys.exit(1)

# Step 3: Test connection
print(f"\n[STEP 3] Testing connection to {arduino_port}...")
try:
    ser = serial.Serial(arduino_port, 9600, timeout=1)
    time.sleep(2)  # Wait for Arduino to initialize
    
    # Clear buffers
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    # Read startup messages
    time.sleep(0.5)
    if ser.in_waiting > 0:
        print("  Arduino startup messages:")
        for _ in range(5):
            if ser.in_waiting > 0:
                msg = ser.readline().decode('utf-8', errors='ignore').strip()
                if msg:
                    print(f"    → {msg}")
            time.sleep(0.1)
    
    # Test ON command
    print("\n  Testing ON command...")
    ser.write(b'ON\n')
    ser.flush()
    time.sleep(0.5)
    
    if ser.in_waiting > 0:
        response = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"    Response: {response}")
        if "PUMP:ON" in response:
            print("    [OK] ON command works!")
        else:
            print("    [WARNING] Unexpected response")
    else:
        print("    [WARNING] No response from Arduino")
    
    # Test OFF command
    print("\n  Testing OFF command...")
    ser.write(b'OFF\n')
    ser.flush()
    time.sleep(0.5)
    
    if ser.in_waiting > 0:
        response = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"    Response: {response}")
        if "PUMP:OFF" in response:
            print("    [OK] OFF command works!")
        else:
            print("    [WARNING] Unexpected response")
    
    ser.close()
    print("\n[SUCCESS] Arduino connection is working!")
    print("\nYou can now start your Flask app:")
    print("  python app.py")
    
except Exception as e:
    print(f"\n[ERROR] Connection test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)

