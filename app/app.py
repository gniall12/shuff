import os
import logging

from flask import Flask, redirect, url_for, request, session, abort, render_template, make_response

from .config import secret_key, frontend_url
from .shuffler import shuffle
from .spotify_oauth import oauth, get_user_playlists


def create_app():
    app = Flask(__name__)
    oauth.init_app(app)
    app.config['SECRET_KEY'] = secret_key
    return app


app = create_app()
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
    return oauth.spotify.authorize_redirect(url_for('handle_token', _external=True))


@app.route('/callback', methods=['GET'])
def handle_token():
    token = oauth.spotify.authorize_access_token()
    if token is None:
        session.pop('access_token', None)
        return redirect(url_for('home'))
    session['access_token'] = token
    return redirect(url_for('home'))


@app.route('/shuffle', methods=['GET'])
def shuffle_playlist():
    if('id' not in request.args or 'name' not in request.args):
        abort(400)
    playlist_id = request.args['id']
    playlist_name = request.args['name']
    new_playlist = shuffle(playlist_id, playlist_name)
    return new_playlist


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('access_token', None)
    return redirect(url_for('login'))


@app.route('/error', methods=['GET'])
def reroute_error():
    code = int(request.args['code'])
    message = request.args['message']
    return render_template('error.html', error_message=message), code


@app.errorhandler(400)
def bad_request(error):
    if(str(request.url_rule).strip() == str(url_for('shuffle_playlist')).strip()):
        return make_response(str(error), 400)
    return render_template('error.html', error_message=error), 400


@app.errorhandler(401)
def unauthorised(error):
    if(str(request.url_rule).strip() == str(url_for('shuffle_playlist')).strip()):
        return make_response(str(error), 401)
    return render_template('error.html', error_message=error), 401


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error_message='This page does not exist'), 404


@app.errorhandler(500)
def server_error(error):
    if(str(request.url_rule).strip() == str(url_for('shuffle_playlist')).strip()):
        return make_response(str(error), 500)
    return render_template('error.html', error_message=error), 500
