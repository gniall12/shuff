import json
from flask import session, abort, Response
from flask_oauthlib.client import OAuth, OAuthResponse
from config import (
    auth_base_url, token_base_url, client_id,
    client_secret, scope, base_url
)

oauth = OAuth()

spotify = oauth.remote_app(
    'spotify',
    consumer_key=client_id,
    consumer_secret=client_secret,
    request_token_params={'scope': scope, 'show_dialog': True},
    base_url=base_url,
    request_token_url=None,
    access_token_method='POST',
    access_token_url=token_base_url,
    authorize_url=auth_base_url
)


def get_user_id():
    user = spotify.get('me')
    return user.data['id']


def get_user_playlists():
    params = {'limit': 50}
    playlists = spotify.get('me/playlists', data=params)
    if(playlists.status == 401):
        abort(Response('Access token expired', 401))
    return playlists.data


def get_playlist_tracks(playlist_id):
    offset = 0
    num_tracks_remaining = None
    tracks = []
    # Can only get 100 tracks per request - multiple requests may be needed
    while True:
        params = {'offset': offset}
        curr_tracks = spotify.get(
            f'playlists/{playlist_id}/tracks', data=params)
        if not num_tracks_remaining:
            num_tracks_remaining = curr_tracks.data['total']
        tracks.extend(curr_tracks.data['items'])
        num_tracks_remaining -= 100
        if num_tracks_remaining <= 0:
            break
        offset += 100
    return [track['track'] for track in tracks]


def get_artist_top_tracks(artist_id):
    tracks = spotify.get(
        f'artists/{artist_id}/top-tracks?country=IE')
    return tracks.data['tracks']


def create_new_playlist(playlist_name, user_id, track_ids):
    print("Creating new playlist")
    url = f'users/{user_id}/playlists'
    body = json.dumps({'name': f'{playlist_name} - Shuffed'})
    new_playlist = spotify.post(
        url, data=body, content_type='application/json')
    return new_playlist.data


def add_tracks_to_playlist(playlist_id, tracks):
    print("Adding new tracks to playlist")
    url = f'playlists/{playlist_id}/tracks'
    n = 100
    tracks_split = [tracks[i:i+n] for i in range(0, len(tracks), n)]
    # Can only add 100 tracks per request - multiple requests may be needed
    for tracks_chunk in tracks_split:
        body = json.dumps({'uris': tracks_chunk})
        snapshot = spotify.post(
            url, data=body, content_type='application/json')
    return snapshot.data


@spotify.tokengetter
def get_spotify_oauth_token():
    try:
        return session['access_token']
    except KeyError:
        abort(Response('No access token', 400))