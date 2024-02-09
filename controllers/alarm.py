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
ALARM_SOUND_PATH = "sounds/ringtone.mp3"
ALARM_THRESHOLD = 8
ALARM_REPETITIONS = 10


#we will have a function to get the remaining alarms
#we will have a function to delete an alarm
#we will have a function to check an alarm
#set a fucntion to turn off the alarm when it goes off

# we store the alarm_- OK
# we create a thread
# the thread check if the alarm is active and fires, or breaks
# we check if the stored alarm still needs to ring
# if it does, we create a thread
# make a validation before and after the thread is created
# ensure that if the app is closed, the alarm will still ring
#create a snooze function
#lower the volume when there is an imput with "Charlie"

alarm_trigger_lock = threading.Lock()

class SetAlarm(threading.Thread):
    def __init__(self, trigger_time, timezone):
        super().__init__()
        self.alarm_id = "test"
        self.trigger_time = trigger_time
        self.status = "active"
        self.timezone = timezone
        print_me(self.timezone)

    def fire_alarm(self):
        i=0
        while i < ALARM_REPETITIONS:
            if self.status == "active":
                playsound(ALARM_SOUND_PATH)
                print_me("Alarm ringing")           
            else:
                print_me("Alarm stopped")
                break    
            i += 1

    def run(self):        
        store_alarm(self.trigger_time, self.timezone, self.status)       
        timezone = pytz.timezone(self.timezone)
        trigger_time_iso = datetime.fromisoformat(self.trigger_time)
        current_time = datetime.now(timezone)
        seconds = int((trigger_time_iso - current_time).total_seconds())
        print_me("Seconds: ", seconds)

        try:
            print_me("Alarm set")
            time.sleep(seconds)
            with alarm_trigger_lock:
                self.fire_alarm(self)                
                
            print_me("Alarm stopped")
            return "alarm_set"
        
        except Exception as e:
            error_handler(e)
            return "alarm_not_set"  



#For testing purposes, remove when done:
alarm_thread = SetAlarm("2023-12-12T23:59:30-03:00", "America/Sao_Paulo")            
alarm = alarm_thread.start()
print_me(alarm)

# def check_thread(cron_expression):

# def stop_thread(cron_expression):

def remove_alarm(id):



# def snooze(cron_expression):

def reinitiate_alarms():
    alarms = get_alarms()
    for alarm in alarms:
        alarm_thread = SetAlarm(alarm[0], alarm[1])            
        alarm = alarm_thread.start()
        print_me(alarm)

