from flask import Flask, render_template, redirect, request
from flask_socketio import SocketIO, emit
from audio_input import start_stream, CONVERSATION_MODE
from settings import *
import json, random, string, base64, requests
from urllib.parse import urlencode
from datetime import datetime
from debug import *
from db import store_data, store_token
from choices import timezones, languages
import threading
import time


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
    thread_running.clear()
    thread = socketio.start_background_task(start_stream(socketio, thread_running))
    emit('stream_status', {'status': 'Charlie is ON'})

@socketio.on('stop_stream')
def handle_stop():
    global thread_running
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
def settings_site():
    if request.method == 'POST':
        for item in request.form:
            try: 
                store_data("settings", item, request.form[item])
            except Exception as e:
                error_handler(e)
    
    if request.method == 'GET':
        options = {
            "timezone": timezones,
            "language": languages,
            "music_app": (
                {"value":"spotify", "label":"Spotify"},            
            ),
            "transcription_system": (
                {"value":"open_ai", "label":"Open AI"},
            ),
            "wake_system": (
                {"value":"charlie", "label":"GM Charlie"},
                {"value":"open_ai", "label":"Open AI"}
            ),
            "wake_word": (
                {"value":"charlie", "label":"Charlie"},
            ),
            "prompt_system": (
                {"value":"open_ai", "label":"Open AI"},
            ),
            "voice_system": (
                {"value":"open_ai", "label":"Open AI"},
            )
        }
        return render_template('settings.html', placeholder_data=settings, options=options)
  


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        for item in request.form:
            try: 
                store_data("admin", item, request.form[item])
            except Exception as e:
                error_handler(e)
        
    if request.method == 'GET':
        print(admin_settings)
        return render_template('admin.html', placeholder_data=admin_settings)

@app.route('/integrations', methods=['GET', 'POST'])
def integrations():
    return render_template('integrations.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
