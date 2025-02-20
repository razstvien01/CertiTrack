from flask import Blueprint, jsonify, request, abort
import sqlite3
import bcrypt
from models.user_model import Role, User
from constants.api_routes import USERS_AR
from constants.methods import GET_M, POST_M, PUT_M, DELETE_M
from constants.config import DATABASE_PATH

# Define a Blueprint for the user API
users_bp = Blueprint('users', __name__)

# Helper function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Helper function to find a user by eid
def find_user(eid):
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM users WHERE eid = ?', (eid,)).fetchone()
    conn.close()
    if user_data:
        return User(
            eid=user_data['eid'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password=user_data['password'],
            role=Role[user_data['role']]
        )
    return None

# Function to hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# GET: Retrieve all users
@users_bp.route(USERS_AR, methods=[GET_M])
def get_users():
    conn = get_db_connection()
    users_data = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    users = [User(
        eid=user['eid'],
        first_name=user['first_name'],
        last_name=user['last_name'],
        password=user['password'],
        role=Role[user['role']]
    ).to_dict() for user in users_data]
    return jsonify(users)

# GET: Retrieve a specific user by eid
@users_bp.route(f'{USERS_AR}/<eid>', methods=[GET_M])
def get_user(eid):
    user = find_user(eid)
    if user:
        return jsonify(user.to_dict())
    else:
        abort(404, description="User not found")

# POST: Create a new user
@users_bp.route(USERS_AR, methods=[POST_M])
def create_user():
    data = request.get_json()
    eid = data.get("eid")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    password = data.get("password")
    role = data.get("role")

    if not all([eid, first_name, last_name, password, role]):
        abort(400, description="Missing required fields")

    if role not in Role.__members__:
        abort(400, description="Invalid role")

    if find_user(eid):
        abort(409, description="User with eid already exists")

    hashed_password = hash_password(password)
    new_user = User(eid=eid, first_name=first_name, last_name=last_name, password=hashed_password, role=Role[role])
    
    conn = get_db_connection()
    conn.execute('INSERT INTO users (eid, first_name, last_name, password, role) VALUES (?, ?, ?, ?, ?)',
                 (new_user.eid, new_user.first_name, new_user.last_name, new_user.password, new_user.role.name))
    conn.commit()
    conn.close()

    return jsonify(new_user.to_dict()), 201

# PUT: Update an existing user
@users_bp.route(f'{USERS_AR}/<eid>', methods=[PUT_M])
def update_user(eid):
    user = find_user(eid)
    if not user:
        abort(404, description="User not found")

    data = request.get_json()
    first_name = data.get("first_name", user.first_name)
    last_name = data.get("last_name", user.last_name)
    password = data.get("password", user.password)
    role = data.get("role", user.role.name)

    if role not in Role.__members__:
        abort(400, description="Invalid role")

    hashed_password = hash_password(password)
    updated_user = User(eid=eid, first_name=first_name, last_name=last_name, password=hashed_password, role=Role[role])

    conn = get_db_connection()
    conn.execute('UPDATE users SET first_name = ?, last_name = ?, password = ?, role = ? WHERE eid = ?',
                 (updated_user.first_name, updated_user.last_name, updated_user.password, updated_user.role.name, updated_user.eid))
    conn.commit()
    conn.close()

    return jsonify(updated_user.to_dict())

# DELETE: Remove a user
@users_bp.route(f'{USERS_AR}/<eid>', methods=[DELETE_M])
def delete_user(eid):
    user = find_user(eid)
    if user:
        conn = get_db_connection()
        conn.execute('DELETE FROM users WHERE eid = ?', (eid,))
        conn.commit()
        conn.close()
        return jsonify({"message": "User deleted successfully"})
    else:
        abort(404, description="User not found")

import os

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@users_bp.route('/submit-certification', methods=[POST_M])
def submit_certification():
    # conn = get_db_connection()  # Change 'certifications.db' to your database name
    # cursor = conn.cursor()
    # cursor.execute('''
    #     DROP TABLE check_certifications
    # ''')

    # conn.commit()
    # conn.close()
    conn = get_db_connection()  # Change 'certifications.db' to your database name
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS check_certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employees_cert_id INTEGER,
            certification TEXT,
            file_path TEXT,
            status TEXT DEFAULT 'Pending',
            EID TEXT
        )
    ''')

    conn.commit()
    conn.close()

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Extract data from request
    employees_cert_id = request.form.get('employees_cert_id')
    certification = request.form.get('certification')
    status = request.form.get('status', 'Pending')  # Default to 'Pending' if no status is provided
    eid = request.form.get('EID')  # Default to 'Pending' if no status is provided

    if file:
        # Save the file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Save data to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO check_certifications (employees_cert_id, certification, file_path, status, EID) VALUES (?, ?, ?, ?, ?)',
            (employees_cert_id, certification, file_path, status, eid)
        )
        conn.commit()
        conn.close()

        return jsonify({'message': 'Certification submitted successfully'}), 200

    return jsonify({'error': 'Failed to upload file'}), 500

@users_bp.route('/approve-certification', methods=['POST'])
def approve_certification():
    data = request.json
    print(data)
    employees_cert_id = data.get('employees_cert_id')
    
    if not employees_cert_id:
        return jsonify({'error': 'Employee Certification ID is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update status to 'Approved' in check_certifications
    cursor.execute('''
        UPDATE check_certifications
        SET status = 'Approved'
        WHERE employees_cert_id = ?
        AND status = 'Pending'
    ''', (employees_cert_id,))
    
    # Update CURRENT_PROGRESS to 'Passed' in employee_certs
    cursor.execute('''
        UPDATE employees_certs
        SET CURRENT_PROGRESS = 'Passed'
        WHERE employees_cert_id = ?
    ''', (employees_cert_id,))
    
    conn.commit()
    updated_rows_check_certifications = cursor.rowcount

    # Check how many rows were updated in the employee_certs table
    cursor.execute('''
        SELECT changes()
    ''')
    updated_rows_employee_certs = cursor.fetchone()[0]

    conn.close()
    
    if updated_rows_check_certifications == 0:
        return jsonify({'error': 'Certification not found or already approved'}), 404

    if updated_rows_employee_certs == 0:
        return jsonify({'error': 'Failed to update CURRENT_PROGRESS in employee_certs'}), 500

    return jsonify({'message': 'Certification approved and progress updated successfully'}), 200


@users_bp.route('/get-pending-certifications', methods=['GET'])
def get_pending_certifications():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all pending certifications
    cursor.execute('''
        SELECT * FROM check_certifications
        WHERE status = 'Pending'
    ''')
    
    certifications = cursor.fetchall()
    conn.close()

    # Convert rows to dictionaries
    column_names = [description[0] for description in cursor.description]
    certifications_list = [dict(zip(column_names, row)) for row in certifications]

    if not certifications_list:
        return jsonify({'message': 'No pending certifications found'}), 404

    return jsonify(certifications_list), 200
