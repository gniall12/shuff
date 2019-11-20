from collections import Counter
import random
from spotify import get_playlist_tracks, get_artist_top_tracks, create_new_playlist, add_tracks_to_playlist

def shuffle(playlist, user_id, access_token):
    playlist_id = playlist['id']
    playlist_name = playlist['name']
    headers = {'Authorization': 'Bearer ' + access_token}
    old_tracks = get_playlist_tracks(playlist_id, headers)
    old_artist_ids = get_old_artists_ids(old_tracks)
    new_track_ids = get_new_track_ids(old_artist_ids, old_tracks, headers)
    new_playlist = create_new_playlist(
        playlist_name, user_id, new_track_ids, headers)
    new_playlist_id = new_playlist['id']
    add_tracks_to_playlist(new_playlist_id, new_track_ids, headers)
    return new_playlist


def get_old_artists_ids(tracks):
    print('Getting old artist ids...')
    artist_ids = [track['artists'][0]['id'] for track in tracks]
    # Some artists have no ID - remove Nones from list
    artist_ids_nones_removed = list(filter(None, artist_ids))
    return artist_ids_nones_removed


def get_new_track_ids(old_artist_ids, old_tracks, headers):
    print('Getting new track ids...')
    new_tracks = []
    artist_count_dict = Counter(old_artist_ids)
    for artist_id in artist_count_dict:
        artist_top_tracks = get_artist_top_tracks(artist_id, headers)
        random.shuffle(artist_top_tracks)
        num_tracks_to_add = artist_count_dict[artist_id]
        num_tracks_added = 0
        for track in artist_top_tracks:
            if not track_exists(track, old_tracks + new_tracks):
                new_tracks.append(track)
                num_tracks_added += 1
            if num_tracks_added == num_tracks_to_add:
                break
    return [track['uri'] for track in new_tracks]


def track_exists(track, existing_tracks):
    for existing_track in existing_tracks:
        if track['id'] == existing_track['id'] or track['name'] == existing_track['name']:
            return True
    return False
