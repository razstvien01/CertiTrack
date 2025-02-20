import streamlit as st
import time
import re

from streamlit_calendar import calendar
from datetime import datetime
from services.events_service import fetch_events
from datetime import datetime

from constants.theme import PRIM_COLOR, BG_COLOR, TEXT_COLOR
from services.events_service import create_event, update_event, delete_event
from constants.persona import ADMIN

def format_event_date(date_str, time_str):
    # Combine date and time into a single datetime object
    try:
        return datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %I:%M%p").strftime("%Y-%m-%d")
    except ValueError:
        return ''

def format_events(events_data):
    events = []
    for event in events_data:
        # Combine the title with the start and end times
        title = f"{event.get('event_name', 'No Title')} {event.get('start_time', '')} - {event.get('end_time', '')}"
        
        # Format the start and end dates
        start_date = format_event_date(event.get('start_date', ''), event.get('start_time', ''))
        end_date = format_event_date(event.get('end_date', ''), event.get('end_time', ''))
        
        # Create the formatted event
        formatted_event = {
            "title": title,
            "color": event.get('color', '#000000'),
            "start": start_date,
            "end": end_date,
            "description": event.get('description', '') if event.get('description') is not None else '',
            "event_id": event.get('event_id', '')
        }
        events.append(formatted_event)
    return events

# Function to display event details
def display_event_details(event):
    # Extract event details
    title = event.get('title', 'No Title')
    start = event.get('start', 'No Start Time')
    end = event.get('end', 'No End Time')
    all_day = 'Yes' if event.get('allDay', False) else 'No'
    background_color = event.get('backgroundColor', '#000000')  # Default to white if no color is provided
    description = event['extendedProps'].get('description', 'No Description')

    # Display event details with enhanced UI
    st.markdown(f"""
    <div style="padding: 10px; border: 5px solid {background_color}; border-radius: 5px;">
        <h3 style="margin-top: 0;">Event Details:</h3>
        <p><strong>Title:</strong> {title}</p>
        <p><strong>Start:</strong> {start}</p>
        <p><strong>End:</strong> {end}</p>
        <p><strong>All Day Event:</strong> {all_day}</p>
        <p><strong>Description:</strong> {description}</p>
    </div>
    """, unsafe_allow_html=True)

# Function to handle adding a new event
@st.dialog("Add New Event")
def add_event():
    title = st.text_input("Event Title")
    description = st.text_area("Event Description")
    start_date = st.date_input("Start Date", datetime.today())
    start_time = st.time_input("Start Time")
    end_date = st.date_input("End Date", datetime.today())
    end_time = st.time_input("End Time")
    color = st.color_picker("Event Color", "#DC143C")

    submit_button = st.button("Confirm", type="primary")

    if submit_button:
        # Input validation
        if not title:
            st.error("Event title is required.")
        elif not description:
            st.error("Event description is required.")
        elif end_date < start_date or (end_date == start_date and end_time <= start_time):
            st.error("End date/time must be after the start date/time.")
        elif not color:
            st.error("Event color must be selected.")
        else:
            # Add the event if all validations pass
            new_event = {
                "event_name": title,
                "description": description,
                "start_date": start_date.strftime("%m/%d/%Y"),  # Format as mm/dd/yyyy
                "start_time": start_time.strftime("%I:%M%p"),
                "end_date": end_date.strftime("%m/%d/%Y"),  # Format as mm/dd/yyyy
                "end_time": end_time.strftime("%I:%M%p"),
                "color": color,
            }
            
            create_event(new_event)
            time.sleep(2)
            st.rerun()
            
# Function to handle updating a selected event
@st.dialog("Update Selected Event")
def update_selected_event():
    # Check if an event is selected
    events = st.session_state.events
    selected_event = st.session_state.selected_event

    event_id = st.session_state.selected_event['extendedProps']['event_id']

    event = next((event for event in events if event['event_id'] == event_id), None)

    # Extract and convert date formats
    start_date_str = selected_event["start"]
    end_date_str = selected_event["end"]

    # Convert date from YYYY-MM-DD to MM/DD/YYYY
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").strftime("%m/%d/%Y")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").strftime("%m/%d/%Y")

    # Regular expression to extract time information
    time_pattern = r'(\d{1,2}:\d{2}[APM]{2}) - (\d{1,2}:\d{2}[APM]{2})'

    event_name = event['title']
    match = re.search(time_pattern, event_name)

    start_time_str = match.group(1)
    end_time_str = match.group(2)

    # Regular expression to match the event name (anything before the time)
    event_name_match = re.match(r'^(.*?)\s\d{1,2}:\d{2}[AP]M', event_name)

    event_name = event_name_match.group(1)

    # Pre-fill the input fields with the selected event's data
    title = st.text_input("Event Title", value=event_name)
    description = st.text_area("Event Description", value=selected_event['extendedProps']['description'])
    start_date = st.date_input("Start Date", value=datetime.strptime(start_date, "%m/%d/%Y"))
    start_time = st.time_input("Start Time", value=datetime.strptime(start_time_str, "%I:%M%p").time())
    end_date = st.date_input("End Date", value=datetime.strptime(end_date, "%m/%d/%Y"))
    end_time = st.time_input("End Time", value=datetime.strptime(end_time_str, "%I:%M%p").time())
    color = st.color_picker("Event Color", value=event["color"])

    submit_button = st.button("Confirm", type="primary")

    if submit_button:
        # Input validation
        if not title:
            st.error("Event title is required.")
        elif not description:
            st.error("Event description is required.")
        elif end_date < start_date or (end_date == start_date and end_time <= start_time):
            st.error("End date/time must be after the start date/time.")
        elif not color:
            st.error("Event color must be selected.")
        else:
            # Update the event if all validations pass
            updated_event = {
                "event_name": title,
                "description": description,
                "start_date": start_date.strftime("%m/%d/%Y"),  # Format as mm/dd/yyyy
                "start_time": start_time.strftime("%I:%M%p"),
                "end_date": end_date.strftime("%m/%d/%Y"),  # Format as mm/dd/yyyy
                "end_time": end_time.strftime("%I:%M%p"),
                "color": color,
            }
            
            update_event(event_id, updated_event)
            st.session_state.selected_event = None

            time.sleep(2)
            st.rerun()

# Function to handle updating a new event
@st.dialog("Delete Selected Event")
def delete_selected_event():
    st.text("Are you sure you want to removed this event?")

    submit_button = st.button("Confirm", type="primary")

    if submit_button:
        selected_event = st.session_state.selected_event
        # Check if an event is selected
        event_id = selected_event['extendedProps']['event_id']
        event_name = selected_event['title']

        # Regular expression to match the event name (anything before the time)
        event_name_match = re.match(r'^(.*?)\s\d{1,2}:\d{2}[AP]M', event_name)
        event_name = event_name_match.group(1)

        delete_event(event_id, event_name)
        time.sleep(2)
        st.rerun()

def show_custom_toast(message, icon="⚠️"):
    """
    Displays a custom toast-like notification in the bottom right corner.
    
    Parameters:
    - message (str): The text to display in the toast.
    - icon (str): An optional icon to display next to the message.
    """
    # Define the HTML structure for the toast
    html = f"""
    <div style="
        position: fixed;
        bottom: 20px; right: 20px;
        padding: 16px;
        border-radius: 10px;
        z-index: 1;
        background-color: {PRIM_COLOR};
        color: {BG_COLOR};
    ">
        <span>{icon}</span>
        <span>{message}</span>
    </div>
    """

    # Inject the HTML into the Streamlit app
    st.markdown(html, unsafe_allow_html=True)

def event_CUD():
    st.sidebar.write("---")
    
    # Event Management buttons with custom CSS classes
    st.sidebar.text("Event Management")

    # Add New Event Button
    if st.sidebar.button("Add New Event"):
        add_event()

    # Update Selected Event Button
    if st.sidebar.button("Update Selected Event"):
        if st.session_state.selected_event:
            update_selected_event()
        else:
            show_custom_toast("Please select an event to update first in the calendar.", icon="⚠️")

    # Delete Selected Event Button
    if st.sidebar.button("Delete Selected Event"):
        if st.session_state.selected_event:
            delete_selected_event()
        else:
            show_custom_toast("Please select an event to delete first in the calendar.", icon="⚠️")
            
def dashboard_page():
    # Custom CSS for the calendar
    custom_css = """
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
        .fc-event {
            border-radius: 4px;
        }
    """

    # Available calendar views
    view_options = [
        "dayGridMonth",
        "timeGridWeek",
        "timeGridDay",
        "listWeek"
    ]

    st.sidebar.subheader("⚙️ Calendar Settings")

    # Move the calendar mode type selector to the sidebar
    calendar_mode = st.sidebar.selectbox(
        "Choose Calendar Mode",
        view_options
    )

    # Fetch events from the server
    events_data = fetch_events()

    # Transform events data into the format required by the calendar
    if events_data:
        events = []
        for event in events_data:
            formatted_event = {
                "title": event.get('event_name', 'No Title'),
                "color": event.get('color', '#FFFFFF'),
                "start": f"{event.get('start_date', '')} {event.get('start_time', '')}",
                "end": f"{event.get('end_date', '')} {event.get('end_time', '')}",
                "description": event.get('description', 'No Description'),
                "event_id": event.get('event_id', '')
            }
            events.append(formatted_event)
    else:
        st.error("No events available.")
        events = []

    formatted_events = format_events(events_data)

    # Initialize session state for events
    if 'events' not in st.session_state:
        st.session_state.events = formatted_events
    else:
        st.session_state.events = formatted_events

    if 'selected_event' not in st.session_state:
        st.session_state.selected_event = None
    
    # Update calendar options
    calendar_options = {
        "editable": "true",
        "selectable": "true",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth",
        },
        "slotMinTime": "06:00:00",
        "slotMaxTime": "18:00:00",
        "initialView": calendar_mode,
        "resources": st.session_state.events
    }

    # Custom CSS for button styling
    st.markdown(f"""
        <style>
        .stButton > button {{
            width: 100%; /* Full width */
            height: 40px; /* Fixed height for uniformity */
            margin-bottom: 10px; /* Spacing between buttons */
            font-size: 16px; /* Adjust font size */
            # color: {TEXT_COLOR}; /* Text color */
            # background-color: {PRIM_COLOR}; /* Background color */
            border: none; /* Remove border */
            border-radius: 5px; /* Rounded corners */
            cursor: pointer; /* Pointer on hover */
        }}
        </style>
        """, unsafe_allow_html=True)

    if st.session_state.persona == ADMIN:
        event_CUD()


    # Page title and description
    st.title("Event Calendar Dashboard")
    st.write("""
    Here, you can view, manage, and add events to your calendar. 
    Use the options on the sidebar to customize your view and manage your events.
    """)

    st.markdown("**Hint:** Adjust the widen view option based on your preference—turn it off to see the full calendar, or leave it on for a wider view for other calendar mode.")
    # Display the calendar
    calendar_widget = calendar(events=st.session_state.events, options=calendar_options, custom_css=custom_css)
    
    # Check if the eventClick callback is present
    if calendar_widget.get("callback") == "eventClick":
        st.session_state.selected_event = event_details = calendar_widget.get("eventClick", {}).get("event", {})
        
        display_event_details(event_details)
    else:
        st.session_state.selected_event = None

# Call the dashboard_page function to render the page
dashboard_page()
