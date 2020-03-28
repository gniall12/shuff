from unittest.mock import patch

from flask import Response
from pytest import raises

from app import spotify_oauth
from app.config import base_url


class DummyResponse(dict):
    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code

    def __getattr__(self, key):
        return self[key]

    def json(self):
        return self.data


@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_get_user_id(create_client_patch, remote_app_patch):
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.get.return_value = DummyResponse({"id": 1})
    user_id = spotify_oauth.get_user_id()
    assert 1 == user_id


@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_get_user_playlists(create_client_patch, remote_app_patch):
    data = {"items": [{"name": "p1", "id": 1}]}
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.get.return_value = DummyResponse(data)
    user_playlists = spotify_oauth.get_user_playlists()
    assert data == user_playlists


@patch("app.spotify_oauth.log.error")
@patch("app.spotify_oauth.abort")
@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_get_user_playlists_error(create_client_patch, remote_app_patch, abort_patch, log_patch):
    data = {"error": "error"}
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.get.return_value = DummyResponse(data, 401)
    spotify_oauth.get_user_playlists()
    assert abort_patch.called
    assert log_patch.called


@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_get_playlist_tracks(create_client_patch, remote_app_patch):
    track = {"name": "song1", "id": "1"}
    data1 = {"items": [{"track": track}], "next": base_url + "next"}
    data2 = {"items": [{"track": track}]}
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.get.side_effect = [
        DummyResponse(data1), DummyResponse(data2)]
    playlist_tracks = spotify_oauth.get_playlist_tracks(1)
    assert [track, track] == playlist_tracks


@patch("app.spotify_oauth.log.error")
@patch("app.spotify_oauth.abort", side_effect=Exception("Aborted"))
@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_get_playlist_tracks_error(create_client_patch, remote_app_patch, abort_patch, log_patch):
    data = {"error": "error message"}
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.get.return_value = DummyResponse(data)
    with raises(Exception):
        spotify_oauth.get_playlist_tracks(1)
    assert log_patch.called
    assert abort_patch.called


@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_get_artist_top_tracks(create_client_patch, remote_app_patch):
    tracks = [{"name": "s1"}, {"name": "s2"}]
    data = {"tracks": tracks}
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.get.return_value = DummyResponse(data)
    top_tracks = spotify_oauth.get_artist_top_tracks("1")
    assert tracks == top_tracks


@patch("app.spotify_oauth.log.error")
@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_get_artist_top_tracks_no_tracks_found(create_client_patch, remote_app_patch, log_patch):
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.get.return_value = DummyResponse({})
    top_tracks = spotify_oauth.get_artist_top_tracks("1")
    assert [] == top_tracks
    assert log_patch.called


@patch("app.spotify_oauth.log.info")
@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_get_artist_top_tracks_error_rate_once(create_client_patch, remote_app_patch, log_patch):
    data1 = {"error": "error_message"}
    tracks = [{"name": "s1"}, {"name": "s2"}]
    data2 = {"tracks": tracks}
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.get.side_effect = [
        DummyResponse(data1, 429), DummyResponse(data2)]
    top_tracks = spotify_oauth.get_artist_top_tracks("1")
    assert tracks == top_tracks
    assert log_patch.called


@patch("app.spotify_oauth.log.info")
@patch("app.spotify_oauth.log.error")
@patch("app.spotify_oauth.time.sleep")
@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_get_artist_top_tracks_error_rate_four(
    create_client_patch, remote_app_patch, sleep_patch, error_patch, info_patch
):
    data = {"error": "error_message"}
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.get.return_value = DummyResponse(data, 429)
    top_tracks = spotify_oauth.get_artist_top_tracks("1")
    assert [] == top_tracks
    assert error_patch.called
    assert info_patch.called


@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_create_new_playlist(create_client_patch, remote_app_patch):
    data = {"items": [{"name": "p1", "id": 1}]}
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.post.return_value = DummyResponse(data)
    new_playlist = spotify_oauth.create_new_playlist("Tune", "1")
    assert data == new_playlist


@patch("app.spotify_oauth.log.error")
@patch("app.spotify_oauth.abort", side_effect=Exception("Aborted"))
@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_create_new_playlist_error(create_client_patch, remote_app_patch, abort_patch, log_patch):
    data = {"error": "error message"}
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.post.return_value = DummyResponse(data, 400)
    with raises(Exception):
        spotify_oauth.create_new_playlist("Tune", "1")
    assert abort_patch.called
    assert log_patch.called


@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_add_tracks_to_playlist(create_client_patch, remote_app_patch):
    data = {"snapshot_id": "123"}
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.post.return_value = DummyResponse(data)
    snapshot = spotify_oauth.add_tracks_to_playlist(
        "123", [{"name": "s1", "id": 1}])
    assert data == snapshot


@patch("app.spotify_oauth.log.error")
@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.spotify_oauth.oauth.create_client")
def test_add_tracks_to_playlist_error(create_client_patch, remote_app_patch, log_patch):
    data = {"error": "error_message"}
    create_client_patch.return_value = remote_app_patch
    remote_app_patch.post.return_value = DummyResponse(data)
    snapshot = spotify_oauth.add_tracks_to_playlist(
        "123", [{"name": "s1", "id": 1}])
    assert log_patch.called
    assert data == snapshot


@patch("app.spotify_oauth.session", {"access_token": "123"})
def test_get_spotify_oauth_token():
    token = spotify_oauth.get_spotify_oauth_token("")
    assert "123" == token


@patch("app.spotify_oauth.session", {})
@patch("app.spotify_oauth.abort", side_effect=Exception("Aborted"))
def test_get_spotify_oauth_token_abort(abort_patch):
    with raises(Exception):
        spotify_oauth.get_spotify_oauth_token("")
    assert abort_patch.called
