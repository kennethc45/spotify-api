import pytest
from unittest.mock import patch
from main import *  
import httpx

@pytest.mark.asyncio
async def test_get_followed_artists_success():
    token: str = "test_token"
    mock_response = {
        "artists": {
            "items": [
                {"id": "1", "name": "Artist One"},
                {"id": "2", "name": "Artist Two"}
            ]
        }
    }

    # Mock the httpx.AsyncClient.get method
    with patch('httpx.AsyncClient.get') as mock_get:
        # Configure the mock to return a successful response
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = json.dumps(mock_response).encode('utf-8')

        artists = await get_followed_artists(token)

        assert len(artists) == 2
        assert artists[0]['id'] == "1"
        assert artists[0]['name'] == "Artist One"
        assert artists[1]['id'] == "2"
        assert artists[1]['name'] == "Artist Two"

@pytest.mark.asyncio
async def test_get_followed_artists_failure():
    token: str = "test_token"

    # Mock the httpx.AsyncClient.get method
    with patch('httpx.AsyncClient.get') as mock_get:
        # Configure the mock to return a failed response
        mock_get.return_value.status_code = 403  # Forbidden status code

        artists = await get_followed_artists(token)

        assert artists == []  # Should return an empty list on error

@pytest.mark.asyncio
async def test_get_followed_artists_empty_response():
    token: str = "test_token"
    mock_response = {
        "artists": {
            "items": []
        }
    }

    # Mock the httpx.AsyncClient.get method
    with patch('httpx.AsyncClient.get') as mock_get:
        # Configure the mock to return a successful response with no artists
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = json.dumps(mock_response).encode('utf-8')

        artists = await get_followed_artists(token)

        assert len(artists) == 0  # Should return an empty list

@pytest.mark.asyncio
async def test_get_artist_albums_success():
    token: str = "test_token"
    artist_id: str = "artist_123"
    mock_response = {
        "items": [
            {"id": "album_1", "name": "Album One", "release_date": "2024-10-01"},
            {"id": "album_2", "name": "Album Two", "release_date": "2024-11-01"},
        ]
    }

    # Mock the httpx.AsyncClient.get method
    with patch('httpx.AsyncClient.get') as mock_get:
        # Configure the mock to return a successful response
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = json.dumps(mock_response).encode('utf-8')

        albums = await get_artist_albums(token, artist_id)

        assert len(albums) == 2
        assert albums[0]['id'] == "album_1"
        assert albums[0]['name'] == "Album One"
        assert albums[0]['release_date'] == "2024-10-01"
        assert albums[1]['id'] == "album_2"
        assert albums[1]['name'] == "Album Two"
        assert albums[1]['release_date'] == "2024-11-01"

@pytest.mark.asyncio
async def test_get_artist_albums_failure():
    token: str = "test_token"
    artist_id: str = "artist_123"

    # Mock the httpx.AsyncClient.get method
    with patch('httpx.AsyncClient.get') as mock_get:
        # Configure the mock to return a successful response
        mock_get.return_value.status_code = 404

        albums = await get_artist_albums(token, artist_id)

        assert albums == []

@pytest.mark.asyncio
async def test_get_artist_albums_empty_response():
    token: str = "test_token"
    artist_id: str = "artist_123"
    mock_response = {
        "items": []
    }

    # Mock the httpx.AsyncClient.get method
    with patch('httpx.AsyncClient.get') as mock_get:
        # Configure the mock to return a successful response
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = json.dumps(mock_response).encode('utf-8')

        albums = await get_artist_albums(token, artist_id)

        assert len(albums) == 0

