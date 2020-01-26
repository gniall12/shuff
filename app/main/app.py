from flask import Flask, redirect, url_for, request, session
from flask_cors import CORS
from config import secret_key, frontend_url
from shuffler import shuffle
from spotify_oauth import oauth, spotify, get_user_playlists

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)
app.config['SECRET_KEY'] = secret_key


@app.route('/login')
def login_redirect():
    return spotify.authorize(callback=url_for('handle_token', _external=True))


@app.route('/callback')
def handle_token():
    resp = spotify.authorized_response()
    if resp is None or resp.get('access_token') is None:
        session.pop('access_token', None)
        return redirect(frontend_url)
    session['access_token'] = (resp['access_token'], '')
    return redirect(frontend_url)


@app.route('/playlists')
def playlists():
    return get_user_playlists()


@app.route('/shuffle', methods=['POST'])
def shuffle_playlist():
    playlist = request.json['playlist']
    new_playlist = shuffle(playlist)
    return new_playlist


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('access_token', None)
    return {'status': 'Logged out'}


if __name__ == '__main__':
    oauth.init_app(app)
    app.run(host='0.0.0.0', debug=True)