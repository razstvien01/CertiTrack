from db import get_db_connection

def create_session_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            eid TEXT,
            role TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expiration_date TIMESTAMP NOT NULL,  -- Added expiration_date column
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Tracks last access time
            is_active BOOLEAN DEFAULT TRUE  -- Indicates if the session is still active
        )
    ''')
    conn.commit()
    conn.close()

def delete_events_table():
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Drop the sessions table
        c.execute('DROP TABLE IF EXISTS events')
        conn.commit()
        print("Events table deleted successfully.")
    except Exception as e:
        print("Error deleting sessions table:", e)
    finally:
        conn.close()


def create_users_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            eid TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def delete_session_table():
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Drop the sessions table
        c.execute('DROP TABLE IF EXISTS sessions')
        conn.commit()
        print("Sessions table deleted successfully.")
    except Exception as e:
        print("Error deleting sessions table:", e)
    finally:
        conn.close()