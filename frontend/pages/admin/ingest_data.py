import streamlit as st
from services.ingest_data_service import upload_csv

def ingest_data():
    st.title("Ingest CSV to the Database")

    st.subheader("Upload CSV File")
    table_name = st.text_input("Table Name")
    operation = st.radio("Operation", options=["Create New Table", "Add Rows to Existing Table"])
    file = st.file_uploader("Choose a CSV file", type="csv")

    if st.button("Upload CSV"):
        if file and table_name:
            try:
                upload_csv(file, table_name, operation)
                st.success(f"Operation '{operation}' was successful on table '{table_name}'.")
            except ValueError as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please provide a table name and select a CSV file.")

ingest_data()
