from flask import Flask, redirect, request, abort, session, jsonify
from flask_cors import CORS, cross_origin
import requests
import urllib
import random
import string

from config import (
    auth_base_url, token_base_url, client_id, client_secret, redirect_uri,
    scope, response_type, secret_key, frontend_url, client_id_b64
)

from shuffler import shuffle

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)
app.config['SECRET_KEY'] = secret_key

users = {}


@app.route('/')
def login_redirect():
    random_string = generate_random_string()
    session['id'] = random_string
    users[session['id']] = {}
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': response_type,
        'state': random_string,
        'show_dialog': True
    }
    url = auth_base_url + '?' + urllib.parse.urlencode(params)
    return redirect(url)


@app.route('/callback')
def handle_token():
    code = request.args.get('code')
    r = requests.post(
        token_base_url,
        data={'grant_type': 'authorization_code',
              'code': code, 'redirect_uri': redirect_uri},
        headers={
            'Authorization': 'Basic ' + client_id_b64,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Access-Control-Allow-Origin': '*'
        }
    )
    users[request.args.get('state')]['access_token'] = r.json()['access_token']
    return redirect(frontend_url)


@app.route('/userinfo')
def get_user_info():
    access_token = users[session['id']]['access_token']
    r = requests.get(base_url + 'me',
                     headers={'Authorization': 'Bearer ' + access_token})
    session['user_id'] = r.json()['id']
    return r.text


@app.route('/playlists')
def get_user_playlists():
    access_token = users[session['id']]['access_token']
    params = {'limit': 50}
    r = requests.get(base_url + 'me/playlists', params=params,
                     headers={'Authorization': 'Bearer ' + access_token})
    return r.text


@app.route('/shuffle', methods=['POST'])
def shuffle_playlist():
    playlist = request.json['playlist']
    access_token = users[session['id']]['access_token']
    user_id = session['user_id']
    new_playlist = shuffle(playlist, user_id, access_token)
    return new_playlist


@app.route('/logout', methods=['GET'])
def logout():
    [session.pop(key) for key in list(session.keys())]
    return {'status': 'Logged out'}


def generate_random_string(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
