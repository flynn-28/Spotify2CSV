# Spotify2CSV
Python script to save a spotify playlist to csv

## Setup
1. create a spotify api app at: (https://developer.spotify.com/dashboard)[https://developer.spotify.com/dashboard]
2. install required packages
```bash
pip install -r requirements.txt
```
3. copy client id and client secret into .env file (see example.env):
```env
CLIENT_ID=
CLIENT_SECRET=
```
3. Copy your playlists id. THE PLAYLIST MUST BE PUBLIC
4. run program with:
```python
python -m main [PLAYLIST_ID]
```

## Usage

```python
python -m main [SPOTIFY_PLAYLIST_ID]
```

Example:
```python
python -m main 37vVbInEzfnXJQjVuU7bAZ
```
