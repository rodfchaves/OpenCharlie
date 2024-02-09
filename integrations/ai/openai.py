# Description: Transcribes audio file 
import requests
from settings import *
from debug import *
import json
from audio_output import play_voice

def transcribe_file(file): 
    """
    Give the transcription of an audio file.

    Parameters:
    file (str): Path to the wav file.

    Returns:
    str: Transcription of the audio file.

    Raises:
    ExceptionType: Explanation of when and why the exception is raised.

    Example:
    transcribe_file('io/input.wav')
    "Charlie, play the song Hello by Adele"
    """


    url = "https://api.openai.com/v1/audio/transcriptions"

    with open(file, 'rb') as f:
        files = {'file': ("speech.mp3", f)}

        data = {
        "model": "whisper-1"
        }

        headers = {
            'Authorization': 'Bearer ' + OPEN_API_KEY 
            }

        try:
            response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code == 200:
                transcription = json.loads(response.text)["text"]
                print_me(f'Transcription successful: {transcription}')               
                return transcription
            else:
                print_me(f"Failed to retrieve audio: Status code {response.status_code}, Response: {response.text}")


        except Exception as e:
            return error_handler(e)



def get_tool_response(tools, transcription):    
    url = "https://api.openai.com/v1/chat/completions"
  
    payload = {
        "model": "gpt-3.5-turbo-1106",
        "messages": [{"role": "user", "content": transcription}],
        "tools": tools       
    }

    headers = {
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + OPEN_API_KEY 
        }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_json = response.json()

        print_me(response.text)
        print_me(response.json())
        print_me(response.status_code)
        print_me(response.headers)

        return response_json

    except Exception as e:        
        return error_handler(e)
    

def voice_me(input):
    
    url = "https://api.openai.com/v1/audio/speech"

    payload = {
    "model": "tts-1",
    "voice": "alloy",
    "input": input,
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
            play_voice(file_path)
        else:
            print_me(f"Failed to retrieve audio: Status code {response.status_code}, Response: {response.text}")
  

    except Exception as e:
        return error_handler(e)


def wake_recon(transcription):
    return "tbd"