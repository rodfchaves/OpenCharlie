"""
This is the main file of the project. It contains the Flask app and the socketio server.

The app is used to render the HTML templates and the socketio server is used to communicate with the frontend.

The app has the following routes:
    - /: The home route, it renders the index.html template.
    - /auth/spotify: The route to authenticate with Spotify. It redirects to the Spotify authorization page.
    - /auth/spotify/callback: The callback route for the Spotify authentication. It stores the access and refresh tokens in the database.
    - /settings: The route to change the settings of the assistant. It renders the settings.html template.
    - /admin: The route to change the admin settings of the assistant.It renders the admin.html template. If you want to serve this app inside a server, this should be protected by a login system.
    - /integrations: The route to see the integrations of the assistant. It renders the integrations.html template.
    
"""

from flask import Flask, render_template, redirect, request
from flask_socketio import SocketIO, emit
from audio_input import start_stream
import json, random, string, base64, requests
from urllib.parse import urlencode
from datetime import datetime, timezone
from debug import *
from db import store_data_settings, store_data_admin, store_token
from choices import timezones, languages
import threading
import time
import importlib

settings_mod = importlib.import_module("settings")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None
thread_running = threading.Event()


@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('start_stream')
def handle_start():
    global thread
    global thread_running
    if thread is None or thread_running.is_set():
        thread_running.clear()
        thread = socketio.start_background_task(start_stream(socketio, thread_running))
        emit('stream_status', {'status': 'Charlie is ON'})

@socketio.on('stop_stream')
def handle_stop():
    global thread_running
    if not thread_running.is_set():
        thread_running.set()
        time.sleep(1)
        emit('stream_status', {'status': 'Charlie is OFF'})


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
        'client_id': settings_mod.SPOTIFY_CLIENT_ID,
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

            credentials = str(base64.b64encode((settings_mod.SPOTIFY_CLIENT_ID + ':' + settings_mod.SPOTIFY_CLIENT_SECRET).encode('ascii')).decode('ascii'))

            headers = { 
                'content-type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + credentials
            }


            response = requests.post(url, data=params, headers=headers)
            
            if response.status_code == 200:

                token = response.json()
                token["created_at"] = str(datetime.now(timezone.utc))
                store_token("spotify", json.dumps(token))
                print(f"Token stored: {token}")
            else:
                print(response.status_code)
                print(response.content)
        time.sleep(2)
        redirect('/settings')
        return "Authentication successful! Please return to the previous page."
    except Exception as e:
        error_handler(e)

@app.route('/settings', methods=['GET', 'POST'])
def settings_site():
    options = {
        "timezone": timezones,
        "language": languages,
        "music_integration": (
            {"value":"spotify", "label":"Spotify"},            
        ),
        "transcription_integration": (
            {"value":"openai", "label":"Open AI"},
        ),
        "wake_integration": (
            {"value":"charlie", "label":"GM Charlie"},
        ),
        "wake_word": (
            {"value":"charlie", "label":"Charlie"},
        ),
        "tools_integration": (
            {"value":"openai", "label":"Open AI"},
        ),
        "voice_integration": (
            {"value":"openai", "label":"Open AI"},
        )
    }
    if request.method == 'POST':
        try: 
            store_data_settings(list(request.form.items()))
            importlib.reload(settings_mod)
            return render_template('settings.html', placeholder_data=settings_mod.settings, options=options)
                
        except Exception as e:                
            error_handler(e)
            return render_template('settings.html', placeholder_data=settings_mod.settings, options=options)
    
    elif request.method == 'GET':
        return render_template('settings.html', placeholder_data=settings_mod.settings, options=options)
  


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        try: 
            store_data_admin(list(request.form.items()))
            importlib.reload(settings_mod)
            return render_template('admin.html', placeholder_data=settings_mod.admin_settings)

        except Exception as e:
            error_handler(e)
        
    elif request.method == 'GET':
        return render_template('admin.html', placeholder_data=settings_mod.admin_settings)

@app.route('/integrations', methods=['GET', 'POST'])
def integrations():
    return render_template('integrations.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
