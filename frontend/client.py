import streamlit as st
import time
import os

from dotenv import load_dotenv
from services.auth_service import authenticate_user
from services.session_service import create_or_update_session, fetch_session, delete_session, cleanup_sessions

from constants.config import APP_NAME
from constants.persona import ADMIN, PROJECT_MANAGER, EMPLOYEE
from constants.theme import BG_COLOR, PRIM_COLOR, COLOR_A, COLOR_B, TEXT_COLOR
from constants.path import ADMIN_PATH, EMPLOYEE_PATH, MANAGER_PATH
from constants.assets import LOGO
from datetime import datetime

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

def config_page():
    st.set_page_config(page_title=APP_NAME, page_icon=LOGO)

# **********************************************************************************************************************************************

    #? FUNCTIONS FOR GENERATION OF PAGES

#* Pages for the ADMIN POC
def admin_poc_pages():
    dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon="🪟")
    employee = st.Page("pages/employee.py", title="Employees", icon="🪪")
    certifications = st.Page("pages/certifications.py", title="Certifications", icon="📜")
    ai_assistant = st.Page("pages/ai_assistant.py", title="CertiGuide", icon="🤖")
    ingest_data = st.Page(f"{ADMIN_PATH}/ingest_data.py", title="Ingest CSV Data", icon="💉")
    profile = st.Page(f"pages/profile.py", title="Profile", icon="👤")

    return [dashboard, employee, certifications, ai_assistant, ingest_data, profile]


def manager_pages():
    dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon="🪟")
    employee = st.Page("pages/employee.py", title="Employees", icon="🪪")
    certifications = st.Page("pages/certifications.py", title="Certifications", icon="📜")
    ai_assistant = st.Page("pages/ai_assistant.py", title="CertiGuide", icon="🤖")
    my_team = st.Page(f"pages/my_team.py", title="My Team", icon="🤝")
    profile = st.Page(f"pages/profile.py", title="Profile", icon="👤")

    return [dashboard, employee, certifications, ai_assistant, my_team, profile]

def employee_pages():
    dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon="🪟")
    certifications = st.Page("pages/certifications.py", title="Certifications", icon="📜")
    profile = st.Page(f"pages/profile.py", title="Profile", icon="👤")
    my_team = st.Page(f"pages/my_team.py", title="My Team", icon="🤝")

    return [dashboard, certifications, profile, my_team]

# **********************************************************************************************************************************************

    #? COMPONENT AND NAVIGATOR FUNCTIONS

def show_login_form():
    st.markdown(
        f"""
        <h1 style="text-align: center; font-size: 3rem; font-weight: bold;">
            Welcome to
            <span style="color: #A100FF;">Accent</span><span style="color: {PRIM_COLOR};">Cert</span>!
        </h1>
        <h2 style="text-align: center; font-size: 1.5rem; font-weight: bold; margin-top: -10px;">
            <em>Accent on the future</em>
        </h2>
        """,
        unsafe_allow_html=True
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    st.markdown(
        f"""
        <p style="font-size: 1rem;">
            Designed to help employees track their <span style="color: {PRIM_COLOR}; font-weight: bold;">certification progress</span>, 
            powered by cutting-edge <span style="color: {COLOR_A}; font-weight: bold;">AI</span> and <span style="color: {COLOR_B}; font-weight: bold;">Data</span> technology.
        </p>
        """,
        unsafe_allow_html=True
    )

    if st.button("Login", type="primary", disabled=st.session_state.logged_in):
        response, success = authenticate_user(username, password)
        
        if success:
            persona = response.get("role")
            st.session_state.logged_in = True
            st.session_state.persona = persona
            st.session_state.EID = username

            # Create a session
            session_response, session_success = create_or_update_session(persona, st.session_state.EID)

            if session_success:
                st.session_state.session_id = session_response.get("session_id")
                st.info("Logging in... Please wait.")
                time.sleep(2)
                st.balloons()
                st.success("Login successful! Redirecting to your dashboard.")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Failed to create a session. Please try again.")
        else:
            st.error("Invalid username or password. Please try again.")

def logout():
    # Clear session state
    delete_session()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    time.sleep(0.1)
    st.rerun()
    

def redirect_dashboard(persona):
    logout_page = st.Page(logout, title="Log out", icon="🔓")
    about = st.Page("pages/about.py", title="About", icon="❓")
    help = st.Page("pages/help.py", title="Help", icon="💡")
    
    if persona == ADMIN:
        pg = st.navigation({
            f"Account Type: {ADMIN}": admin_poc_pages(),
            "Information": [about, help],
            "Account": [logout_page]
        })

        pg.run()

    elif persona == PROJECT_MANAGER:
        pg = st.navigation({
            f"Account Type: {PROJECT_MANAGER}": manager_pages(),
            "Information": [about, help],
            "Account": [logout_page]
        })
        pg.run()

    elif persona == EMPLOYEE:
        pg = st.navigation({
            f"Account Type: {EMPLOYEE}": employee_pages(),
            "Information": [about, help],
            "Account": [logout_page]
        })
        pg.run()
        

def check_session():
    session_response, session_success = fetch_session()
    if session_success:
        cleanup_expired_sessions(session_response)
    else:
        st.session_state.logged_in = False
        st.session_state.persona = None
        st.session_state.EID = None
        st.session_state.session_id = None
        # st.rerun()

def init_states():
    # Initialize session state to keep track of login status and persona
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'persona' not in st.session_state:
        st.session_state.persona = None
    if 'EID' not in st.session_state:
        st.session_state.EID = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None


def cleanup_expired_sessions(session_response):
    expiration_date = datetime.fromisoformat(session_response.get("expiration_date"))
    if expiration_date < datetime.utcnow():
        st.warning("Session expired. Please log in again.")
        logout()
    else:
        st.session_state.logged_in = True
        st.session_state.persona = session_response.get('role')
        st.session_state.EID = session_response.get('eid')
        st.session_state.session_id = session_response.get('session_id')

# **********************************************************************************************************************************************

    #? MAIN FUNCTION

def main():
    config_page()
    init_states()
    
    st.markdown(
        f"""
        <style>
        html, body {{
            height: 100%;
            margin: 0;
        }}
        .main {{
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            box-sizing: border-box;
        }}
        .header {{
            width: 100%;
            padding-top: 4rem;
            padding-right: 2.5rem;
            background-color: {BG_COLOR};
            color: white;
            text-align: right;
            font-size: 1.5rem;
            font-weight: bold;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
            color: #000000;
        }}
        .title {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            font-size: 1.2rem;
            color: {TEXT_COLOR};
        }}
        .stTextInput input {{
            padding: 0.75rem;
            border-radius: 5px;
            border: 1px solid #ddd;
            font-size: 1rem;
        }}
        .stButton>button {{
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
            margin-top: 1rem;
        }}
        .stTextInput input:focus {{
            border-color: {PRIM_COLOR};
            outline: none;
            box-shadow: 0px 0px 5px rgba(105, 105, 105, 0.5);
        }}
        .stAlert {{
            margin-top: 1rem;
        }}
        .footer {{
            position: fixed;
            bottom: 0;
            right: 0;
            width: 100%;
            text-align: right;
            padding: 1rem;
            font-size: 0.75rem;
            color: #888;
            background-color: {BG_COLOR};
        }}
        .hidden {{
            display: none;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Check and clean up expired sessions
    check_session()

    if st.session_state.logged_in:
        # Display header with title in upper-right corner after login
        st.markdown(
            f"""
            <div class="header">
                <span style="color: #A100FF;">Accent</span><span style="color: {PRIM_COLOR};">Cert</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        redirect_dashboard(st.session_state.persona)
    else:
        login_page = st.Page("client.py", title="Log in", icon=":material/login:")
        pg = st.navigation([login_page])
        pg.run()
        st.image(LOGO, width=100, use_column_width=False)
        show_login_form()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="footer">
            &copy; 2024 {APP_NAME}. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == '__main__':
    main()
