from settings import *

#Main Functions
if TRANSCRIPTION_SYSTEM != "none":
    transcribe_file = getattr(importlib.import_module("integrations.transcription." + TRANSCRIPTION_SYSTEM), "transcribe_file")
    print("TRANSCRIPTION_SYSTEM: ", TRANSCRIPTION_SYSTEM)   

if PROMPT_SYSTEM != "none":
    get_tool_response = getattr(importlib.import_module("integrations.conversation." + PROMPT_SYSTEM), "get_tool_response")
    print("PROMPT_SYSTEM: ", PROMPT_SYSTEM)   

if WAKE_SYSTEM != "none":
    is_wake = getattr(importlib.import_module("integrations.wake." + WAKE_SYSTEM), "is_wake")
    print("WAKE_SYSTEM: ", WAKE_SYSTEM)

if MUSIC_INTEGRATION != "none":
    music_module = importlib.import_module("integrations.music." + MUSIC_INTEGRATION)
    print("MUSIC_INTEGRATION: ", MUSIC_INTEGRATION)   

if VOICE_SYSTEM != "none":
    voice_me = importlib.import_module("integrations.voice." + VOICE_SYSTEM)
    print("VOICE_SYSTEM: ", VOICE_SYSTEM)   