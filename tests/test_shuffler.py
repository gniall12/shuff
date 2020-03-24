from unittest.mock import patch

from app import shuffler

playlist = {"id": 1, "name": "choones"}

tracks = [
    {
        "id": "1",
        "album": "Hold On",
        "artists": [{"name": "Little Dragon", "id": "1"}],
        "name": "Hold On",
        "uri": "1",
    },
    {
        "id": "2",
        "album": "Circles",
        "artists": [{"name": "Mac Miller", "id": "2"}],
        "name": "Blue World",
        "uri": "2",
    },
    {
        "id": "3",
        "album": "Baby",
        "artists": [{"name": "Four Tet", "id": "3"}],
        "name": "Baby",
        "uri": "3",
    },
]

test_track = {
    "id": "5",
    "album": "Test",
    "artists": [{"name": "Test", "id": None}],
    "name": "Test",
    "uri": "5",
}

new_playlist = {"id": 2}

@patch("app.shuffler.add_tracks_to_playlist")
@patch("app.shuffler.create_new_playlist", return_value=new_playlist)
@patch("app.shuffler.get_artist_top_tracks", return_value=[test_track])
@patch("app.shuffler.get_playlist_tracks", return_value=tracks)
@patch("app.shuffler.get_user_id", return_value="1")
def test_shuffle(
    get_user_id_patch,
    get_playlist_tracks_patch,
    get_artist_top_tracks_patch,
    create_new_playlist_patch,
    add_tracks_to_playlist_patch,
):
    playlist_shuffled = shuffler.shuffle(playlist['id'], playlist['name'])
    assert get_user_id_patch.called
    assert get_playlist_tracks_patch.called
    assert get_artist_top_tracks_patch.called
    assert create_new_playlist_patch.called
    assert add_tracks_to_playlist_patch.called
    assert new_playlist == playlist_shuffled


def test_get_old_artists_ids():
    assert ["1", "2", "3"] == shuffler.get_old_artists_ids(tracks)


def test_get_old_artists_ids_with_nones():
    new_tracks = tracks.copy()
    new_tracks.append(test_track)
    assert ["1", "2", "3"] == shuffler.get_old_artists_ids(new_tracks)


@patch("app.shuffler.get_artist_top_tracks", return_value=[test_track])
def test_get_new_track_ids(get_artist_top_tracks_patch):
    x = shuffler.get_new_track_ids([1], tracks)
    assert ["5"] == x


def test_track_exists_by_id():
    track = {
        "id": "1",
        "album": "You and I",
        "artists": [{"name": "Caribou", "id": "4"}],
        "name": "You and I",
    }
    assert shuffler.track_exists(track, tracks)


def test_track_exists_by_name():
    track = {
        "id": "4",
        "album": "Warpaint",
        "artists": [{"name": "Warpaint", "id": "4"}],
        "name": "Baby",
    }
    assert shuffler.track_exists(track, tracks)


def test_track_doesnt_exist():
    track = {
        "id": "5",
        "album": "Supernatural",
        "artists": [{"name": "Floorplan", "id": "4"}],
        "name": "Oasis",
    }
    assert not shuffler.track_exists(track, tracks)

