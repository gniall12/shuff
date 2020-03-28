# shuff

[shuff.niallg.ie](https://shuff.niallg.ie)

Refresh your playlists with different songs by the same artists.

Motivation: I was getting tired of my playlists, but Spotify's recommendations consistently included artists I didn't like.

Previously built as a REST API serving JSON to an Angular front-end. Switched to full-stack Flask app for simpler maintenance and development, and to learn more about building full-stack flask apps.

[Spotify API](https://developer.spotify.com/documentation/web-api/)

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

1. Create python virtual environment python3 -m venv env
2. Activate virtual environment source env/bin/activate
3. Run `pip install -r requirements.txt` to install packages
4. Create .env file with environment variables:  
   export SPOTIFY_CLIENT_ID=\<your-client-id\>  
   export SPOTIFY_CLIENT_SECRET=\<your-client-secret\>  
   export SPOTIFY_REDIRECT_URI=http://localhost:5000/callback/  
   export SHUFF_SECRET_KEY=\<your-secret-key\>  
   export FLASK_APP=app/app
5. Run code using `flask run`  
   
## Testing
Follow steps 1-4 above, and then

5. `pip install -e .`
6. `pytest`
7. Running coverage 
   1. `coverage run -m pytest`
   2. `coverage report`

Pull requests and suggestions for features are welcome
