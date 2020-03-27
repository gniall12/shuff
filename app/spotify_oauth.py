import json
import time
import logging

from flask import session, abort
from authlib.integrations.flask_client import OAuth

from .config import (
    auth_base_url, token_base_url, client_id,
    client_secret, scope, base_url
)

log = logging.getLogger(__name__)


def get_spotify_oauth_token(name):
    try:
        return session['access_token']
    except KeyError:
        abort(400, 'No access token')


oauth = OAuth(fetch_token=get_spotify_oauth_token)

oauth.register(
    name='spotify',
    client_id=client_id,
    client_secret=client_secret,
    access_token_url=token_base_url,
    authorize_url=auth_base_url,
    authorize_params={'scope': scope, 'show_dialog': True},
    api_base_url=base_url,
)


def get_user_id():
    log.info('Getting user id')
    user = oauth.spotify.get('me')
    return user.json()['id']


def get_user_playlists():
    log.info('Getting user playlists')
    spotify = oauth.spotify
    playlists = spotify.get('me/playlists?limit=50')
    if 'error' in playlists.json():
        log.error(playlists.json())
    if(playlists.status_code == 401):
        abort(401, 'Access token expired')
    return playlists.json()


def get_playlist_tracks(playlist_id):
    log.info(f'Getting playlist tracks for playlist {playlist_id}')
    url = f'playlists/{playlist_id}/tracks'
    playlist_tracks = []
    # Can only get 100 tracks per request - multiple requests may be needed
    while url:
        tracks = oauth.spotify.get(url)
        if 'error' in tracks.json():
            log.error(tracks.json())
            abort(500, 'Could not retrieve playlist tracks')
        playlist_tracks.extend(tracks.json()['items'])
        url = None
        if 'next' in tracks.json() and tracks.json()['next']:
            url = tracks.json()['next'].split(base_url)[1]
    log.info(f'{len(playlist_tracks)} found')
    return [track['track'] for track in playlist_tracks]


def get_artist_top_tracks(artist_id, attempt_count=0):
    tracks = oauth.spotify.get(
        f'artists/{artist_id}/top-tracks?country=IE')
    if 'error' in tracks.json():
        log.error(tracks.json())
        if(tracks.status_code == 429) and attempt_count < 3:
            attempt_count += 1
            log.info(f'Rate limit exceeded - attempt number {attempt_count}')
            time.sleep(5)
            return get_artist_top_tracks(artist_id, attempt_count)
    try:
        return tracks.json()['tracks']
    except KeyError:
        log.error('Could not retrieve top tracks for artist id: {artist_id}')
        return []


def create_new_playlist(playlist_name, user_id):
    log.info('Creating new playlist')
    url = f'users/{user_id}/playlists'
    body = {'name': f'{playlist_name} - Shuffed'}
    new_playlist = oauth.spotify.post(
        url, json=body)
    if 'error' in new_playlist.json():
        log.error(new_playlist.json())
        abort(500, 'Error creating playlist')
    return new_playlist.json()


def add_tracks_to_playlist(playlist_id, tracks):
    log.info("Adding new tracks to playlist")
    if(len(tracks) == 0):
        abort(500, 'No tracks found to add to playlist')
    url = f'playlists/{playlist_id}/tracks'
    n = 100
    tracks_split = [tracks[i:i+n] for i in range(0, len(tracks), n)]
    # Can only add 100 tracks per request - multiple requests may be needed
    for tracks_chunk in tracks_split:
        body = {'uris': tracks_chunk}
        snapshot = oauth.spotify.post(url, json=body)
        if 'error' in snapshot.json():
            log.error(snapshot.json())
    return snapshot.json()
