import json
from dotenv import load_dotenv
import os
import base64
from requests import post, get

load_dotenv()

client_id:str = os.getenv("CLIENT_ID")
client_secret:str = os.getenv("CLIENT_SECRET")

# print(f"Client ID: {client_id}")
# print(f"Client Secret: {client_secret}")

def get_token():
    auth_string:str = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64:str = str(base64.b64encode(auth_bytes), "utf-8")

    url:str = "https://accounts.spotify.com/api/token" 
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token  = json_result["access_token"]

    return token 

def get_auth_headers(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url:str = "https://api.spotify.com/v1/search"
    headers = get_auth_headers(token)
    query:str = f"q={artist_name}&type=artist&limit=1"

    query_url:str = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result[0]



token = get_token()
# print(f"Token: {token}")
result = search_for_artist(token, "ACDC")
print(f"Result: {result["name"]}")