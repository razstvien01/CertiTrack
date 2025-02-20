from flask import Flask, request, jsonify, Blueprint
import sqlite3
from sqlite3 import Error

from constants.config import DATABASE_PATH
from constants.methods import GET_M, POST_M, PUT_M, DELETE_M
from constants.api_routes import EVENTS_AR

events_bp = Blueprint('events', __name__)

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

@events_bp.route(EVENTS_AR, methods=[POST_M])
def create_event():
    data = request.json
    event_name = data.get('event_name')
    start_date = data.get('start_date')
    start_time = data.get('start_time')
    end_date = data.get('end_date')
    end_time = data.get('end_time')
    description = data.get("description")
    color = data.get("color")


    if not event_name or not start_date or not start_time or not end_date or not end_time:
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO events (event_name, start_date, start_time, end_date, end_time, description, color)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (event_name, start_date, start_time, end_date, end_time, description, color))
        conn.commit()
    except Error as e:
        conn.rollback()
        return jsonify({"status": "error", "message": f"Failed to create event: {e}"}), 500
    finally:
        conn.close()

    return jsonify({"status": "success", "message": "Event created successfully"}), 201

@events_bp.route(EVENTS_AR, methods=[GET_M])
def get_events():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM events')
        rows = cursor.fetchall()
        events = [dict(row) for row in rows]
    except Error as e:
        return jsonify({"status": "error", "message": f"Failed to retrieve events: {e}"}), 500
    finally:
        conn.close()

    return jsonify(events), 200

@events_bp.route(f'{EVENTS_AR}/<int:event_id>', methods=[PUT_M])
def update_event(event_id):
    data = request.json
    event_name = data.get('event_name')
    start_date = data.get('start_date')
    start_time = data.get('start_time')
    end_date = data.get('end_date')
    end_time = data.get('end_time')
    color = data.get('color')

    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE events
        SET event_name = COALESCE(?, event_name),
            start_date = COALESCE(?, start_date),
            start_time = COALESCE(?, start_time),
            end_date = COALESCE(?, end_date),
            end_time = COALESCE(?, end_time),
            color = COALESCE(?, color)
        WHERE event_id = ?
        ''', (event_name, start_date, start_time, end_date, end_time, color, event_id))
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Event not found."}), 404
        conn.commit()
    except Error as e:
        conn.rollback()
        return jsonify({"status": "error", "message": f"Failed to update event: {e}"}), 500
    finally:
        conn.close()

    return jsonify({"status": "success", "message": "Event updated successfully"}), 200

@events_bp.route(f'{EVENTS_AR}/<int:event_id>', methods=[DELETE_M])
def delete_event(event_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM events WHERE event_id = ?', (event_id,))
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Event not found."}), 404
        conn.commit()
    except Error as e:
        conn.rollback()
        return jsonify({"status": "error", "message": f"Failed to delete event: {e}"}), 500
    finally:
        conn.close()

    return jsonify({"status": "success", "message": "Event deleted successfully"}), 200
