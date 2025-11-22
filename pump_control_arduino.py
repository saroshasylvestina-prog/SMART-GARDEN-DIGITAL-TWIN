"""
Pump Control Module for Arduino via Serial Communication
Controls water pump connected to Arduino pin 8 via serial commands
"""
import time
import threading
from datetime import datetime
import serial
import serial.tools.list_ports

class PumpControlArduino:
    """Water pump controller via Arduino serial communication"""
    
    def __init__(self, port=None, baudrate=9600, pin=8, active_low=True):
        """
        Initialize pump control via Arduino
        
        Args:
            port: Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
                 If None, will auto-detect
            baudrate: Serial communication speed (default: 9600)
            pin: GPIO pin number on Arduino (default 8)
            active_low: If True, relay is active-low (LOW = ON, HIGH = OFF)
        """
        self.port = port
        self.baudrate = baudrate
        self.pin = pin
        self.active_low = active_low
        self.is_on = False
        self.last_state_change = None
        self.auto_off_timer = None
        self.default_duration = 2.0
        self.serial_connection = None
        self.use_simulation = False
        self.connection_check_thread = None
        self.connection_check_running = False
        self.last_connection_check = None
        
        # Try to find and connect to Arduino
        if port is None:
            port = self._find_arduino_port()
        
        # Store the port we're trying to use
        self.target_port = port
        
        if port:
            # Try to connect with retry logic
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    print(f"[ARDUINO] Attempting to connect to {port} (attempt {attempt + 1}/{max_retries})...")
                    
                    # Try to close port if it's already open (might be from previous session)
                    try:
                        temp_ser = serial.Serial(port, baudrate, timeout=0.1)
                        temp_ser.close()
                        time.sleep(0.5)
                    except:
                        pass  # Port might not be open, that's OK
                    
                    self.serial_connection = serial.Serial(
                        port, 
                        baudrate, 
                        timeout=1,
                        write_timeout=1,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE
                    )
                    time.sleep(2)  # Wait for Arduino to initialize
                    
                    # Clear any existing data
                    self.serial_connection.reset_input_buffer()
                    self.serial_connection.reset_output_buffer()
                    
                    print(f"[ARDUINO] Connected to {port} at {baudrate} baud")
                    print(f"[ARDUINO] Pump control initialized on pin {self.pin}")
                    print(f"[ARDUINO] Relay type: {'active-low' if self.active_low else 'active-high'}")
                    
                    # Read any startup messages from Arduino
                    time.sleep(0.5)
                    startup_messages = []
                    for _ in range(5):  # Read up to 5 startup lines
                        if self.serial_connection.in_waiting > 0:
                            try:
                                msg = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                                if msg:
                                    startup_messages.append(msg)
                            except:
                                break
                        time.sleep(0.1)
                    
                    if startup_messages:
                        print(f"[ARDUINO] Startup messages:")
                        for msg in startup_messages:
                                    print(f"  -> {msg}")
                    
                    # Ensure pump is OFF at startup
                    self.turn_off()
                    
                    # Success! Break out of retry loop
                    break
                    
                except serial.SerialException as e:
                    error_msg = str(e)
                    if "Access is denied" in error_msg or "PermissionError" in error_msg:
                        if attempt < max_retries - 1:
                            print(f"[ARDUINO] Port {port} is busy (likely Arduino Serial Monitor is open)")
                            print(f"[ARDUINO] Waiting {retry_delay} seconds before retry...")
                            print(f"[ARDUINO] -> Please CLOSE Arduino Serial Monitor if it's open!")
                            time.sleep(retry_delay)
                            continue
                        else:
                            print(f"[ARDUINO ERROR] Port {port} is still busy after {max_retries} attempts")
                            print(f"[ARDUINO] SOLUTION:")
                            print(f"  1. Close Arduino IDE Serial Monitor")
                            print(f"  2. Close any other programs using {port}")
                            print(f"  3. Restart this application")
                            print(f"[ARDUINO] Using simulation mode for now")
                            self.use_simulation = True
                            self.serial_connection = None
                            break
                    else:
                        print(f"[ARDUINO ERROR] Serial port error: {e}")
                        if attempt < max_retries - 1:
                            print(f"[ARDUINO] Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            print(f"[ARDUINO] Using simulation mode")
                            self.use_simulation = True
                            self.serial_connection = None
                            break
                            
                except Exception as e:
                    print(f"[ARDUINO ERROR] Failed to connect: {e}")
                    if attempt < max_retries - 1:
                        print(f"[ARDUINO] Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        import traceback
                        traceback.print_exc()
                        print(f"[ARDUINO] Using simulation mode")
                        self.use_simulation = True
                        self.serial_connection = None
                        break
        else:
            print(f"[ARDUINO] No Arduino found - using simulation mode")
            self.use_simulation = True
        
        # Start periodic connection checking
        self._start_connection_checking()
    
    def _find_arduino_port(self):
        """Auto-detect Arduino serial port"""
        ports = serial.tools.list_ports.comports()
        
        # First, check if COM5 exists (user preference)
        for port in ports:
            if port.device.upper() == 'COM5':
                print(f"[ARDUINO] Found COM5: {port.device} - {port.description}")
                return port.device
        
        # If COM5 not found, try auto-detect
        for port in ports:
            # Common Arduino identifiers
            if any(keyword in port.description.upper() for keyword in 
                   ['ARDUINO', 'USB SERIAL', 'CH340', 'CP210', 'FTDI']):
                print(f"[ARDUINO] Found potential Arduino: {port.device} - {port.description}")
                return port.device
        
        # If no Arduino found, list all ports
        if ports:
            print("[ARDUINO] Available serial ports:")
            for port in ports:
                print(f"  - {port.device}: {port.description}")
        else:
            print("[ARDUINO] No serial ports found")
        
        return None
    
    def _check_connection(self):
        """Check if Arduino is actually connected and responsive"""
        # Check if target port exists in system
        if self.target_port is None:
            if not self.use_simulation:
                print(f"[ARDUINO CHECK] No target port - switching to simulation")
                self.use_simulation = True
                self.serial_connection = None
            return False
        
        # Check if port exists in available ports
        available_ports = [p.device for p in serial.tools.list_ports.comports()]
        port_exists = self.target_port in available_ports
        
        if not port_exists:
            # Port no longer exists - disconnect
            if not self.use_simulation:
                print(f"[ARDUINO CHECK] Port {self.target_port} not found - switching to simulation")
                if self.serial_connection and self.serial_connection.is_open:
                    try:
                        self.serial_connection.close()
                    except:
                        pass
                self.use_simulation = True
                self.serial_connection = None
            return False
        
        # Port exists - check if we have an active connection
        if self.serial_connection is None or not self.serial_connection.is_open:
            # Try to reconnect (non-blocking, quick check)
            try:
                # Quick connection test - don't wait long
                test_connection = serial.Serial(
                    self.target_port,
                    self.baudrate,
                    timeout=0.5,
                    write_timeout=0.5
                )
                time.sleep(0.3)  # Brief wait
                test_connection.reset_input_buffer()
                test_connection.reset_output_buffer()
                
                # Quick test - send STATUS and check for response
                test_connection.write(b"STATUS\n")
                test_connection.flush()
                time.sleep(0.3)
                
                # If we got any response, connection is good
                if test_connection.in_waiting > 0 or test_connection.is_open:
                    # Connection is good - use it
                    if self.serial_connection:
                        try:
                            self.serial_connection.close()
                        except:
                            pass
                    self.serial_connection = test_connection
                    self.use_simulation = False
                    print(f"[ARDUINO CHECK] Reconnected to {self.target_port}")
                    return True
                else:
                    # No response - close test connection
                    try:
                        test_connection.close()
                    except:
                        pass
                    self.use_simulation = True
                    self.serial_connection = None
                    return False
            except (serial.SerialException, OSError) as e:
                # Port might be busy or not responding
                self.use_simulation = True
                self.serial_connection = None
                return False
            except Exception as e:
                print(f"[ARDUINO CHECK] Reconnection error: {e}")
                self.use_simulation = True
                self.serial_connection = None
                return False
        else:
            # Connection exists - verify it's still responsive (quick check)
            try:
                if self.serial_connection.is_open:
                    # Quick test - just check if port is still open
                    # Don't send command to avoid blocking
                    self.use_simulation = False
                    return True
                else:
                    self.use_simulation = True
                    return False
            except (serial.SerialException, OSError) as e:
                print(f"[ARDUINO CHECK] Connection lost: {e}")
                try:
                    self.serial_connection.close()
                except:
                    pass
                self.serial_connection = None
                self.use_simulation = True
                return False
    
    def _start_connection_checking(self):
        """Start background thread to periodically check connection"""
        if self.connection_check_thread is None or not self.connection_check_thread.is_alive():
            self.connection_check_running = True
            self.connection_check_thread = threading.Thread(target=self._connection_check_loop, daemon=True)
            self.connection_check_thread.start()
            print(f"[ARDUINO] Started connection checking thread")
    
    def _connection_check_loop(self):
        """Background loop to periodically check Arduino connection"""
        while self.connection_check_running:
            try:
                self.last_connection_check = datetime.now()
                was_connected = not self.use_simulation
                is_connected = self._check_connection()
                
                if was_connected != is_connected:
                    if is_connected:
                        print(f"[ARDUINO CHECK] Connection restored to {self.target_port}")
                    else:
                        print(f"[ARDUINO CHECK] Connection lost - using simulation mode")
            except Exception as e:
                print(f"[ARDUINO CHECK ERROR] Connection check failed: {e}")
            
            # Check every 5 seconds
            time.sleep(5)
    
    def _send_command(self, command):
        """Send command to Arduino via serial"""
        if self.use_simulation or self.serial_connection is None:
            print(f"[ARDUINO SIMULATION] Command: {command}")
            return True
        
        try:
            if not self.serial_connection.is_open:
                self.serial_connection.open()
                time.sleep(0.5)  # Wait for connection to stabilize
            
            # Clear any existing data in buffer
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()
            
            # Send command with newline
            command_bytes = f"{command}\n".encode('utf-8')
            bytes_written = self.serial_connection.write(command_bytes)
            self.serial_connection.flush()
            
            print(f"[ARDUINO] Sent command: '{command}' ({bytes_written} bytes)")
            
            # Wait a bit for Arduino to process
            time.sleep(0.2)
            
            # Read all available responses
            responses = []
            max_wait = 0.5  # Maximum time to wait for response
            start_time = time.time()
            
            while (time.time() - start_time) < max_wait:
                if self.serial_connection.in_waiting > 0:
                    try:
                        line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            responses.append(line)
                            print(f"[ARDUINO] Response: {line}")
                    except Exception as e:
                        print(f"[ARDUINO] Error reading response: {e}")
                
                # If we got a response, check if it's complete
                if responses and ("PUMP:ON" in responses[-1] or "PUMP:OFF" in responses[-1] or "ERROR" in responses[-1]):
                    break
                
                time.sleep(0.05)  # Small delay between reads
            
            # Check if we got a valid response
            if responses:
                last_response = responses[-1]
                if "ERROR" in last_response.upper():
                    print(f"[ARDUINO] Arduino returned error: {last_response}")
                    return False
                elif "PUMP:ON" in last_response or "PUMP:OFF" in last_response:
                    return True
                else:
                    # Got some response, assume success
                    return True
            else:
                print(f"[ARDUINO WARNING] No response from Arduino for command: {command}")
                print(f"[ARDUINO] This might be OK if Arduino is processing the command")
                # Still return True - command might have been processed even without response
                return True
            
        except serial.SerialException as e:
            print(f"[ARDUINO ERROR] Serial port error: {e}")
            print(f"[ARDUINO] Try: Close Arduino Serial Monitor, restart Python app")
            return False
        except Exception as e:
            print(f"[ARDUINO ERROR] Serial communication failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def turn_on(self):
        """Turn the pump ON"""
        try:
            result = self._send_command("ON")
            if result:
                self.is_on = True
                self.last_state_change = datetime.now()
                print(f"[PUMP] Turned ON via Arduino")
                return True
            else:
                print(f"[PUMP] Failed to turn ON - Arduino error")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to turn pump ON: {e}")
            return False
    
    def turn_off(self):
        """Turn the pump OFF"""
        try:
            # Cancel any pending auto-off timer
            if self.auto_off_timer is not None:
                self.auto_off_timer.cancel()
                self.auto_off_timer = None
            
            print(f"[PUMP] Turn OFF called at: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
            result = self._send_command("OFF")
            if result:
                self.is_on = False
                self.last_state_change = datetime.now()
                print(f"[PUMP] Turned OFF via Arduino")
                return True
            else:
                print(f"[PUMP] Failed to turn OFF - Arduino error")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to turn pump OFF: {e}")
            return False
    
    def turn_on_for_duration(self, duration_seconds):
        """Turn pump ON for a specific duration, then automatically turn OFF"""
        # Cancel any existing timer first
        if self.auto_off_timer is not None:
            self.auto_off_timer.cancel()
            self.auto_off_timer = None
        
        # Ensure duration is exactly what was requested (no rounding)
        duration_seconds = float(duration_seconds)
        
        result = self.turn_on()
        if result:
            # Create timer with exact duration
            self.auto_off_timer = threading.Timer(duration_seconds, self.turn_off)
            self.auto_off_timer.start()
            print(f"[PUMP] Scheduled auto-turn-off in exactly {duration_seconds} seconds")
            print(f"[PUMP] Timer started at: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        return result
    
    def set_duration(self, duration_seconds):
        """Set default pump duration"""
        if duration_seconds > 0:
            self.default_duration = float(duration_seconds)
            print(f"[PUMP] Default duration set to {self.default_duration} seconds")
            return True
        return False
    
    def get_duration(self):
        """Get default pump duration"""
        return self.default_duration
    
    def get_status(self):
        """Get current pump status"""
        # Connection status is updated by background thread, just return current state
        # Don't call _check_connection() here to avoid blocking
        is_connected = (self.serial_connection is not None and 
                       self.serial_connection.is_open and 
                       not self.use_simulation and
                       self.target_port is not None)
        
        return {
            'is_on': self.is_on,
            'pin': self.pin,
            'mode': 'Simulation' if self.use_simulation else 'Arduino Serial',
            'relay_type': 'active-low' if self.active_low else 'active-high',
            'connected': is_connected,
            'port': self.target_port if self.target_port else (self.port if self.port else 'N/A'),
            'last_state_change': self.last_state_change.strftime('%Y-%m-%d %H:%M:%S') if self.last_state_change else 'Never',
            'default_duration': self.default_duration,
            'last_connection_check': self.last_connection_check.strftime('%Y-%m-%d %H:%M:%S') if self.last_connection_check else 'Never'
        }
    
    def __del__(self):
        """Cleanup serial connection"""
        # Stop connection checking thread
        self.connection_check_running = False
        if self.connection_check_thread and self.connection_check_thread.is_alive():
            self.connection_check_thread.join(timeout=1)
        
        # Close serial connection
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.turn_off()  # Ensure pump is OFF
                self.serial_connection.close()
            except:
                pass

