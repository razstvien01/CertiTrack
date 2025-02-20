import requests
import streamlit as st

from constants.config import API_URL, SECRET_KEY
from constants.api_routes import LLM_AR

def get_data_from_api():
    headers = {'Authorization': f'Bearer {SECRET_KEY}'}
    response = requests.get(f"{API_URL}/{LLM_AR}", headers=headers)
    
    if response.status_code == 200:
        return response.json().get('database', [])
    else:
        st.error(f"Error fetching data: {response.status_code}")
        return []
    

def ask_llm(question):
    # Replace this with your Azure OpenAI API call
    response = requests.post(f"{API_URL}/{LLM_AR}", json={"question": question}, headers={'Authorization': f'Bearer {SECRET_KEY}'})
    if response.status_code == 200:
        st.markdown(f"### CertiGuide Response:")
        st.success(response.json().get('answer', 'No answer provided'))
    else:
        st.error(f"Error fetching data: {response.status_code}")

def get_suggested_questions():
    headers = {'Authorization': f'Bearer {SECRET_KEY}'}
    response = requests.get(f"{API_URL}/{LLM_AR}/suggested-questions", headers=headers)
    
    if response.status_code == 200:
        return response.json().get('suggested_questions', [])
    else:
        st.error(f"Error fetching suggested questions: {response.status_code}")
        return []
