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

    # Check if the token request was successful
    if result.status_code != 200:
        print("Failed to retrieve token:", result.content)
        return None
    
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

    # Check if the search request was successful
    if result.status_code != 200:
        print("Error searching for artist:", result.content)
        return None
    
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url:str = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_headers(token)
    result = get(url, headers=headers)

    # Check if the song retrieval request was successful
    if result.status_code != 200:
        print("Error retrieving songs:", result.content)
        return []
    
    json_result = json.loads(result.content)["tracks"]
    return json_result

if __name__ == "__main__":
    token = get_token()
    if not token:
        print("Token retrieval failed.")
    else:
        result = search_for_artist(token, "ACDC")
        if result:
            artist_id = result["id"]
            songs = get_songs_by_artist(token, artist_id)
            if songs:
                # Display the top 10 songs for the artist
                for idx, song in enumerate(songs):
                    print(f"{idx + 1}. {song['name']}")
            else:
                print("No songs found for the artist.")
