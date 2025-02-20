import sqlite3
import pandas as pd
from io import StringIO

from constants.config import DATABASE_PATH

def upload_csv(file, table_name, operation):
    csv_data = file.read().decode('utf-8')
    
    if operation == "Create New Table":
        create_table_from_csv(csv_data, table_name)
    elif operation == "Add Rows to Existing Table":
        add_rows_to_table(csv_data, table_name)
    else:
        raise ValueError("Invalid operation selected.")

def create_table_from_csv(csv_data, table_name):
    # Convert the byte data to a StringIO object
    csv_data = StringIO(csv_data)
    
    # Read CSV into DataFrame
    df = pd.read_csv(csv_data)
    
    # Connect to SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Drop the table if it exists
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    # Remove trailing 's' from table_name if it exists
    if table_name.endswith('s'):
        base_table_name = table_name[:-1] + "_id"
    else:
        base_table_name = table_name + "_id"
    
    # Escape column names for SQLite compatibility
    def escape_column_name(name):
        # Escape column names that start with a number or contain special characters
        if name[0].isdigit() or any(c in name for c in [' ', '-', '(', ')', '/', '\\']):
            return f'"{name}"'
        return name

    # Prepare columns and SQL statements
    columns = ', '.join([f"{escape_column_name(col)} TEXT" for col in df.columns])
    
    print("Columns for table:", columns)
    
    create_table_sql = f"""
    CREATE TABLE {table_name} (
        {base_table_name} INTEGER PRIMARY KEY AUTOINCREMENT,
        {columns},
        color TEXT
    )
    """ if table_name == 'events' else f"""
    CREATE TABLE {table_name} (
        {base_table_name} INTEGER PRIMARY KEY AUTOINCREMENT,
        {columns}
    )
    """
    
    print("Create table SQL:", create_table_sql)
    cursor.execute(create_table_sql)
    
    # Insert rows into the table
    for index, row in df.iterrows():
        placeholders = ', '.join(['?' for _ in row])
        if table_name == 'events':
            insert_sql = f"INSERT INTO {table_name} ({', '.join(map(escape_column_name, df.columns))}, color) VALUES ({placeholders}, ?)"
            print("Insert SQL:", insert_sql)
            cursor.execute(insert_sql, tuple(row) + ('#000000',))  # Default color value if not provided
        else:
            insert_sql = f"INSERT INTO {table_name} ({', '.join(map(escape_column_name, df.columns))}) VALUES ({placeholders})"
            print("Insert SQL:", insert_sql)
            cursor.execute(insert_sql, tuple(row))  # Default color value if not provided
    
    # Commit and close the connection
    conn.commit()
    conn.close()

def add_rows_to_table(csv_data, table_name):
    # Convert the byte data to a StringIO object
    csv_data = StringIO(csv_data)
    
    # Read CSV into DataFrame
    df = pd.read_csv(csv_data)
    
    # Connect to SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if cursor.fetchone() is None:
        raise ValueError(f"Table '{table_name}' does not exist.")
    
    # Insert rows into the existing table
    for index, row in df.iterrows():
        placeholders = ', '.join(['?' for _ in row])
        insert_sql = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({placeholders})"
        cursor.execute(insert_sql, tuple(row))
    
    # Commit and close the connection
    conn.commit()
    conn.close()
