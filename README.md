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
    - Run 'upytest test_main.py' to start tests
    - uvicorn main:app --host 0.0.0.0 --port 8888

# Endpoints 
- http://127.0.0.1:8000/login (Does not work?)
- http://localhost:8888/login

