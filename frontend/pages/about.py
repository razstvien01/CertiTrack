import streamlit as st
import time

def pop_out_effect(texts, interval=2.0):
 
    placeholder = st.empty()
    accumulated_text = ""  # To keep track of all displayed text
    
    for text in texts:
        # Apply font styles and sizes using inline CSS
        accumulated_text += f'<div style="font-size: 15px; font-family: Arial, sans-serif; color: #333;">{text}</div><br>'
        placeholder.markdown(accumulated_text, unsafe_allow_html=True)  # Display accumulated text
        time.sleep(interval)  # Wait before showing the next message

# Set up the Streamlit app
# Apply custom font style to the title
st.markdown("""
    <h1 style='font-family: Arial, sans-serif; color: #4CAF50;'>
        About <span style='color: purple;'>Accent</span>Cert App
    </h1>
""", unsafe_allow_html=True)


# Apply custom font style to the text content
st.markdown("""
    <p style='font-family: Arial, sans-serif; color: #555;'>This Employee Web Application Certification Tracker serves as a centralized platform to manage and monitor the certification progress and performance of an employee within an organization.</p>
""", unsafe_allow_html=True)

# List of text messages to display with pop-out effect
texts_to_display = [
    "<b>Certification Management</b>: Easily add, update, and manage your certifications with detailed information such as expiration dates, issuing organizations, and renewal requirements",
    "<b>Customizable Alerts</b>: Set custom alerts for various certification-related activities, such as upcoming training sessions or deadlines",
    "<b>Reporting and Analytics</b>: Generate comprehensive reports and analytics to review your certification history, upcoming renewals, and overall progress",
    "<b>Multi-User Support</b>: Manage certifications for multiple users or team members with role-based access and administrative controls",
    "<b>Integration with External Systems</b>: Seamlessly integrate with external systems or databases to import and sync certification data",
    "<b>User-Friendly Interface</b>: Enjoy an intuitive and easy-to-navigate interface designed for efficient certification management"
]

# Hardcoded interval for the pop-out effect
interval = 2.0

# Start the pop-out effect
if st.button("Key Features"):
    pop_out_effect(texts_to_display, interval)