#!/usr/bin/env python3
"""
Test Arduino Serial Connection for Pump Control
"""
import time
import sys

print("="*60)
print("ARDUINO PUMP CONTROL TEST")
print("="*60)

# Check if pyserial is installed
try:
    import serial
    import serial.tools.list_ports
    print("\n[OK] PySerial is installed")
except ImportError:
    print("\n[ERROR] PySerial not installed!")
    print("Install it with: pip install pyserial")
    sys.exit(1)

# Find Arduino
print("\n[STEP 1] Looking for Arduino...")
ports = serial.tools.list_ports.comports()
arduino_port = None

for port in ports:
    print(f"  Found: {port.device} - {port.description}")
    # Common Arduino identifiers
    if any(keyword in port.description.upper() for keyword in 
           ['ARDUINO', 'USB SERIAL', 'CH340', 'CP210', 'FTDI']):
        arduino_port = port.device
        print(f"  -> This looks like an Arduino!")

if not arduino_port:
    if ports:
        print("\n[WARNING] No Arduino detected, but found ports:")
        print("  Try manually specifying the port")
        print("  Example: COM3 on Windows, /dev/ttyUSB0 on Linux")
    else:
        print("\n[ERROR] No serial ports found!")
        print("  - Check USB cable connection")
        print("  - Check Device Manager (Windows) or lsusb (Linux)")
    sys.exit(1)

print(f"\n[OK] Using Arduino on: {arduino_port}")

# Connect to Arduino
print("\n[STEP 2] Connecting to Arduino...")
try:
    ser = serial.Serial(arduino_port, 9600, timeout=1)
    time.sleep(2)  # Wait for Arduino to initialize
    print(f"[OK] Connected to {arduino_port} at 9600 baud")
except Exception as e:
    print(f"[ERROR] Failed to connect: {e}")
    sys.exit(1)

# Clear any existing data
ser.flushInput()
ser.flushOutput()

# Wait for Arduino ready message
print("\n[STEP 3] Waiting for Arduino ready message...")
time.sleep(1)
if ser.in_waiting > 0:
    while ser.in_waiting > 0:
        line = ser.readline().decode().strip()
        print(f"  Arduino: {line}")

# Test commands
print("\n[STEP 4] Testing pump control commands...")

commands = [
    ("STATUS", "Check current status"),
    ("ON", "Turn pump ON"),
    ("STATUS", "Check status (should be ON)"),
    ("OFF", "Turn pump OFF"),
    ("STATUS", "Check status (should be OFF)"),
]

for cmd, description in commands:
    print(f"\n  Testing: {cmd} - {description}")
    
    # Send command
    ser.write(f"{cmd}\n".encode())
    ser.flush()
    
    # Wait for response
    time.sleep(0.5)
    
    # Read response
    if ser.in_waiting > 0:
        response = ser.readline().decode().strip()
        print(f"    Response: {response}")
        
        # Check for errors
        if "ERROR" in response.upper():
            print(f"    [WARNING] Arduino returned error!")
        elif cmd == "ON" and "PUMP:ON" in response:
            print(f"    [OK] Pump should be ON now (check LED and pump)")
        elif cmd == "OFF" and "PUMP:OFF" in response:
            print(f"    [OK] Pump should be OFF now (check LED and pump)")
    else:
        print(f"    [WARNING] No response from Arduino")
    
    # Small delay between commands
    time.sleep(0.5)

# Final status check
print("\n[STEP 5] Final status check...")
ser.write("STATUS\n".encode())
ser.flush()
time.sleep(0.5)
if ser.in_waiting > 0:
    response = ser.readline().decode().strip()
    print(f"  Final status: {response}")

# Cleanup
print("\n[STEP 6] Cleaning up...")
ser.write("OFF\n".encode())  # Ensure pump is OFF
ser.flush()
time.sleep(0.5)
ser.close()
print("[OK] Connection closed")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print("\nIf pump responded to commands:")
print("  -> Arduino communication is working!")
print("  -> You can now use PumpControlArduino in your app")
print("\nIf pump didn't respond:")
print("  1. Check relay wiring (VCC, GND, IN, NO/COM)")
print("  2. Check if relay LED responds")
print("  3. Check Arduino Serial Monitor for errors")
print("="*60)

