# Description: Transcribes audio file 
import requests
from settings import *
from debug import *
import json
from audio_output import play_voice

def voice_me(text, CONVERSATION_MODE=False):
    """
    Convert text to speech using OpenAI's API.
    text (str): The text to be converted to speech.
    CONVERSATION_MODE (bool): The mode of the conversation.

    Returns:
    The conversation mode after playing the voice.

    """
    
    url = "https://api.openai.com/v1/audio/speech"

    payload = {
    "model": "tts-1",
    "voice": "alloy",
    "input": text,
    "response_format": "mp3",
    "speed": 1.0   
    }

    headers = {
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + OPEN_API_KEY 
        }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        file_path = "io/voice_me.mp3"

        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
            return play_voice(file_path, CONVERSATION_MODE)
        else:
            print(f"Failed to retrieve audio: Status code {response.status_code}, Response: {response.text}")
            return CONVERSATION_MODE

    except Exception as e:        
        error_handler(e)
        return False

