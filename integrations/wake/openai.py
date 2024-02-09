# Description: Transcribes audio file and checks if the wake word is present. If the wake word is present, it will call the main_prompt function.
from settings import *
from debug import *
from audio_input import to_write
import re
from controllers.main import main_prompt
from db import store_conversation_log

def is_wake(frames):
    file = to_write(frames)
    transcription = transcribe_file(file)
    print_me("Transcription: ", transcription)
    if re.search(str(WAKE_WORD + "*"), transcription, re.IGNORECASE) or conversation_mode == True:
        conversation_mode = main_prompt(transcription) 
        store_conversation_log(transcription, "none", "user") 
        return transcription
    else:
        return False