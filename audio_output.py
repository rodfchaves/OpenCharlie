from settings import *
from controllers.volume import *
import pygame
from db import *
from debug import *


#Play the audio file
def play_voice(audio_file, CONVERSATION_MODE=False):
    global VOLUME_STATUS #from volume.py, it will be used and altered by two different files inside their functions: audio_input.py and audio_output.py   
    try:

        pygame.mixer.init()
        sound = pygame.mixer.Sound(audio_file)
        channel = pygame.mixer.find_channel()
        channel.play(sound)
        print("Playing audio")
        
        while channel.get_busy():
            pygame.time.wait(100)
        
        if CONVERSATION_MODE == False:
            VOLUME_STATUS = original_volume(20)
            return CONVERSATION_MODE
        else:
            return True

    except Exception as e:
        error_handler(e)
        return False
        


