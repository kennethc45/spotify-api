# spotify-api
API to display the latest songs of artists that users' follow

# Prerequisites
- Install Docker
- Python 3.12.3

# Steps
1. Clone repository and navigate to it:
    - git clone https://github.com/"GIT_USERNAME"/spotify-api.git

    - cd spotify-api

2. Run this command to build and run the docker container: 
    - docker build -t spotify-api -f docker/Dockerfile . && docker run --name spotify-api-container -p 8888:8888 spotify-api

3. Login w/ your spotify account and grant authorization to the API

# Testing
 - Run 'upytest test_main.py' to start tests

# Endpoints 
###  Login 
- **URL**: `http://localhost:8888/login`
- **Method**: `GET`
- **Description**: The login endpoint prompts the user for their Spotify login. If successful, it will then prompt the user to grant authorization access to the application through the OAuth protocol.
- **Response**: 
  - **Success**: Redirects to `http://localhost:8888/callback`
  - **Error**: Returns an error message if authentication fails.

