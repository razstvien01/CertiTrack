from flask import Blueprint, jsonify, request
import sqlite3
import bcrypt
from functools import wraps

from constants.config import DATABASE_PATH
from constants.api_routes import AUTH_AR
from constants.methods import POST_M

# Define a Blueprint for authentication
auth_bp = Blueprint('auth', __name__)

# Helper function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Decorator to require a token for authentication
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Implement token checking logic here
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route(f'{AUTH_AR}/login', methods=[POST_M])
@token_required
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve user based on EID
        cursor.execute('SELECT eid, password, role FROM users WHERE eid = ?', (username,))
        user = cursor.fetchone()

        conn.close()

        if user:
            hashed_password = user['password']
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                return jsonify({
                    "message": "Login successful",
                    "eid": user['eid'],
                    "role": user['role']
                }), 200
            else:
                return jsonify({"error": "Invalid username or password"}), 401
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500