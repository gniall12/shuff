from unittest.mock import patch
import json

import pytest

from app import app


@pytest.fixture()
def test_client():
    return app.app.test_client()


@patch("app.app.get_user_playlists")
def test_home(get_user_playlists_patch, test_client):
    with patch("app.app.session", {"access_token": "123"}) as session:
        response = test_client.get("/")
        assert get_user_playlists_patch.called


@patch("app.app.url_for")
@patch("app.app.redirect")
def test_home_not_logged_in(redirect_patch, url_for_patch, test_client):
    with patch("app.app.session", {}) as session:
        response = test_client.get("/")
        assert redirect_patch.called
        assert url_for_patch.called


@patch("app.app.url_for")
@patch("app.app.redirect")
def test_home_playlists_exception(redirect_patch, url_for_patch, test_client):
    with patch("app.app.session", {"access_token": "123"}) as session:
        test_client.get("/")
        assert redirect_patch.called
        assert url_for_patch.called


@patch("app.app.url_for")
@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.app.oauth.create_client")
def test_login_redirect(create_client_patch, remote_app_patch, url_for_patch, test_client):
    create_client_patch.return_value = remote_app_patch
    test_client.get("/login-redirect")
    assert remote_app_patch.authorize_redirect.called


@patch("app.app.redirect")
@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.app.oauth.create_client")
def test_handle_token(create_client_patch, remote_app_patch, redirect_patch, test_client):
    with patch("app.app.session", dict()) as session:
        resp = "123"
        create_client_patch.return_value = remote_app_patch
        remote_app_patch.authorize_access_token.return_value = resp
        response = test_client.get("/callback")
        assert redirect_patch.called
        assert "123" == session.get("access_token")


@patch("app.app.redirect")
@patch('authlib.integrations.flask_client.FlaskRemoteApp')
@patch("app.app.oauth.create_client")
def test_handle_token_no_response(
    create_client_patch, remote_app_patch, redirect_patch, test_client
):
    with patch("app.app.session", {"access_token": "123"}) as session:
        create_client_patch.return_value = remote_app_patch
        remote_app_patch.authorize_access_token.return_value = None
        response = test_client.get("/callback")
        assert redirect_patch.called
        assert "access_token" not in session


@patch("app.app.shuffle")
def test_shuffle(shuffle_patch, test_client):
    playlist = {"name": "p1", "id": "1"}
    shuffle_patch.return_value = playlist
    response = test_client.get("/shuffle?id=123&name=123")
    assert playlist == json.loads(response.data)


def test_shuffle_bad_request(test_client):
    response = test_client.get("/shuffle")
    assert 400 == response.status_code


def test_logout(test_client):
    with patch("app.app.session", {"access_token": "123"}) as session:
        response = test_client.get("/logout")
        assert "access_token" not in session
