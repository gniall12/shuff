from app import shuffler

tracks = [
    {
        "id": 1,
        "album": "Hold On",
        "artists": [{"name": "Little Dragon", "id": "1"}],
        "name": "Hold On",
    },
    {
        "id": 2,
        "album": "Circles",
        "artists": [{"name": "Mac Miller", "id": "2"}],
        "name": "Blue World",
    },
    {
        "id": 3,
        "album": "Baby",
        "artists": [{"name": "Four Tet", "id": "3"}],
        "name": "Baby",
    },
]


def test_get_old_artists_ids():
    assert ["1", "2", "3"] == shuffler.get_old_artists_ids(tracks)


def test_get_old_artists_ids_with_nones():
    tracks.append(
        {
            "id": "5",
            "album": "Test",
            "artists": [{"name": "Test", "id": None}],
            "name": "Test",
        }
    )
    assert ["1", "2", "3"] == shuffler.get_old_artists_ids(tracks)


def test_track_exists_by_id():
    track = {
        "id": 1,
        "album": "You and I",
        "artists": [{"name": "Caribou", "id": "4"}],
        "name": "You and I",
    }
    assert shuffler.track_exists(track, tracks)


def test_track_exists_by_name():
    track = {
        "id": 4,
        "album": "Warpaint",
        "artists": [{"name": "Warpaint", "id": "4"}],
        "name": "Baby",
    }
    assert shuffler.track_exists(track, tracks)


def test_track_doesnt_exist():
    track = {
        "id": 5,
        "album": "Supernatural",
        "artists": [{"name": "Floorplan", "id": "4"}],
        "name": "Oasis",
    }
    assert not shuffler.track_exists(track, tracks)

