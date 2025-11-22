"""
Pump Control Module for Smart Garden Digital Twin
Controls water pump connected to GPIO pin 8 (Raspberry Pi) or via Arduino Serial (Windows)
"""
import time
import threading
import sys
import platform
from datetime import datetime

# IMMEDIATE FIX: Set pin to OFF state as soon as module loads
# This prevents relay from staying ON during application startup
def _immediate_pin_setup():
    """Set GPIO pin 8 to HIGH immediately to turn relay OFF"""
    try:
        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)
        try:
            GPIO.cleanup()
        except:
            pass
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(8, GPIO.OUT)
        GPIO.output(8, GPIO.HIGH)  # HIGH = OFF for active-low relay
        print("[IMMEDIATE] Pin 8 set to HIGH (Relay OFF) - before initialization")
        # Don't cleanup here - let PumpControl handle it properly
    except:
        pass  # GPIO not available, will be handled in PumpControl

# Call immediately when module loads
_immediate_pin_setup()

class PumpControl:
    """Water pump controller"""
    
    def __init__(self, pin=8, use_simulation=True, active_low=False):
        """
        Initialize pump control
        
        Args:
            pin: GPIO pin number (default 8)
            use_simulation: If True, use simulated control instead of real GPIO
            active_low: If True, relay is active-low (LOW = ON, HIGH = OFF)
                        If False, relay is active-high (HIGH = ON, LOW = OFF)
        """
        self.pin = pin
        self.use_simulation = use_simulation
        self.active_low = active_low  # Relay type: active-low or active-high
        self.is_on = False
        self.last_state_change = None
        self.auto_off_timer = None  # Timer for automatic turn-off
        self.default_duration = 2.0  # Default duration in seconds
        
        # Initialize GPIO if not in simulation mode
        if not self.use_simulation:
            try:
                import RPi.GPIO as GPIO
                # Disable warnings about channel already in use
                GPIO.setwarnings(False)
                # Clean up any previous GPIO setup (important!)
                try:
                    GPIO.cleanup()
                except:
                    pass
                
                GPIO.setmode(GPIO.BCM)
                
                # Set initial state based on relay type
                # For active-low: HIGH = OFF (relay LED off, pump off)
                # For active-high: LOW = OFF (relay LED off, pump off)
                initial_state = GPIO.HIGH if self.active_low else GPIO.LOW
                
                # Setup pin with initial state
                GPIO.setup(self.pin, GPIO.OUT, initial=initial_state)
                
                # Explicitly set the pin state again to ensure it's correct
                GPIO.output(self.pin, initial_state)
                
                # Verify the pin state
                time.sleep(0.2)  # Delay to ensure pin is set
                actual_state = GPIO.input(self.pin)
                
                self.gpio = GPIO
                relay_type = "active-low" if self.active_low else "active-high"
                print(f"[REAL] Pump control initialized on GPIO pin {self.pin} ({relay_type})")
                print(f"[REAL] Initial state: OFF (Pin set to {'HIGH' if self.active_low else 'LOW'})")
                print(f"[REAL] Verified pin state: {actual_state} (0=LOW, 1=HIGH)")
                
                if self.active_low:
                    if actual_state != 1:  # Should be HIGH (1) for OFF
                        print(f"[WARNING] Pin state mismatch! Expected HIGH (1) but got {actual_state}")
                else:
                    if actual_state != 0:  # Should be LOW (0) for OFF
                        print(f"[WARNING] Pin state mismatch! Expected LOW (0) but got {actual_state}")
                        
            except ImportError:
                self.use_simulation = True
                print(f"[SIMULATION] Pump control (RPi.GPIO not available, using simulation)")
            except Exception as e:
                self.use_simulation = True
                print(f"[ERROR] Pump GPIO initialization failed: {e}, using simulation")
                import traceback
                traceback.print_exc()
        else:
            print(f"[SIMULATION] Pump control initialized on pin {self.pin}")
    
    def turn_on(self):
        """Turn the pump ON"""
        try:
            if not self.use_simulation:
                # Re-import GPIO to ensure it's available
                try:
                    import RPi.GPIO as GPIO
                    self.gpio = GPIO
                except ImportError:
                    print(f"[PUMP] ERROR - RPi.GPIO not available")
                    self.is_on = True
                    self.last_state_change = datetime.now()
                    return True
                
                # Ensure GPIO is properly set up (re-initialize if needed)
                try:
                    # Try to read pin - if it fails, we need to re-setup
                    _ = GPIO.input(self.pin)
                except (RuntimeError, ValueError):
                    # Pin not set up, re-initialize
                    print(f"[PUMP] Re-initializing GPIO pin {self.pin}...")
                    GPIO.setwarnings(False)
                    GPIO.setmode(GPIO.BCM)
                    GPIO.setup(self.pin, GPIO.OUT)
                
                # For active-low: LOW = ON, for active-high: HIGH = ON
                pin_state = GPIO.LOW if self.active_low else GPIO.HIGH
                
                # Set the pin state
                GPIO.output(self.pin, pin_state)
                
                # Verify the pin was set correctly (with multiple attempts)
                time.sleep(0.15)  # Small delay for pin to settle
                actual_state = GPIO.input(self.pin)
                expected_state = 0 if self.active_low else 1
                
                # If state doesn't match, try setting it again
                if actual_state != expected_state:
                    print(f"[PUMP] First attempt failed, retrying...")
                    GPIO.output(self.pin, pin_state)
                    time.sleep(0.15)
                    actual_state = GPIO.input(self.pin)
                
                pin_state_str = "LOW" if self.active_low else "HIGH"
                print(f"[PUMP] Turned ON (Pin {self.pin} = {pin_state_str})")
                print(f"[PUMP] Verified pin state: {actual_state} (Expected: {expected_state})")
                
                if actual_state != expected_state:
                    print(f"[WARNING] Pin state mismatch! Expected {expected_state} but got {actual_state}")
                    print(f"[WARNING] Relay might not be activating. Check wiring and relay power.")
                    print(f"[WARNING] Try running: python test_pump_button.py")
                else:
                    print(f"[PUMP] Pin state correct - Relay should be ON")
                    print(f"[PUMP] Green LED should be ON, pump should be running")
            else:
                print(f"[PUMP] SIMULATION MODE - No actual GPIO control")
            
            self.is_on = True
            self.last_state_change = datetime.now()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to turn pump ON: {e}")
            import traceback
            traceback.print_exc()
            # Still update state even if GPIO fails
            self.is_on = True
            self.last_state_change = datetime.now()
            return True
    
    def turn_off(self):
        """Turn the pump OFF"""
        # Cancel any pending auto-off timer
        if self.auto_off_timer is not None:
            self.auto_off_timer.cancel()
            self.auto_off_timer = None
        
        try:
            if not self.use_simulation and hasattr(self, 'gpio'):
                # For active-low: HIGH = OFF, for active-high: LOW = OFF
                pin_state = self.gpio.HIGH if self.active_low else self.gpio.LOW
                self.gpio.output(self.pin, pin_state)
                
                # Verify the pin was set correctly
                time.sleep(0.1)  # Small delay for pin to settle
                actual_state = self.gpio.input(self.pin)
                expected_state = 1 if self.active_low else 0
                
                pin_state_str = "HIGH" if self.active_low else "LOW"
                print(f"[PUMP] Turned OFF (Pin {self.pin} = {pin_state_str})")
                print(f"[PUMP] Verified pin state: {actual_state} (Expected: {expected_state})")
                
                if actual_state != expected_state:
                    print(f"[WARNING] Pin state mismatch! Expected {expected_state} but got {actual_state}")
                else:
                    print(f"[PUMP] Pin state correct - Relay should be OFF")
            else:
                if self.use_simulation:
                    print(f"[PUMP] SIMULATION MODE - No actual GPIO control")
                else:
                    print(f"[PUMP] WARNING - GPIO not initialized properly")
            
            self.is_on = False
            self.last_state_change = datetime.now()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to turn pump OFF: {e}")
            import traceback
            traceback.print_exc()
            # Still update state even if GPIO fails
            self.is_on = False
            self.last_state_change = datetime.now()
            return True
    
    def toggle(self):
        """Toggle pump state"""
        if self.is_on:
            return self.turn_off()
        else:
            return self.turn_on()
    
    def turn_on_for_duration(self, duration_seconds):
        """
        Turn the pump ON for a specific duration, then automatically turn it OFF
        
        Args:
            duration_seconds: Duration in seconds to keep pump ON
        """
        # Cancel any existing timer
        if self.auto_off_timer is not None:
            self.auto_off_timer.cancel()
        
        # Turn pump on
        result = self.turn_on()
        
        if result:
            # Schedule automatic turn-off
            self.auto_off_timer = threading.Timer(duration_seconds, self.turn_off)
            self.auto_off_timer.start()
            print(f"[PUMP] Scheduled auto-turn-off in {duration_seconds} seconds")
        
        return result
    
    def set_duration(self, duration_seconds):
        """
        Set default pump duration
        
        Args:
            duration_seconds: Duration in seconds (default 1.0)
        """
        if duration_seconds > 0:
            self.default_duration = float(duration_seconds)
            print(f"[PUMP] Default duration set to {self.default_duration} seconds")
            return True
        return False
    
    def get_duration(self):
        """Get current default pump duration"""
        return self.default_duration
    
    def get_status(self):
        """Get pump status"""
        return {
            'is_on': self.is_on,
            'pin': self.pin,
            'mode': 'Simulation' if self.use_simulation else 'Real GPIO',
            'relay_type': 'active-low' if self.active_low else 'active-high',
            'connected': True,  # Pump control is always "connected" (available), state is ON/OFF
            'last_state_change': self.last_state_change.strftime('%Y-%m-%d %H:%M:%S') if self.last_state_change else 'Never',
            'default_duration': self.default_duration
        }

# Global pump control instance
# Auto-detect platform: Windows = Arduino Serial, Linux = GPIO
print("\n" + "="*50)
print("INITIALIZING PUMP CONTROL")
print("="*50)

# Check if we're on Windows (use Arduino) or Linux/Raspberry Pi (use GPIO)
if platform.system() == 'Windows':
    # Windows: Use Arduino Serial communication
    try:
        from pump_control_arduino import PumpControlArduino
        # Auto-detect Arduino port (or specify manually: port='COM5')
        pump = PumpControlArduino(port=None, active_low=True)
        print("[INIT] Using Arduino Serial control (Windows)")
    except ImportError:
        print("[WARNING] pump_control_arduino not available, using simulation")
        pump = PumpControl(pin=8, use_simulation=True, active_low=True)
    except Exception as e:
        print(f"[WARNING] Arduino connection failed: {e}, using simulation")
        pump = PumpControl(pin=8, use_simulation=True, active_low=True)
else:
    # Linux/Raspberry Pi: Use GPIO
    # Immediately set pin to OFF state before creating instance (for active-low relay)
    try:
        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)
        try:
            GPIO.cleanup()
        except:
            pass
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(8, GPIO.OUT)
        GPIO.output(8, GPIO.HIGH)  # Set HIGH immediately for active-low (OFF state)
        print("[IMMEDIATE] Pin 8 set to HIGH (Relay OFF) - before pump control initialization")
        GPIO.cleanup()  # Cleanup, will be re-initialized properly in PumpControl
    except:
        pass  # If GPIO not available, continue with normal initialization
    
    pump = PumpControl(pin=8, use_simulation=False, active_low=True)  # Active-LOW relay: LOW=ON, HIGH=OFF
    print("[INIT] Using GPIO control (Raspberry Pi/Linux)")

# Ensure pump is OFF immediately after initialization
if not pump.use_simulation:
    try:
        # Force turn off to ensure correct state
        pump.turn_off()
        print("[IMMEDIATE] Pump forced to OFF state after initialization")
    except:
        pass

print("="*50 + "\n")

