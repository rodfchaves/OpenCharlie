"""
Simple function to write audio frames to a .wav file.
"""

from settings import CHANNELS, FORMAT, RATE
import wave
import pyaudio as p
from debug import error_handler

def to_write(frames, write_path='io/input.wav'):
    try:
        wf = wave.open(write_path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print("Wrote to", write_path)
        return write_path  
    except Exception as e:
        error_handler(e)
        return False