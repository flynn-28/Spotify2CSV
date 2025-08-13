# import modules
import time                    # sleeping to avoid rate limits
import random                  # random numbers
import requests                # making api requests
import base64                  # encoding client id and seccret
import unicodedata             # title normalization
import re                      # parsing regular expressions
from dotenv import load_dotenv # loading enviornment variables
import sys                     # cli args and exiting
import os                      # reading files
import pandas as pd            # dataframes and csv

# function to save client id and secret
def save_client(CLIENT_ID, CLIENT_SECRET):
    with open(".env", "w") as f:                                         # open file
        f.write(f"CLIENT_ID={CLIENT_ID}\nCLIENT_SECRET={CLIENT_SECRET}") # write to file
        f.close                                                          # close file
    print("SAVED to .env")    

# function to import client id and secret
def load_env():
    # load from file
    load_dotenv()                              # load file
    CLIENT_ID = os.getenv("CLIENT_ID")         # load id
    CLIENT_SECRET = os.getenv("CLIENT_SECRET") # load secret

    # load from input (if not in env)
    if not CLIENT_ID:                                    # check if id is in env
        CLIENT_ID = input("Spotify client id: ")         # prompt for id if missing

    if not CLIENT_SECRET:                                # check if secret is in env
        CLIENT_SECRET = input("Spotify client secret: ") # prompt for secret if missing

    # optional saving logic if missing from env
    if (not os.getenv("CLIENT_ID") or not os.getenv("CLIENT_SECRET")) and (CLIENT_ID and CLIENT_SECRET): # if client id or secret isnt in env and was provided
        save = input("Save id and secret? (Y/n): ")                                                      # prompt to save
        if save.lower() == "y":                                                                          # check input
            save_client(CLIENT_ID, CLIENT_SECRET)                                                        # save
        elif save.lower() == "n":                                                                        # check if no
            print("Not saving")                                                                          # message
        else:                                                                                            # invalid input/default
            print("Invalid option, saving anyway")                                                       # message
            save_client(CLIENT_ID, CLIENT_SECRET)                                                        # save (default)

    return CLIENT_ID, CLIENT_SECRET         # return client id and secret
    
# function to request an api token using client id and token
def request_token(CLIENT_ID, CLIENT_SECRET):
    # define constants
    url = "https://accounts.spotify.com/api/token"                                # set url
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"                                     # make auth string using id and secret
    headers = {                                                                   # set authorization header
        "Authorization": f"Basic {base64.b64encode(auth_str.encode()).decode()}", # set encoded id/secret as auth
        "Content-Type": "application/x-www-form-urlencoded"                       # type auth string
    }

    data = {                                                                      # type of data to return
        "grant_type": "client_credentials"                                        # requesting client credentials
    }

    # make auth request
    try:
        res = requests.post(url, headers=headers, data=data) # post header and data to url
        res.raise_for_status()                               # ake sure no errors
        return res.json()["access_token"]                    # return token
    except Exception as e:                                   # catch error
        print(f"ERROR: {e}")                                 # print error
        return None                                          # return nothing

# function to flatten nested lists (for genre logic)
def flatten_list(x):
    flat = []
    for i in x:                          # iterate through items
        if isinstance(i, list):          # check if item is a list
            flat.extend(flatten_list(i)) # run recursivly if item is a list
        else:                            # if item is not a list
            flat.append(i)               # append item to flattened list
    return flat                          # return flattened list

# function to scrape playlist
def extract_songs(playlist_id):
    # set vars
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    playlist = requests.get(url, headers=auth_header)
    tracks = playlist.json()["tracks"]
    songs = tracks["items"]
    data = []

    # run while there are songs left
    while tracks:
        # iterating through songs
        for i in songs:                                                # iterate through songs
            track = i["track"]                                         # extract song specific info
            name = f"{track["name"]}"                                  # extract song name
            album = f"{track["album"]["name"]}"                        # extract album name
            artists = f"{[j["name"] for j in track["artists"]]}"       # extract each arists name
            artist_ids = ",".join([j["id"] for j in track["artists"]]) # extract each artists id, join with comma
            artists_data = requests.get(f"https://api.spotify.com/v1/artists?ids={artist_ids}", headers=auth_header).json()["artists"]
            genres = flatten_list([i["genres"] for i in artists_data]) # extract and flatten artist genres
            date = track["album"]["release_date"]                      # extract date
            row = {                                                    # dictionary to store data
                "Name": name,                                          # set name
                "Album": album,                                        # set album
                "Artist(s)": artists,                                  # set artists
                "Genre(s)": genres,                                    # set genres
                "Release": date                                        # set release date
            }
            data.append(row)                                           # append row to data
            time.sleep(random.uniform(0.3, 0.7))                       # sleep to avoid rate limiting
        
        # check if theres another page of songs
        if tracks.get("next"):                                                # check if the next page exists
            tracks = requests.get(tracks["next"], headers=auth_header).json() # set tracks to the next page
        else:                                                                 # if there are no more pages
            break                                                             # break loop

    return data # return data

# function to clean file name
def clean_filename(name):
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII') # normalize ascii characters 
    name = re.sub(r'[^\w\s-]', '', name)                                                 # remove special characters
    name = re.sub(r'\s+', '_', name)                                                     # replace whitespae with underscores
    return name.strip('_')                                                               # remove leading/trailing underscores

# function to save data   
def save_data(data, playlist_id):
    df = pd.DataFrame(data)                                                                             # convert data to dataframe
    playlist = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}", headers=auth_header) # request playlist
    playlist_name = playlist.json()["name"]                                                             # get playlist and extract na,e
    df.to_csv(f"{clean_filename(playlist_name)}.csv", index=False)                                      # save dataframe to csv

CLIENT_ID, CLIENT_SECRET = load_env() # set client id and secret

# set auth header
auth_header = {
    "Authorization": f"Bearer {request_token(CLIENT_ID, CLIENT_SECRET)}"
}

# get playlist id
try:
	playlist_id = sys.argv[1] # see if argument passed
except:
	playlist_id = input("Enter id of playlist. MUST BE PUBLIC: ") # prompt if arg not passed
    
data = extract_songs(playlist_id) # extract songs
save_data(data, playlist_id)      # save songs to csv
