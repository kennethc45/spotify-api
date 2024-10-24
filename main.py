import json
from dotenv import load_dotenv
import os
import base64
from requests import post, get
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

# SETUP
load_dotenv()
client_id:str = os.getenv("CLIENT_ID")
client_secret:str = os.getenv("CLIENT_SECRET")
redirect_uri:str = os.getenv("REDIRECT_URI")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/login")
async def login():
    print("Login endpoint called")
    scope:str = "user-follow-read user-library-read"
    auth_url:str = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
    print("Redirecting to: ", auth_url)
    return RedirectResponse(url=auth_url)

@app.get("/callback")
async def callback(request: Request):
    print("Callback")
    code = request.query_params.get('code')

    if not code:
        return {"Error": "No code returned in callback."}
    
    token = get_token(code)

    if token:
        print("Getting artists")
        followed_artists = get_followed_artists(token)
        recent_songs = {}
        if followed_artists:
            for artist in followed_artists:
                artist_name = artist["name"]
                artist_id = artist["id"]
                
                songs = get_recent_songs_by_artist(token, artist_id)
                if len(songs) > 0:
                    recent_songs[artist_name] = songs
        else:
            print("Cannot find followed artists!")

        return recent_songs
    else:
        print("Error: Token retrieval failed.")
        return RedirectResponse(url="/login")

def get_token(code):
    auth_string:str = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64:str = str(base64.b64encode(auth_bytes), "utf-8")

    url:str = "https://accounts.spotify.com/api/token" 
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }

    result = post(url, headers=headers, data=data)

    if result.status_code != 200:
        print("Failed to retrieve token:", result.status_code, result.content)
        return None
    
    json_result = json.loads(result.content)
    return json_result["access_token"]

def get_auth_headers(token):
    return {"Authorization": "Bearer " + token}


# CRUD OPERATIONS
def search_for_artist(token, artist_name):
    url:str = "https://api.spotify.com/v1/search"
    headers = get_auth_headers(token)
    query:str = f"q={artist_name}&type=artist&limit=1" 

    query_url:str = url + "?" + query
    result = get(query_url, headers=headers)

    if result.status_code != 200:
        print("Error searching for artist:", result.content)
        return None
    
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result[0]

def get_artist_albums(token, artist_id):
    url:str = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = get_auth_headers(token)
    result = get(url, headers=headers)

    if result.status_code != 200:
        print("Error retrieving artist's albums:", result.content)
        return []
    
    json_result = json.loads(result.content)
    return json_result["items"]

def get_recent_songs_by_artist(token, artist_id):
    albums = get_artist_albums(token, artist_id)
    recent_songs = []
    two_weeks_ago = datetime.now() - timedelta(weeks=2)

    for album in albums:
        released_date = datetime.strptime(album['release_date'], "%Y-%m-%d")

        if released_date > two_weeks_ago:
            url = f"https://api.spotify.com/v1/albums/{album['id']}/tracks"
            headers = get_auth_headers(token)
            result = get(url, headers=headers)

            if result.status_code == 200:
                tracks = json.loads(result.content)["items"]
                for track in tracks:
                    recent_songs.append({
                        'name': track['name'],
                        'external_url': track['external_urls']['spotify'],
                        'release_date': album['release_date'],
                        'album_name': album['name']
                    })

    return recent_songs

# def get_songs_by_artist(token, artist_id):
#     url:str = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
#     headers = get_auth_headers(token)
#     result = get(url, headers=headers)

#     # Check if the song retrieval request was successful
#     if result.status_code != 200:
#         print("Error retrieving songs:", result.content)
#         return []
    
#     json_result = json.loads(result.content)["tracks"]
#     return json_result

def get_followed_artists(token):
    url:str = "https://api.spotify.com/v1/me/following?type=artist&limit=50"
    headers = get_auth_headers(token)
    result = get(url, headers=headers)

    if result.status_code != 200:
        print("Error retrieving followed artists:", result.content)
        return []
    
    json_result = json.loads(result.content)
    # print("Followed artists response:", json_result)
    return json_result["artists"]["items"]
