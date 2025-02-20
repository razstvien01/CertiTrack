import requests
import streamlit as st

from constants.config import API_URL
from constants.api_routes import EVENTS_AR

def fetch_events():
    """Fetch event data from the API and return it as JSON."""
    response = requests.get(f"{API_URL}/{EVENTS_AR}")
    if response.status_code == 200:
        # Directly return the JSON data
        data = response.json()
        return data
    else:
        st.error("Failed to fetch event data from the server.")
        return []  # Return an empty list in case of failure

def fetch_event(event_id):
    """Fetch a single event's details from the API."""
    response = requests.get(f"{API_URL}/{EVENTS_AR}/{event_id}")
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error(f"Failed to fetch data for event ID {event_id}.")
        return None

def create_event(event_data):
    """Create a new event via the API."""
    response = requests.post(f"{API_URL}/{EVENTS_AR}", json=event_data)
    if response.status_code == 201:
        st.success(f"Event {event_data['event_name']} created successfully.")
    else:
        st.error("Failed to create event.")

def update_event(event_id, event_data):
    print(event_data)
    """Update an existing event via the API."""
    response = requests.put(f"{API_URL}/{EVENTS_AR}/{event_id}", json=event_data)
    if response.status_code == 200:
        st.success(f"Event {event_data['event_name']} updated successfully.")
    else:
        st.error(f"Failed to update event {event_id}.")

def delete_event(event_id, event_name):
    """Delete an event via the API."""
    response = requests.delete(f"{API_URL}/{EVENTS_AR}/{event_id}")
    if response.status_code == 200:
        st.success(f"Event {event_name} deleted successfully.")
    else:
        st.error(f"Failed to delete event {event_id}.")
