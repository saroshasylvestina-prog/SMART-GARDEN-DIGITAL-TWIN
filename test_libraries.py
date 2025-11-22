"""Test script to check if hardware libraries are available"""
print("="*50)
print("CHECKING HARDWARE LIBRARY AVAILABILITY")
print("="*50)

# Check Adafruit_DHT
try:
    import Adafruit_DHT
    print("[OK] Adafruit_DHT: INSTALLED")
    REAL_DHT_AVAILABLE = True
except ImportError as e:
    print("[X] Adafruit_DHT: NOT INSTALLED")
    print(f"   Error: {e}")
    REAL_DHT_AVAILABLE = False

# Check RPi.GPIO
try:
    import RPi.GPIO as GPIO
    print("[OK] RPi.GPIO: INSTALLED")
    REAL_GPIO_AVAILABLE = True
except ImportError as e:
    print("[X] RPi.GPIO: NOT INSTALLED")
    print(f"   Error: {e}")
    REAL_GPIO_AVAILABLE = False

# Check spidev
try:
    import spidev
    print("[OK] spidev: INSTALLED")
    REAL_SPI_AVAILABLE = True
except ImportError as e:
    print("[X] spidev: NOT INSTALLED")
    print(f"   Error: {e}")
    REAL_SPI_AVAILABLE = False

print("="*50)
print("SUMMARY")
print("="*50)
if REAL_DHT_AVAILABLE:
    print("[OK] DHT sensors can use REAL hardware")
else:
    print("[X] DHT sensors will use SIMULATION (library not installed)")

if REAL_GPIO_AVAILABLE and REAL_SPI_AVAILABLE:
    print("[OK] Analog sensors (MQ135, LDR, Moisture) can use REAL hardware")
else:
    print("[X] Analog sensors will use SIMULATION (libraries not installed)")

print("\n[INFO] To use REAL hardware:")
if not REAL_DHT_AVAILABLE:
    print("   - Install Adafruit_DHT: pip install Adafruit-DHT")
if not REAL_GPIO_AVAILABLE:
    print("   - RPi.GPIO is only available on Raspberry Pi")
if not REAL_SPI_AVAILABLE:
    print("   - spidev is only available on Raspberry Pi")

