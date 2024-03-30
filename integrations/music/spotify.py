'''
Integration with Spotify functions available.
These functions are activated by the tools present in controllers/tools/tools_music.py and are called by the main_prompt function in controllers/main.py

You need to have Spotify installed in your system to use this integration
This integration uses the Spotify API to control the playback
The following functions are available:
open_spotify()
    Open Spotify    
refreshing_token()
    Refresh the token if it is expired
get_device()
    Returns the active device ID or the first device ID
search_music()
    Search the music and returns the URI
play_music()
    Search the music and play it
pause_playback()
    Pause the playback
resume_playback()
    Resume the playback
seek_to_position()
    Advance the playback in X miliseconds, if used with 0 value, it will restart the playback
skip_to_next()
    Skip to the next track
skip_to_previous()
    Skip to the previous track
toggle_shuffle()
    Toggle shuffle
get_information()
    Get information of the current track
change_device()
    Change to the next device, if it exists and keeps playing the playback 
'''

import requests, json, base64
from datetime import datetime, timedelta, timezone
from debug import *
import subprocess
import time
from db import get_token, store_token
from integrations_mod import voice_me, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
import re
from dateutil import parser



utc_datetime = datetime.now(timezone.utc)    
token_data = get_token("spotify")
created_at = parser.parse(token_data["spotify"]["created_at"])
EXPIRE_IN = created_at + timedelta(seconds=token_data["spotify"]["expires_in"])
DEVICE_ID = False #Global variable to store the device ID
ACCESS_TOKEN = token_data["spotify"]["access_token"]
REFRESH_TOKEN = token_data["spotify"]["refresh_token"]
print("Access token: ", ACCESS_TOKEN)
print("Old token: ", REFRESH_TOKEN)
print("Expire in: ", EXPIRE_IN)
print("Current time: ", utc_datetime)

def refreshing_token():
    global ACCESS_TOKEN
    try:        
        #If there is a refresh token, checks expiration date
        if REFRESH_TOKEN:
            #If the token is still valid, returns the token
            if EXPIRE_IN > utc_datetime:
                print("Token still valid")
                return ACCESS_TOKEN
            
            #If the token is expired, refreshes the token
            else:

                url = "https://accounts.spotify.com/api/token"
                
                credentials = str(base64.b64encode((SPOTIFY_CLIENT_ID + ':' + SPOTIFY_CLIENT_SECRET).encode('ascii')).decode('ascii'))
                params = {
                    "grant_type": "refresh_token",
                    "refresh_token": REFRESH_TOKEN 
                }
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded", 
                    "Authorization": "Basic " + credentials
                }                            
                response = requests.post(url, headers=headers, params=params)

                if response.status_code == 200:
                    print("Success: ", response.status_code)
                    print(response.content)

                    token = response.json()
                    token["created_at"] = str(utc_datetime)
                    if "refresh_token" not in token:
                        token["refresh_token"] = REFRESH_TOKEN
                    
                    store_token("spotify", json.dumps(token))

                else:
                    print("Error: ", response.status_code)
                    print(response.content)
                    return "Error: " + str(response.status_code)

                print(response.json())

                ACCESS_TOKEN = response.json()["access_token"] 
                return ACCESS_TOKEN
        else:
            return "Refresh token not found, please authenticate first"
    except Exception as e:
        error_handler(e)
        return False

def open_spotify():
    try:
        # Attempt to open Spotify (assuming it's installed as a Debian package or directly)
        subprocess.Popen(["spotify"])
        print("Spotify opened successfully (direct/Debian package).")
    except subprocess.CalledProcessError:
        try:
            # Attempt to open Spotify via Snap
            subprocess.Popen(["snap", "run", "spotify"])
            print("Spotify opened successfully (Snap).")
        except subprocess.CalledProcessError:
            try:
                # Attempt to open Spotify via Flatpak
                subprocess.Popen(["flatpak", "run", "com.spotify.Client"])
                print("Spotify opened successfully (Flatpak).")
            except subprocess.CalledProcessError:
                print("Failed to open Spotify. Please ensure it is installed.")

#Get available devices
def get_device():
    access_token = refreshing_token()     
    try:
        url = "https://api.spotify.com/v1/me/player/devices"
        
        headers = {
            "Authorization": "Bearer " + access_token
            }
        
        print("Headers: ", headers)
    
        response = requests.get(url, headers=headers)
        print(f'Response: {response.json()}')
        print(f'Device length: {len(response.json()["devices"])}')
        for device in response.json()["devices"]:
            if not re.search(str("amzn" + "*"), device["id"], re.IGNORECASE):
                if device["is_active"]:
                    print("Active device found")
                    return device["id"]                    
                elif device["id"]:
                    print("No active devices found")
                    return response.json()["devices"][0]["id"]
        print("No devices found at all")
        return False
    except Exception as e:
        error_handler(e)
        return False

#Search music
def search_music(query, track_type, access_token):
    try: 
        url = "https://api.spotify.com/v1/search"
        params = {
            "q": query,
            "type": track_type,
            "limit": 1,
        }
        headers = {
            "Authorization": "Bearer " + access_token
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code < 300:
            print ("Success (search_music): ", response.status_code)
            print(response.content)
            track_type_selector = track_type + "s"
            track_uri = response.json()[track_type_selector]["items"][0]["uri"]
            print("Track URI: ", track_uri)
            return track_uri              
        else:
            print ("Error (search_music): ", response.status_code)
            print(response.content)
            return False
    except Exception as e:
        error_handler(e)
        return False

#Play the music
def play_music(query, track_type, response_message):
    global DEVICE_ID
    DEVICE_ID = get_device()
    print("Device ID: ", DEVICE_ID)
    while DEVICE_ID == False:
        open_spotify()
        time.sleep(1)
        if get_device():
            DEVICE_ID = get_device()
            print("Device ID: ", DEVICE_ID)
              
    access_token = refreshing_token()
    try:
        track_uri = search_music('"' + query + '"', track_type, access_token)
        if track_uri:
            voice_me(response_message)
        else: 
            return False

        if track_type in ["track", "show", "episode", "audiobook"]:
            data = {"uris": [track_uri] }
        else:
            data = {"context_uri": track_uri }    

        url = "https://api.spotify.com/v1/me/player/play"

        params = {
            "device_id": DEVICE_ID
        }  
        print(f'params: {params}')  
        headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json"
        }    
    
        response = requests.put(url, headers=headers, params=params, data=json.dumps(data))
        if response.status_code == 204:
            print ("Success (play_music): ", response.status_code)
            print(response.content)     
            return False       
        else:
            print ("Error (play_music): ", response.status_code)
            print(response.content)        
            return False
    except Exception as e:
        error_handler(e)
        return False

#Pause the playback
def pause_playback():
    access_token = refreshing_token()
    try:    
        url = "https://api.spotify.com/v1/me/player/pause?device_id=" + DEVICE_ID
        headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json"
            }
        response = requests.put(url, headers=headers)
        print ("Success (pause music): ", response.status_code)
        print(response.content)
        return False
    except Exception as e:
        error_handler(e)
        return False    

#Resume the playback
def resume_playback():
    access_token = refreshing_token()
    url = "https://api.spotify.com/v1/me/player/play?device_id=" + DEVICE_ID
    
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
        }

    try:
        response = requests.put(url, headers=headers)
        print ("Success (pause music): ", response.status_code)
        print(response.content)
        return False
    except Exception as e:
        error_handler(e)
        return False
    
#Advance the playback in X miliseconds
def seek_to_position(position_ms):    
    access_token = refreshing_token()
    
    url = "https://api.spotify.com/v1/me/player/seek?device_id=" + DEVICE_ID
    
    headers = {
        "Authorization": "Bearer " + access_token
        }
    if position_ms < 0:
        current_position = get_information()["progress_ms"]
        if current_position + position_ms < 0:
            position_ms = 0
        else:
            position_ms = current_position + position_ms
    params = {
        "position_ms": position_ms
    }

    try:
        response = requests.put(url, headers=headers, params=params)
        print("Success (seek_to_position): ", response.status_code)
        print(response.content)
        return False
    except Exception as e:
        error_handler(e)
        return False

#Skip to the next track
def skip_to_next(jumps=1):
    access_token = refreshing_token()
    url = "https://api.spotify.com/v1/me/player/next?device_id=" + DEVICE_ID
    
    headers = {
        "Authorization": "Bearer " + access_token,
        }
    try:            
        for i in range(jumps):
            response = requests.post(url, headers=headers)
            if response.status_code == 204:
                print("Success (skip_to_next): ", response.status_code)
                print(response.content)            
            else:
                print("Error (skip_to_next): ", response.status_code)
                print(response.content)
            return False
    except Exception as e:
        error_handler(e)
        return False

#Skip to the previous track
def skip_to_previous(jumps=1):    
    access_token = refreshing_token()
    url = "https://api.spotify.com/v1/me/player/previous?device_id=" + DEVICE_ID
    
    headers = {
        "Authorization": "Bearer " + access_token,
        }
    try:
        for i in range(jumps):
            response = requests.post(url, headers=headers)
            if response.status_code == 204:
                print("Success (skip_to_previous): ", response.status_code)
                print(response.content)            
            else:
                print("Error (skip_to_previous): ", response.status_code)
                print(response.content)
            return False
    except Exception as e:
            error_handler(e)
            return False

#Get Playback status
def playback_status(): 
    access_token = refreshing_token()   
    url = "https://api.spotify.com/v1/me/player"
    
    headers = {
        "Authorization": "Bearer " + access_token
        }
    try:
        response = requests.get(url, headers=headers)
        if response:
            print("Success (playback_status): ", response.status_code)
            print(response.content)
            return response.json()
        else:
            return False
    except Exception as e:
        error_handler(e)
        return False

#Toggle shuffle 
def toggle_shuffle():    
    access_token = refreshing_token()    
    shuffle_state = playback_status().get("shuffle_state")
    if shuffle_state == "false":
        shuffle_state = "true"
    elif shuffle_state == "true":
        shuffle_state = "false" 


    if shuffle_state != False:
        url = "https://api.spotify.com/v1/me/player/shuffle?state=" + shuffle_state + "&device_id=" + DEVICE_ID
    
        headers = {
            "Authorization": "Bearer " + access_token
        }

        try:
            response = requests.put(url, headers=headers)
            print("Success (toggle_shuffle): ", response.status_code)
            print(response.content)
            return False
        except Exception as e:
            error_handler(e)
            return False

#Get information of the current track (still in development)
# def get_information():    
#     information = {}
#     access_token = refreshing_token()
#     url = "https://api.spotify.com/v1/me/player/currently-playing"
    
#     headers = {
#         "Authorization": "Bearer " + access_token
#         }
#     try:
#         response = requests.put(url, headers=headers)
#         if response:
#             information["artist_name"] = response.json()["item"]["artists"][0]["name"]
#             information["track_name"] = response.json()["item"]["name"]
#             information["duration_ms"] = response.json()["item"]["duration_ms"]
#             information["progress_ms"] = response.json()["progress_ms"]
#         print("Success (get_information): ", response.status_code)
#         print(response.content)
#         return information
#     except Exception as e:
#         error_handler(e)
#         return False
  
#Change to the next device, if it exists and keeps playing the playback  
def change_device():
    access_token = refreshing_token()
    url = "https://api.spotify.com/v1/me/player/devices"
    
    headers = {
        "Authorization": "Bearer " + access_token,
        }
    try:
        response = requests.put(url, headers=headers)
        is_next = False        
        if len(response.json()["devices"]) > 1:
            for i, device in response.json()["devices"]:
                if is_next == False and device["id"] == DEVICE_ID:
                    is_next = True 
                elif is_next == False and len(response.json()["devices"]) == i+1:
                    return "No additional devices found"
                elif is_next == True:
                    url = "https://api.spotify.com/v1/me/player"
                    headers = {
                        "Authorization": "Bearer " + access_token,
                        "Content-Type": "application/json"
                    }
                    data = {
                        "device_ids": [
                            device["id"]
                        ],
                        "play": "true"
                    }
                    try:
                        response = requests.put(url, headers=headers, data=json.dumps(data))
                        print("Success (change_device): ", response.status_code)
                        print(response.content)
                    except:
                        print("Error (change_device): ", response.status_code)
                        print(response.content)
               
        return False
    except Exception as e: 
        error_handler(e)
        return False