from settings import *
from controllers.volume import *
import pygame
from db import *
from debug import *


#Play the audio file
def play_voice(audio_file, CONVERSATION_MODE=False):
    global volume_status #from volume.py, it will be used and altered by two different files inside their functions: audio_input.py and audio_output.py   
    try:

        pygame.mixer.init()
        sound = pygame.mixer.Sound(audio_file)
        channel = pygame.mixer.find_channel()
        channel.play(sound)
        print_me("Playing audio")
        
        while channel.get_busy():
            pygame.time.wait(100)
        
        if CONVERSATION_MODE == False:
            volume_status = original_volume(20)
            return False
        else:
            return True

    except Exception as e:
        print_me(error_handler(e))
        


