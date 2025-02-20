import streamlit as st
import requests
import pandas as pd
import json

from constants.config import API_URL
from constants.api_routes import EMPLOYEES_AR

def fetch_employees():
    """Fetch data from the API and return it as a DataFrame."""
    response = requests.get(f"{API_URL}/{EMPLOYEES_AR}")
    if response.status_code == 200:
        data = response.json().get("employees", [])
        df = pd.DataFrame(data)
    else:
        st.error("Failed to fetch data from the server.")
        df = pd.DataFrame()  # Empty dataframe in case of failure
    return df

def fetch_certifications():
    """Fetch certification data from the API."""
    response = requests.get(f"{API_URL}/{EMPLOYEES_AR}/get_certifications")
    if response.status_code == 200:
        return pd.read_json(response.text)
    else:
        st.error("Failed to fetch certification data.")
        return pd.DataFrame()
    
def fetch_certificates():
    """Fetch certification data from the API."""
    response = requests.get(f"{API_URL}/{EMPLOYEES_AR}/certificates")
    if response.status_code == 200:
        data = response.json()  # Convert response to JSON
        certificates = pd.DataFrame(data['certificates'])  # Convert JSON data to DataFrame
        return certificates
    else:
        st.error("Failed to fetch certificates data.")
        return pd.DataFrame()

def update_progress(eid, certification):
    """Update certification progress via the API."""
    payload = {
        "eid": eid,
        "certification": certification
    }
    response = requests.post(f"{API_URL}/{EMPLOYEES_AR}/update_progress", json=payload)
    if response.status_code == 200:
        st.success(f"Database updated for EID: {eid} with Certification: {certification}")
    else:
        st.error("Failed to update the database.")

def add_certification(payload):
    # Make a POST request to your API
    try:
        response = requests.post(f"{API_URL}/{EMPLOYEES_AR}/certification", json=payload)

        if response.status_code == 201:
            st.success("Certification added successfully!")
        else:
            st.error(f"Failed to add certification: {response.json().get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while connecting to the server: {str(e)}")

def update_certification(employees_cert_id, data):
    # Construct the URL for updating certification
    url = f"{API_URL}/update_certification/{employees_cert_id}"
    
    try:
        # Make the PATCH request to your API
        response = requests.patch(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            st.success("Certification updated successfully!")
        else:
            st.error(f"Failed to update certification: {response.json().get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while connecting to the server: {str(e)}")

def delete_certification(cert_id):
    try:
        # Send DELETE request to the API endpoint
        response = requests.delete(f"{API_URL}/delete_certification/{cert_id}")

        # Check response status code
        if response.status_code == 200:
            st.success("Certification deleted successfully!")
        elif response.status_code == 404:
            st.warning('Certification not found.')
        else:
            st.error(f"Failed to delete certification: {response.json().get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while connecting to the server: {str(e)}")

def send_certification_data(employees_cert_id, file_path, certification, status, eid):
    files = {'file': (file_path)}
    data = {'employees_cert_id': employees_cert_id, 'certification': certification, 'status': status, 'EID': eid}
    response = requests.post(f"{API_URL}/submit-certification", data=data, files=files)
    
    if response.status_code == 200:
        st.success("Certification submitted successfully.")
    else:
        st.error(f"Failed to submit certification: {response.json().get('error', 'Unknown error')}")

def fetch_pending_certifications():
    try:
        response = requests.get(f"{API_URL}/get-pending-certifications")
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching pending certifications: {e}")
        return None

def approve_certification(employees_cert_id):
    try:
        response = requests.post(f"{API_URL}/approve-certification", json={
            'employees_cert_id': employees_cert_id
        })
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"Error approving certification: {e}")
        return None