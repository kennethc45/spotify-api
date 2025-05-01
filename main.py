from requests import post, get
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from spotify_api import get_token, get_followed_artists, get_recent_songs, client_id, redirect_uri, releases


# Creates API through FastAPI
app = FastAPI()

template = Jinja2Templates(directory="views")

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

@app.get("/callback")
async def callback(request: Request) -> None:
    # Retrieve authorization code from query parameters of approved OAuth protocol
    code = request.query_params.get('code')

    # If no code is received, return an error message
    if not code:
        return {"Error": "No code returned in callback."}
    
    # Exchange authorization code for an access token
    token = await get_token(code)

    if not token:
        return {"Error": "Token Exchange failed"}
    
    redirect_url: str = f"/releases?token={token}"

    return RedirectResponse(url=redirect_url)

@app.get('/releases')
async def index(req: Request, token: str):
    recent_songs = await releases(token)

    return template.TemplateResponse (
        name="callback.html",
        context={"request": req, "recent_songs": recent_songs}
    )