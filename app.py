from flask import Flask, render_template, redirect, request
from settings import *
import json, random, string, base64, requests
from urllib.parse import urlencode
from datetime import datetime
from debug import *
from db import get_values, CONN, store_data, store_token


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/auth/spotify', methods=['GET', 'POST'])
#For more information about the authorization flow, see https://developer.spotify.com/documentation/web-api/tutorials/code-flow

def spotify_auth():

    redirect_uri = 'http://127.0.0.1:5000/auth/spotify/callback'
    url = 'https://accounts.spotify.com/authorize'

    letters = string.ascii_letters   

    state = ''.join(random.choice(letters) for i in range(16))
    scope = 'user-read-private user-read-email streaming app-remote-control user-read-currently-playing user-read-playback-state user-modify-playback-state'

    params =     {
        'response_type': 'code',
        'client_id': SPOTIFY_CLIENT_ID,
        'scope': scope,
        'redirect_uri': redirect_uri,
        'state': state,
        'show_dialog': True
        }


    return redirect(url + '?' + urlencode(params))

#Callback function for the authorization flow
@app.route('/auth/spotify/callback', methods=['GET', 'POST'])
def spotify_callback():
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        redirect_uri = 'http://127.0.0.1:5000/auth/spotify/callback'


        #Request access and refresh tokens
        if state == None:
            return "Authorization failed"
        else:
            url = 'https://accounts.spotify.com/api/token'
            params = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri
            }

            credentials = str(base64.b64encode((SPOTIFY_CLIENT_ID + ':' + SPOTIFY_CLIENT_SECRET).encode('ascii')).decode('ascii'))

            print('credentials ', credentials)

            headers = { 
                'content-type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + credentials
            }


            response = requests.post(url, data=params, headers=headers)
            
            if response.status_code == 200:

                token = response.json()
                token["created_at"] = str(datetime.utcnow())
                store_token("spotify", json.dumps(token))
            else:
                print(response.status_code)
                print(response.content)


        print(response.status_code)
        print(response.content)

        return "Authentication successful! Please return to the previous page."
    except Exception as e:
        error_handler(e)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        for item in request.form:
            try: 
                store_data("settings", item, request.form[item])
            except Exception as e:
                error_handler(e)
    
    if request.method == 'GET':
        results = get_values(settings)
        options = {
            "timezone": (
                {"value":"America/New_York", "label":"America/New_York"},
                {"value":"America/Chicago", "label":"America/Chicago"}                
            ),
            "language": (
                {"value":"en-US", "label":"English US"},
                {"value":"pt-BR", "label":"Brazilian Portuguese"}                      
            ),
            "sound_app": (
                {"value":"spotify", "label":"Spotify"}
            ),
            "transcription_system": (
                {"value":"open_ai", "label":"Open AI"}
            ),
            "wake_system": (
                {"value":"charlie", "label":"GM Charlie"},
                {"value":"open_ai", "label":"Open AI"}
            ),
            "wake_word": (
                {"value":"charlie", "label":"Charlie"}
            ),
            "prompt_system": (
                {"value":"open_ai", "label":"Open AI"}
            ),
            "voice_system": (
                {"value":"open_ai", "label":"Open AI"}
            )
        }
        print(settings)
        return render_template('settings.html', placeholder_data=results, options=options)
  


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        for item in request.form:
            try: 
                store_data("admin", item, request.form[item])
            except Exception as e:
                error_handler(e)
        
    if request.method == 'GET':
        results = get_values(admin_settings)
        return render_template('admin.html', placeholder_data=results)

@app.route('/integrations', methods=['GET', 'POST'])
def integrations():
    return render_template('integrations.html')

@app.route('/images/<path:path>')
def send_image(path):
    return send_from_directory('images', path)



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
