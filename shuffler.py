import requests
import json
import config
from flask import abort

base_url = config.base_url

def shuffle(playlist, user_id, access_token):
    playlist_id = playlist['id']
    playlist_name = playlist['name']
    headers={'Authorization': 'Bearer ' + access_token}
    old_tracks = get_playlist_tracks(playlist_id, headers)
    old_artist_ids = get_old_artists_ids(old_tracks)
    new_track_ids = get_new_track_ids(old_artist_ids, old_tracks, headers)
    new_playlist_id = create_new_playlist(playlist_name, user_id, new_track_ids, headers)
    add_tracks_to_playlist(new_playlist_id, new_track_ids, headers)
    return new_track_ids

def get_playlist_tracks(playlist_id, headers):
    print('Getting playlist tracks...')
    url = f'{base_url}playlists/{playlist_id}/tracks'
    r = requests.get(url, headers=headers)
    tracks = r.json()['items']
    return [track['track'] for track in tracks]

def get_old_artists_ids(tracks):
    print('Getting old artist ids...')
    artist_ids = [track['artists'][0]['id'] for track in tracks]
    # Some artists have no ID - remove Nones from list
    artist_ids_nones_removed = list(filter(None, artist_ids)) 
    return artist_ids_nones_removed

def get_new_track_ids(old_artist_ids, old_tracks, headers):
    print('Getting new track ids...')
    new_tracks = []
    for artist_id in old_artist_ids:
        track_added = False
        i = 0
        artist_top_tracks = get_artist_top_tracks(artist_id, headers)
        while not track_added and i<len(artist_top_tracks):
            if not track_exists(artist_top_tracks[i], old_tracks + new_tracks):
                new_tracks.append(artist_top_tracks[i])
                track_added = True
            i += 1
    return [track['uri'] for track in new_tracks]

def get_artist_top_tracks(artist_id, headers):
    url = f'{base_url}artists/{artist_id}/top-tracks?country=IE'
    r = requests.get(url, headers=headers)
    tracks = r.json()['tracks']
    return tracks

def track_exists(track, existing_tracks):
    for existing_track in existing_tracks:
        if track['id'] == existing_track['id'] or track['name'] == existing_track['name']:
            return True
    return False

def create_new_playlist(playlist_name, user_id, track_ids, headers):
    headers['Content-Type'] = 'application/json'
    url = f'{base_url}users/{user_id}/playlists'
    body = json.dumps({'name': f'{playlist_name} - Shuffed'})
    r = requests.post(url, data=body, headers=headers)
    playlist_id = r.json()['id']
    return playlist_id

def add_tracks_to_playlist(playlist_id, tracks, headers):
    url = f'{base_url}playlists/{playlist_id}/tracks'
    body = json.dumps({'uris': tracks})
    r = requests.post(url, data=body, headers=headers)
    return r.text
