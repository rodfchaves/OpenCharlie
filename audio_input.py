import pyaudio
import audioop
from settings import CHANNELS, FORMAT, RATE, CHUNK, RECORD_SECONDS, VOLUME_CHANGE, CONV_SECONDS, VOLUME_STATUS
from settings_systems import is_wake
import threading
from controllers.volume import *
from controllers.main import *
from slugify import slugify
import datetime
from db import *
from debug import *
from to_write import to_write

CONVERSATION_MODE = False


"""
Audio input > Transcribe > Controllers.Main > Controllers > Audio Output 

If the user starts talking, decrease the volume
If there is a conversation, decrease the volume
After same time of silence, increase the volume
If the va starts talking, decrease the volume
"""

storage_path = 'io/storage/' + slugify(str(datetime.datetime.now().utcnow())) + '.wav' 


    
# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print_me("Listening to the microphone...")

"""
max_total_time = maximum number of seconds to record
max_idle_time = maximum number of seconds of silence before stopping recording
total_time = starting total time for the loop
"""

def start_stream():
    """
    Start the stream and record audio.

    Raises:
    ExceptionType: Explanation of when and why the exception is raised.

    """

    global VOLUME_STATUS #from volume.py, it will be used and altered by two different files inside their functions: audio_input.py and audio_output.py
    global CONVERSATION_MODE
    global STREAM_STATUS
    STREAM_STATUS = 'idle'
    idle_frames = 0
    max_idle_frames = 3
    frames = []
    volume_threshold = 300
    status = 'idle'
    range_threshold = int(RATE / CHUNK * RECORD_SECONDS)
    max_total_frames = int(RATE / CHUNK * RECORD_SECONDS)
    wake_total_frames = int(RATE / CHUNK * 0.6)
    total_frames = 0
    max_conv_idle = int(RATE / CHUNK * CONV_SECONDS) #number of seconds to wait for the user reply
    conv_idle = 6
    VOLUME_STATUS = 'original'

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            rms = audioop.rms(data, 2)  
            print_me(f'rms: {rms}')
            print_me(f'status: {STREAM_STATUS}')
            print_me(f'range_threshold: {range_threshold}')
            print_me(f'VOLUME_STATUS: {VOLUME_STATUS}')
            print_me(f'CONVERSATION_MODE: {CONVERSATION_MODE}')
            print_me(f'total_frames: {len(frames)}')
            print_me(f'idle_frames: {idle_frames}')

            #if CONVERSATION_MODE is true, starts the time to wait for the user reply
            if STREAM_STATUS != "working":
                
                #If RMS is greater than threshold, add to frames
                if CONVERSATION_MODE == False:
                    if  STREAM_STATUS == 'idle' and rms > volume_threshold:
                        STREAM_STATUS = 'recording'
                        print_me(status)
                        total_frames += 1
        
                    if STREAM_STATUS == 'recording' and total_frames >= wake_total_frames:
                        print_me("WAKE MODE")
                        CONVERSATION_MODE = is_wake(frames)
                        frames = []
                        total_frames = 0
                        STREAM_STATUS = 'idle'
                
                elif CONVERSATION_MODE == True:
                    if idle_frames <= max_conv_idle:                    
                        if VOLUME_STATUS == 'original':
                            VOLUME_STATUS = decrease_volume(VOLUME_CHANGE)
                            VOLUME_STATUS = 'decreased'
                            STREAM_STATUS = 'recording'
                    
                    elif idle_frames >= max_conv_idle or total_frames >= max_total_frames:
                        file = to_write(frames)
                        transcription = transcribe_file(file)
                        CONVERSATION_MODE = main_prompt(transcription)      
                
                if rms > volume_threshold:                
                    idle_frames = 0
                    frames.append(data)

                elif rms < volume_threshold and STREAM_STATUS == 'recording':
                    frames.append(data)             
                    if idle_frames >= max_idle_frames or idle_frames >= max_conv_idle:
                        print_me(f'idle_frames: {idle_frames}')
                        
                        if CONVERSATION_MODE == True:                   
                            file = to_write(frames)
                            transcription = transcribe_file(file)
                            CONVERSATION_MODE = main_prompt(transcription)
                        elif CONVERSATION_MODE == False:
                            print_me("WAKE MODE 2 ")
                            CONVERSATION_MODE = is_wake(frames)
                            idle_frames = 0  
                        frames = []
                        STREAM_STATUS = 'idle'
                        total_frames = 0
                        idle_frames = 0
                    elif idle_frames <= max_idle_frames:
                        print_me(f'idle_frames: {idle_frames}')
                        idle_frames += 1
                        total_frames += 1


    except Exception as e: 
        stream.stop_stream()
        stream.close()
        p.terminate()  
        error_handler(e)


stream_thread = threading.Thread(target=start_stream)
stream_thread.start()

