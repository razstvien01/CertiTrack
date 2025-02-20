import pandas as pd
import sqlite3

def ingest_csv_to_db(csv_file_path, db_path, ddl_path):
    #Load CSV Data
    df = pd.read_csv(csv_file_path)

    #Clean and Preparing Column Names
    df.columns = df.columns.str.replace('[^0-9a-zA-Z]+', '_', regex = True)
    df.columns = ['col_' + col if col[0].isdigit() else col for col in df.columns]

    # Connect to SQLite Database
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Execute DDL File to Create the Table
    with open(ddl_path,'r') as file:
        create_table_statement = file.read()

    cur.execute(create_table_statement)
    con.commit()

    # Ingest data into the table
    df.to_sql('database_table', con, if_exists='append', index=False)

    # Close the connection
    con.close()

if __name__ == "__main__":
    csv_file_path = 'backend/data/input/Certification_Dummy_Data.csv'
    db_path = 'backend/data/output/project_database.db'
    ddl_path = 'backend/SQL/DDL/create_database_table.sql'

    ingest_csv_to_db(csv_file_path, db_path, ddl_path)