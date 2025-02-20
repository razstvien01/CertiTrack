import os
import json
import sqlite3
import pandas as pd
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# To fetch data from db. You need to connect to sqlite3 DB.
def fetch_data_from_db(db_path, query):
    con = sqlite3.connect(db_path)
    result_df = pd.read_sql_query(query,con)
    con.close()
    return result_df.to_dict(orient='records')

def generate_prompt(result_list):
    return f"""
    Refer to this dataset {result_list}.
    Find ONLY the HIGHEST number of certifications where a specific value (e.g., 'Passed').
    I only need the JSON list in this Format: {{"Name_of_Cert": "Name of the Certificate", "Number_Passed": "Total number that Passed"}}
    """

def get_openai_response(prompt):
    client = AzureOpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
    azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version = os.environ["OPENAI_API_VERSION"],
    )

    completion = client.chat.completions.create(
    model = os.environ["CHAT_COMPLETIONS_DEPLOYMENT_NAME"],
    messages = [
        {
            "role": "system",
            "content": "You are the most efficient Data Scientist and a JSON generator. You also doesnt give any other explanation."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature = 0
    )

    return json.loads(completion.to_json()).get("choices")[0].get('message').get('content')

def generate_dml_script(table_name, json_data):
    sql_statements = []
    for record in json_data:
        columns = ', '.join(record.keys())
        values = ', '.join(f"'{value}'" for value in record.values())
        sql_statement = f"INSERT OR IGNORE INTO {table_name} ({columns}) VALUES ({values});"
        sql_statements.append(sql_statement)
    return sql_statements

def write_dml_to_file(dml_statements, dml_directory, dml_file_name):
    os.makedirs(dml_directory, exist_ok=True)
    file_path = os.path.join(dml_directory, dml_file_name)

    with open(file_path, 'w') as file:
        for statement in dml_statements:
            file.write(statement + "\n")

def execute_dml_script_from_file(db_path, dml_file, ddl_file):
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    with open(ddl_file, 'r') as f:
        ddl_script = f.read()
        cur.execute(ddl_script)

    with open(dml_file, 'r') as file:
        dml_statements = file.read().split(';')
        for statement in dml_statements:
            if statement.strip():
                cur.execute(statement.strip() + ';')
    
    con.commit()
    con.close()


if __name__ == "__main__":
    # Path of the database and your query for its SQL table
    db_path = 'backend/data/output/project_database.db'
    query = "SELECT TARGET_CERTIFICATION, COUNT(*) as num_passed FROM database_table WHERE CURRENT_PROGRESS = 'Passed' GROUP BY TARGET_CERTIFICATION ORDER BY num_passed DESC LIMIT 10"

    # Directory to write DML file
    dml_directory = 'backend/SQL/DML'

    # Fetch data from the database
    result_list = fetch_data_from_db(db_path, query)

    # Generate the prompt
    prompt = generate_prompt(result_list)

    # Get the response from OpenAI
    response = get_openai_response(prompt)
    json_data = json.loads(response) #Response should have double quotes in them. So edit in the structure format in the prompt

    # Generate DML statement for the Selected Table
    # table_name = os.path.splitext(os.path.basename(empty_table_ddl_file))[0]
    table_name = "Cert_HiNum_Employees"
    dml_statements = generate_dml_script(table_name, json_data)

    # Write DML statements to a file
    dml_file_name = 'generated_dml_for_Cert_HiNum_Employees.sql'
    write_dml_to_file(dml_statements, dml_directory, dml_file_name)

    # Execute DML statements from file
    dml_file_path = os.path.join(dml_directory, dml_file_name)
    ddl_file_path = 'backend/SQL/DDL/create_Cert_HiNum_Employees.sql'
    execute_dml_script_from_file(db_path, dml_file_path, ddl_file_path)

    print("DML Statements executed successfully")