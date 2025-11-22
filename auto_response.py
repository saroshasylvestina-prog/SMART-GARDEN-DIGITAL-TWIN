"""
Automated Plant Response System
Automatically responds to sensor conditions by controlling the pump
"""
from pump_control import pump
from datetime import datetime
import time
import threading

# Import Telegram notifier (will be None if not configured)
try:
    from telegram_notifier import telegram
except ImportError:
    telegram = None

class AutoResponse:
    """Automated response system for plant care"""
    
    def __init__(self, enabled=True):
        """
        Initialize auto-response system
        
        Args:
            enabled: If True, auto-responses are active
        """
        self.enabled = enabled
        self.running = False
        self.response_thread = None
        self.last_moisture_response = None
        self.last_temperature_response = None
        self.response_cooldown = 300  # 5 minutes between same type of responses
        
        # Response thresholds
        self.moisture_low_threshold = 30  # Turn pump ON if below this
        self.moisture_high_threshold = 80  # Turn pump OFF if above this
        self.temperature_high_threshold = 30  # Turn pump ON if above this (cooling)
        self.pump_duration_seconds = 60  # Run pump for 60 seconds when auto-triggered
        
        print(f"[AUTO-RESPONSE] Initialized (Enabled: {self.enabled})")
    
    def check_and_respond(self, temp, humidity, moisture_percentage):
        """
        Check sensor conditions and respond automatically
        
        Args:
            temp: Temperature in Celsius
            humidity: Humidity percentage
            moisture_percentage: Soil moisture percentage
        """
        if not self.enabled:
            return
        
        now = datetime.now()
        responses = []
        
        # 1. MOISTURE RESPONSE: Low moisture (dry) = Turn pump ON for 1 second
        if moisture_percentage is not None:
            if moisture_percentage < self.moisture_low_threshold:
                # Check cooldown
                if (self.last_moisture_response is None or 
                    (now - self.last_moisture_response).total_seconds() > self.response_cooldown):
                    
                    print(f"[AUTO-RESPONSE] Low moisture (dry) detected ({moisture_percentage}% < {self.moisture_low_threshold}%)")
                    print(f"[AUTO-RESPONSE] Turning pump ON for exactly 2.0 seconds")
                    # Turn on for exactly 2.0 seconds when soil is dry
                    # Ensure any previous timer is cancelled first
                    if pump.auto_off_timer is not None:
                        pump.auto_off_timer.cancel()
                        pump.auto_off_timer = None
                    pump.turn_on_for_duration(2.0)
                    print(f"[AUTO-RESPONSE] Pump should turn OFF automatically in 2.0 seconds")
                    self.last_moisture_response = now
                    responses.append({
                        'type': 'moisture_low',
                        'action': 'pump_on',
                        'reason': f'Moisture too low (dry): {moisture_percentage}%',
                        'duration': 2.0
                    })
                    
                    # Send Telegram notification
                    if telegram and telegram.enabled:
                        telegram.send_auto_response(
                            'moisture_low',
                            'pump_on',
                            f'Moisture too low (dry): {moisture_percentage}%',
                            2.0
                        )
            
            elif moisture_percentage > self.moisture_high_threshold:
                # High moisture = Turn pump OFF (if it was auto-turned on)
                if pump.is_on:
                    print(f"[AUTO-RESPONSE] High moisture detected ({moisture_percentage}% > {self.moisture_high_threshold}%)")
                    print(f"[AUTO-RESPONSE] Turning pump OFF")
                    pump.turn_off()
                    responses.append({
                        'type': 'moisture_high',
                        'action': 'pump_off',
                        'reason': f'Moisture too high: {moisture_percentage}%'
                    })
                    
                    # Send Telegram notification
                    if telegram and telegram.enabled:
                        telegram.send_auto_response(
                            'moisture_high',
                            'pump_off',
                            f'Moisture too high: {moisture_percentage}%'
                        )
        
        # 2. TEMPERATURE RESPONSE: High temperature = Turn pump ON (cooling)
        # Note: Temperature response disabled per requirements - only manual button and dry soil trigger pump
        # Keeping code structure but not executing automatic temperature response
        if temp is not None:
            if temp > self.temperature_high_threshold:
                # Check cooldown
                if (self.last_temperature_response is None or 
                    (now - self.last_temperature_response).total_seconds() > self.response_cooldown):
                    
                    # Temperature-based auto-response disabled per requirements
                    # Pump should only turn on for dry soil (1 second) or manual button (0.25 seconds)
                    pass
        
        return responses
    
    def _auto_pump_off(self, reason):
        """Automatically turn pump off after duration"""
        # This method is no longer needed as turn_on_for_duration handles auto-turn-off
        # Keeping for backward compatibility but it's handled by PumpControl now
        if pump.is_on:
            print(f"[AUTO-RESPONSE] Auto-turning pump OFF (Reason: {reason})")
            pump.turn_off()
    
    def _monitor_and_respond(self):
        """Background thread to monitor sensors and respond"""
        from sensor import sensor, moisture_sensor
        
        while self.running:
            try:
                # Read sensors
                temp, humidity = sensor.read_sensor()
                moisture_percentage, _ = moisture_sensor.read_sensor()
                
                # Check and respond
                self.check_and_respond(temp, humidity, moisture_percentage)
                
            except Exception as e:
                print(f"[AUTO-RESPONSE ERROR] {e}")
            
            time.sleep(30)  # Check every 30 seconds
    
    def start(self):
        """Start the auto-response monitoring"""
        if not self.running and self.enabled:
            self.running = True
            self.response_thread = threading.Thread(target=self._monitor_and_respond, daemon=True)
            self.response_thread.start()
            print("[AUTO-RESPONSE] Started monitoring")
    
    def stop(self):
        """Stop the auto-response monitoring"""
        self.running = False
        if self.response_thread:
            self.response_thread.join(timeout=2)
        print("[AUTO-RESPONSE] Stopped monitoring")
    
    def get_status(self):
        """Get auto-response status"""
        return {
            'enabled': self.enabled,
            'running': self.running,
            'moisture_low_threshold': self.moisture_low_threshold,
            'moisture_high_threshold': self.moisture_high_threshold,
            'temperature_high_threshold': self.temperature_high_threshold,
            'pump_duration_seconds': self.pump_duration_seconds,
            'last_moisture_response': self.last_moisture_response.strftime('%Y-%m-%d %H:%M:%S') if self.last_moisture_response else None,
            'last_temperature_response': self.last_temperature_response.strftime('%Y-%m-%d %H:%M:%S') if self.last_temperature_response else None
        }
    
    def set_enabled(self, enabled):
        """Enable or disable auto-responses"""
        self.enabled = enabled
        if enabled and not self.running:
            self.start()
        elif not enabled and self.running:
            self.stop()
        print(f"[AUTO-RESPONSE] {'Enabled' if enabled else 'Disabled'}")

# Global auto-response instance
auto_response = AutoResponse(enabled=True)
auto_response.start()

