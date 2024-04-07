"""
This file is used to import the integrations from the different systems
"""

from settings import *
import importlib

#Main Functions
if TRANSCRIPTION_INTEGRATION != "none":
    transcribe_file = getattr(importlib.import_module("integrations.transcription." + TRANSCRIPTION_INTEGRATION), "transcribe_file")
    print("TRANSCRIPTION_SYSTEM: ", TRANSCRIPTION_INTEGRATION)   

if TOOLS_INTEGRATION != "none":
    get_tool_response = getattr(importlib.import_module("integrations.tools." + TOOLS_INTEGRATION), "get_tool_response")
    print("PROMPT_SYSTEM: ", TOOLS_INTEGRATION)   

if WAKE_INTEGRATION != "none":
    is_wake = getattr(importlib.import_module("integrations.wake." + WAKE_INTEGRATION), "is_wake")
    print("WAKE_SYSTEM: ", WAKE_INTEGRATION)

if VOICE_INTEGRATION != "none":
    voice_me = getattr(importlib.import_module("integrations.voice." + VOICE_INTEGRATION), "voice_me")
    print("VOICE_SYSTEM: ", VOICE_INTEGRATION) 

if MUSIC_INTEGRATION != "none":
    music_module = importlib.import_module("integrations.music." + MUSIC_INTEGRATION)
    print("MUSIC_INTEGRATION: ", MUSIC_INTEGRATION)   

  