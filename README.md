# spotify-api
API to display the latest songs of artists that users' follow

# Steps
1. Run 'python3 -m venv tutorial-env' to build environment

2. Run 'source tutorial-env/bin/activate' to activate environment

3. Install these packages:
    - pip3 install python-dotenv
    - pip3 install requests
    - pip3 install fastapi uvicorn
    - pip3 install pytest httpx pytest-asyncio

4. Run 'uvicorn main:app --reload' to start the api
    - If the log in page won't show up due to cookies or denied access, then run the command below
        - uvicorn main:app --host 0.0.0.0 --port 8888 --reload

    - Run 'upytest test_main.py' to start tests

# Endpoints 
- http://127.0.0.1:8000/login (For uvicorn main:app --reload)
- http://localhost:8888/login (For uvicorn main:app --host 0.0.0.0 --port 8888 --reload)

