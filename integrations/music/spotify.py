import requests, json, base64
from settings import *
from datetime import datetime, timedelta
from controllers.music import *
from debug import *

if VOICE_SYSTEM != "none":
    voice_me = getattr( importlib.import_module("integrations.ai." + VOICE_SYSTEM), "voice_me")
    print_me("VOICE_SYSTEM: ", VOICE_SYSTEM)  

utc_datetime = datetime.utcnow()    

token_data = json.loads(get_token("spotify"))
OLD_TOKEN = token_data["refresh_token"]
EXPIRE_AT = datetime.strptime(token_data["created_at"], '%Y-%m-%d %H:%M:%S.%f') + timedelta(seconds=token_data["expires_in"])


'''
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

print_me("OLD_TOKEN:" , OLD_TOKEN)

def refreshing_token():
    #If there is a refresh token, checks expiration date
    if OLD_TOKEN:

        #If the token is still valid, returns the token
        if EXPIRE_AT > utc_datetime:
            print_me("Token still valid")
            return token_data["access_token"]
        
        #If the token is expired, refreshes the token
        else:

            url = "https://accounts.spotify.com/api/token"
            
            credentials = str(base64.b64encode((SPOTIFY_CLIENT_ID + ':' + SPOTIFY_CLIENT_SECRET).encode('ascii')).decode('ascii'))

            params = {
                "grant_type": "refresh_token",
                "refresh_token": OLD_TOKEN 
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded", 
                "Authorization": "Basic " + credentials
                }
            
            response = requests.post(url, headers=headers, params=params)

            if response.status_code == 200:
                print_me("Success: ", response.status_code)
                print_me(response.content)

                token = response.json()
                token["created_at"] = str(datetime.utcnow())
                if "refresh_token" not in token:
                    token["refresh_token"] = OLD_TOKEN

                with open('tokens/spotify.json', 'w', encoding='utf-8') as outfile:
                    json.dump(token, outfile, ensure_ascii=False, indent=4)

            else:
                print_me("Error: ", response.status_code)
                print_me(response.content)
                return "Error: " + str(response.status_code)
            

            print_me(response.json())

            ACCESS_TOKEN = response.json()["access_token"] 

            return ACCESS_TOKEN

    else:
        return "Refresh token not found, please authenticate first"

#Get available devices
def get_device():    
    
    url = "https://api.spotify.com/v1/me/player/devices"
    
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        }

    try:
        response = requests.put(url, headers=headers)
        if len(response.json()["devices"]):
            for device in response.json()["devices"]:
                if device["is_active"]:
                    return device["id"]
                else:
                    return response.json()["devices"][0]["id"]
        else:
            return "No devices found"        

    except Exception as e:
        return error_handler(e)
    


ACCESS_TOKEN = refreshing_token()
DEVICE_ID = get_device()



#Search music
def search_music(query, track_type):
    url = "https://api.spotify.com/v1/search"
    params = {
        "q": query,
        "type": track_type,
        "limit": 1,

    }
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN
        }

    try: 
        response = requests.get(url, headers=headers, params=params)
        
        print_me("Success: ", response.status_code)
        print_me(response.content)

        track_type_selector = track_type + "s"       

        track_uri = response.json()[track_type_selector]["items"][0]["uri"]
        print_me("Track: ", track_uri)
        return track_uri
    except Exception as e:
        return error_handler(e)

#Play the music
def play_music(query, track_type, response_message):
    
    try: 
        track_uri = search_music(query, track_type)
        if track_uri:
            voice_me(response_message)
        else: 
            return False
    except:
        return False

    if track_type in ["track", "show", "episode", "audiobook"]:
        data = {"uris": [track_uri] }
    else:
        data = {"context_uri": track_uri }    

    url = "https://api.spotify.com/v1/me/player/play"
    
    params = {
        "device_id": DEVICE_ID
    }   
    
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json"
        }
    
    try:
        response = requests.put(url, headers=headers, params=params, data=json.dumps(data))
        print ("Success (play_music): ", response.status_code)
        print_me(response.content)
        
        return True
    except Exception as e:
        return error_handler(e)

#Pause the playback
def pause_playback():    
    
    url = "https://api.spotify.com/v1/me/player/pause"
    
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json"
        }

    try:
        response = requests.put(url, headers=headers)
        print ("Success (pause music): ", response.status_code)
        print_me(response.content)
        return response
    except Exception as e: 
        return error_handler(e)
    

#Resume the playback
def resume_playback():    
    
    url = "https://api.spotify.com/v1/me/player/play"
    
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json"
        }

    try:
        response = requests.put(url, headers=headers)
        print ("Success (pause music): ", response.status_code)
        print_me(response.content)
        return response
    except Exception as e:
        return error_handler(e)
    
#Advance the playback in X miliseconds
def seek_to_position(position_ms):    
    
    url = "https://api.spotify.com/v1/me/player/seek"
    
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN
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
        print ("Success (seek_to_position): ", response.status_code)
        print_me(response.content)
        return response
    except Exception as e:
        return error_handler(e)

#Skip to the next track
def skip_to_next(jumps=1):    
    
    url = "https://api.spotify.com/v1/me/player/next"
    
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        }
    for i in range(jumps):
        try:            
            response = requests.put(url, headers=headers)
            print ("Success (skip_to_next): ", response.status_code)
            print_me(response.content)
            return response
        except Exception as e:
            return error_handler(e)

#Skip to the previous track
def skip_to_previous(jumps=1):    
    
    url = "https://api.spotify.com/v1/me/player/previous"
    
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        }
    for i in range(jumps):
        try:
            response = requests.put(url, headers=headers)
            print ("Success (skip_to_previous): ", response.status_code)
            print_me(response.content)
            return response
        except Exception as e:
            return error_handler(e)

#Toggle shuffle 
def toggle_shuffle():    
    
    url = "https://api.spotify.com/v1/me/player/shuffle"
    
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN
        }

    try:
        response = requests.put(url, headers=headers)
        print ("Success (toggle_shuffle): ", response.status_code)
        print_me(response.content)
        return response
    except Exception as e:
        return error_handler(e)

#Get information of the current track
def get_information():    
    information = {}
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN
        }
    try:
        response = requests.put(url, headers=headers)
        if response:
            information["artist_name"] = response.json()["item"]["artists"][0]["name"]
            information["track_name"] = response.json()["item"]["name"]
            information["duration_ms"] = response.json()["item"]["duration_ms"]
            information["progress_ms"] = response.json()["progress_ms"]
        print ("Success (get_information): ", response.status_code)
        print_me(response.content)
        return information
    except Exception as e:
        return error_handler(e)
  
#Change to the next device, if it exists and keeps playing the playback  
def change_device():    
    
    url = "https://api.spotify.com/v1/me/player/devices"
    
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
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
                        "Authorization": "Bearer " + ACCESS_TOKEN,
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
                        print ("Success (change_device): ", response.status_code)
                        print_me(response.content)
                        return response
                    except:
                        print_me("Error (change_device): ", response.status_code)
                        print_me(response.content)
                        return "Error: " + str(response.status_code)
               
        else:
            return "No additional devices found"        

        print_me(response.content)
    except exception as e:
        return error_handler(e)