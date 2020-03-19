import os
import logging

from flask import Flask, redirect, url_for, request, session, abort, Response, render_template
from flask_cors import CORS

from .config import secret_key, frontend_url
from .shuffler import shuffle
from .spotify_oauth import oauth, spotify, get_user_playlists

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)
app.config['SECRET_KEY'] = secret_key
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


@app.route('/', methods=['GET'])
def home():
    if('access_token' not in session):
        return(redirect(url_for('login')))
    try:
        playlists = get_user_playlists()
    except:
        return redirect(url_for('login'))
    return render_template('home.html', playlists=playlists)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login-redirect', methods=['GET'])
def login_redirect():
    return spotify.authorize(callback=url_for('handle_token', _external=True))


@app.route('/callback', methods=['GET'])
def handle_token():
    resp = spotify.authorized_response()
    if resp is None or resp.get('access_token') is None:
        session.pop('access_token', None)
        return redirect(url_for('home'))
    session['access_token'] = (resp['access_token'], '')
    return redirect(url_for('home'))


@app.route('/shuffle', methods=['GET'])
def shuffle_playlist():
    if('id' not in request.args or 'name' not in request.args):
        abort(400)
    print(request.args)
    playlist_id = request.args['id']
    playlist_name = request.args['name']
    new_playlist = shuffle(playlist_id, playlist_name)
    return new_playlist


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('access_token', None)
    return redirect(url_for('login'))
