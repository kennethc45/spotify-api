import json
from dotenv import load_dotenv
import os
import base64
from requests import post, get
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import time 
import asyncio 
import httpx

# Loads in environment variables to connect to the Spotify Web API
load_dotenv()
client_id:str = os.getenv("CLIENT_ID")
client_secret:str = os.getenv("CLIENT_SECRET")
redirect_uri:str = os.getenv("REDIRECT_URI")

# Creates API through FastAPI
app = FastAPI()

# Disable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Allows requests from any origin
    allow_credentials=True, # Allows credentials to be included in requests
    allow_methods=["*"],    # Allows all HTTP methods
    allow_headers=["*"],    # Allows all headers in requests
)

# KEYPOINTS
# 1. Tokens are needed to make requests to Sotify Web API
# 2. Headers are used to authenticate requests (they include the token)

# Login endpoint that initiates OAuth protocol in Spotify
@app.get("/login")
async def login():
    # Define the scope of permissions requested from user
    scope:str = "user-follow-read user-library-read"
    # Construct the Spotify authorization URL w/ necessary parameters 
    auth_url:str = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
    # Redirects user to Spotify login and initiates OAuth protocol
    return RedirectResponse(url=auth_url)

# Callback endoint that showcases the recent releases of the users followed artists after login
@app.get("/callback")
async def callback(request: Request):
    # Retrieve authorization code from query parameters of approved OAuth protocol
    code = request.query_params.get('code')

    # If no code is received, return an error message
    if not code:
        return {"Error": "No code returned in callback."}
    
    # Exchange authorization code for an access token
    token = await get_token(code)

    if token:
        # Get the list of artists that the user follows
        followed_artists = await get_followed_artists(token)
        # Initialize a dictionary to hold recent songs
        recent_songs = {}

        # If followed artists are found, then fetch their recent releases
        if followed_artists:
            start_time = time.time()    # Marks starting time for query
            tasks = []                  # List to hold aysnchronous tasks

            # Loop through each followed artist
            for artist in followed_artists:
                artist_name = artist["name"]
                artist_id = artist["id"]
                
                # Create a task to fetch recent songs for artist
                tasks.append(get_recent_songs(token, artist_id, artist_name, recent_songs))

            # Runs all tasks concurrently
            await asyncio.gather(*tasks)    

            # Measures query time to retrieve recent releases
            total_duration = time.time() - start_time
            print(f"Time to retrieve recent releases: {total_duration * 1000:.2f} ms")
        else:
            print("Cannot find followed artists!")

        # Return recent songs for followed artists
        return recent_songs
    else:
        print("Error: Token retrieval failed.")
        return RedirectResponse(url="/login")

# Function to returns access token in exchange for an authorization code
async def get_token(code):
    # Create authorization string by combining the client ID and client secret
    auth_string:str = client_id + ":" + client_secret
    # Encode the authorization string in UTF-8
    auth_bytes = auth_string.encode("utf-8")
    # Encode the authorization bytes in Base64
    auth_base64:str = str(base64.b64encode(auth_bytes), "utf-8")

    # Define token endpoint URL for Spotify
    url:str = "https://accounts.spotify.com/api/token" 
    # Set the request headers for authorization and content type
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Define the data needed for the POST request to obtain the token
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }

    # Make an aynchronous POST request to the token endpoint
    async with httpx.AsyncClient() as client:
                result = await client.post(url, headers=headers, data=data)

    if result.status_code != 200:
        print("Failed to retrieve token:", result.status_code, result.content)
        return None
    
    # Parse the JSON response to get the access token
    json_result = json.loads(result.content)
    # Return the access token
    return json_result["access_token"]

# Function to generate authorization headers for API requests
def get_auth_headers(token):
    return {"Authorization": "Bearer " + token}


# CRUD OPERATIONS

# Function to retrieve recent songs for a given artist
async def get_recent_songs(token, artist_id, artist_name, recent_songs):
    # Get the list of albums for the artist
    albums = await get_artist_albums(token, artist_id)
    # Calculate the date two weeks ago for filtering recent releases
    two_weeks_ago = datetime.now() - timedelta(weeks=4)

    # Loop through each album of the artist
    for album in albums:
        # Get the release date for the album
        released_date = album.get('release_date')

        # If the release date is in YYYY format, assume January 1st of that year
        if len(released_date) == 4:
            released_date = f"{released_date}-01-01"
        else:
            # Validate the release date format
            try:
                datetime.strptime(released_date, "%Y-%m-%d")
            except ValueError:
                # Log an error for invalid release date format
                print(f"Invalid data format for album: {album['name']}, date: {released_date}")
                # Skip to next album
                continue

        # Convert release date string to a datetime object
        released_date = datetime.strptime(released_date, "%Y-%m-%d")

        # Check if the album was released within the last two weeks
        if released_date > two_weeks_ago:
            # Define URL to get the tracks of the album
            url = f"https://api.spotify.com/v1/albums/{album['id']}/tracks"
            # Get authorization headers
            headers = get_auth_headers(token)

            # Make an asynchronous GET request to retrieve album tracks
            async with httpx.AsyncClient() as client:
                result = await client.get(url, headers=headers)

            # If the request is successful, process the tracks
            if result.status_code == 200:
                # Load the tracks from the JSON response
                tracks = json.loads(result.content)["items"]
                # Populate the recent_songs dictionary from callback endpoint with track information
                recent_songs[artist_name] = [
                    {
                        'name': track['name'],
                        'external_url': track['external_urls']['spotify'],
                        'release_date': album['release_date'],
                        'album_name': album['name']
                    }
                    for track in tracks
                ]

# Function to get all albums for a given artist
async def get_artist_albums(token, artist_id):
    # Define the URL to retrieve the artist's albums
    url:str = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    # Get authorization headers
    headers = get_auth_headers(token)

    # Make an asynchronous GET request to retrieve the artist's albums
    async with httpx.AsyncClient() as client:
        result = await client.get(url, headers=headers)

    if result.status_code != 200:
        return []
    
    # Load and return the list of albums from the JSON response
    json_result = json.loads(result.content)
    return json_result["items"]


# Function to retrieve the users followed artists
async def get_followed_artists(token):
    # Define the URL to get followed artists
    url:str = "https://api.spotify.com/v1/me/following?type=artist&limit=50"
    # Get authorization headers
    headers = get_auth_headers(token)


    # Make an asynchronous GET request to retrieve followed artists
    async with httpx.AsyncClient() as client:
        result = await client.get(url, headers=headers)

    if result.status_code != 200:
        return []
    
    # Load and return the lsit of followed artists from the JSON response
    json_result = json.loads(result.content)
    return json_result["artists"]["items"]
