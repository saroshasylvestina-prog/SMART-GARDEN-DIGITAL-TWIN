#!/usr/bin/env python3
"""
Check current pump duration settings and active schedules
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from scheduler import scheduler
    from auto_response import auto_response
    from pump_control import pump
    
    print("="*60)
    print("PUMP DURATION CHECK")
    print("="*60)
    
    # Check pump default duration
    print(f"\n[PUMP] Default Duration: {pump.get_duration()} seconds")
    
    # Check auto-response threshold
    print(f"[AUTO-RESPONSE] Moisture Threshold: {auto_response.moisture_low_threshold}%")
    print(f"[AUTO-RESPONSE] Pump Duration: 1.0 seconds (fixed)")
    
    # Check schedules
    schedules = scheduler.get_schedules()
    print(f"\n[SCHEDULER] Active Schedules: {len(schedules)}")
    
    if schedules:
        print("\nSchedule Details:")
        for i, schedule in enumerate(schedules, 1):
            print(f"\n  Schedule {i}:")
            print(f"    ID: {schedule.get('id', 'unknown')}")
            print(f"    Time: {schedule.get('start_time', 'unknown')}")
            print(f"    Duration: {schedule.get('duration_seconds', 'unknown')} seconds")
            print(f"    Enabled: {schedule.get('enabled', False)}")
            
            if schedule.get('duration_seconds', 1.0) != 1.0:
                print(f"    ⚠️  WARNING: This schedule uses {schedule.get('duration_seconds')} seconds, not 1 second!")
    else:
        print("  No schedules configured")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Pump default: {pump.get_duration()}s")
    print(f"Auto-response: 1.0s (when moisture < {auto_response.moisture_low_threshold}%)")
    
    if schedules:
        durations = [s.get('duration_seconds', 1.0) for s in schedules if s.get('enabled', False)]
        if durations:
            print(f"Scheduler: {durations} seconds (from active schedules)")
            if any(d != 1.0 for d in durations):
                print("\n⚠️  ISSUE FOUND: Some schedules use 2 seconds!")
                print("   Solution: Remove or update schedules with 2-second duration")
    else:
        print("Scheduler: No active schedules")
    
    print("="*60)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

