import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import plotly.express as px

from services.employee_service import fetch_employees

def filter_dataframe(df, filters):
    """Filter the dataframe based on multiple filters."""
    df_filtered = df.copy()

    # Apply search term filter
    search_term = filters.get('search_term')
    if search_term:
        df_filtered = df_filtered[
            (df_filtered["FIRST_NAME"].str.contains(search_term, case=False)) | 
            (df_filtered["LAST_NAME"].str.contains(search_term, case=False)) | 
            (df_filtered["EID"].str.contains(search_term, case=False)) |
            (df_filtered["EMPLOYEE_ID"].astype(str).str.contains(search_term, case=False))
        ]

    # Apply project filter
    project_filter = filters.get('project_filter')
    if project_filter and project_filter != "All Projects":
        df_filtered = df_filtered[df_filtered["PROJECT_NAME"] == project_filter]

    # Apply management level filter
    management_level_filter = filters.get('management_level_filter')
    if management_level_filter and management_level_filter != "All Levels":
        df_filtered = df_filtered[df_filtered["MANAGEMENT_LEVEL"] == management_level_filter]
    
    # Apply capability filter
    capability_filter = filters.get('capability_filter')
    if capability_filter and capability_filter != "All Capabilities":
        df_filtered = df_filtered[df_filtered["CAPABILITY"] == capability_filter]

    # Apply manager EID filter
    manager_eid_filter = filters.get('manager_eid_filter')
    if manager_eid_filter and manager_eid_filter != "All Managers":
        df_filtered = df_filtered[df_filtered["MANAGER_EID"] == manager_eid_filter]

    # Apply employee status filter
    employee_status_filter = filters.get('employee_status_filter')
    if employee_status_filter and employee_status_filter != "All Statuses":
        df_filtered = df_filtered[df_filtered["EMPLOYEE_STATUS"] == employee_status_filter]
    
    return df_filtered

def display_employee_details(df_filtered, filters):
    """Display the filtered employee details with prioritized columns."""
    if df_filtered.empty:
        st.warning("⚠️ No employee found. Please adjust your filters and try again.")
    else:
        st.markdown("### 👤 Employee Details")

        # List of all columns
        all_columns = [
            'EMPLOYEE_ID', 'FIRST_NAME', 'LAST_NAME', 'EID',
            'PROJECT_NAME', 'MANAGER_EID', 'MANAGEMENT_LEVEL', 'CAPABILITY',
            'EMPLOYEE_STATUS'
        ]

        # Priority columns based on selected filters
        priority_columns = []
        if filters.get('search_term'):
            priority_columns.extend(['EMPLOYEE_ID', 'FIRST_NAME', 'LAST_NAME', 'EID'])
        if filters.get('project_filter') and filters.get('project_filter') != "All Projects":
            priority_columns.append('PROJECT_NAME')
        if filters.get('management_level_filter') and filters.get('management_level_filter') != "All Levels":
            priority_columns.append('MANAGEMENT_LEVEL')
        if filters.get('capability_filter') and filters.get('capability_filter') != "All Capabilities":
            priority_columns.append('CAPABILITY')
        if filters.get('manager_eid_filter') and filters.get('manager_eid_filter') != "All Managers":
            priority_columns.append('MANAGER_EID')
        if filters.get('employee_status_filter') and filters.get('employee_status_filter') != "All Statuses":
            priority_columns.append('EMPLOYEE_STATUS')

        # Remove duplicates and ensure all priority columns are in the all_columns list
        priority_columns = list(dict.fromkeys(priority_columns))
        priority_columns = [col for col in all_columns if col in priority_columns]
        
        # Reorder columns, putting priority columns first
        columns_to_display = priority_columns + [col for col in all_columns if col not in priority_columns]
        df_filtered = df_filtered[columns_to_display]

        st.dataframe(df_filtered, use_container_width=True)


def display_summary_report(df_filtered):
    """Display a summary report of the filtered employee data with visualizations."""
    if not df_filtered.empty:
        st.markdown("### 📊 Searched Summary Report")
        
        # Summary statistics
        total_employees = df_filtered.shape[0]
        unique_projects = df_filtered["PROJECT_NAME"].nunique()
        unique_capabilities = df_filtered["CAPABILITY"].nunique()
        
        # Display the summary as text in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Total Employees:** {total_employees}")
        
        with col2:
            st.write(f"**Unique Projects:** {unique_projects}")
        
        with col3:
            st.write(f"**Unique Capabilities:** {unique_capabilities}")
        
        # Prepare data for the bar chart
        summary_data = pd.DataFrame({
            'Metric': ['Total Employees', 'Unique Projects', 'Unique Capabilities'],
            'Count': [total_employees, unique_projects, unique_capabilities]
        })
        
        # Create a bar chart for the summary data
        summary_chart = px.bar(summary_data, x='Metric', y='Count', title='Summary of Employees, Projects, and Capabilities')
        st.plotly_chart(summary_chart, use_container_width=True)
    else:
        st.warning("⚠️ No data available to display summary report.")

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

def display_management_level_distribution(df_filtered):
    """Display the distribution of employees across management levels."""
    if not df_filtered.empty:
        st.markdown("### 📈 Management Level Distribution")
        fig = px.pie(df_filtered, names='MANAGEMENT_LEVEL', title='Distribution of Employees by Management Level')
        st.plotly_chart(fig, use_container_width=True)

def display_capability_distribution(df_filtered):
    """Display the distribution of employees across capabilities."""
    if not df_filtered.empty:
        st.markdown("### 📊 Capability Distribution")
        fig = px.bar(df_filtered, x='CAPABILITY', title='Distribution of Employees by Capability')
        st.plotly_chart(fig, use_container_width=True)

def display_project_distribution(df_filtered):
    """Display the distribution of employees across projects."""
    if not df_filtered.empty:
        st.markdown("### 🗂 Project Distribution")
        fig = px.bar(df_filtered, x='PROJECT_NAME', title='Number of Employees by Project')
        st.plotly_chart(fig, use_container_width=True)

def employee_page():
    # Header and description
    st.header("🪪 Employee Management Section")
    st.write("""
    Search for employees by their first name, last name, employee ID (EID), or filter by various criteria such as project, management level, and capability.
    """)

    st.markdown("**Hint:** To view the entire calendar, please turn off the widen view option for a more complete display.")

    # Fetch and process data
    df = fetch_employees()

    # Sidebar filters
    st.sidebar.header("🔍 Filters")

    # Search bar for employee tracking
    st.sidebar.markdown("#### 🔍 Search for an Employee")
    search_term = st.sidebar.text_input("Enter the employee's First Name, Last Name, EID, or Employee ID")

    # Manager EID filter
    st.sidebar.markdown("#### 👨‍💼 Filter by Manager EID")
    manager_eids = sorted(pd.unique(df["MANAGER_EID"].dropna()))  # Remove None values before sorting
    selected_manager_eid = st.sidebar.selectbox(
        "Select Manager EID",
        ["All Managers"] + manager_eids
    )

    # Project filter
    st.sidebar.markdown("#### 📁 Filter by Project")
    project_names = sorted(pd.unique(df["PROJECT_NAME"].dropna()))  # Remove None values before sorting
    selected_project = st.sidebar.selectbox(
        "Select a Project", 
        ["All Projects"] + project_names
    )

    # Management level filter
    st.sidebar.markdown("#### 🏢 Filter by Management Level")
    management_levels = sorted(pd.unique(df["MANAGEMENT_LEVEL"].dropna()))  # Remove None values before sorting
    selected_management_level = st.sidebar.selectbox(
        "Select Management Level",
        ["All Levels"] + management_levels
    )

    # Capability filter
    st.sidebar.markdown("#### 🔧 Filter by Capability")
    capabilities = sorted(pd.unique(df["CAPABILITY"].dropna()))  # Remove None values before sorting
    selected_capability = st.sidebar.selectbox(
        "Select Capability",
        ["All Capabilities"] + capabilities
    )

    # Employee status filter
    st.sidebar.markdown("#### ✨ Filter by Employee Status")
    employee_status = sorted(pd.unique(df["EMPLOYEE_STATUS"].dropna()))  # Remove None values before sorting
    select_employee_status = st.sidebar.selectbox(
        "Select Employee Status",
        ["All Statuses"] + employee_status
    )

    # Collect filters in a dictionary
    filters = {
        'search_term': search_term,
        'project_filter': selected_project,
        'management_level_filter': selected_management_level,
        'capability_filter': selected_capability,
        'manager_eid_filter': selected_manager_eid,
        'employee_status_filter': select_employee_status
    }

    # Filter dataframe based on all filters
    df_filtered = filter_dataframe(df, filters)

    # Display employee table with dynamic column order
    display_employee_details(df_filtered, filters)

    # Display summary report
    display_summary_report(df_filtered)
    
    # Display visualizations
    display_management_level_distribution(df_filtered)
    display_capability_distribution(df_filtered)
    display_project_distribution(df_filtered)
    
    # Footer and additional information
    st.markdown("---")
    st.write("""
    Use the filters and search bar in the sidebar to refine your search for employees based on various criteria. 
    The results will display the employee's details along with relevant project and capability information.
    """)

    # Add download button to export filtered data
    generate_csv_download_link(df_filtered, "filtered_employee_data")

employee_page()