import requests
import streamlit as st

from constants.config import API_URL
from constants.api_routes import INGEST_AR

def upload_csv(file, table_name, operation):
    files = {'file': file}
    data = {'table_name': table_name, 'operation': operation}

    response = requests.post(f"{API_URL}/{INGEST_AR}/upload_csv", files=files, data=data)
    
    if response.status_code == 200:
        st.success(response.json()['message'])
    else:
        st.error("Failed to upload")
        st.error(response.json().get('error', 'Failed to upload CSV.'))
