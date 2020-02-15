from unittest.mock import patch
from flask_oauthlib.client import OAuthResponse
from flask import Response
from http.client import HTTPResponse
from app import spotify_oauth


class DummyResponse(dict):
    def __init__(self, data, status=200):
        self.data = data
        self.status = status

    def __getattr__(self, key):
        return self[key]


@patch("app.spotify_oauth.spotify.get")
def test_get_user_id(spotify_get_patch):
    spotify_get_patch.return_value = DummyResponse({"id": 1})
    user_id = spotify_oauth.get_user_id()
    assert 1 == user_id


@patch("app.spotify_oauth.spotify.get")
def test_get_user_playlists(spotify_get_patch):
    data = {"items": [{"name": "p1", "id": 1}]}
    spotify_get_patch.return_value = DummyResponse(data)
    user_playlists = spotify_oauth.get_user_playlists()
    assert data == user_playlists


@patch("app.spotify_oauth.log.error")
@patch("app.spotify_oauth.abort")
@patch("app.spotify_oauth.spotify.get")
def test_get_user_playlists_error(spotify_get_patch, abort_patch, log_patch):
    data = {"error": "error"}
    spotify_get_patch.return_value = DummyResponse(data, 401)
    user_playlists = spotify_oauth.get_user_playlists()
    assert abort_patch.called
    assert log_patch.called
