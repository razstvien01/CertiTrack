import requests
import os
from dotenv import load_dotenv
from constants.api_routes import SESSION_AR

load_dotenv()

API_URL = os.getenv("API_URL")

# Function to create or update a session
def create_or_update_session(role, eid):
    try:
        url = f"{API_URL}/{SESSION_AR}/create_or_update"
        data = {
            "role": role,
            "eid": eid
        }
        response = requests.post(url, json=data)

        if response.status_code == 201:
            return response.json(), True
        else:
            return response.json(), False

    except Exception as e:
        print("Error:", e)
        return {'error': str(e)}, False

# Function to fetch the current session
def fetch_session():
    try:
        url = f"{API_URL}/{SESSION_AR}/fetch"
        response = requests.get(url)

        if response.status_code == 200:
            session_data = response.json()
            return session_data, True
        else:
            return response.json(), False

    except Exception as e:
        print("Error:", e)
        return {'error': str(e)}, False

# Function to delete the current session
def delete_session():
    try:
        url = f"{API_URL}/{SESSION_AR}/delete"
        response = requests.delete(url)

        if response.status_code == 200:
            return response.json(), True
        else:
            return response.json(), False

    except Exception as e:
        print("Error:", e)
        return {'error': str(e)}, False

# Function to clean up expired sessions
def cleanup_sessions():
    try:
        url = f"{API_URL}/{SESSION_AR}/cleanup"
        response = requests.post(url)

        if response.status_code == 200:
            return response.json(), True
        else:
            return response.json(), False

    except Exception as e:
        print("Error:", e)
        return {'error': str(e)}, False
