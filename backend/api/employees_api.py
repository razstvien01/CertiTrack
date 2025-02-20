from flask import jsonify, Blueprint, request
import sqlite3
from constants.config import DATABASE_PATH
from constants.api_routes import EMPLOYEES_AR
from constants.methods import GET_M, POST_M, DELETE_M, PUT_M, PATCH_M
import pandas as pd

employees_bp = Blueprint('employees', __name__)

# Helper function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This allows us to get dictionary-like rows
    return conn

@employees_bp.route(f"{EMPLOYEES_AR}/certifications", methods=[GET_M])
def get_cert_employees():
    """Fetch all employees."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the SQL query
        cursor.execute("SELECT * FROM employees_certs")
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        employees = [dict(row) for row in rows]

        conn.close()

        return jsonify({"employees": employees}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@employees_bp.route(f"{EMPLOYEES_AR}/certificates", methods=[GET_M])
def get_certificates():
    """Fetch all certificates."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the SQL query
        cursor.execute("SELECT * FROM certifications")
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        certificates = [dict(zip(columns, row)) for row in rows]

        conn.close()

        return jsonify({"certificates": certificates}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employees_bp.route(EMPLOYEES_AR, methods=[GET_M])
def get_employees():
    """Fetch all employees with distinct EIDs and selected columns."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the SQL query with DISTINCT on EID and select only the desired columns
        cursor.execute("""
            SELECT DISTINCT
                EMPLOYEE_ID,
                FIRST_NAME,
                LAST_NAME,
                EID,
                MANAGEMENT_LEVEL,
                CAPABILITY,
                PROJECT_NAME,
                MANAGER_EID,
                EMPLOYEE_STATUS
            FROM employees_certs
            ORDER BY EID
        """)
        
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        employees = [
            {
                "EMPLOYEE_ID": row[0],
                "FIRST_NAME": row[1],
                "LAST_NAME": row[2],
                "EID": row[3],
                "MANAGEMENT_LEVEL": row[4],
                "CAPABILITY": row[5],
                "PROJECT_NAME": row[6],
                "MANAGER_EID": row[7],
                "EMPLOYEE_STATUS": row[8]
            }
            for row in rows
        ]

        conn.close()

        return jsonify({"employees": employees}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@employees_bp.route(f"{EMPLOYEES_AR}/<EID>", methods=[GET_M])
def get_employee_by_id(EID):
    """Fetch an employee by their ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the SQL query to get the employee by ID
        cursor.execute("SELECT * FROM employees_certs WHERE EID = ?", (EID,))
        row = cursor.fetchone()

        conn.close()

        if row:
            employee = dict(row)
            return jsonify({"employee": employee}), 200
        else:
            return jsonify({"message": "Employee not found"}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@employees_bp.route(EMPLOYEES_AR, methods=[POST_M])
def add_employee():
    """Add a new employee."""
    try:
        new_employee = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        print(new_employee)

        # Insert new employee record, ensure column name is correctly handled
        cursor.execute("""
            INSERT INTO employees_certs (FIRST_NAME, LAST_NAME, EID, TARGET_CERTIFICATION, 
                                         [1ST_TARGET_CERTIFICATION_DATE], RETAKE_EXAM_DATE, EXPIRATION_DATE, PROJECT_NAME)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_employee['FIRST_NAME'], new_employee['LAST_NAME'], new_employee['EID'], 
              new_employee['TARGET_CERTIFICATION'], new_employee['1ST_TARGET_CERTIFICATION_DATE'],
              new_employee['RETAKE_EXAM_DATE'], new_employee['EXPIRATION_DATE'], new_employee['PROJECT_NAME']))

        conn.commit()
        conn.close()

        return jsonify({"message": "Employee added successfully"}), 201

    except Exception as e:
        # Log the error with traceback for easier debugging
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@employees_bp.route(f"{EMPLOYEES_AR}/<employee_id>", methods=[PUT_M])
def update_employee(employee_id):
    """Update an existing employee."""
    try:
        updated_employee = request.json
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update employee record
        cursor.execute("""
            UPDATE employees_certs
            SET FIRST_NAME = ?, LAST_NAME = ?, EID = ?, TARGET_CERTIFICATION = ?, 
                col_1ST_TARGET_CERTIFICATION_DATE = ?, RETAKE_EXAM_DATE = ?, EXPIRATION_DATE = ?, PROJECT_NAME = ?
            WHERE id = ?
        """, (updated_employee['FIRST_NAME'], updated_employee['LAST_NAME'], updated_employee['EID'], 
              updated_employee['TARGET_CERTIFICATION'], updated_employee['col_1ST_TARGET_CERTIFICATION_DATE'],
              updated_employee['RETAKE_EXAM_DATE'], updated_employee['EXPIRATION_DATE'], updated_employee['PROJECT_NAME'], 
              employee_id))

        conn.commit()
        conn.close()

        return jsonify({"message": "Employee updated successfully"}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employees_bp.route(f"{EMPLOYEES_AR}/<employee_id>", methods=[PATCH_M])
def modify_employee(employee_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the JSON data from the request
        data = request.get_json()

        # Dynamically generate the SQL UPDATE query based on provided fields
        fields = ', '.join(f"{key} = ?" for key in data.keys())
        values = list(data.values()) + [employee_id]

        # Execute the SQL UPDATE query
        cursor.execute(f"UPDATE employees_certs SET {fields} WHERE employee_id = ?", values)
        conn.commit()

        # Check if any row was actually updated
        if cursor.rowcount == 0:
            return jsonify({'message': 'Employee not found'}), 404

        conn.close()

        return jsonify({'message': 'Employee updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 50

@employees_bp.route(f"{EMPLOYEES_AR}/<employee_id>", methods=[DELETE_M])
def delete_employee(employee_id):
    """Delete an employee."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete employee record
        cursor.execute("DELETE FROM employees_certs WHERE id = ?", (employee_id,))

        conn.commit()
        conn.close()

        return jsonify({"message": "Employee deleted successfully"}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employees_bp.route(f'{EMPLOYEES_AR}/get_certifications', methods=[GET_M])
def get_certifications():
    try:
        con = get_db_connection()
        if isinstance(con, tuple):  # This checks if get_db_connection returned an error tuple
            return con

        # Modified SQL query
        query = """
        SELECT 
            ec.*,
            ce.Certification_Level
        FROM 
            employees_certs AS ec
        INNER JOIN 
            certifications AS ce
        ON 
            ec.TARGET_CERTIFICATION = ce.Certification_Name
        """
        df = pd.read_sql_query(query, con)
        con.close()
        
        if df.empty:
            return jsonify({'message': 'No data found in the database.'}), 404
        
        return df.to_json(orient='records')

    except sqlite3.Error as e:
        return jsonify({'error': f'Database query failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500


@employees_bp.route(f'{EMPLOYEES_AR}/update_progress', methods=[POST_M])
def update_progress():
    try:
        data = request.json
        eid = data.get('eid')
        certification = data.get('certification')

        if not eid or not certification:
            return jsonify({'error': 'Missing eid or certification'}), 400

        con = get_db_connection()
        if isinstance(con, tuple):  # This checks if connect_db returned an error tuple
            return con

        cursor = con.cursor()
        update_query = """
        UPDATE employees_certs
        SET CURRENT_PROGRESS = 'Passed'
        WHERE EID = ? AND TARGET_CERTIFICATION = ?
        """
        
        cursor.execute(update_query, (eid, certification))
        con.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'No records updated. Please check EID and Certification.'}), 404
        
        con.close()
        return jsonify({'message': f'Database updated for EID: {eid} with Certification: {certification}'})

    except sqlite3.Error as e:
        return jsonify({'error': f'Database update failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    
# Route to add a new certificate
@employees_bp.route(f'{EMPLOYEES_AR}/certification', methods=[POST_M])
def add_certification():
    try:
        data = request.json

        # Prepare data for insertion, handling potential missing fields
        first_name = data.get('FIRST_NAME')
        last_name = data.get('LAST_NAME')
        eid = data.get('EID')
        emp_id = data.get('EMPLOYEE_ID')
        manager_eid = data.get('MANAGER_EID')
        management_level = data.get('MANAGEMENT_LEVEL')
        capability = data.get('CAPABILITY')
        employee_status = data.get('EMPLOYEE_STATUS')
        with_voucher = data.get('WITH_VOUCHER')
        current_progress = data.get('CURRENT_PROGRESS')
        target_certification = data.get('TARGET_CERTIFICATION')
        first_target_date = data.get('1ST_TARGET_CERTIFICATION_DATE')  # Ensure this column name is correctly escaped or renamed
        retake_exam_date = data.get('RETAKE_EXAM_DATE')
        expiration_date = data.get('EXPIRATION_DATE')
        fiscal_year = data.get('FISCAL_YEAR')
        quarter = data.get('QUARTER')
        month = data.get('MONTH')
        project_name = data.get('PROJECT_NAME')

        print(data)

        # Handle optional fields and defaults
        if expiration_date == 'None':
            expiration_date = None
        if retake_exam_date == 'None':
            retake_exam_date = None

        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO employees_certs (
                    FIRST_NAME, LAST_NAME, EID, EMPLOYEE_ID, MANAGEMENT_LEVEL, CAPABILITY, PROJECT_NAME,
                    MANAGER_EID, TARGET_CERTIFICATION, "1ST_TARGET_CERTIFICATION_DATE", WITH_VOUCHER,
                    EXPIRATION_DATE, FISCAL_YEAR, MONTH, QUARTER, EMPLOYEE_STATUS, CURRENT_PROGRESS
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                first_name, last_name, eid, emp_id, management_level, capability, project_name,
                manager_eid, target_certification, first_target_date, with_voucher,
                expiration_date, fiscal_year, month, quarter, employee_status, current_progress  # Placeholder for RETAKES_EXAM_DATE
            ))
            conn.commit()

        
        return jsonify({"message": "Certificate added successfully."}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add certificate: {str(e)}"}), 500

# Route to get a certificate by EID
@employees_bp.route(f'{EMPLOYEES_AR}/certificates/<string:eid>', methods=[GET_M])
def get_certificate_by_eid(eid):
    try:
        with employees_bp() as conn:
            cur = conn.execute('SELECT * FROM certificates WHERE EID = ?', (eid,))
            row = cur.fetchone()
            if row:
                return jsonify(dict(row)), 200
            else:
                return jsonify({"error": "Certificate not found."}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve certificate: {str(e)}"}), 500

# Route to update a certificate by EID
@employees_bp.route(f'{EMPLOYEES_AR}/certificates/<string:eid>', methods=[PUT_M])
def update_certificate(eid):
    try:
        data = request.json
        with get_db_connection() as conn:
            conn.execute('''
                UPDATE certificates SET 
                    FIRST_NAME = ?, LAST_NAME = ?, MANAGEMENT_LEVEL = ?, CAPABILITY = ?, 
                    PROJECT_NAME = ?, MANAGER_EID = ?, TARGET_CERTIFICATION = ?, 
                    FIRST_TARGET_CERTIFICATION = ?, CURRENT_PROGRESS = ?, 
                    WITH_VOUCHER = ?, FIRST_TAKE_RESULT = ?, RETAKE_EXAM_DATE = ?, 
                    RETAKE_RESULT = ?, EXPIRATION_DATE = ?, FISCAL_YEAR = ?, 
                    MONTH = ?, QUARTER = ?
                WHERE EID = ?
            ''', (
                data.get('FIRST_NAME'), data.get('LAST_NAME'), data.get('MANAGEMENT_LEVEL'),
                data.get('CAPABILITY'), data.get('PROJECT_NAME'), data.get('MANAGER_EID'),
                data.get('TARGET_CERTIFICATION'), data.get('FIRST_TARGET_CERTIFICATION'),
                data.get('CURRENT_PROGRESS'), data.get('WITH_VOUCHER'), data.get('FIRST_TAKE_RESULT'),
                data.get('RETAKE_EXAM_DATE'), data.get('RETAKE_RESULT'), data.get('EXPIRATION_DATE'),
                data.get('FISCAL_YEAR'), data.get('MONTH'), data.get('QUARTER'), eid
            ))
            conn.commit()
        return jsonify({"message": "Certificate updated successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update certificate: {str(e)}"}), 500

@employees_bp.route('/update_certification/<int:cert_id>', methods=['PATCH'])
def update_certification(cert_id):
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Validate and sanitize input data
    fields = [
        'FIRST_NAME', 'LAST_NAME', 'EID', 'EMPLOYEE_ID', 'MANAGER_EID', 'MANAGEMENT_LEVEL',
        'CAPABILITY', 'EMPLOYEE_STATUS', 'WITH_VOUCHER', 'CURRENT_PROGRESS',
        'TARGET_CERTIFICATION', '1ST_TARGET_CERTIFICATION_DATE', 'RETAKE_EXAM_DATE',
        'EXPIRATION_DATE', 'FISCAL_YEAR', 'QUARTER', 'MONTH', 'PROJECT_NAME'
    ]
    
    updates = {field: value for field, value in data.items() if field in fields}
    
    if not updates:
        return jsonify({'error': 'No valid fields to update'}), 400
    
    # Build the SET clause of the SQL query
    set_clause = ', '.join([f'"{field}" = ?' for field in updates.keys()])
    
    query = f"UPDATE employees_certs SET {set_clause} WHERE employees_cert_id = ?"
    values = list(updates.values()) + [cert_id]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return jsonify({'message': 'Certificate updated successfully'}), 200
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/delete_certification/<int:cert_id>', methods=['DELETE'])
def delete_certification(cert_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the certification exists
        cursor.execute("SELECT * FROM employees_certs WHERE employees_cert_id = ?", (cert_id,))
        if cursor.fetchone() is None:
            conn.close()
            return jsonify({'error': 'Certification not found'}), 404
        
        # Perform the deletion
        cursor.execute("DELETE FROM employees_certs WHERE employees_cert_id = ?", (cert_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Certification deleted successfully'}), 200
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    
# Handle invalid URL paths
@employees_bp.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "The requested URL was not found on the server."}), 404

# Handle internal server errors
@employees_bp.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error occurred."}), 500