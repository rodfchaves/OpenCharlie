"""
This module is responsible for handling the communication with OpenAI API.
There is a maximum of 128 functions that can be sent in a single request.
"""

import requests
from settings import *
from debug import *
import json
from audio_output import play_voice

def get_tool_response(tools, transcription):    
    url = "https://api.openai.com/v1/chat/completions"
  
    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": transcription}, {"role": "system", "content": "Do not ommit the required properties."}],
        "tools": tools       
    }

    headers = {
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + OPEN_API_KEY 
        }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_json = response.json()

        print(response.text)
        print(response.json())
        print(response.status_code)
        print(response.headers)

        return response_json

    except Exception as e:        
        return error_handler(e)
    
