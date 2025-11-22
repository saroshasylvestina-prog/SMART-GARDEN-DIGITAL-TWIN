"""
Pump Scheduler Module for Smart Garden Digital Twin
Handles scheduled pump on/off times
"""
import threading
import time
from datetime import datetime, time as dt_time
from pump_control import pump

class PumpScheduler:
    """Scheduler for automatic pump control"""
    
    def __init__(self):
        self.schedules = []  # List of schedule dictionaries
        self.running = False
        self.scheduler_thread = None
        
    def add_schedule(self, schedule_id, start_time, duration_seconds, days=None, enabled=True):
        """
        Add a pump schedule
        
        Args:
            schedule_id: Unique identifier for the schedule
            start_time: Time string in format "HH:MM" (24-hour)
            duration_seconds: How long to run the pump in seconds (default: 2.0)
            days: List of days (0=Monday, 6=Sunday) or None for all days
            enabled: Whether schedule is active
        """
        # Remove existing schedule with same ID
        self.schedules = [s for s in self.schedules if s['id'] != schedule_id]
        
        # Default duration to 2 seconds if not provided
        if duration_seconds is None:
            duration_seconds = 2.0
        
        schedule = {
            'id': schedule_id,
            'start_time': start_time,
            'duration_seconds': float(duration_seconds),
            'days': days if days else [0, 1, 2, 3, 4, 5, 6],  # All days by default
            'enabled': enabled,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.schedules.append(schedule)
        print(f"[SCHEDULER] Added schedule: {schedule_id} - {start_time} for {duration_seconds} seconds")
        return schedule
    
    def remove_schedule(self, schedule_id):
        """Remove a schedule"""
        self.schedules = [s for s in self.schedules if s['id'] != schedule_id]
        print(f"[SCHEDULER] Removed schedule: {schedule_id}")
    
    def get_schedules(self):
        """Get all schedules"""
        return self.schedules
    
    def _parse_time(self, time_str):
        """Parse time string HH:MM to time object"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return dt_time(hour, minute)
        except:
            return None
    
    def _check_schedules(self):
        """Check schedules and control pump"""
        while self.running:
            try:
                now = datetime.now()
                current_time = now.time()
                current_weekday = now.weekday()  # 0=Monday, 6=Sunday
                
                pump_should_be_on = False
                active_schedule = None
                
                for schedule in self.schedules:
                    if not schedule['enabled']:
                        continue
                    
                    # Check if today is in the schedule's days
                    if current_weekday not in schedule['days']:
                        continue
                    
                    start_time = self._parse_time(schedule['start_time'])
                    if not start_time:
                        continue
                    
                    # Calculate start time
                    start_datetime = datetime.combine(now.date(), start_time)
                    duration_seconds = schedule.get('duration_seconds', 2.0)
                    
                    # Calculate end time by adding seconds
                    from datetime import timedelta
                    end_datetime = start_datetime + timedelta(seconds=duration_seconds)
                    
                    # Check if current time is within the scheduled window
                    current_datetime = datetime.combine(now.date(), current_time)
                    
                    # Calculate time difference in seconds
                    time_diff = (current_datetime - start_datetime).total_seconds()
                    
                    # Check if we're within the duration window (0 to duration_seconds)
                    if 0 <= time_diff < duration_seconds:
                        pump_should_be_on = True
                        active_schedule = schedule['id']
                        break
                    # Handle case where end time crosses midnight
                    elif end_datetime.date() > start_datetime.date():
                        # Schedule crosses midnight - check if we're past start or before end (next day)
                        if current_datetime >= start_datetime:
                            pump_should_be_on = True
                            active_schedule = schedule['id']
                            break
                        # Check if we're before end time on next day
                        next_day_end = datetime.combine(end_datetime.date(), current_time)
                        if current_datetime < next_day_end:
                            pump_should_be_on = True
                            active_schedule = schedule['id']
                            break
                
                # Control pump based on schedule
                if pump_should_be_on and not pump.is_on:
                    duration = schedule.get('duration_seconds', 2.0)
                    print(f"[SCHEDULER] Turning pump ON (Schedule: {active_schedule}) at {current_time.strftime('%H:%M:%S')} for {duration} seconds")
                    # Use turn_on_for_duration to automatically turn off after duration
                    pump.turn_on_for_duration(duration)
                elif not pump_should_be_on and pump.is_on:
                    # Check if pump was turned on by scheduler
                    # Only turn off if no manual override
                    print(f"[SCHEDULER] Turning pump OFF (Schedule ended) at {current_time.strftime('%H:%M:%S')}")
                    pump.turn_off()
                
                # Debug output every 5 minutes (at :00 and :05 minutes)
                if now.minute % 5 == 0 and now.second < 30:
                    print(f"[SCHEDULER DEBUG] Time: {current_time.strftime('%H:%M:%S')}, Weekday: {current_weekday}, Pump should be ON: {pump_should_be_on}, Active: {active_schedule}, Total schedules: {len(self.schedules)}")
                
            except Exception as e:
                print(f"[SCHEDULER ERROR] {e}")
                import traceback
                traceback.print_exc()
            
            time.sleep(30)  # Check every 30 seconds
    
    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._check_schedules, daemon=True)
            self.scheduler_thread.start()
            print("[SCHEDULER] Started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)
        print("[SCHEDULER] Stopped")
    
    def get_status(self):
        """Get scheduler status"""
        return {
            'running': self.running,
            'schedules_count': len(self.schedules),
            'schedules': self.schedules
        }

# Global scheduler instance
print("\n" + "="*50)
print("INITIALIZING PUMP SCHEDULER")
print("="*50)
scheduler = PumpScheduler()
scheduler.start()  # Start scheduler automatically
print("="*50 + "\n")

