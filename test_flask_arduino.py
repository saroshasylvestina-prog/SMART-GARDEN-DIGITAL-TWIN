#!/usr/bin/env python3
"""
Test if Flask app can communicate with Arduino
This tests the actual connection used by the Flask app
"""
import requests
import time

print("="*60)
print("TESTING FLASK APP ARDUINO CONNECTION")
print("="*60)

# Test 1: Check pump status
print("\n[TEST 1] Getting pump status...")
try:
    response = requests.get("http://localhost:5000/api/pump/status", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Pump Status:")
        print(f"  - Is ON: {data.get('is_on', 'unknown')}")
        print(f"  - Mode: {data.get('mode', 'unknown')}")
        print(f"  - Connected: {data.get('connected', 'unknown')}")
        print(f"  - Port: {data.get('port', 'N/A')}")
        print(f"  - Relay Type: {data.get('relay_type', 'unknown')}")
        
        if data.get('mode') == 'Simulation':
            print("\n[WARNING] Pump is in SIMULATION mode!")
            print("  -> Arduino connection not working")
            print("  -> Check console output when Flask app started")
        elif data.get('connected'):
            print("\n[OK] Arduino is connected!")
        else:
            print("\n[WARNING] Arduino connection status unclear")
    else:
        print(f"[ERROR] Status check failed: {response.status_code}")
except Exception as e:
    print(f"[ERROR] Failed to connect to Flask app: {e}")
    print("  -> Make sure Flask app is running: python app.py")

# Test 2: Try to turn pump ON
print("\n[TEST 2] Testing pump ON command...")
try:
    response = requests.post(
        "http://localhost:5000/api/pump/on",
        json={"duration": 1.0},
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Pump ON command sent!")
        print(f"  - Success: {data.get('success', False)}")
        print(f"  - Message: {data.get('message', 'N/A')}")
        print("\n  -> Check console output for Arduino communication")
        print("  -> Check if pump actually turned ON")
        
        # Wait a moment
        time.sleep(1.5)
        
        # Check status again
        status_response = requests.get("http://localhost:5000/api/pump/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"\n  Current status: {'ON' if status_data.get('is_on') else 'OFF'}")
    else:
        print(f"[ERROR] Pump ON failed: {response.status_code}")
        try:
            error_data = response.json()
            print(f"  Error: {error_data.get('error', 'Unknown error')}")
        except:
            print(f"  Response: {response.text}")
except Exception as e:
    print(f"[ERROR] Failed to send ON command: {e}")

# Test 3: Try to turn pump OFF
print("\n[TEST 3] Testing pump OFF command...")
try:
    response = requests.post("http://localhost:5000/api/pump/off", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Pump OFF command sent!")
        print(f"  - Success: {data.get('success', False)}")
        print(f"  - Message: {data.get('message', 'N/A')}")
    else:
        print(f"[ERROR] Pump OFF failed: {response.status_code}")
except Exception as e:
    print(f"[ERROR] Failed to send OFF command: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print("\nNext steps:")
print("1. Check Flask app console output for Arduino messages")
print("2. Look for: [ARDUINO] Sent command: 'ON'")
print("3. Look for: [ARDUINO] Response: PUMP:ON")
print("4. If you see 'SIMULATION MODE', Arduino connection failed")
print("5. Make sure Arduino Serial Monitor is CLOSED")
print("="*60)

