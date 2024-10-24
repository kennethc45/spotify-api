import os
from dotenv import load_dotenv

import json
import unittest
from unittest.mock import Mock, patch 
from main import *
from fastapi import FastAPI, logger
from fastapi.testclient import TestClient

load_dotenv()

client_id:str = os.getenv("CLIENT_ID")
client_secret:str = os.getenv("CLIENT_SECRET")
redirect_uri:str = os.getenv("REDIRECT_URI")
client = TestClient(app)

class TestSpotifyAPI(unittest.TestCase):
    @patch('main.get')
    @patch('main.get_auth_headers')
    def test_get_followed_artists_success(self, mock_get_auth_headers, mock_get):
        mock_token: str = 'test_token'
        mock_response_data = {
            "artists": {
                "items": [
                    {"name": "Artist 1", "id": "1"},
                    {"name": "Artist 2", "id": "2"}
                ]
            }
        }

        mock_get.return_value = Mock(status_code = 200, content=json.dumps(mock_response_data).encode('utf-8'))
        mock_get_auth_headers.return_value = {"Authorization": "Bearer " + mock_token}

        followed_artists = get_followed_artists(mock_token)

        self.assertEqual(len(followed_artists), 2)
        self.assertEqual(followed_artists[0]['name'], "Artist 1")
        self.assertEqual(followed_artists[1]['name'], "Artist 2")

    @patch('main.get')
    @patch('main.get_auth_headers')
    def test_get_followed_artists_failure(self, mock_get_auth_headers, mock_get):
        mock_token: str = 'test_token'

        mock_get.return_value = Mock(status_code = 404, content=json.dumps({"Error": "Not Found"}).encode('utf-8'))
        mock_get_auth_headers.return_value = {"Authorization": "Bearer " + mock_token}

        followed_artists = get_followed_artists(mock_token)


        self.assertEqual(followed_artists, [])

    @patch('main.get')
    @patch('main.get_auth_headers')
    def test_get_artists_albums_success(self, mock_get_auth_headers, mock_get):
        mock_token: str = 'test_token'
        mock_artist_id: str = "1"
        mock_response_data = {
            "items": [
                {
                    "album_type": "album",
                    "artists": [
                        {"name": "Artist Name", "id": mock_artist_id}
                    ],
                    "id": "album_id",
                    "name": "Album Name",
                    "release_date": "2023-01-01",
                    "total_tracks": 10,
                    "external_urls": {
                        "spotify": "https://open.spotify.com/album/album_id"
                    },
                    "images": [
                        {"url": "https://image.url/album.jpg", "height": 640, "width": 640}
                    ]
                }
            ],
            "limit": 20,
            "offset": 0,
            "total": 50
        }

        mock_get.return_value = Mock(status_code = 200, content=json.dumps(mock_response_data).encode('utf-8'))
        mock_get_auth_headers.return_value = {"Authorization": "Bearer " + mock_token}

        artists_albums = get_artist_albums(mock_token, mock_artist_id)

        self.assertEqual(len(artists_albums), 1)
        self.assertEqual(artists_albums[0]['name'], "Album Name")
        self.assertEqual(artists_albums[0]['artists'][0]['name'], "Artist Name")

    @patch('main.get')
    @patch('main.get_auth_headers')
    def test_get_artists_albums_failure(self, mock_get_auth_headers, mock_get):
        mock_token: str = 'test_token'
        mock_artist_id: str = "1"

        mock_get.return_value = Mock(status_code = 404, content=json.dumps({"Error": "Not Found"}).encode('utf-8'))
        mock_get_auth_headers.return_value = {"Authorization": "Bearer " + mock_token}

        artists_albums = get_artist_albums(mock_token, mock_artist_id)


        self.assertEqual(artists_albums, [])



if __name__ == "__main__":
    unittest.main()

