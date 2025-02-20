from flask import jsonify, Blueprint, request

from constants.api_routes import INGEST_AR
from constants.methods import POST_M

from services.ingest_data_service import create_table_from_csv, add_rows_to_table
# from db.schema import delete_events_table

ingest_data_bp = Blueprint('ingest_data', __name__)

@ingest_data_bp.route(f'{INGEST_AR}/upload_csv', methods=[POST_M])
def upload_csv():
    # delete_events_table()
    
    # Get table name, operation, and CSV data from request
    table_name = request.form.get('table_name')
    operation = request.form.get('operation')
    file = request.files['file']
    
    if not table_name or not file or not operation:
        return jsonify({"error": "Table name, operation, and CSV file are required"}), 400
    
    # Read CSV data as a string
    csv_data = file.read().decode('utf-8')
    
    # Perform the requested operation
    if operation == "Create New Table":
        create_table_from_csv(csv_data, table_name)
    elif operation == "Add Rows to Existing Table":
        add_rows_to_table(csv_data, table_name)
    else:
        return jsonify({"error": "Invalid operation"}), 400
    
    return jsonify({"message": f"Operation '{operation}' on table '{table_name}' completed successfully"}), 200
