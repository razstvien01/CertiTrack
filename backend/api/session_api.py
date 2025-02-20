from flask import Blueprint, jsonify, request
import sqlite3
from datetime import datetime, timedelta
from constants.config import DATABASE_PATH
from constants.api_routes import SESSION_AR
from constants.methods import POST_M, GET_M, DELETE_M
import uuid

# Define a Blueprint for session management
session_bp = Blueprint('session', __name__)

# Helper function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Function to create or update the session
@session_bp.route(f'{SESSION_AR}/create_or_update', methods=[POST_M])
def create_or_update_session():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if a session already exists
        cursor.execute('SELECT * FROM sessions LIMIT 1')
        existing_session = cursor.fetchone()

        expiration_date = datetime.utcnow() + timedelta(hours=1)  # Session valid for 1 hour
        last_accessed = datetime.utcnow()

        print("EID:", request.json.get('eid'))
        print("Expiration:", expiration_date)
        print("Last accessed:", last_accessed)
        print("Role:", request.json.get('role'))

        if existing_session:
            # Update the existing session
            cursor.execute(
                'UPDATE sessions SET expiration_date = ?, last_accessed = ?, role = ?, eid = ?, is_active = TRUE WHERE session_id = ?',
                (expiration_date, last_accessed, request.json.get('role'), request.json.get('eid'), existing_session['session_id'])
            )
        else:
            # Create a new session
            session_id = str(uuid.uuid4())  # Generate a unique session ID
            cursor.execute(
                'INSERT INTO sessions (session_id, expiration_date, role, eid) VALUES (?, ?, ?, ?)',
                (session_id, expiration_date, request.json.get('role'), request.json.get('eid'))
            )

        conn.commit()
        conn.close()

        return jsonify({"message": "Session created or updated successfully", "expiration_date": expiration_date.isoformat()}), 201

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

# Function to fetch the current session
@session_bp.route(f'{SESSION_AR}/fetch', methods=[GET_M])
def fetch_session():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM sessions LIMIT 1')
        session = cursor.fetchone()

        conn.close()

        if session:
            expiration_date = datetime.fromisoformat(session['expiration_date'])
            if expiration_date < datetime.utcnow():
                return jsonify({"error": "Session has expired"}), 410  # Gone
            return jsonify(dict(session)), 200
        else:
            return jsonify({"error": "No active session found"}), 404

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

# Function to delete the session
@session_bp.route(f'{SESSION_AR}/delete', methods=[DELETE_M])
def delete_session():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM sessions WHERE is_active = TRUE LIMIT 1')
        conn.commit()

        if cursor.rowcount > 0:
            conn.close()
            return jsonify({"message": "Session deleted successfully"}), 200
        else:
            return jsonify({"error": "No active session found"}), 404

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

# Function to delete expired sessions
@session_bp.route(f'{SESSION_AR}/cleanup', methods=[POST_M])
def cleanup_sessions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete sessions where the expiration date is in the past
        cursor.execute('DELETE FROM sessions WHERE expiration_date < ? AND is_active = TRUE', (datetime.utcnow(),))
        conn.commit()

        rows_deleted = cursor.rowcount
        conn.close()

        return jsonify({"message": f"{rows_deleted} expired sessions deleted"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500
