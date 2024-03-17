from db import get_values
import importlib
import pyaudio



"""
AUDIO INPUT SETTINGS
RATE = number of frames per second
CHUNK = number of rates the signals are split into
Every second, a number of frames equal to RATE/CHUNK are recorded
RECORD_SECONDS = number of seconds to record
"""

CHUNK = 11025
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10
CONV_SECONDS = 8

settings = get_values("settings")
admin_settings = get_values("admin")
print(admin_settings)


#INTEGRATIONS
#Music
MUSIC_INTEGRATION = settings["music_app"] #default = "none"

# AI
TRANSCRIPTION_SYSTEM = settings["transcription_system"] #default = "openai"
WAKE_SYSTEM = settings["wake_system"] #default = "charlie"
AI_TOOLS = settings["prompt_system"] #default = "openai"
WAKE_WORD = settings["wake_word"] #default = "charlie"
PROMPT_SYSTEM = settings["prompt_system"] #default = "openai"
VOICE_SYSTEM = settings["voice_system"] #default = "openai"

#OPEN AI
OPEN_API_KEY = admin_settings["open_api_key"]

#SPOTIFY
SPOTIFY_CLIENT_ID = admin_settings["spotify_client_id"] #default = none
SPOTIFY_CLIENT_SECRET = admin_settings["spotify_client_secret"]

#TIMEZONE https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE = settings["timezone"]


#LANGUAGE https://cloud.google.com/speech-to-text/docs/languages
LANGUAGE = settings["language"]


VOLUME_LEVELS = settings["volume_levels"] #default = 24


#GLOBALS
VOLUME_CHANGE = 20
VOLUME_STATUS = 'original'


print("SPOTIFY_CLIENT_ID: " + SPOTIFY_CLIENT_ID)
print("SPOTIFY_CLIENT_SECRET: " + SPOTIFY_CLIENT_SECRET)

