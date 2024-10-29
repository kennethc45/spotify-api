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
    scope:str = "user-follow-read user-library-read"
    auth_url:str = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
    return RedirectResponse(url=auth_url)

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get('code')

    if not code:
        return {"Error": "No code returned in callback."}
    
    token = await get_token(code)

    if token:
        followed_artists = await get_followed_artists(token)
        recent_songs = {}
        if followed_artists:
            start_time = time.time()
            tasks = []
            for artist in followed_artists:
                artist_name = artist["name"]
                artist_id = artist["id"]
                
                tasks.append(get_recent_songs(token, artist_id, artist_name, recent_songs))

            await asyncio.gather(*tasks)

            total_duration = time.time() - start_time
            print(f"Time to retrieve recent releases: {total_duration * 1000:.2f} ms")
        else:
            print("Cannot find followed artists!")

        return recent_songs
    else:
        print("Error: Token retrieval failed.")
        return RedirectResponse(url="/login")

async def get_token(code):
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

    async with httpx.AsyncClient() as client:
                result = await client.post(url, headers=headers, data=data)

    if result.status_code != 200:
        print("Failed to retrieve token:", result.status_code, result.content)
        return None
    
    json_result = json.loads(result.content)
    return json_result["access_token"]

def get_auth_headers(token):
    return {"Authorization": "Bearer " + token}


# CRUD OPERATIONS
async def get_recent_songs(token, artist_id, artist_name, recent_songs):
    albums = await get_artist_albums(token, artist_id)
    two_weeks_ago = datetime.now() - timedelta(weeks=4)

    for album in albums:
        released_date = album.get('release_date')

        if len(released_date) == 4:
            released_date = f"{released_date}-01-01"
        else:
            try:
                datetime.strptime(released_date, "%Y-%m-%d")
            except ValueError:
                print(f"Invalid data format for album: {album['name']}, date: {released_date}")
                continue

        released_date = datetime.strptime(released_date, "%Y-%m-%d")

        if released_date > two_weeks_ago:
            url = f"https://api.spotify.com/v1/albums/{album['id']}/tracks"
            headers = get_auth_headers(token)

            async with httpx.AsyncClient() as client:
                result = await client.get(url, headers=headers)

            if result.status_code == 200:
                tracks = json.loads(result.content)["items"]
                recent_songs[artist_name] = [
                    {
                        'name': track['name'],
                        'external_url': track['external_urls']['spotify'],
                        'release_date': album['release_date'],
                        'album_name': album['name']
                    }
                    for track in tracks
                ]

async def get_artist_albums(token, artist_id):
    url:str = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = get_auth_headers(token)

    async with httpx.AsyncClient() as client:
        result = await client.get(url, headers=headers)

    if result.status_code != 200:
        return []
    
    json_result = json.loads(result.content)
    return json_result["items"]

async def get_followed_artists(token):
    url:str = "https://api.spotify.com/v1/me/following?type=artist&limit=50"
    headers = get_auth_headers(token)

    async with httpx.AsyncClient() as client:
        result = await client.get(url, headers=headers)

    if result.status_code != 200:
        return []
    
    json_result = json.loads(result.content)
    return json_result["artists"]["items"]
