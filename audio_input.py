import pyaudio
import audioop
from settings import *
import threading
from controllers.volume import *
from controllers.main import *
from slugify import slugify
import datetime
from db import *
from debug import *
import wave

conversation_mode = False

"""
Audio input > Transcribe > Controllers.Main > Controllers > Audio Output 

If the user starts talking, decrease the volume
If there is a conversation, decrease the volume
After same time of silence, increase the volume
If the va starts talking, decrease the volume
"""
write_path = 'io/input.wav'

def to_write(frames):
    wf = wave.open(write_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return write_path  

def check_wake(frames):
    
    storage_path = 'io/storage/' + slugify(str(datetime.datetime.now().utcnow())) + '.wav'  

    print_me("Transcribing...")
    try:
        if is_wake(frames):            
            to_write(frames, storage_path)
        else:
            print_me("Not charlie")
    except Exception as e:
        error_handler(e)
    
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

    global volume_status #from volume.py, it will be used and altered by two different files inside their functions: audio_input.py and audio_output.py
    idle_frames = 0
    max_idle_frame = 0
    frames = []
    volume_threshold = 800
    status = 'idle'
    range_threshold = int(RATE / CHUNK * RECORD_SECONDS)
    max_total_frames = int(RATE / CHUNK * RECORD_SECONDS)
    total_frames = 0
    max_idle_reply = int(RATE / CHUNK * REPLY_SECONDS) #number of seconds to wait for the user reply
    idle_reply = 0
    global conversation_mode
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            rms = audioop.rms(data, 2)  
            print_me(f'rms: {rms}')
            print_me(f'status: {status}')
            print_me(f'range_threshold: {range_threshold}')
            print_me(f'VOLUME_STATUS: {volume_status}')

            if conversation_mode == True and idle_reply <= max_idle_reply:
                idle_reply += 1
            elif conversation_mode == True and idle_reply > max_idle_reply:
                conversation_mode = False
                idle_reply = 0

            if status == 'recording' and volume_status == 'original' and conversation_mode == False:
                volume_status = decrease_volume(20)
                

            #If RMS is greater than threshold, add to frames
            if rms > volume_threshold and status == 'idle':
                status = 'recording'
                print_me(status) #recording
                print_me(f'RMS loudness: {rms}')
                frames.append(data)
                total_frames += 1

            
            #If RMS is less than threshold, add to idle time
            elif rms > volume_threshold and status == 'recording' and total_frames <= max_total_frames:
                print_me(f'RMS loudness: {rms}')
                frames.append(data)
                print_me(f'total time: {total_frames}')
                print_me(f'frame length: {len(frames)}')
                idle_frames = 0
                total_frames += 1

            elif rms > volume_threshold and status == 'recording' and total_frames > max_total_frames:
                print_me(f'RMS loudness: {rms}')
                print_me(f'total time: {total_frames}')
                print_me(f'frame length: {len(frames)}')
                frames.append(data)
                check_wake(frames)
                
                # await loop.run_in_executor(executor, lambda: write_to_file(frames))

                total_frames = 0
                idle_frames = 0
                frames = []
                status = 'idle'
                print_me(status)
                print_me('done recording')

            elif rms < volume_threshold and status == 'recording' and idle_frames <= max_idle_frame:
                print_me(f'idle time 1: {idle_frames}')
                frames.append(data)
                idle_frames += 1
                total_frames += 1
            
            elif rms < volume_threshold and status == 'recording' and idle_frames > max_idle_frame:
                print_me(f'idle time 2: {idle_frames}')
                frames.append(data)
                check_wake(frames)

                # await loop.run_in_executor(executor, lambda: write_to_file(frames))

                status = 'idle'
            
            elif rms < volume_threshold and status == 'idle':
                idle_frames = 0
                total_frames = 0
                frames = []
              

    except Exception as e: 
        stream.stop_stream()
        stream.close()
        p.terminate()  
        error_handler(e)


stream_thread = threading.Thread(target=start_stream)
stream_thread.start()

