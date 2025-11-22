"""
DHT Sensor Module for Smart Garden Digital Twin
Supports both simulated and real DHT sensor readings
"""
import random
import time
from datetime import datetime

# Try to import Adafruit_DHT for real sensor support
try:
    import Adafruit_DHT
    REAL_SENSOR_AVAILABLE = True
except ImportError:
    REAL_SENSOR_AVAILABLE = False
    print("Adafruit_DHT not installed. Using simulated sensor data.")
    print("To use real sensor, install: pip install Adafruit-DHT")

class DHTSensor:
    """DHT Sensor handler for temperature and humidity readings"""
    
    def __init__(self, sensor_type=22, pin=4, use_simulation=True):
        """
        Initialize DHT sensor
        
        Args:
            sensor_type: DHT sensor type (11 or 22)
            pin: GPIO pin number (default 4)
            use_simulation: If True, use simulated data instead of real sensor
        """
        self.sensor_type = sensor_type
        self.pin = pin
        self.use_simulation = use_simulation or not REAL_SENSOR_AVAILABLE
        self.connected = False
        self.last_reading_time = None
        self.temperature = None
        self.humidity = None
        
        # Initialize sensor
        self._initialize_sensor()
    
    def _initialize_sensor(self):
        """Initialize the sensor connection"""
        if self.use_simulation:
            print(f"[SIMULATION] DHT{self.sensor_type} sensor initialized on pin {self.pin}")
            self.connected = True  # Simulation mode = connected to simulation system
        else:
            try:
                # Test sensor connection
                humidity, temperature = Adafruit_DHT.read_retry(
                    self.sensor_type, self.pin
                )
                if humidity is not None and temperature is not None:
                    self.connected = True
                    print(f"[REAL] DHT{self.sensor_type} sensor connected on pin {self.pin}")
                else:
                    self.connected = False
                    print(f"[ERROR] Failed to read from DHT{self.sensor_type} sensor on pin {self.pin}")
            except Exception as e:
                self.connected = False
                print(f"[ERROR] Sensor initialization failed: {e}")
    
    def read_sensor(self):
        """Read temperature and humidity from sensor"""
        # First, try to detect real hardware even in simulation mode
        if self.use_simulation:
            # Try to detect real hardware first (only if library is available)
            if REAL_SENSOR_AVAILABLE:
                try:
                    humidity, temperature = Adafruit_DHT.read_retry(
                        self.sensor_type, self.pin
                    )
                    if humidity is not None and temperature is not None:
                        # Real hardware detected! Switch to real mode
                        self.use_simulation = False
                        self.connected = True
                        print(f"[REAL] DHT{self.sensor_type} sensor detected and connected on pin {self.pin}")
                        self.temperature = round(temperature, 1)
                        self.humidity = round(humidity, 1)
                        self.last_reading_time = datetime.now()
                        return self.temperature, self.humidity
                except Exception as e:
                    # No real hardware, continue with simulation
                    # Only log if it's not a common "no hardware" error
                    if "No module named" not in str(e) and "GPIO" not in str(e):
                        print(f"[DEBUG] Hardware detection attempt failed: {e}")
                    pass
            
            # Simulate realistic temperature and humidity values
            # Temperature: 15-30°C (typical garden range)
            # Humidity: 40-80% (typical garden range)
            self.temperature = round(random.uniform(18.0, 26.0), 1)
            self.humidity = round(random.uniform(45.0, 75.0), 1)
        else:
            # Real mode - try to read from hardware
            if not REAL_SENSOR_AVAILABLE:
                # Library not available, fall back to simulation
                self.use_simulation = True
                self.connected = False
                print(f"[WARNING] Adafruit_DHT library not available, switching to simulation")
                # Continue with simulation
                self.temperature = round(random.uniform(18.0, 26.0), 1)
                self.humidity = round(random.uniform(45.0, 75.0), 1)
            else:
                try:
                    humidity, temperature = Adafruit_DHT.read_retry(
                        self.sensor_type, self.pin
                    )
                    if humidity is not None and temperature is not None:
                        # Update connection status on successful read
                        if not self.connected:
                            self.connected = True
                            print(f"[REAL] DHT{self.sensor_type} sensor connected on pin {self.pin}")
                        self.temperature = round(temperature, 1)
                        self.humidity = round(humidity, 1)
                    else:
                        # Failed to read - mark as disconnected
                        if self.connected:
                            self.connected = False
                            print(f"[WARNING] DHT{self.sensor_type} sensor disconnected")
                        return None, None
                except Exception as e:
                    print(f"[ERROR] Sensor read failed: {e}")
                    # Mark as disconnected on error
                    if self.connected:
                        self.connected = False
                        print(f"[WARNING] DHT{self.sensor_type} sensor disconnected due to error")
                    return None, None
        
        self.last_reading_time = datetime.now()
        return self.temperature, self.humidity
    
    def get_status(self):
        """Get sensor connection status and last reading"""
        return {
            'connected': self.connected,
            'sensor_type': f'DHT{self.sensor_type}',
            'pin': self.pin,
            'mode': 'Simulation' if self.use_simulation else 'Real Sensor',
            'temperature': self.temperature,
            'humidity': self.humidity,
            'last_reading': self.last_reading_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_reading_time else 'Never',
            'real_sensor_available': REAL_SENSOR_AVAILABLE
        }

class MQ135Sensor:
    """MQ135 Air Quality Sensor handler for CO2, NH3, NOx, and other gas readings"""
    
    def __init__(self, analog_pin=0, use_simulation=True):
        """
        Initialize MQ135 sensor
        
        Args:
            analog_pin: Analog pin number (default 0 for A0)
            use_simulation: If True, use simulated data instead of real sensor
        """
        self.analog_pin = analog_pin
        self.use_simulation = use_simulation
        self.connected = False
        self.last_reading_time = None
        self.air_quality = None
        self.co2_ppm = None
        self.nh3_ppm = None
        self.nox_ppm = None
        
        # Initialize sensor
        self._initialize_sensor()
    
    def _initialize_sensor(self):
        """Initialize the sensor connection"""
        if self.use_simulation:
            print(f"[SIMULATION] MQ135 sensor initialized on analog pin A{self.analog_pin}")
            self.connected = True  # Simulation mode = connected to simulation system
        else:
            try:
                # Try to import ADC library (for Raspberry Pi or similar)
                try:
                    import RPi.GPIO as GPIO
                    import spidev
                    self.spi = spidev.SpiDev()
                    self.spi.open(0, 0)
                    self.connected = True
                    print(f"[REAL] MQ135 sensor connected on analog pin A{self.analog_pin}")
                except ImportError:
                    # Fallback to simulation if libraries not available
                    self.use_simulation = True
                    self.connected = True  # Simulation mode = connected to simulation system
                    print(f"[SIMULATION] MQ135 sensor (RPi libraries not available, using simulation)")
            except Exception as e:
                self.connected = False
                print(f"[ERROR] MQ135 sensor initialization failed: {e}")
    
    def _read_analog(self, channel, force_read=False):
        """Read analog value from MCP3008 ADC (for Raspberry Pi)
        
        Args:
            channel: ADC channel number
            force_read: If True, attempt to read even in simulation mode (for hardware detection)
        """
        if self.use_simulation and not force_read:
            return None
        try:
            # MCP3008 ADC reading (if using SPI ADC)
            spi = self.spi if hasattr(self, 'spi') and self.spi else None
            if spi is None:
                return None
            adc = spi.xfer2([1, (8 + channel) << 4, 0])
            data = ((adc[1] & 3) << 8) + adc[2]
            return data
        except:
            return None
    
    def read_sensor(self):
        """Read air quality data from MQ135 sensor"""
        # First, try to detect real hardware even in simulation mode
        if self.use_simulation:
            # Try to detect real hardware first
            try:
                import RPi.GPIO as GPIO
                import spidev
                test_spi = spidev.SpiDev()
                test_spi.open(0, 0)
                # Temporarily set spi for reading
                old_spi = getattr(self, 'spi', None)
                self.spi = test_spi
                analog_value = self._read_analog(self.analog_pin, force_read=True)
                test_spi.close()
                if old_spi:
                    self.spi = old_spi
                if analog_value is not None and 0 <= analog_value <= 1023:
                    # Real hardware detected! Switch to real mode
                    self.use_simulation = False
                    self.spi = spidev.SpiDev()
                    self.spi.open(0, 0)
                    self.connected = True
                    print(f"[REAL] MQ135 sensor detected and connected on analog pin A{self.analog_pin}")
                    # Read actual value
                    analog_value = self._read_analog(self.analog_pin)
                    voltage = (analog_value / 1023.0) * 3.3
                    self.air_quality = round((voltage / 3.3) * 500, 1)
                    self.co2_ppm = round(400 + (voltage * 200), 1)
                    self.nh3_ppm = round(voltage * 10, 1)
                    self.nox_ppm = round(voltage * 20, 1)
                    self.last_reading_time = datetime.now()
                    return self.air_quality, self.co2_ppm, self.nh3_ppm, self.nox_ppm
            except:
                # No real hardware, continue with simulation
                pass
            
            # Simulate realistic air quality values
            # Air Quality Index: 0-500 (0-50 good, 51-100 moderate, 101-150 unhealthy)
            self.air_quality = round(random.uniform(20.0, 80.0), 1)
            # CO2 in ppm: 400-1000 normal, >1000 high
            self.co2_ppm = round(random.uniform(400.0, 800.0), 1)
            # NH3 in ppm: 0-25 normal
            self.nh3_ppm = round(random.uniform(5.0, 20.0), 1)
            # NOx in ppm: 0-50 normal
            self.nox_ppm = round(random.uniform(10.0, 40.0), 1)
        else:
            try:
                # Read analog value
                analog_value = self._read_analog(self.analog_pin)
                if analog_value is None:
                    # Failed to read - mark as disconnected
                    if self.connected:
                        self.connected = False
                        print(f"[WARNING] MQ135 sensor disconnected")
                    return None, None, None
                
                # Update connection status on successful read
                if not self.connected:
                    self.connected = True
                    print(f"[REAL] MQ135 sensor connected on analog pin A{self.analog_pin}")
                
                # Convert to voltage (0-3.3V for MCP3008 with 3.3V reference)
                voltage = (analog_value / 1023.0) * 3.3
                
                # MQ135 calibration (simplified - actual calibration requires specific formulas)
                # These are approximate conversions
                self.air_quality = round((voltage / 3.3) * 500, 1)
                self.co2_ppm = round(400 + (voltage * 200), 1)
                self.nh3_ppm = round(voltage * 10, 1)
                self.nox_ppm = round(voltage * 15, 1)
            except Exception as e:
                print(f"[ERROR] MQ135 sensor read failed: {e}")
                return None, None, None
        
        self.last_reading_time = datetime.now()
        return self.air_quality, self.co2_ppm, self.nh3_ppm, self.nox_ppm
    
    def get_status(self):
        """Get sensor connection status and last reading"""
        return {
            'connected': self.connected,
            'sensor_type': 'MQ135',
            'analog_pin': f'A{self.analog_pin}',
            'mode': 'Simulation' if self.use_simulation else 'Real Sensor',
            'air_quality': self.air_quality,
            'co2_ppm': self.co2_ppm,
            'nh3_ppm': self.nh3_ppm,
            'nox_ppm': self.nox_ppm,
            'last_reading': self.last_reading_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_reading_time else 'Never'
        }

# Global sensor instances
print("\n" + "="*50)
print("INITIALIZING DHT SENSOR")
print("="*50)
sensor = DHTSensor(sensor_type=22, pin=4, use_simulation=True)
print("="*50 + "\n")

print("\n" + "="*50)
print("INITIALIZING MQ135 SENSOR")
print("="*50)
mq135_sensor = MQ135Sensor(analog_pin=0, use_simulation=True)
print("="*50 + "\n")

class LDRSensor:
    """LDR (Light Dependent Resistor) Sensor handler for light intensity readings"""
    
    def __init__(self, analog_pin=1, use_simulation=True):
        """
        Initialize LDR sensor
        
        Args:
            analog_pin: Analog pin number (default 1 for A1)
            use_simulation: If True, use simulated data instead of real sensor
        """
        self.analog_pin = analog_pin
        self.use_simulation = use_simulation
        self.connected = False
        self.last_reading_time = None
        self.light_intensity = None  # in lux
        self.light_percentage = None  # 0-100%
        
        # Initialize sensor
        self._initialize_sensor()
    
    def _initialize_sensor(self):
        """Initialize the sensor connection"""
        if self.use_simulation:
            print(f"[SIMULATION] LDR sensor initialized on analog pin A{self.analog_pin}")
            self.connected = True  # Simulation mode = connected to simulation system
        else:
            try:
                # Try to import ADC library (for Raspberry Pi or similar)
                try:
                    import RPi.GPIO as GPIO
                    import spidev
                    self.spi = spidev.SpiDev()
                    self.spi.open(0, 0)
                    self.connected = True
                    print(f"[REAL] LDR sensor connected on analog pin A{self.analog_pin}")
                except ImportError:
                    # Fallback to simulation if libraries not available
                    self.use_simulation = True
                    self.connected = True  # Simulation mode = connected to simulation system
                    print(f"[SIMULATION] LDR sensor (RPi libraries not available, using simulation)")
            except Exception as e:
                self.connected = False
                print(f"[ERROR] LDR sensor initialization failed: {e}")
    
    def _read_analog(self, channel, force_read=False):
        """Read analog value from MCP3008 ADC (for Raspberry Pi)
        
        Args:
            channel: ADC channel number
            force_read: If True, attempt to read even in simulation mode (for hardware detection)
        """
        if self.use_simulation and not force_read:
            return None
        try:
            # MCP3008 ADC reading (if using SPI ADC)
            spi = self.spi if hasattr(self, 'spi') and self.spi else None
            if spi is None:
                return None
            adc = spi.xfer2([1, (8 + channel) << 4, 0])
            data = ((adc[1] & 3) << 8) + adc[2]
            return data
        except:
            return None
    
    def read_sensor(self):
        """Read light intensity from LDR sensor"""
        # First, try to detect real hardware even in simulation mode
        if self.use_simulation:
            # Try to detect real hardware first
            try:
                import RPi.GPIO as GPIO
                import spidev
                test_spi = spidev.SpiDev()
                test_spi.open(0, 0)
                # Temporarily set spi for reading
                old_spi = getattr(self, 'spi', None)
                self.spi = test_spi
                analog_value = self._read_analog(self.analog_pin, force_read=True)
                test_spi.close()
                if old_spi:
                    self.spi = old_spi
                if analog_value is not None and 0 <= analog_value <= 1023:
                    # Real hardware detected! Switch to real mode
                    self.use_simulation = False
                    self.spi = spidev.SpiDev()
                    self.spi.open(0, 0)
                    self.connected = True
                    print(f"[REAL] LDR sensor detected and connected on analog pin A{self.analog_pin}")
                    # Read actual value
                    analog_value = self._read_analog(self.analog_pin)
                    voltage = (analog_value / 1023.0) * 3.3
                    self.light_intensity = round((voltage / 3.3) * 100000, 1)
                    self.light_percentage = round((voltage / 3.3) * 100, 1)
                    self.last_reading_time = datetime.now()
                    return self.light_intensity, self.light_percentage
            except:
                # No real hardware, continue with simulation
                pass
            
            # Simulate realistic light intensity values
            # Light intensity: 0-100000 lux (0-1000 typical indoor, 10000+ bright sunlight)
            # Simulate day/night cycle variation
            import time
            hour = time.localtime().tm_hour
            if 6 <= hour <= 18:  # Daytime
                self.light_intensity = round(random.uniform(500.0, 50000.0), 1)
            else:  # Nighttime
                self.light_intensity = round(random.uniform(0.0, 100.0), 1)
            
            # Convert to percentage (0-100%)
            self.light_percentage = round((self.light_intensity / 100000.0) * 100, 1)
        else:
            try:
                # Read analog value
                analog_value = self._read_analog(self.analog_pin)
                if analog_value is None:
                    # Failed to read - mark as disconnected
                    if self.connected:
                        self.connected = False
                        print(f"[WARNING] LDR sensor disconnected")
                    return None, None
                
                # Update connection status on successful read
                if not self.connected:
                    self.connected = True
                    print(f"[REAL] LDR sensor connected on analog pin A{self.analog_pin}")
                
                # Convert to voltage (0-3.3V for MCP3008 with 3.3V reference)
                voltage = (analog_value / 1023.0) * 3.3
                
                # LDR calibration (simplified - actual calibration requires specific formulas)
                # LDR resistance decreases with light, so higher voltage = more light
                self.light_intensity = round((voltage / 3.3) * 100000, 1)
                self.light_percentage = round((voltage / 3.3) * 100, 1)
            except Exception as e:
                print(f"[ERROR] LDR sensor read failed: {e}")
                # Mark as disconnected on error
                if self.connected:
                    self.connected = False
                    print(f"[WARNING] LDR sensor disconnected due to error")
                return None, None
        
        self.last_reading_time = datetime.now()
        return self.light_intensity, self.light_percentage
    
    def get_status(self):
        """Get sensor connection status and last reading"""
        return {
            'connected': self.connected,
            'sensor_type': 'LDR',
            'analog_pin': f'A{self.analog_pin}',
            'mode': 'Simulation' if self.use_simulation else 'Real Sensor',
            'light_intensity': self.light_intensity,
            'light_percentage': self.light_percentage,
            'last_reading': self.last_reading_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_reading_time else 'Never'
        }

# Global LDR sensor instance
print("\n" + "="*50)
print("INITIALIZING LDR SENSOR")
print("="*50)
ldr_sensor = LDRSensor(analog_pin=1, use_simulation=True)
print("="*50 + "\n")

class MoistureSensor:
    """Soil Moisture Sensor handler for soil moisture readings"""
    
    def __init__(self, analog_pin=2, use_simulation=True):
        """
        Initialize Moisture sensor
        
        Args:
            analog_pin: Analog pin number (default 2 for A2)
            use_simulation: If True, use simulated data instead of real sensor
        """
        self.analog_pin = analog_pin
        self.use_simulation = use_simulation
        self.connected = False
        self.last_reading_time = None
        self.moisture_percentage = None  # 0-100%
        self.moisture_raw = None  # Raw ADC value
        
        # Initialize sensor
        self._initialize_sensor()
    
    def _initialize_sensor(self):
        """Initialize the sensor connection"""
        if self.use_simulation:
            print(f"[SIMULATION] Moisture sensor initialized on analog pin A{self.analog_pin}")
            self.connected = True  # Simulation mode = connected to simulation system
        else:
            try:
                # Try to import ADC library (for Raspberry Pi or similar)
                try:
                    import RPi.GPIO as GPIO
                    import spidev
                    self.spi = spidev.SpiDev()
                    self.spi.open(0, 0)
                    self.connected = True
                    print(f"[REAL] Moisture sensor connected on analog pin A{self.analog_pin}")
                except ImportError:
                    # Fallback to simulation if libraries not available
                    self.use_simulation = True
                    self.connected = True  # Simulation mode = connected to simulation system
                    print(f"[SIMULATION] Moisture sensor (RPi libraries not available, using simulation)")
            except Exception as e:
                self.connected = False
                print(f"[ERROR] Moisture sensor initialization failed: {e}")
    
    def _read_analog(self, channel, force_read=False):
        """Read analog value from MCP3008 ADC (for Raspberry Pi)
        
        Args:
            channel: ADC channel number
            force_read: If True, attempt to read even in simulation mode (for hardware detection)
        """
        if self.use_simulation and not force_read:
            return None
        try:
            # MCP3008 ADC reading (if using SPI ADC)
            spi = self.spi if hasattr(self, 'spi') and self.spi else None
            if spi is None:
                return None
            adc = spi.xfer2([1, (8 + channel) << 4, 0])
            data = ((adc[1] & 3) << 8) + adc[2]
            return data
        except:
            return None
    
    def read_sensor(self):
        """Read soil moisture from sensor"""
        # First, try to detect real hardware even in simulation mode
        if self.use_simulation:
            # Try to detect real hardware first
            try:
                import RPi.GPIO as GPIO
                import spidev
                test_spi = spidev.SpiDev()
                test_spi.open(0, 0)
                # Temporarily set spi for reading
                old_spi = getattr(self, 'spi', None)
                self.spi = test_spi
                analog_value = self._read_analog(self.analog_pin, force_read=True)
                test_spi.close()
                if old_spi:
                    self.spi = old_spi
                if analog_value is not None and 0 <= analog_value <= 1023:
                    # Real hardware detected! Switch to real mode
                    self.use_simulation = False
                    self.spi = spidev.SpiDev()
                    self.spi.open(0, 0)
                    self.connected = True
                    print(f"[REAL] Moisture sensor detected and connected on analog pin A{self.analog_pin}")
                    # Read actual value
                    analog_value = self._read_analog(self.analog_pin)
                    voltage = (analog_value / 1023.0) * 3.3
                    self.moisture_percentage = round((voltage / 3.3) * 100, 1)
                    self.moisture_raw = analog_value
                    self.last_reading_time = datetime.now()
                    return self.moisture_percentage, self.moisture_raw
            except:
                # No real hardware, continue with simulation
                pass
            
            # Simulate realistic soil moisture values
            # Moisture: 0-100% (0% = dry, 100% = waterlogged)
            # Typical garden soil: 20-60%
            self.moisture_percentage = round(random.uniform(25.0, 65.0), 1)
            # Raw value: 0-1023 (ADC range)
            self.moisture_raw = round((self.moisture_percentage / 100.0) * 1023, 0)
        else:
            try:
                # Read analog value
                analog_value = self._read_analog(self.analog_pin)
                if analog_value is None:
                    # Failed to read - mark as disconnected
                    if self.connected:
                        self.connected = False
                        print(f"[WARNING] Moisture sensor disconnected")
                    return None, None
                
                # Update connection status on successful read
                if not self.connected:
                    self.connected = True
                    print(f"[REAL] Moisture sensor connected on analog pin A{self.analog_pin}")
                
                # Convert to voltage (0-3.3V for MCP3008 with 3.3V reference)
                voltage = (analog_value / 1023.0) * 3.3
                
                # Moisture sensor calibration (simplified)
                # Higher voltage = more moisture (lower resistance)
                # Typical range: 0-3.3V maps to 0-100% moisture
                self.moisture_percentage = round((voltage / 3.3) * 100, 1)
                self.moisture_raw = analog_value
            except Exception as e:
                print(f"[ERROR] Moisture sensor read failed: {e}")
                # Mark as disconnected on error
                if self.connected:
                    self.connected = False
                    print(f"[WARNING] Moisture sensor disconnected due to error")
                return None, None
        
        self.last_reading_time = datetime.now()
        return self.moisture_percentage, self.moisture_raw
    
    def get_status(self):
        """Get sensor connection status and last reading"""
        return {
            'connected': self.connected,
            'sensor_type': 'Moisture',
            'analog_pin': f'A{self.analog_pin}',
            'mode': 'Simulation' if self.use_simulation else 'Real Sensor',
            'moisture_percentage': self.moisture_percentage,
            'moisture_raw': self.moisture_raw,
            'last_reading': self.last_reading_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_reading_time else 'Never'
        }

# Global Moisture sensor instance
print("\n" + "="*50)
print("INITIALIZING MOISTURE SENSOR")
print("="*50)
moisture_sensor = MoistureSensor(analog_pin=2, use_simulation=True)
print("="*50 + "\n")

