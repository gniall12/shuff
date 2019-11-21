import requests
import json
from config import base_url
from flask import abort


def get_playlist_tracks(playlist_id, headers):
    offset = 0
    num_tracks_remaining = None
    tracks = []
    # Can only get 100 tracks per request - multiple requests may be needed
    while True:
        params = {'offset': offset}
        url = f'{base_url}playlists/{playlist_id}/tracks'
        r = requests.get(url, headers=headers, params=params)
        if not num_tracks_remaining:
            num_tracks_remaining = r.json()['total']
        tracks.extend(r.json()['items'])
        num_tracks_remaining -= 100
        if num_tracks_remaining <= 0:
            break
        offset += 100
    return [track['track'] for track in tracks]


def get_artist_top_tracks(artist_id, headers):
    url = f'{base_url}artists/{artist_id}/top-tracks?country=IE'
    r = requests.get(url, headers=headers)
    tracks = r.json()['tracks']
    return tracks


def create_new_playlist(playlist_name, user_id, track_ids, headers):
    headers['Content-Type'] = 'application/json'
    url = f'{base_url}users/{user_id}/playlists'
    body = json.dumps({'name': f'{playlist_name} - Shuffed'})
    r = requests.post(url, data=body, headers=headers)
    return r.json()


def add_tracks_to_playlist(playlist_id, tracks, headers):
    url = f'{base_url}playlists/{playlist_id}/tracks'
    n = 100
    tracks_split = [tracks[i:i+n] for i in range(0, len(tracks), n)]
    # Can only add 100 tracks per request - multiple requests may be needed
    for tracks_chunk in tracks_split:
        body = json.dumps({'uris': tracks_chunk})
        r = requests.post(url, data=body, headers=headers)
    return r.text
