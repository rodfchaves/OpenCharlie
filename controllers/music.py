"""
This module is responsible for handling the music controller.
"""


import requests
import json
from audio_output import *
from integrations_mod import music_module

def play_music(query):
    url = "https://api.openai.com/v1/chat/completions"
    print("play the music")


    tools = [
        {
            "type": "function",
            "function": {
                "name": "play_music",
                "description": "Search for a song, artist, podcast, show, audiobook, episode, playlist or album on a music player and play it.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The name of the song, artist, podcast, show, audiobook, episode, playlist or album, e.g. The Beatles.",
                        },
                        "track_type": {
                            "type": "string", 
                            "enum": ["track", "artist", "album", "playlist", "show", "episode", "audiobook"],
                            "description": "The type of the element, e.g. album. Should default to track if you are not sure."
                        },
                    },
                    "required": ["query", "track_type"],
                },
            },
        }  
    ]
    
    payload = {
        "model": "gpt-3.5-turbo-1106",
        "messages": [{"role": "user", "content": query}],
        "tools": tools       
    }

    headers = {
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + OPEN_API_KEY 
        }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_json = response.json()
        arguments = json.loads(response_json["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"])
        query = arguments["query"]
        track_type = arguments["track_type"]
        
        print("The query: ", query)
        print("The element type: ", track_type)

        music_module.tool_play_music(query, track_type)


    except Exception as e:
        print(f"Exception: {e}")




    # print(response.text)
    # print(response.json())
    # print(response.status_code)
    # print(response.headers)