import wave

def to_write(frames, write_path):
    wf = wave.open(write_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return write_path  



if TRANSCRIPTION_SYSTEM != "none":
    transcribe_file = getattr(importlib.import_module("integrations.transcription." + TRANSCRIPTION_SYSTEM), "transcribe_file")
    print_me("TRANSCRIPTION_SYSTEM: ", TRANSCRIPTION_SYSTEM)   

if WAKE_SYSTEM != "none":
    is_wake = getattr(importlib.import_module("integrations.wake." + WAKE_SYSTEM), "is_wake")
    print_me("WAKE_SYSTEM: ", WAKE_SYSTEM)