"""
Telegram Notification System for Smart Garden Digital Twin
Sends plant status updates, alerts, and automated response notifications to Telegram
"""
import requests
import json
from datetime import datetime

class TelegramNotifier:
    """Telegram bot notification handler"""
    
    def __init__(self, bot_token=None, chat_id=None, enabled=True):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token (get from @BotFather)
            chat_id: Telegram chat ID (user or group)
            enabled: If True, notifications are active
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = enabled and bot_token and chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}" if bot_token else None
        self.last_notification_time = {}
        self.notification_cooldown = 300  # 5 minutes between same type of notifications
        
        if self.enabled:
            print(f"[TELEGRAM] Notifier initialized (Chat ID: {chat_id})")
        else:
            print(f"[TELEGRAM] Notifier disabled (missing token or chat_id)")
    
    def send_message(self, message, parse_mode='HTML'):
        """
        Send a message to Telegram
        
        Args:
            message: Message text to send
            parse_mode: 'HTML' or 'Markdown'
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.base_url:
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"[TELEGRAM ERROR] Failed to send message: {e}")
            return False
    
    def send_alert(self, alert_type, message, value=None, threshold=None):
        """
        Send an alert notification
        
        Args:
            alert_type: Type of alert (temperature, moisture, etc.)
            message: Alert message
            value: Current sensor value
            threshold: Threshold value
        """
        if not self.enabled:
            return
        
        # Check cooldown
        now = datetime.now()
        alert_key = f"alert_{alert_type}"
        if (alert_key in self.last_notification_time and 
            (now - self.last_notification_time[alert_key]).total_seconds() < self.notification_cooldown):
            return
        
        # Format message
        emoji_map = {
            'temperature': '🌡️',
            'humidity': '💧',
            'moisture': '🌱',
            'light': '☀️',
            'air_quality': '🌬️',
            'co2': '💨'
        }
        
        emoji = emoji_map.get(alert_type, '⚠️')
        formatted_message = f"{emoji} <b>Plant Alert!</b>\n\n"
        formatted_message += f"{message}\n\n"
        if value is not None:
            formatted_message += f"Current: {value}"
            if threshold is not None:
                formatted_message += f" (Threshold: {threshold})"
        
        if self.send_message(formatted_message):
            self.last_notification_time[alert_key] = now
    
    def send_auto_response(self, response_type, action, reason, duration=None):
        """
        Send automated response notification
        
        Args:
            response_type: Type of response (moisture_low, temperature_high, etc.)
            action: Action taken (pump_on, pump_off)
            reason: Reason for action
            duration: Duration in seconds (if applicable)
        """
        if not self.enabled:
            return
        
        # Format message
        emoji = '🤖' if action == 'pump_on' else '⏸️'
        formatted_message = f"{emoji} <b>Automated Plant Response</b>\n\n"
        formatted_message += f"<b>Action:</b> Pump {'ON' if action == 'pump_on' else 'OFF'}\n"
        formatted_message += f"<b>Reason:</b> {reason}\n"
        
        if duration:
            formatted_message += f"<b>Duration:</b> {duration} seconds\n"
        
        formatted_message += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        self.send_message(formatted_message)
    
    def send_status_summary(self, sensor_data):
        """
        Send a status summary of all sensors
        
        Args:
            sensor_data: Dictionary with sensor readings
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        message = "🌿 <b>Plant Status Summary</b>\n\n"
        
        # Temperature & Humidity
        if 'temperature' in sensor_data and sensor_data.get('temperature') is not None:
            temp = sensor_data.get('temperature')
            message += f"🌡️ <b>Temperature:</b> {temp}°C\n"
        
        if 'humidity' in sensor_data and sensor_data.get('humidity') is not None:
            humidity = sensor_data.get('humidity')
            message += f"💧 <b>Humidity:</b> {humidity}%\n\n"
        
        # Moisture
        if 'moisture_percentage' in sensor_data and sensor_data.get('moisture_percentage') is not None:
            moisture = sensor_data.get('moisture_percentage')
            status = "🟢 Good" if 20 <= moisture <= 80 else "🟡 Low" if moisture < 20 else "🔴 High"
            message += f"🌱 <b>Soil Moisture:</b> {moisture}% {status}\n\n"
        
        # Light
        if 'light_intensity' in sensor_data and sensor_data.get('light_intensity') is not None:
            light = sensor_data.get('light_intensity')
            message += f"☀️ <b>Light:</b> {light} lux\n\n"
        
        # Air Quality
        if 'air_quality' in sensor_data and sensor_data.get('air_quality') is not None:
            aqi = sensor_data.get('air_quality')
            status = "🟢 Good" if aqi <= 50 else "🟡 Moderate" if aqi <= 100 else "🔴 Poor"
            message += f"🌬️ <b>Air Quality:</b> {aqi} AQI {status}\n\n"
        
        message += f"<i>Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return self.send_message(message)
    
    def send_daily_report(self, sensor_data, alerts_count=0, auto_responses_count=0):
        """
        Send a daily summary report
        
        Args:
            sensor_data: Dictionary with sensor readings
            alerts_count: Number of alerts today
            auto_responses_count: Number of auto-responses today
        """
        if not self.enabled:
            return
        
        message = "📊 <b>Daily Plant Report</b>\n\n"
        message += self._format_sensor_data(sensor_data)
        message += f"\n⚠️ <b>Alerts Today:</b> {alerts_count}\n"
        message += f"🤖 <b>Auto-Responses:</b> {auto_responses_count}\n"
        message += f"\n<i>Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        self.send_message(message)
    
    def _format_sensor_data(self, sensor_data):
        """Format sensor data for messages"""
        text = ""
        if 'temperature' in sensor_data:
            text += f"🌡️ Temperature: {sensor_data['temperature']}°C\n"
        if 'humidity' in sensor_data:
            text += f"💧 Humidity: {sensor_data['humidity']}%\n"
        if 'moisture_percentage' in sensor_data:
            text += f"🌱 Moisture: {sensor_data['moisture_percentage']}%\n"
        if 'light_intensity' in sensor_data:
            text += f"☀️ Light: {sensor_data['light_intensity']} lux\n"
        if 'air_quality' in sensor_data:
            text += f"🌬️ Air Quality: {sensor_data['air_quality']} AQI\n"
        return text
    
    def test_connection(self):
        """Test Telegram bot connection"""
        if not self.enabled:
            return False
        
        test_message = "🤖 <b>Smart Garden Bot Test</b>\n\n"
        test_message += "If you receive this message, your Telegram integration is working!"
        test_message += f"\n\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return self.send_message(test_message)

# Global Telegram notifier instance
# Bot token is set as constant
BOT_TOKEN = "8525417557:AAFlmGdtVRbAr1RTY4msMSgDgnxXuveR8yk"

# Chat ID can be set via environment variable or web interface
import os
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', None)

telegram = TelegramNotifier(
    bot_token=BOT_TOKEN,
    chat_id=CHAT_ID,
    enabled=True if BOT_TOKEN and CHAT_ID else False
)

