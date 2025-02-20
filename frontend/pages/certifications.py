import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import time

from datetime import datetime
from services.employee_service import fetch_certifications, fetch_certificates, add_certification as add_cert, send_certification_data
from constants.persona import ADMIN, PROJECT_MANAGER
from constants.theme import PRIM_COLOR, BG_COLOR
from services.employee_service import update_certification, delete_certification, fetch_pending_certifications, approve_certification

from io import BytesIO

def generate_csv_download_link(df, filename_prefix):
    """Generate a download link for a CSV file with the current date and time."""
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{filename_prefix}_{current_time}.csv"
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    st.download_button(
        label="📥 Download CSV",
        data=csv_buffer,
        file_name=filename,
        mime="text/csv"
    )

def truncate_string(s, max_length):
    if len(s) > max_length:
        return s[:max_length - 3] + '...'  # Subtract 3 to account for the length of '...'
    return s

def plot_certifications_by_level(df):
    st.subheader("Certifications by Level 🏆")

    level_counts = df['Certification_Level'].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=level_counts.index, y=level_counts.values, ax=ax, palette="viridis", hue=level_counts.index, legend=False)
    ax.set_xlabel("Certification Level", fontsize=10)
    ax.set_ylabel("Count", fontsize=10)
    ax.set_title("Number of Certifications by Level", fontsize=12)
    ax.tick_params(axis='x', labelsize=7)
    ax.tick_params(axis='y', labelsize=8)
    st.pyplot(fig)

def plot_progress_distribution(df):
    st.subheader("Progress Distribution 📈")

    progress_counts = df['CURRENT_PROGRESS'].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=progress_counts.index, y=progress_counts.values, ax=ax, palette="coolwarm", hue=progress_counts.index, legend=False)
    ax.set_xlabel("Current Progress", fontsize=10)
    ax.set_ylabel("Count", fontsize=10)
    ax.set_title("Distribution of Certification Progress", fontsize=12)
    ax.tick_params(axis='x', labelsize=7.5)
    ax.tick_params(axis='y', labelsize=8)
    st.pyplot(fig)

def plot_certifications_by_project(df):
    st.subheader("Certifications by Project 🗂️")

    # Calculate the count of certifications by project
    project_counts = df['PROJECT_NAME'].value_counts().reset_index()
    project_counts.columns = ['Project Name', 'Count']

    # Create an interactive bar plot using Plotly
    fig = px.bar(
        project_counts,
        x='Project Name',
        y='Count',
        color='Project Name',
        title="Number of Certifications by Project",
        labels={'Project Name': 'Project Name', 'Count': 'Number of Certifications'},
        height=400
    )

    # Update layout for better readability
    fig.update_layout(
        xaxis_title="Project Name",
        yaxis_title="Count",
        xaxis_tickangle=-45,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_certifications_by_manager(df):
    st.subheader("Certifications by Manager 👨‍💼")

    # Calculate the count of certifications by manager
    manager_counts = df['MANAGER_EID'].value_counts().reset_index()
    manager_counts.columns = ['Manager EID', 'Count']

    # Create an interactive bar plot using Plotly
    fig = px.bar(
        manager_counts,
        x='Manager EID',
        y='Count',
        color='Manager EID',
        title="Number of Certifications by Manager",
        labels={'Manager EID': 'Manager EID', 'Count': 'Number of Certifications'},
        height=400
    )

    # Update layout for better readability
    fig.update_layout(
        xaxis_title="Manager EID",
        yaxis_title="Count",
        xaxis_tickangle=-45,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_certifications_by_year(df):
    st.subheader("Certifications by Year 📅")

    year_counts = df['Fiscal_Year'].value_counts().sort_index(ascending=False)
    fig, ax = plt.subplots()
    sns.lineplot(x=year_counts.index, y=year_counts.values, ax=ax, marker="o", color="b")
    ax.set_xlabel("Fiscal Year", fontsize=10)
    ax.set_ylabel("Count", fontsize=10)
    ax.set_title("Number of Certifications by Fiscal Year", fontsize=12)
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    ax.invert_xaxis()  # Reverse the x-axis
    st.pyplot(fig)  

def plot_certifications_by_quarter(df):
    st.subheader("Certifications by Quarter 📅")

    quarter_counts = df['Quarter'].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=quarter_counts.index, y=quarter_counts.values, ax=ax, palette="husl", hue=quarter_counts.index, legend=False)
    ax.set_xlabel("Quarter", fontsize=10)
    ax.set_ylabel("Count", fontsize=10)
    ax.set_title("Number of Certifications by Quarter", fontsize=12)
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    st.pyplot(fig)

# Dialog to handle adding a new certification
@st.dialog("Add New Certification")
def add_certification(df):
    st.session_state['dialog_open'] = True
    st.write("### Add New Certification")

    # Function to filter and sort unique values, excluding None values
    def filter_values(column_name):
        unique_values = df[column_name].dropna().unique()  # Drop None values
        return sorted(unique_values)

    # Input fields
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    eid = st.text_input("EID")  # Selectbox for Employee ID
    emp_id = st.text_input("Employee ID")
    manager_eid = st.selectbox("Manager EID", filter_values("MANAGER_EID"))  # Selectbox for Manager EID
    management_level = st.selectbox("Management Level", filter_values("MANAGEMENT_LEVEL"))  # Selectbox for Management Level
    capability = st.selectbox("Capability", filter_values("CAPABILITY"))  # Selectbox for Capability
    employee_status = st.selectbox("Employee Status", filter_values("EMPLOYEE_STATUS"))  # Selectbox for Employee Status
    with_voucher = st.selectbox("With Voucher", ["Yes", "Requested", "No"])  # Selectbox for Voucher Status
    current_progress = st.selectbox("Current Progress", ["In progress - 1st take", "In progress - 2nd take", "Passed", "Failed"])  # Selectbox for Current Progress
    
    project_name = st.selectbox("Project Name", filter_values("PROJECT_NAME"))
    fiscal_year = st.selectbox("Fiscal Year", filter_values("Fiscal_Year"))  # Selectbox for Fiscal Year
    quarter = st.selectbox("Quarter", filter_values("Quarter"))  # Selectbox for Quarter

    # Expiration date input with an option for no expiration date
    expiration_date_option = st.selectbox("Expiration Date Option", ["Has Expiration Date", "No Expiration Date"])
    if expiration_date_option == "Has Expiration Date":
        expiration_date = st.date_input("Expiration Date")
    else:
        expiration_date = None

    month = expiration_date.strftime("%B") if expiration_date else "Unknown"
    st.write(f"Month based on expiration date: {month}")

    # Fetch certification names for dropdown
    certification_names = fetch_certificates()
    if 'Certification_Name' not in certification_names:
        st.error("Failed to fetch certification names.")
        return
    
    target_certification = st.selectbox("Target Certification", certification_names['Certification_Name'])
    first_target_date = st.date_input("1st Target Certification Date", datetime.today())

    # Prepare the data to send to the API
    if st.button("Confirm", type="primary"):
        # Validate inputs
        if not first_name or not last_name or not eid or not manager_eid or not project_name:
            st.error("All fields are required.")
            return
        
        # Convert date to the correct format
        first_target_date_str = first_target_date.strftime("%m/%d/%Y")
        expiration_date_str = expiration_date.strftime("%m/%d/%Y") if expiration_date else None

        # Create the payload
        payload = {
            'FIRST_NAME': first_name,
            'LAST_NAME': last_name,
            'EID': eid,
            'EMPLOYEE_ID': emp_id,
            'MANAGER_EID': manager_eid,
            'MANAGEMENT_LEVEL': management_level,
            'CAPABILITY': capability,
            'EMPLOYEE_STATUS': employee_status,
            'WITH_VOUCHER': with_voucher,
            'CURRENT_PROGRESS': current_progress,
            'TARGET_CERTIFICATION': target_certification,
            '1ST_TARGET_CERTIFICATION_DATE': first_target_date_str,
            'RETAKE_EXAM_DATE': None,  # Placeholder if not provided
            'EXPIRATION_DATE': expiration_date_str,  # Will be None if not provided
            'FISCAL_YEAR': fiscal_year,
            'QUARTER': quarter,
            'MONTH': month,
            'PROJECT_NAME': project_name
        }

        add_cert(payload)

        time.sleep(2)
        st.rerun()

@st.dialog("Update Selected Certification")
def update_selected_certification(selected_certification, df):
    st.session_state['dialog_open'] = True
    st.write("### Update Selected Certification")

    # Function to filter and sort unique values, excluding None values
    def filter_values(column_name):
        unique_values = df[column_name].dropna().unique()  # Drop None values
        return list(sorted(unique_values))  # Ensure the result is a list

    # Function to safely get the selected option
    def get_selected_option(options, value):
        options_list = list(options)  # Ensure options is a list
        if value in options_list:
            return value
        return options_list[0] if options_list else None

    # Input fields
    first_name = st.text_input("First Name", value=selected_certification.get('FIRST_NAME', ''))
    last_name = st.text_input("Last Name", value=selected_certification.get('LAST_NAME', ''))
    eid = st.text_input("EID", value=selected_certification.get('EID', ''))
    emp_id = st.text_input("Employee ID", value=selected_certification.get('EMPLOYEE_ID', ''))
    
    # Filtered options
    manager_eid_options = filter_values("MANAGER_EID")
    manager_eid = get_selected_option(manager_eid_options, selected_certification.get('MANAGER_EID'))
    manager_eid = st.selectbox("Manager EID", manager_eid_options, index=manager_eid_options.index(manager_eid) if manager_eid in manager_eid_options else 0)
    
    management_level_options = filter_values("MANAGEMENT_LEVEL")
    management_level = get_selected_option(management_level_options, selected_certification.get('MANAGEMENT_LEVEL'))
    management_level = st.selectbox("Management Level", management_level_options, index=management_level_options.index(management_level) if management_level in management_level_options else 0)
    
    capability_options = filter_values("CAPABILITY")
    capability = get_selected_option(capability_options, selected_certification.get('CAPABILITY'))
    capability = st.selectbox("Capability", capability_options, index=capability_options.index(capability) if capability in capability_options else 0)
    
    employee_status_options = filter_values("EMPLOYEE_STATUS")
    employee_status = get_selected_option(employee_status_options, selected_certification.get('EMPLOYEE_STATUS'))
    employee_status = st.selectbox("Employee Status", employee_status_options, index=employee_status_options.index(employee_status) if employee_status in employee_status_options else 0)
    
    with_voucher_options = ["Yes", "Requested", "No"]
    with_voucher = get_selected_option(with_voucher_options, selected_certification.get('WITH_VOUCHER'))
    with_voucher = st.selectbox("With Voucher", with_voucher_options, index=with_voucher_options.index(with_voucher) if with_voucher in with_voucher_options else 0)
    
    current_progress_options = ["In progress - 1st take", "In progress - 2nd take", "Passed", "Failed"]
    current_progress = get_selected_option(current_progress_options, selected_certification.get('CURRENT_PROGRESS'))
    current_progress = st.selectbox("Current Progress", current_progress_options, index=current_progress_options.index(current_progress) if current_progress in current_progress_options else 0)

    project_name_options = filter_values("PROJECT_NAME")
    project_name = get_selected_option(project_name_options, selected_certification.get('PROJECT_NAME'))
    project_name = st.selectbox("Project Name", project_name_options, index=project_name_options.index(project_name) if project_name in project_name_options else 0)
    
    fiscal_year_options = filter_values("Fiscal_Year")
    fiscal_year = get_selected_option(fiscal_year_options, selected_certification.get('FISCAL_YEAR'))
    fiscal_year = st.selectbox("Fiscal Year", fiscal_year_options, index=fiscal_year_options.index(fiscal_year) if fiscal_year in fiscal_year_options else 0)
    
    quarter_options = filter_values("Quarter")
    quarter = get_selected_option(quarter_options, selected_certification.get('QUARTER'))
    quarter = st.selectbox("Quarter", quarter_options, index=quarter_options.index(quarter) if quarter in quarter_options else 0)

    # Expiration date input with an option for no expiration date
    expiration_date_option = st.selectbox("Expiration Date Option", ["Has Expiration Date", "No Expiration Date"], index=["Has Expiration Date", "No Expiration Date"].index("Has Expiration Date" if selected_certification.get('EXPIRATION_DATE') else "No Expiration Date"))
    if expiration_date_option == "Has Expiration Date":
        expiration_date = st.date_input("Expiration Date", value=datetime.strptime(selected_certification.get('EXPIRATION_DATE', '01/01/2024'), "%m/%d/%Y"))
    else:
        expiration_date = None

    month = expiration_date.strftime("%B") if expiration_date else "Unknown"
    st.write(f"Month based on expiration date: {month}")

    # Fetch certification names for dropdown
    certification_names = fetch_certificates()
    if 'Certification_Name' not in certification_names:
        st.error("Failed to fetch certification names.")
        return

    target_certification_options = certification_names['Certification_Name']
    target_certification = get_selected_option(target_certification_options, selected_certification.get('TARGET_CERTIFICATION'))
    target_certification = st.selectbox("Target Certification", target_certification_options, index=target_certification_options.index(target_certification) if target_certification in target_certification_options else 0)

    first_target_date = st.date_input("1st Target Certification Date", value=datetime.strptime(selected_certification.get('1ST_TARGET_CERTIFICATION_DATE', '01/01/2024'), "%m/%d/%Y"))

    # Prepare the data to send to the API
    if st.button("Confirm", type="primary"):
        # Validate inputs
        if not first_name or not last_name or not eid or not manager_eid or not project_name:
            st.error("All fields are required.")
            return
        
        # Convert date to the correct format
        first_target_date_str = first_target_date.strftime("%m/%d/%Y")
        expiration_date_str = expiration_date.strftime("%m/%d/%Y") if expiration_date else None
        
        # Create the payload
        payload = {
            'FIRST_NAME': first_name,
            'LAST_NAME': last_name,
            'EID': eid,
            'EMPLOYEE_ID': emp_id,
            'MANAGER_EID': manager_eid,
            'MANAGEMENT_LEVEL': management_level,
            'CAPABILITY': capability,
            'EMPLOYEE_STATUS': employee_status,
            'WITH_VOUCHER': with_voucher,
            'CURRENT_PROGRESS': current_progress,
            'TARGET_CERTIFICATION': target_certification,
            '1ST_TARGET_CERTIFICATION_DATE': first_target_date_str,
            'EXPIRATION_DATE': expiration_date_str,  # Will be None if not provided
            'FISCAL_YEAR': fiscal_year,
            'QUARTER': quarter,
            'MONTH': month,
            'PROJECT_NAME': project_name,
        }
        update_certification(str(selected_certification['employees_cert_id']), payload)

        time.sleep(2)
        st.rerun()


# Dialog to handle deleting a selected certification
@st.dialog("Delete Selected Certification")
def delete_selected_certification(employees_cert_id):
    st.write(f"Are you sure you want to delete the selected certification?")

    if st.button("Confirm Deletion", type='primary'):
        delete_certification(employees_cert_id)
        
        time.sleep(2)
        st.rerun()


def sort_by_ranking(levels):
    RANKING_ORDER = {
        'Fundamentals/Practitioner': 1,
        'Associate': 2,
        'Professional/Specialty': 3,
        'Expert': 4,
    }
    return pd.Categorical(levels, categories=RANKING_ORDER, ordered=True)

def move_column_to_front(df, column_name):
    if column_name in df.columns:
        cols = df.columns.tolist()
        cols.insert(0, cols.pop(cols.index(column_name)))
        df = df[cols]
    return df

def certificates_page():
    st.title("🎓 Detailed Certificates")

    # Fetch certification data from the API
    df = fetch_certificates()

    if not df.empty:
        # Sidebar filters
        st.sidebar.header("🔍 Filters")
        name_filter = st.sidebar.text_input("🔍 Search by Certificate Name", "")
        
        # Add filter for levels
        level_filter = st.sidebar.selectbox("📜 Select Level", ["All Levels"] + list(pd.unique(df["Certification_Level"])))
        
        # Sort by levels
        sort_by = st.sidebar.radio("Sort by Level", ["No Sorting", "Ascending", "Descending"])

        # Add a filter for the rankings
        group_by_ranking = st.sidebar.checkbox("Group by Certification Levels", value=False)
        
        df = df.drop(columns='certification_id')

        # Apply filters
        df_filtered = df.copy()

        if name_filter:
            df_filtered = df_filtered[df_filtered["Certification_Name"].str.contains(name_filter, case=False, na=False)]
            df_filtered = move_column_to_front(df_filtered, "Certification_Name")

        if level_filter != "All Levels":
            df_filtered = df_filtered[df_filtered["Certification_Level"] == level_filter]
            df_filtered = move_column_to_front(df_filtered, "Certification_Level")

        # Sort data by level
        if sort_by == "Ascending":
            df_filtered["Certification_Level"] = sort_by_ranking(df_filtered["Certification_Level"])
            df_filtered = df_filtered.sort_values(by="Certification_Level", ascending=True)
        elif sort_by == "Descending":
            df_filtered["Certification_Level"] = sort_by_ranking(df_filtered["Certification_Level"])
            df_filtered = df_filtered.sort_values(by="Certification_Level", ascending=False)

        # Group by certification level if selected
        if group_by_ranking:
            df_filtered = df_filtered.groupby('Certification_Level').apply(lambda x: x).reset_index(drop=True)

        st.write("Detailed Certificate Data:")
        st.dataframe(df_filtered)  # Display the DataFrame in Streamlit
    else:
        st.warning("No certificate data available.")

    if st.button("Back to Certifications"):
        st.session_state['page'] = 'certifications'
        st.rerun()  # Force a page rerun to navigate back to the certifications page


def upload_cert():
    st.subheader("✅ Update Certification Progress")
    uploaded_file = st.file_uploader("Upload Certificate (File Name: <EID>-<Certification Name>)")

    if uploaded_file is not None:
        # Extract the file name without the extension
        file_name = os.path.splitext(uploaded_file.name)[0]

        # Split the file name by '-'
        parts = file_name.split('-')

        # Check if we have exactly 2 parts
        if len(parts) != 2:
            st.error("File name must contain exactly one dash to separate EID and certification.")
            return

        eid, certification = parts

        # Define the upload path
        upload_path = 'uploads'
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        # Create the full file path
        file_path = os.path.join(upload_path, uploaded_file.name)

        # Save the file
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())

        st.success(f"Uploaded certificate for {eid} - {certification}")

        # Store file info in session state
        st.session_state['uploaded_file_info'] = {
            'file_name': uploaded_file.name,
            'certification': certification,
        }
            
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

def display_approval_dialog(selected_cert):
    if selected_cert:
        with st.expander("Certificate Approval", expanded=True):
            st.write(f"**Employee Certification ID**: {selected_cert.get('employees_cert_id', 'N/A')}")
            st.write(f"**Employee ID**: {selected_cert.get('EMPLOYEE_ID', 'N/A')}")
            st.write(f"**First Name**: {selected_cert.get('FIRST_NAME', 'N/A')}")
            st.write(f"**Last Name**: {selected_cert.get('LAST_NAME', 'N/A')}")
            st.write(f"**EID**: {selected_cert.get('EID', 'N/A')}")
            st.write(f"**Management Level**: {selected_cert.get('MANAGEMENT_LEVEL', 'N/A')}")
            st.write(f"**Capability**: {selected_cert.get('CAPABILITY', 'N/A')}")
            st.write(f"**Project Name**: {selected_cert.get('PROJECT_NAME', 'N/A')}")
            st.write(f"**Manager EID**: {selected_cert.get('MANAGER_EID', 'N/A')}")
            st.write(f"**Target Certification**: {selected_cert.get('TARGET_CERTIFICATION', 'N/A')}")
            st.write(f"**1st Target Certification Date**: {selected_cert.get('1ST_TAKE_RESULT', 'N/A')}")
            st.write(f"**Current Progress**: {selected_cert.get('CURRENT_PROGRESS', 'N/A')}")
            st.write(f"**With Voucher**: {selected_cert.get('WITH_VOUCHER', 'N/A')}")
            st.write(f"**1st Take Result**: {selected_cert.get('1ST_TAKE_RESULT', 'N/A')}")
            st.write(f"**Retake Exam Date**: {selected_cert.get('RETAKE_EXAM_DATE', 'N/A')}")
            st.write(f"**Retake Result**: {selected_cert.get('RETAKE_RESULT', 'N/A')}")
            st.write(f"**Expiration Date**: {selected_cert.get('EXPIRATION_DATE', 'N/A')}")
            st.write(f"**Fiscal Year**: {selected_cert.get('Fiscal_Year', 'N/A')}")
            st.write(f"**Month**: {selected_cert.get('Month', 'N/A')}")
            st.write(f"**Quarter**: {selected_cert.get('Quarter', 'N/A')}")
            st.write(f"**Employee Status**: {selected_cert.get('EMPLOYEE_STATUS', 'N/A')}")
            st.write(f"**Certification Level**: {selected_cert.get('Certification_Level', 'N/A')}")
            
            st.write("**Upload New Certificate**:")
            upload_cert()

            # Add a select box to choose the status
            # status = st.selectbox("Select Status", options=["Pending", "Approved", "Rejected"], index=0)

            if st.button("Submit for Approval"):
                # Retrieve uploaded file info from session state
                uploaded_info = st.session_state.get('uploaded_file_info')
                
                if uploaded_info:
                    file_name = uploaded_info['file_name']
                    certification = uploaded_info['certification']
                    employees_cert_id = selected_cert.get('employees_cert_id')

                    # Send data to API
                    file_path = os.path.join('uploads', file_name)
                    send_certification_data(employees_cert_id, file_path, certification, 'Pending', selected_cert.get('EID', 'N/A'))
                else:
                    st.error("No file uploaded. Please upload a certificate first.")

# Assuming you have the request functions defined as above
def display_approvers_page():
    st.title("Certification Approval Dashboard")

    # Fetch pending certifications
    if st.button("Fetch Pending Certifications"):
        with st.spinner("Fetching pending certifications..."):
            pending_certifications = fetch_pending_certifications()
            if pending_certifications:
                st.session_state['pending_certifications'] = pending_certifications
                st.success("Pending certifications fetched successfully.")
            else:
                st.error("Failed to fetch pending certifications.")

    if 'pending_certifications' in st.session_state:
        pending_certifications = st.session_state['pending_certifications']

        # Display pending certifications
        if pending_certifications:
            st.subheader("Pending Certifications")

            for cert in pending_certifications:
                with st.expander(f"Certification ID: {cert['employees_cert_id']}", expanded=False):
                    st.write(f"**Certification**: {cert['certification']}")
                    st.write(f"**Status**: {cert['status']}")
                    st.write(f"**EID**: {cert['EID']}")
                    # st.write(f"**File Path**: {cert['file_path']}")
                    # nicolen.e.aricayos-AWS Certified Cloud Practitioner-8_15_2024.png

                    # Display the image
                    image_path = cert['file_path']
                    if image_path:  # Ensure the file exists
                        st.image(f"uploads/{cert['EID']}-{cert['certification']}.png", caption="Uploaded Certificate", use_column_width=True)
                    else:
                        st.write("Image not available.")

                    if st.button(f"Approve Certification ID: {cert['employees_cert_id']}", key=cert['employees_cert_id']):
                        with st.spinner("Approving certification..."):
                            result = approve_certification(cert['employees_cert_id'])
                            if result:
                                st.success("Certification approved successfully.")
                                # Refresh pending certifications
                                pending_certifications = fetch_pending_certifications()
                                if pending_certifications:
                                    st.session_state['pending_certifications'] = pending_certifications
                                # time.sleep(2)
                                # st.rerun()
                            else:
                                st.error("Failed to approve certification.")
        else:
            st.write("No pending certifications to display.")
    else:
        st.write("Click 'Fetch Pending Certifications' to load pending certifications.")

    if st.button("Back to Certifications"):
        st.session_state['page'] = 'certifications'
        st.rerun()  # Force a page rerun to navigate back to the certifications page
                    
def certification_page():
    print('session:', st.session_state)
    if 'page' not in st.session_state:
        st.session_state['page'] = 'certifications'
    
    # Ensure that the session state is set correctly
    if 'edited_rows' not in st.session_state:
        st.session_state['edited_rows'] = {}

    
    if st.session_state['page'] == 'certificates':
        certificates_page()
    elif st.session_state['page'] == 'check_certificates':
        display_approvers_page()
    elif st.session_state.persona == ADMIN or st.session_state.persona == PROJECT_MANAGER:
        st.title("📜 Certifications")

        st.markdown("""
            You can view and filter detailed certification data for employees. 
            Use the sidebar filters to refine the results based on various criteria such as employee ID, certification name, 
            employee status, management level, and more. You can also search for specific certifications and sort the results 
            by certification level to get a clearer picture of the data. If you have certificates to upload, please use the 
            upload feature provided. This page helps in managing and tracking the progress of employee certifications efficiently.
        """)

        df = fetch_certifications()

        st.sidebar.header("🎛️ **Filters**")

        # Function to filter and sort unique values, excluding None values
        def filter_values(column_name):
            unique_values = df[column_name].dropna().unique()  # Drop None values
            return sorted(unique_values)

        # Sidebar Filters
        e_id_filter = st.sidebar.text_input("🔍 **Search by EID, Employee ID, First Name, Last Name**", help="Search for employees by their EID, Employee ID, First Name, or Last Name.")
        certification_filter = st.sidebar.selectbox("📜 **Certification**", ["All Certifications"] + filter_values("TARGET_CERTIFICATION"), help="Filter by specific certification.")
        employee_status_filter = st.sidebar.selectbox("✨ **Employee Status**", ["All Employee Statuses"] + filter_values("EMPLOYEE_STATUS"), help="Filter by the employee's current status.")
        current_progress_filter = st.sidebar.selectbox("📈 **Current Progress**", ["All Progress"] + ["Passed", "Failed", "In progress - 1st take", "In progress - 2nd take"], help="Filter by the current progress of the certification.")
        management_level_filter = st.sidebar.selectbox("🏷️ **Management Level**", ["All Management Levels"] + filter_values("MANAGEMENT_LEVEL"), help="Filter by the management level of the employee.")
        capability_filter = st.sidebar.selectbox("🔧 **Capability**", ["All Capabilities"] + filter_values("CAPABILITY"), help="Filter by the employee's capability.")
        fiscal_year_filter = st.sidebar.selectbox("📅 **Fiscal Year**", ["All Fiscal Years"] + filter_values("Fiscal_Year"), help="Filter by the fiscal year.")
        quarter_filter = st.sidebar.selectbox("🗓️ **Quarter**", ["All Quarters"] + filter_values("Quarter"), help="Filter by the quarter.")
        month_filter = st.sidebar.selectbox("📆 **Month**", ["All Months"] + filter_values("Month"), help="Filter by the month.")
        project_filter = st.sidebar.selectbox("📁 **Project Name**", ["All Project Names"] + filter_values("PROJECT_NAME"), help="Filter by the project associated with the certification.")
        manager_eid_filter = st.sidebar.selectbox("👤 **Manager EID**", ["All Manager EIDs"] + filter_values("MANAGER_EID"), help="Filter by the manager's EID.")

        if "Certification_Level" in df.columns:
            level_filter = st.sidebar.selectbox("📜 **Certification Level**", ["All Certification Levels"] + filter_values("Certification_Level"), help="Filter by the level of certification.")
        else:
            level_filter = "All Certification Levels"
            st.sidebar.write("ℹ️ **Note:** Certification Level filter is not available in the dataset.")

        sort_by = st.sidebar.radio("🔃 **Sort by Certification Level**", ["No Sorting", "Ascending", "Descending"], help="Sort the results based on certification level.")

        group_by_filter = st.sidebar.selectbox("🗂️ **Group By**", 
            ["No Grouping"] + 
            ["EID", "EMPLOYEE_ID", "FIRST_NAME", "LAST_NAME", "TARGET_CERTIFICATION", 
            "EMPLOYEE_STATUS", "CAPABILITY", "MANAGEMENT_LEVEL", 
            "Fiscal_Year", "Quarter", "Month", "PROJECT_NAME", "MANAGER_EID", "Certification_Level", "CURRENT_PROGRESS"], help="Group the data by the selected column.")

        df_filtered = df.copy()

        if e_id_filter:
            combined_columns = df_filtered["EID"].astype(str) + " " + \
                            df_filtered["EMPLOYEE_ID"].astype(str) + " " + \
                            df_filtered["FIRST_NAME"].astype(str) + " " + \
                            df_filtered["LAST_NAME"].astype(str)
            df_filtered = df_filtered[combined_columns.str.contains(e_id_filter, case=False, na=False)]

        if certification_filter != "All Certifications":
            df_filtered = df_filtered[df_filtered["TARGET_CERTIFICATION"] == certification_filter]
            df_filtered = move_column_to_front(df_filtered, "TARGET_CERTIFICATION")
        if employee_status_filter != "All Employee Statuses":
            df_filtered = df_filtered[df_filtered["EMPLOYEE_STATUS"] == employee_status_filter]
            df_filtered = move_column_to_front(df_filtered, "EMPLOYEE_STATUS")
        if current_progress_filter != "All Progress":
            df_filtered = df_filtered[df_filtered["CURRENT_PROGRESS"] == current_progress_filter]
            df_filtered = move_column_to_front(df_filtered, "CURRENT_PROGRESS")
        if management_level_filter != "All Management Levels":
            df_filtered = df_filtered[df_filtered["MANAGEMENT_LEVEL"] == management_level_filter]
            df_filtered = move_column_to_front(df_filtered, "MANAGEMENT_LEVEL")
        if capability_filter != "All Capabilities":
            df_filtered = df_filtered[df_filtered["CAPABILITY"] == capability_filter]
            df_filtered = move_column_to_front(df_filtered, "CAPABILITY")
        if fiscal_year_filter != "All Fiscal Years":
            df_filtered = df_filtered[df_filtered["Fiscal_Year"] == fiscal_year_filter]
            df_filtered = move_column_to_front(df_filtered, "Fiscal_Year")
        if quarter_filter != "All Quarters":
            df_filtered = df_filtered[df_filtered["Quarter"] == quarter_filter]
            df_filtered = move_column_to_front(df_filtered, "Quarter")
        if month_filter != "All Months":
            df_filtered = df_filtered[df_filtered["Month"] == month_filter]
            df_filtered = move_column_to_front(df_filtered, "Month")
        if project_filter != "All Project Names":
            df_filtered = df_filtered[df_filtered["PROJECT_NAME"] == project_filter]
            df_filtered = move_column_to_front(df_filtered, "PROJECT_NAME")
        if manager_eid_filter != "All Manager EIDs":
            df_filtered = df_filtered[df_filtered["MANAGER_EID"] == manager_eid_filter]
            df_filtered = move_column_to_front(df_filtered, "MANAGER_EID")

        if level_filter != "All Certification Levels":
            df_filtered = df_filtered[df_filtered["Certification_Level"] == level_filter]
            df_filtered = move_column_to_front(df_filtered, "Certification_Level")

        if sort_by == "Ascending":
            df_filtered["Certification_Level"] = sort_by_ranking(df_filtered["Certification_Level"])
            df_filtered = df_filtered.sort_values(by="Certification_Level", ascending=True)
        elif sort_by == "Descending":
            df_filtered["Certification_Level"] = sort_by_ranking(df_filtered["Certification_Level"])
            df_filtered = df_filtered.sort_values(by="Certification_Level", ascending=False)

        if group_by_filter != "No Grouping":
            df_filtered = df_filtered.groupby(group_by_filter).apply(lambda x: x).reset_index(drop=True)
        
        # Displaying DataFrame with selection capabilities
        event = st.dataframe(
            df_filtered,
            key="data",
            on_select="rerun",
            selection_mode="multi-row"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
    
        with col1:
            if st.session_state.get('persona') == ADMIN and st.button("Add New Certification"):
                add_certification(df)

        with col2:
            if st.session_state.get('persona') == ADMIN and st.button("Update Selected Certification"):
                if len(event.selection.rows) == 1:

                    update_selected_certification(df_filtered.iloc[event.selection.rows[0]], df)
                elif len(event.selection.rows) < 1:
                    show_custom_toast("Please select a certification to update.")
                else:
                    show_custom_toast("Please select only one certification to update.")

        with col3:
            if st.session_state.get('persona') == ADMIN and st.button("Delete Selected Certification"):
                if len(event.selection.rows) == 1:
                    delete_selected_certification(df_filtered.iloc[event.selection.rows[0]]['employees_cert_id'])
                elif len(event.selection.rows) < 1:
                    show_custom_toast("Please select a certification to delete.")
                else:
                    show_custom_toast("Please select only one certification to delete.")

        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("View All Certifications"):
                st.session_state['page'] = 'certificates'
                st.rerun()  # Force a page rerun to navigate to the certificates page
        with col2:
            if st.button("For Checking Certificates"):
                st.session_state['page'] = 'check_certificates'
                st.rerun()

        # Add download button to export filtered data
        generate_csv_download_link(df_filtered, "filtered_certification_data")

        st.write('---')
        
        # Add visualizations
        plot_certifications_by_level(df_filtered)
        plot_progress_distribution(df_filtered)
        plot_certifications_by_project(df_filtered)
        plot_certifications_by_manager(df_filtered)
        plot_certifications_by_year(df_filtered)
        plot_certifications_by_quarter(df_filtered)

    else:
        st.title("📜 My Certifications")

        # Fetch certifications data
        df = fetch_certifications()

        # Filter the DataFrame based on the EID from the session state
        e_id = st.session_state.get('EID', '')
        if e_id:
            df_filtered = df[df['EID'] == e_id]
        else:
            df_filtered = df

        # Displaying DataFrame with selection capabilities
        event = st.dataframe(
            df_filtered,
            key="data",
            on_select="rerun",
            selection_mode="multi-row"
        )

        if len(event.selection.rows) == 1:
            selected_cert = df_filtered.iloc[event.selection.rows[0]].to_dict()
            st.session_state['selected_cert'] = selected_cert

        # Button to view detailed certificates
        if st.button("View Detailed Certificates"):
            st.session_state['page'] = 'certificates'
            st.rerun()

        # Display approval dialog if there's a selected certificate
        selected_cert = st.session_state.get('selected_cert', None)
        if selected_cert and len(event.selection.rows) == 1:
            display_approval_dialog(selected_cert)
        else:
            st.write("Please select a certification to view details and approve.")


certification_page()
