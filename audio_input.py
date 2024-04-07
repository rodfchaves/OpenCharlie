"""
This file contains the audio input stream. It listens to the microphone and records the audio.
"""

import pyaudio
import audioop
from settings import CHANNELS, FORMAT, RATE, CHUNK, RECORD_SECONDS, VOLUME_CHANGE, CONV_SECONDS, VOLUME_STATUS
from integrations_mod import is_wake, transcribe_file
from controllers.volume import *
from controllers.main import *
from slugify import slugify
import datetime
from db import *
from debug import *
from to_write import to_write
import time
from playsound import playsound

CONVERSATION_SOUND_PATH = "sounds/start.mp3"
ALARM_SOUND_PATH = "sounds/ringtone.mp3"
CONVERSATION_MODE = False

storage_path = 'io/storage/' + slugify(str(datetime.datetime.now(datetime.timezone.utc))) + '.wav' 
    
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Listening to the microphone...")

def start_stream(socketio, thread_running):
    """
    Start the stream and record audio.
    If the conversation mode is off, the stream will check for the wake word inside an RMS threshold.
    If the conversation mode is on, the volume will be decreased and no wake word will be needed and the stream will record everything until it reaches the max_conv_frames or max _idle.
    Once it reaches the max_conv_frames or max _idle, it will transcribe the file and call the main prompt to check for the next action.

    CONVERSATION_MODE (bool): If the user is in a conversation, the volume will be decreased and no wake word will be needed. If not, the stream will check for the wake word inside an RMS threshold.

    STREAM_STATUS (str): The status of the stream. If the stream is idle, it will not record. It only changes to recording if the user - or any other noise - speaks louder than the RMS threshold. If it is recording, it will record everything until it reaches the max_conv_frames or max _idle.

    VOLUME_STATUS (str): The status of the volume. If the user is in a conversation or the voice assistant is voicing something, the volume will be decreased. If not, it will be original.

    volume_threshold (int): The threshold for the RMS. If the RMS is greater than the threshold, the stream will start recording.

    total_frames (int): The total number of frames recorded.

    max_total_frames (int): The maximum number of frames to record.

    max_wake_frames (int): The maximum number of frames to record for the wake word.

    max_conv_frames (int): The maximum number of frames to record for the conversation mode.

    Raises:
    ExceptionType: Explanation of when and why the exception is raised.

    """

    global VOLUME_STATUS #from volume.py, it will be used and altered by two different files inside their functions: audio_input.py and audio_output.py
    global CONVERSATION_MODE
    global STREAM_STATUS
    STREAM_STATUS = 'idle'
    idle_frames = 0
    max_idle = int(RATE / CHUNK * 2)
    frames = []
    volume_threshold = 200
    total_frames = 0
    max_total_frames = int(RATE / CHUNK * RECORD_SECONDS)
    max_wake_frames = int(RATE / CHUNK * 0.6)
    max_conv_frames = int(RATE / CHUNK * CONV_SECONDS) 
    VOLUME_STATUS = 'original'

    try:
        while True and not thread_running.is_set():
            socketio.emit('stream_status', {'status': 'Charlie is ON'})
            data = stream.read(CHUNK, exception_on_overflow=False)
            rms = audioop.rms(data, 2)  
            print(f'rms: {rms}')
            print(f'status: {STREAM_STATUS}')
            print(f'VOLUME_STATUS: {VOLUME_STATUS}')
            print(f'CONVERSATION_MODE: {CONVERSATION_MODE}')
            print(f'total_frames: {len(frames)}')
            print(f'idle_frames: {idle_frames}')
            print(f'thread_running: {thread_running}')
           
            socketio.emit('conversation_mode', {'data': CONVERSATION_MODE})
                      
            if CONVERSATION_MODE == False:
                #This is for after the conversation mode is finished and you want to return the system volume to the original level
                if STREAM_STATUS == 'idle' and VOLUME_STATUS == "decreased":
                    VOLUME_STATUS = original_volume(VOLUME_CHANGE)
                    VOLUME_STATUS = 'original'
                    STREAM_STATUS = 'recording'
                    total_frames += 1

                #Activate the STREAM_STATUS to recording if the audio output is higher than the RMS threshold while in idle mode
                if  STREAM_STATUS == 'idle' and rms > volume_threshold:
                    STREAM_STATUS = 'recording'
                    total_frames += 1

                #If you already have the minimum number of frames for the wake word, check if it is the wake word    
                if STREAM_STATUS == 'recording' and total_frames >= max_wake_frames:
                    CONVERSATION_MODE = is_wake(frames)
                    if CONVERSATION_MODE :
                        playsound(CONVERSATION_SOUND_PATH)
                    frames = []
                    total_frames = 0
                    STREAM_STATUS = 'idle'
                
                #If RMS is higher than the RMS threshold, add to the frames and reset the idle_frames counter
                elif rms > volume_threshold:                
                    idle_frames = 0
                    frames.append(data)

                #If STREAM_STATUS is recording, even with a low RMS,add to the frame
                elif rms < volume_threshold and STREAM_STATUS == 'recording':
                    frames.append(data)

                    #If idle_frames are higher than the max_idle or the max_conv_frames, check if it is the wake word             
                    if idle_frames >= max_idle or idle_frames >= max_conv_frames:
                        CONVERSATION_MODE = is_wake(frames)
                        if CONVERSATION_MODE :
                            playsound(CONVERSATION_SOUND_PATH)
                        idle_frames = 0  
                        frames = []
                        STREAM_STATUS = 'idle'
                        total_frames = 0
                        idle_frames = 0
                    elif idle_frames <= max_idle:
                        idle_frames += 1
                        total_frames += 1
                            
            elif CONVERSATION_MODE == True:
                frames.append(data)
                #This is for the starting of a conversation, when the volume is decreased
                if idle_frames <= max_conv_frames and VOLUME_STATUS == 'original':
                    VOLUME_STATUS = decrease_volume(VOLUME_CHANGE)
                    VOLUME_STATUS = 'decreased'
                    STREAM_STATUS = 'recording'
                
                #Even if the conversation is active, it shouldn't start adding frames unless the RMS is higher than the threshold, to prevent the system from recording noise and using too much of the API
                elif rms > volume_threshold and STREAM_STATUS == "idle": 
                    idle_frames = 0
                    STREAM_STATUS = 'recording'
                
                #If you already have the maximum number of frames for the conversation, transcribe the file and call the main prompt
                elif idle_frames >= max_conv_frames or total_frames >= max_total_frames:
                    file = to_write(frames)
                    transcription = transcribe_file(file)
                    CONVERSATION_MODE = main_prompt(transcription)
                    if CONVERSATION_MODE :
                            playsound(CONVERSATION_SOUND_PATH)      

                elif rms > volume_threshold and STREAM_STATUS == "recording":                
                    idle_frames = 0
                                    
                elif rms < volume_threshold:
                    #If you are already recording the conversation, keep it recording even with low RMS
                    if STREAM_STATUS == "recording" and idle_frames >= max_idle:
                        stream.stop_stream()
                        file = to_write(frames)
                        transcription = transcribe_file(file)
                        #The TEMPORARY_MODE exists to change the CONVERSATION_MODE only after the sound is played
                        TEMPORARY_MODE = main_prompt(transcription)
                        if TEMPORARY_MODE :
                            playsound(CONVERSATION_SOUND_PATH)
                        CONVERSATION_MODE = TEMPORARY_MODE
                        stream.start_stream()
                        frames = []
                        STREAM_STATUS = 'idle'
                        total_frames = 0
                        idle_frames = 0
                                            
                    #If no one is speaking, turn off the conversation mode and do nothing
                    elif STREAM_STATUS == "idle" and idle_frames >= (max_idle + max_conv_frames):
                        CONVERSATION_MODE = False
                        frames = []
                        STREAM_STATUS = 'idle'
                        total_frames = 0
                        idle_frames = 0
                    else:
                        idle_frames += 1
                        total_frames += 1
            else:
                time.sleep(1)
                socketio.emit('stream_status', {'status': 'Charlie is OFF'})

    except Exception as e: 
        stream.stop_stream()
        stream.close()
        p.terminate()  
        error_handler(e)


