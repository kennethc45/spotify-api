import os
from fastapi import FastAPI
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from requests import post, get
from main import app

load_dotenv()

client_id:str = os.getenv("CLIENT_ID")
client_secret:str = os.getenv("CLIENT_SECRET")
redirect_uri:str = os.getenv("REDIRECT_URI")
client = TestClient(app)

def test_login_redirect(capsys):
    response = client.get("/login")
    
    # captured = capsys.readouterr()
    assert client_id == "53915387c6114eb8a5f3d8938bbd05ee", "CLIENT_ID does not match"
    assert client_secret == "6c51a876d02f45329c079c79d80d6c8a", "CLIENT_SECRET does not match"
    assert redirect_uri == "http://localhost:8888/callback", "REDIRECT_URI does not match"

    assert response.status_code == 302
    assert "Location" in response.headers 

    auth_url = response.headers["Location"]
    assert "https://accounts.spotify.com/authorize" in auth_url
    assert f"client_id={client_id}" in auth_url
    assert "response_type=code" in auth_url
    assert f"redirect_uri={redirect_uri}" in auth_url
    assert "scope=user-follow-read" in auth_url

