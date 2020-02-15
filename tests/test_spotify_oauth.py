import sys
from http.client import HTTPResponse
from unittest.mock import patch

from flask_oauthlib.client import OAuthResponse
from flask import Response
from pytest import raises

from app import spotify_oauth
from app.config import base_url


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


@patch("app.spotify_oauth.spotify.get")
def test_get_playlist_tracks(spotify_get_patch):
    track = {"name": "song1", "id": "1"}
    data1 = {"items": [{"track": track}], "next": base_url + "next"}
    data2 = {"items": [{"track": track}]}
    spotify_get_patch.side_effect = [DummyResponse(data1), DummyResponse(data2)]
    playlist_tracks = spotify_oauth.get_playlist_tracks(1)
    assert [track, track] == playlist_tracks


@patch("app.spotify_oauth.log.error")
@patch("app.spotify_oauth.abort", side_effect=Exception("Aborted"))
@patch("app.spotify_oauth.spotify.get")
def test_get_playlist_tracks_error(spotify_get_patch, abort_patch, log_patch):
    data = {"error": "error message"}
    spotify_get_patch.return_value = DummyResponse(data)
    with raises(Exception):
        playlist_tracks = spotify_oauth.get_playlist_tracks(1)
    assert log_patch.called
    assert abort_patch.called