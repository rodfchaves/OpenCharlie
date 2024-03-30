"""
This file is responsible for the alarm functionality. It contains the functions to set, stop, and snooze alarms.
Still in development.
"""


import threading
import time
from datetime import datetime
from playsound import playsound
import json
import random
import string
import pytz
import os
from db import store_alarm, get_alarms
from debug import *

#Constants
ALARM_THRESHOLD = 8
ALARM_REPETITIONS = 10

alarm_trigger_lock = threading.Lock()

class SetAlarm(threading.Thread):
    def __init__(self, trigger_time, timezone):
        super().__init__()
        self.alarm_id = "test"
        self.trigger_time = trigger_time
        self.status = "active"
        self.timezone = timezone
        print(self.timezone)

    def fire_alarm(self):
        i=0
        while i < ALARM_REPETITIONS:
            if self.status == "active":
                playsound(ALARM_SOUND_PATH)
                print("Alarm ringing")           
            else:
                print("Alarm stopped")
                break    
            i += 1

    def run(self):        
        store_alarm(self.trigger_time, self.timezone, self.status)       
        timezone = pytz.timezone(self.timezone)
        trigger_time_iso = datetime.fromisoformat(self.trigger_time)
        current_time = datetime.now(timezone)
        seconds = int((trigger_time_iso - current_time).total_seconds())
        print("Seconds: ", seconds)

        try:
            print("Alarm set")
            time.sleep(seconds)
            with alarm_trigger_lock:
                self.fire_alarm(self)                
                
            print("Alarm stopped")
            return "alarm_set"
        
        except Exception as e:
            error_handler(e)
            return "alarm_not_set"  


# def check_thread(cron_expression):

# def stop_thread(cron_expression):

# def remove_alarm(id):

# def snooze(cron_expression):

def reinitiate_alarms():
    alarms = get_alarms()
    for alarm in alarms:
        alarm_thread = SetAlarm(alarm[0], alarm[1])            
        alarm = alarm_thread.start()
        print(alarm)

