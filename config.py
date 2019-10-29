import os

auth_base_url = 'https://accounts.spotify.com/authorize'
token_base_url = 'https://accounts.spotify.com/api/token'
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
scope = 'playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative'
response_type = 'code'
secret_key = os.getenv('SHUFF_SECRET_KEY')
base_url = 'https://api.spotify.com/v1/'