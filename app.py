from flask import Flask, render_template, jsonify, request
from sensor import sensor, mq135_sensor, ldr_sensor, moisture_sensor
from scheduler import scheduler
from auto_response import auto_response
from telegram_notifier import telegram
from plant_disease_detector import plant_detector
import json
import time
import os
from werkzeug.utils import secure_filename

# Import pump control - Use Arduino Serial for Windows
# For Raspberry Pi, use: from pump_control import pump
# For Arduino on Windows, use: from pump_control_arduino import PumpControlArduino

import sys
import platform

# Detect if we're on Windows (likely using Arduino) or Linux (likely Raspberry Pi)
if platform.system() == 'Windows':
    # Use Arduino Serial control for Windows
    try:
        from pump_control_arduino import PumpControlArduino
        # Auto-detect Arduino port, or specify manually: port='COM5'
        pump = PumpControlArduino(port=None, active_low=True)
        print("[APP START] Using Arduino Serial control for pump")
    except ImportError:
        print("[WARNING] pump_control_arduino not available, using simulation")
        from pump_control import pump
        pump.use_simulation = True
else:
    # Use GPIO control for Raspberry Pi/Linux
    from pump_control import pump
    print("[APP START] Using GPIO control for pump")

# Ensure pump is OFF immediately when app starts
if not pump.use_simulation:
    try:
        pump.turn_off()
        print("[APP START] Pump set to OFF state immediately")
    except Exception as e:
        print(f"[APP START] Warning: Could not set pump OFF: {e}")

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    # Read sensor data for display on home page
    temp, humidity = sensor.read_sensor()
    dht_status = sensor.get_status()
    
    # Read MQ135 sensor data
    mq135_sensor.read_sensor()
    mq135_status = mq135_sensor.get_status()
    
    # Read LDR sensor data
    ldr_sensor.read_sensor()
    ldr_status = ldr_sensor.get_status()
    
    # Read Moisture sensor data
    moisture_sensor.read_sensor()
    moisture_status = moisture_sensor.get_status()
    
    # Get pump status
    pump_status = pump.get_status()
    
    # Get scheduler status
    scheduler_status = scheduler.get_status()
    
    # Get auto-response status
    auto_response_status = auto_response.get_status()
    
    return render_template('index.html', sensor_status=dht_status, mq135_status=mq135_status, ldr_status=ldr_status, moisture_status=moisture_status, pump_status=pump_status, scheduler_status=scheduler_status, auto_response_status=auto_response_status)

@app.route("/sensor")
def sensor_status():
    """Display DHT sensor connection status and readings"""
    # Read sensor data
    print("\n" + "="*50)
    print("DHT SENSOR CONNECTION STATUS")
    print("="*50)
    temp, humidity = sensor.read_sensor()
    status = sensor.get_status()
    
    # Print connection details to console
    print(f"Status: {'CONNECTED' if status['connected'] else 'DISCONNECTED'}")
    print(f"Sensor Type: {status['sensor_type']}")
    print(f"Mode: {status['mode']}")
    if temp is not None and humidity is not None:
        print(f"Temperature: {temp}°C")
        print(f"Humidity: {humidity}%")
    print(f"Last Reading: {status['last_reading']}")
    print("="*50 + "\n")
    
    return render_template('sensor.html', sensor_status=status)

@app.route("/api/sensor")
def sensor_api():
    """API endpoint for sensor data (JSON)"""
    sensor.read_sensor()
    status = sensor.get_status()
    return jsonify(status)

@app.route("/api/sensor/read")
def sensor_read():
    """Force a new sensor reading"""
    temp, humidity = sensor.read_sensor()
    status = sensor.get_status()
    if temp is not None and humidity is not None:
        return jsonify({
            'success': True,
            'temperature': temp,
            'humidity': humidity,
            'connected': status['connected'],
            'timestamp': sensor.last_reading_time.strftime('%Y-%m-%d %H:%M:%S') if sensor.last_reading_time else None
        })
    else:
        return jsonify({
            'success': False,
            'connected': status['connected'],
            'error': 'Failed to read sensor'
        }), 500

@app.route("/mq135")
def mq135_status():
    """Display MQ135 sensor connection status and readings"""
    # Read sensor data
    print("\n" + "="*50)
    print("MQ135 SENSOR CONNECTION STATUS")
    print("="*50)
    air_quality, co2, nh3, nox = mq135_sensor.read_sensor()
    status = mq135_sensor.get_status()
    
    # Print connection details to console
    print(f"Status: {'CONNECTED' if status['connected'] else 'DISCONNECTED'}")
    print(f"Sensor Type: {status['sensor_type']}")
    print(f"Analog Pin: {status['analog_pin']}")
    print(f"Mode: {status['mode']}")
    if air_quality is not None:
        print(f"Air Quality Index: {air_quality}")
        print(f"CO2: {co2} ppm")
        print(f"NH3: {nh3} ppm")
        print(f"NOx: {nox} ppm")
    print(f"Last Reading: {status['last_reading']}")
    print("="*50 + "\n")
    
    return render_template('mq135.html', sensor_status=status)

@app.route("/api/mq135")
def mq135_api():
    """API endpoint for MQ135 sensor data (JSON)"""
    mq135_sensor.read_sensor()
    status = mq135_sensor.get_status()
    return jsonify(status)

@app.route("/api/mq135/read")
def mq135_read():
    """Force a new MQ135 sensor reading"""
    air_quality, co2, nh3, nox = mq135_sensor.read_sensor()
    status = mq135_sensor.get_status()
    if air_quality is not None:
        return jsonify({
            'success': True,
            'air_quality': air_quality,
            'co2_ppm': co2,
            'nh3_ppm': nh3,
            'nox_ppm': nox,
            'connected': status['connected'],
            'timestamp': mq135_sensor.last_reading_time.strftime('%Y-%m-%d %H:%M:%S') if mq135_sensor.last_reading_time else None
        })
    else:
        return jsonify({
            'success': False,
            'connected': status['connected'],
            'error': 'Failed to read MQ135 sensor'
        }), 500

@app.route("/ldr")
def ldr_status():
    """Display LDR sensor connection status and readings"""
    # Read sensor data
    print("\n" + "="*50)
    print("LDR SENSOR CONNECTION STATUS")
    print("="*50)
    light_intensity, light_percentage = ldr_sensor.read_sensor()
    status = ldr_sensor.get_status()
    
    # Print connection details to console
    print(f"Status: {'CONNECTED' if status['connected'] else 'DISCONNECTED'}")
    print(f"Sensor Type: {status['sensor_type']}")
    print(f"Analog Pin: {status['analog_pin']}")
    print(f"Mode: {status['mode']}")
    if light_intensity is not None:
        print(f"Light Intensity: {light_intensity} lux")
        print(f"Light Percentage: {light_percentage}%")
    print(f"Last Reading: {status['last_reading']}")
    print("="*50 + "\n")
    
    return render_template('ldr.html', sensor_status=status)

@app.route("/api/ldr")
def ldr_api():
    """API endpoint for LDR sensor data (JSON)"""
    ldr_sensor.read_sensor()
    status = ldr_sensor.get_status()
    return jsonify(status)

@app.route("/api/ldr/read")
def ldr_read():
    """Force a new LDR sensor reading"""
    light_intensity, light_percentage = ldr_sensor.read_sensor()
    status = ldr_sensor.get_status()
    if light_intensity is not None:
        return jsonify({
            'success': True,
            'light_intensity': light_intensity,
            'light_percentage': light_percentage,
            'connected': status['connected'],
            'timestamp': ldr_sensor.last_reading_time.strftime('%Y-%m-%d %H:%M:%S') if ldr_sensor.last_reading_time else None
        })
    else:
        return jsonify({
            'success': False,
            'connected': status['connected'],
            'error': 'Failed to read LDR sensor'
        }), 500

@app.route("/moisture")
def moisture_status():
    """Display Moisture sensor connection status and readings"""
    # Read sensor data
    print("\n" + "="*50)
    print("MOISTURE SENSOR CONNECTION STATUS")
    print("="*50)
    moisture_percentage, moisture_raw = moisture_sensor.read_sensor()
    status = moisture_sensor.get_status()
    
    # Print connection details to console
    print(f"Status: {'CONNECTED' if status['connected'] else 'DISCONNECTED'}")
    print(f"Sensor Type: {status['sensor_type']}")
    print(f"Analog Pin: {status['analog_pin']}")
    print(f"Mode: {status['mode']}")
    if moisture_percentage is not None:
        print(f"Moisture: {moisture_percentage}%")
        print(f"Raw Value: {moisture_raw}")
    print(f"Last Reading: {status['last_reading']}")
    print("="*50 + "\n")
    
    return render_template('moisture.html', sensor_status=status)

@app.route("/api/moisture")
def moisture_api():
    """API endpoint for Moisture sensor data (JSON)"""
    moisture_sensor.read_sensor()
    status = moisture_sensor.get_status()
    return jsonify(status)

@app.route("/api/moisture/read")
def moisture_read():
    """Force a new Moisture sensor reading"""
    moisture_percentage, moisture_raw = moisture_sensor.read_sensor()
    status = moisture_sensor.get_status()
    if moisture_percentage is not None:
        return jsonify({
            'success': True,
            'moisture_percentage': moisture_percentage,
            'moisture_raw': moisture_raw,
            'connected': status['connected'],
            'timestamp': moisture_sensor.last_reading_time.strftime('%Y-%m-%d %H:%M:%S') if moisture_sensor.last_reading_time else None
        })
    else:
        return jsonify({
            'success': False,
            'connected': status['connected'],
            'error': 'Failed to read Moisture sensor'
        }), 500

@app.route("/api/pump/status")
def pump_status_api():
    """Get pump status"""
    status = pump.get_status()
    return jsonify(status)

@app.route("/api/pump/duration", methods=['POST'])
def set_pump_duration():
    """Set pump duration in seconds"""
    data = request.get_json() or {}
    duration = data.get('duration', 1.0)
    
    try:
        duration = float(duration)
        if duration <= 0:
            return jsonify({
                'success': False,
                'error': 'Duration must be greater than 0'
            }), 400
        
        result = pump.set_duration(duration)
        if result:
            return jsonify({
                'success': True,
                'duration': pump.get_duration(),
                'message': f'Pump duration set to {duration} seconds'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to set duration'
            }), 500
    except (ValueError, TypeError):
        return jsonify({
            'success': False,
            'error': 'Invalid duration value'
        }), 400

@app.route("/api/pump/on", methods=['POST'])
def pump_on():
    """Turn pump ON for configured duration"""
    print("\n" + "="*60)
    print("API CALL: /api/pump/on")
    print("="*60)
    
    try:
        data = request.get_json() or {}
        print(f"Request data: {data}")
        duration = data.get('duration', pump.get_duration())  # Use provided duration or default
        
        # Validate duration
        try:
            duration = float(duration)
            if duration <= 0:
                duration = pump.get_duration()
                print(f"Invalid duration, using default: {duration}")
        except (ValueError, TypeError):
            duration = pump.get_duration()
            print(f"Duration parse error, using default: {duration}")
        
        print(f"Final duration: {duration} seconds")
        print(f"Pump simulation mode: {pump.use_simulation}")
        print(f"Pump active_low: {pump.active_low}")
        
        print("\n" + "-"*60)
        print(f"ATTEMPTING TO TURN PUMP ON ({duration} seconds)")
        print("-"*60)
        
        # Turn on for specified duration
        result = pump.turn_on_for_duration(duration)
        
        print("-"*60)
        print("PUMP CONTROL RESULT")
        print("-"*60)
        
        status = pump.get_status()
        print(f"Pump Status: {'ON' if status['is_on'] else 'OFF'}")
        print(f"GPIO Pin: {status['pin']}")
        print(f"Mode: {status['mode']}")
        print(f"Relay Type: {status.get('relay_type', 'unknown')}")
        print(f"Auto-turn-off scheduled in {duration} seconds")
        print("="*60 + "\n")
        
        if result:
            return jsonify({
                'success': True,
                'status': 'on',
                'message': f'Pump turned ON (will auto-turn-off in {duration} seconds)',
                'duration': duration,
                'pump_status': status
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to turn pump ON - check console for details'
            }), 500
            
    except Exception as e:
        print(f"[ERROR] Exception in pump_on endpoint: {e}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route("/api/pump/off", methods=['POST'])
def pump_off():
    """Turn pump OFF"""
    print("\n" + "="*50)
    print("PUMP CONTROL: TURNING OFF")
    print("="*50)
    result = pump.turn_off()
    status = pump.get_status()
    print(f"Pump Status: {'ON' if status['is_on'] else 'OFF'}")
    print(f"GPIO Pin: {status['pin']}")
    print(f"Mode: {status['mode']}")
    print("="*50 + "\n")
    
    if result:
        return jsonify({
            'success': True,
            'status': 'off',
            'message': 'Pump turned OFF',
            'pump_status': status
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to turn pump OFF'
        }), 500

@app.route("/api/pump/toggle", methods=['POST'])
def pump_toggle():
    """Toggle pump state"""
    print("\n" + "="*50)
    print("PUMP CONTROL: TOGGLE")
    print("="*50)
    result = pump.toggle()
    status = pump.get_status()
    print(f"Pump Status: {'ON' if status['is_on'] else 'OFF'}")
    print(f"GPIO Pin: {status['pin']}")
    print(f"Mode: {status['mode']}")
    print("="*50 + "\n")
    
    if result:
        return jsonify({
            'success': True,
            'status': 'on' if status['is_on'] else 'off',
            'message': f"Pump turned {'ON' if status['is_on'] else 'OFF'}",
            'pump_status': status
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to toggle pump'
        }), 500

@app.route("/api/scheduler", methods=['GET'])
def scheduler_api():
    """Get scheduler status and schedules"""
    status = scheduler.get_status()
    return jsonify(status)

@app.route("/api/scheduler/add", methods=['POST'])
def scheduler_add():
    """Add a new schedule"""
    data = request.get_json()
    
    schedule_id = data.get('id', f"schedule_{int(time.time())}")
    start_time = data.get('start_time')  # Format: "HH:MM"
    duration_seconds = data.get('duration_seconds', 2.0)  # Default: 2 seconds
    days = data.get('days', None)  # List of days [0-6] or None for all
    enabled = data.get('enabled', True)
    
    if not start_time:
        return jsonify({
            'success': False,
            'error': 'start_time is required (format: HH:MM)'
        }), 400
    
    # Validate duration
    try:
        duration_seconds = float(duration_seconds)
        if duration_seconds <= 0:
            return jsonify({
                'success': False,
                'error': 'duration_seconds must be greater than 0'
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'success': False,
            'error': 'Invalid duration_seconds value'
        }), 400
    
    schedule = scheduler.add_schedule(schedule_id, start_time, duration_seconds, days, enabled)
    
    print("\n" + "="*50)
    print("SCHEDULER: ADDED NEW SCHEDULE")
    print("="*50)
    print(f"Schedule ID: {schedule_id}")
    print(f"Start Time: {start_time}")
    print(f"Duration: {duration_seconds} seconds")
    print(f"Days: {days if days else 'All days'}")
    print(f"Enabled: {enabled}")
    print("="*50 + "\n")
    
    return jsonify({
        'success': True,
        'message': 'Schedule added successfully',
        'schedule': schedule
    })

@app.route("/api/scheduler/remove/<schedule_id>", methods=['POST'])
def scheduler_remove(schedule_id):
    """Remove a schedule"""
    scheduler.remove_schedule(schedule_id)
    
    print("\n" + "="*50)
    print("SCHEDULER: REMOVED SCHEDULE")
    print("="*50)
    print(f"Schedule ID: {schedule_id}")
    print("="*50 + "\n")
    
    return jsonify({
        'success': True,
        'message': 'Schedule removed successfully'
    })

@app.route("/api/scheduler/toggle/<schedule_id>", methods=['POST'])
def scheduler_toggle(schedule_id):
    """Toggle a schedule on/off"""
    for schedule in scheduler.schedules:
        if schedule['id'] == schedule_id:
            schedule['enabled'] = not schedule['enabled']
            print(f"[SCHEDULER] Toggled schedule {schedule_id} to {'enabled' if schedule['enabled'] else 'disabled'}")
            return jsonify({
                'success': True,
                'message': f"Schedule {'enabled' if schedule['enabled'] else 'disabled'}",
                'schedule': schedule
            })
    
    return jsonify({
        'success': False,
        'error': 'Schedule not found'
    }), 404

@app.route("/api/alerts/check")
def check_alerts():
    """Check all sensor conditions and return alerts"""
    alerts = []
    auto_responses = []
    
    # Read all sensors
    temp, humidity = sensor.read_sensor()
    air_quality, co2, nh3, nox = mq135_sensor.read_sensor()
    light_intensity, light_percentage = ldr_sensor.read_sensor()
    moisture_percentage, moisture_raw = moisture_sensor.read_sensor()
    
    # Check for automated responses
    if auto_response.enabled:
        auto_responses = auto_response.check_and_respond(temp, humidity, moisture_percentage)
        
        # Send Telegram notifications for auto-responses
        for response in auto_responses:
            telegram.send_auto_response(
                response['type'],
                response['action'],
                response['reason'],
                response.get('duration')
            )
    
    # Temperature alerts
    if temp is not None:
        if temp > 30:
            alert = {
                'type': 'temperature',
                'severity': 'high',
                'message': f'Temperature is too high: {temp}°C. I need water to cool down.',
                'value': temp,
                'threshold': 30
            }
            alerts.append(alert)
            # Send Telegram notification
            telegram.send_alert('temperature', alert['message'], temp, 30)
        elif temp < 10:
            alert = {
                'type': 'temperature',
                'severity': 'low',
                'message': f'Temperature is too low: {temp}°C. I need warmth.',
                'value': temp,
                'threshold': 10
            }
            alerts.append(alert)
            # Send Telegram notification
            telegram.send_alert('temperature', alert['message'], temp, 10)
    
    # Humidity alerts
    if humidity is not None:
        if humidity < 30:
            alerts.append({
                'type': 'humidity',
                'severity': 'low',
                'message': f'Humidity is too low: {humidity}%. I need more moisture.',
                'value': humidity,
                'threshold': 30
            })
        elif humidity > 80:
            alerts.append({
                'type': 'humidity',
                'severity': 'high',
                'message': f'Humidity is too high: {humidity}%. Too much moisture.',
                'value': humidity,
                'threshold': 80
            })
    
    # Air Quality alerts
    if air_quality is not None:
        if air_quality > 100:
            alerts.append({
                'type': 'air_quality',
                'severity': 'high',
                'message': f'Air quality is poor: {air_quality} AQI. I need fresh air.',
                'value': air_quality,
                'threshold': 100
            })
    
    # CO2 alerts
    if co2 is not None:
        if co2 > 1000:
            alerts.append({
                'type': 'co2',
                'severity': 'high',
                'message': f'CO2 level is high: {co2} ppm. I need fresh air.',
                'value': co2,
                'threshold': 1000
            })
    
    # Light alerts
    if light_intensity is not None:
        if light_intensity < 100:
            alert = {
                'type': 'light',
                'severity': 'low',
                'message': f'Light is too low: {light_intensity} lux. I need sunlight.',
                'value': light_intensity,
                'threshold': 100
            }
            alerts.append(alert)
            # Send Telegram notification
            telegram.send_alert('light', alert['message'], light_intensity, 100)
    
    # Moisture alerts
    if moisture_percentage is not None:
        if moisture_percentage < 30:
            alert = {
                'type': 'moisture',
                'severity': 'low',
                'message': f'Soil moisture is too low: {moisture_percentage}%. I need water.',
                'value': moisture_percentage,
                'threshold': 30
            }
            alerts.append(alert)
            # Send Telegram notification
            telegram.send_alert('moisture', alert['message'], moisture_percentage, 30)
        elif moisture_percentage > 80:
            alert = {
                'type': 'moisture',
                'severity': 'high',
                'message': f'Soil moisture is too high: {moisture_percentage}%. Too much water.',
                'value': moisture_percentage,
                'threshold': 80
            }
            alerts.append(alert)
            # Send Telegram notification
            telegram.send_alert('moisture', alert['message'], moisture_percentage, 80)
    
    return jsonify({
        'success': True,
        'alerts': alerts,
        'alert_count': len(alerts),
        'has_alerts': len(alerts) > 0,
        'auto_responses': auto_responses,
        'auto_response_enabled': auto_response.enabled
    })

@app.route("/api/auto-response/status")
def auto_response_status():
    """Get auto-response system status"""
    return jsonify(auto_response.get_status())

@app.route("/api/auto-response/toggle", methods=['POST'])
def auto_response_toggle():
    """Enable or disable auto-response system"""
    data = request.get_json() or {}
    enabled = data.get('enabled', not auto_response.enabled)
    auto_response.set_enabled(enabled)
    return jsonify({
        'success': True,
        'enabled': auto_response.enabled,
        'message': f'Auto-response system {"enabled" if auto_response.enabled else "disabled"}'
    })

@app.route("/api/telegram/status")
def telegram_status():
    """Get Telegram notifier status"""
    return jsonify({
        'enabled': telegram.enabled,
        'configured': telegram.bot_token is not None and telegram.chat_id is not None
    })

@app.route("/api/telegram/configure", methods=['POST'])
def telegram_configure():
    """Configure Telegram bot token and chat ID (or phone number)"""
    data = request.get_json() or {}
    bot_token = data.get('bot_token', '').strip()
    chat_id = data.get('chat_id', '').strip()
    phone_number = data.get('phone_number', '').strip()
    
    if not bot_token:
        return jsonify({
            'success': False,
            'error': 'Bot Token is required'
        }), 400
    
    if not chat_id and not phone_number:
        return jsonify({
            'success': False,
            'error': 'Either Chat ID or Phone Number is required'
        }), 400
    
    # Update bot token
    telegram.bot_token = bot_token
    telegram.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    # Handle phone number - try to get chat ID from recent bot messages
    if phone_number:
        # Try to get chat ID from phone number by checking recent updates
        chat_id_from_phone = _get_chat_id_from_phone(bot_token, phone_number)
        if chat_id_from_phone:
            telegram.chat_id = chat_id_from_phone
            telegram.enabled = True
            print(f"[TELEGRAM] Configuration updated (Phone: {phone_number} -> Chat ID: {chat_id_from_phone})")
            return jsonify({
                'success': True,
                'message': 'Telegram configured successfully using phone number!'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not find Chat ID for this phone number. Please send a message to the bot first, then try again.'
            }), 400
    else:
        # Use provided chat_id
        telegram.chat_id = chat_id
        telegram.enabled = True
        print(f"[TELEGRAM] Configuration updated (Chat ID: {chat_id})")
        return jsonify({
            'success': True,
            'message': 'Telegram configuration updated successfully'
        })

def _get_chat_id_from_phone(bot_token, phone_number):
    """
    Try to get Chat ID from phone number by checking recent bot updates
    
    Args:
        bot_token: Telegram bot token
        phone_number: Phone number string (e.g., "+1234567890")
    
    Returns:
        Chat ID if found, None otherwise
    """
    try:
        import requests
        # Get recent updates from bot
        updates_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(updates_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('result'):
                # Get the most recent message's chat ID
                # The user needs to have sent a message to the bot first
                for update in reversed(data['result']):  # Check most recent first
                    if 'message' in update:
                        message = update['message']
                        if 'chat' in message:
                            chat_id = str(message['chat']['id'])
                            # Return the most recent chat ID
                            # Note: This assumes the user has messaged the bot
                            return chat_id
    except Exception as e:
        print(f"[TELEGRAM ERROR] Failed to resolve chat ID from phone: {e}")
    
    return None

@app.route("/api/telegram/test", methods=['POST'])
def telegram_test():
    """Test Telegram connection"""
    if telegram.test_connection():
        return jsonify({
            'success': True,
            'message': 'Test message sent to Telegram!'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to send test message. Check bot token and chat ID.'
        }), 500

@app.route("/api/telegram/status-summary", methods=['POST'])
def telegram_status_summary():
    """Send current plant status summary to Telegram"""
    # Check if Telegram is configured
    if not telegram.enabled or not telegram.bot_token or not telegram.chat_id:
        return jsonify({
            'success': False,
            'error': 'Telegram not configured. Please enter Bot Token and Chat ID, then click "Save Configuration" first.'
        }), 400
    
    # Read all sensors
    temp, humidity = sensor.read_sensor()
    air_quality, co2, nh3, nox = mq135_sensor.read_sensor()
    light_intensity, light_percentage = ldr_sensor.read_sensor()
    moisture_percentage, moisture_raw = moisture_sensor.read_sensor()
    
    sensor_data = {
        'temperature': temp,
        'humidity': humidity,
        'moisture_percentage': moisture_percentage,
        'light_intensity': light_intensity,
        'air_quality': air_quality,
        'co2_ppm': co2
    }
    
    result = telegram.send_status_summary(sensor_data)
    if result:
        return jsonify({
            'success': True,
            'message': 'Status summary sent to Telegram!'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to send status summary. Check Telegram bot token and chat ID.'
        }), 500

@app.route("/plant-scan")
def plant_scan_page():
    """Display plant disease scanning page"""
    return render_template('plant_scan.html')

@app.route("/api/plant/scan", methods=['POST'])
def plant_scan():
    """Scan plant image for diseases"""
    try:
        # Check if file is in request
        if 'image' not in request.files:
            # Try to get image from JSON (base64)
            data = request.get_json()
            if data and 'image' in data:
                image_data = data['image']
                result = plant_detector.detect_disease(image_data)
                return jsonify(result)
            else:
                return jsonify({
                    'success': False,
                    'error': 'No image provided'
                }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if file and allowed_file(file.filename):
            # Read image data
            image_data = file.read()
            
            # Detect disease
            result = plant_detector.detect_disease(image_data)
            
            # Save uploaded file for reference
            filename = secure_filename(file.filename)
            timestamp = int(time.time())
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            result['uploaded_file'] = filename
            
            print("\n" + "="*50)
            print("PLANT DISEASE SCAN")
            print("="*50)
            if result.get('success'):
                disease = result.get('disease', {})
                print(f"Detected: {disease.get('name', 'Unknown')}")
                print(f"Confidence: {disease.get('confidence', 0)}%")
                print(f"Severity: {disease.get('severity', 'unknown')}")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
            print("="*50 + "\n")
            
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP'
            }), 400
            
    except Exception as e:
        print(f"[ERROR] Plant scan error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/plant/diseases")
def get_all_diseases():
    """Get information about all known diseases"""
    diseases = plant_detector.get_all_diseases()
    return jsonify({
        'success': True,
        'diseases': diseases
    })

@app.route("/api/plant/disease/<disease_name>")
def get_disease_info(disease_name):
    """Get detailed information about a specific disease"""
    disease_info = plant_detector.get_disease_info(disease_name)
    if disease_info:
        return jsonify({
            'success': True,
            'disease': disease_info
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Disease not found'
        }), 404

if __name__ == "__main__":
    print("Starting Flask app...")
    print("Server will be available at http://127.0.0.1:5000/ or http://localhost:5000/")
    app.run(host='0.0.0.0', port=5000, debug=True)

