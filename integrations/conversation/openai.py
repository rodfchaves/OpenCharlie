# Transcribes audio file 
import requests
from settings import *
from debug import *
import json
from audio_output import play_voice

def get_tool_response(tools, transcription):    
    url = "https://api.openai.com/v1/chat/completions"
  
    payload = {
        "model": "gpt-4",
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

        print(response.text)
        print(response.json())
        print(response.status_code)
        print(response.headers)

        return response_json

    except Exception as e:        
        return error_handler(e)
    
