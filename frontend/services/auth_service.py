import requests
import os

from dotenv import load_dotenv
from constants.api_routes import AUTH_AR

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
API_URL = os.getenv("API_URL")

def authenticate_user(username, password):
    data = {"username": username, "password": password}
    headers = {'Authorization': f'Bearer {SECRET_KEY}'}
    response = requests.post(f"{API_URL}/{AUTH_AR}/login", json=data, headers=headers)

    if response.status_code == 200:
        return response.json(), True
    else:
        return response.json(), False
