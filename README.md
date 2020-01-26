# shuff

Backend for [shuff.niallg.ie](https://shuff.niallg.ie) using the [Spotify API](https://developer.spotify.com/documentation/web-api/)

## Project Background

Refresh your playlists with different songs by the same artists.

Motivation: I was getting tired of my playlists, but Spotify's recommendations consistently included artists I didn't like.

## Details

OAuth 2 authorisation flow used to log in and store user credentials in session variable.

Algorithm to shuffle playlist:
1. Get playlist ID.
2. Get all tracks from playlist.
3. Create a dictionary mapping artist ID to the number of tracks by that artist in the playlist.
4. Get the IDs of the top 10 tracks by each artist.
    * Add track if it doesn't exist in the original playlist or the newly created playlist.
    * Repeat until the desired number of tracks are added, or all of the top 10 tracks exist in either the original playlist or the new playlist. 
    
## Running Code

1. Create python virtual environment (https://docs.python-guide.org/dev/virtualenvs/)
2. Run `pip install -r requirements.txt` to install packages
3. Run code using `python -m flask run`  

Pull requests and suggestions for features are welcome
