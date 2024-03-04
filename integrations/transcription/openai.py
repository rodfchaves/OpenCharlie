# Description: Transcribes audio file 
import requests
from settings import *
from debug import *
import json

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
        "model": "whisper-1",
        "language": "en"
        }

        headers = {
            'Authorization': 'Bearer ' + OPEN_API_KEY 
            }

        try:
            response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code == 200:
                transcription = json.loads(response.text)["text"]
                print(f'Transcription successful: {transcription}')
                return transcription
            else:
                print(f"Failed to retrieve audio: Status code {response.status_code}, Response: {response.text}")


        except Exception as e:
            return error_handler(e)
