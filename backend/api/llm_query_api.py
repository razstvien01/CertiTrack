from flask import jsonify, Blueprint, request
import sqlite3

from constants.config import DATABASE_PATH
from constants.methods import POST_M
from constants.api_routes import LLM_AR
from services.llm_service import generate_response, generate_sql_query

llm_query_bp = Blueprint('llm_query', __name__)

#! Working QUESTIONS
#* in there progress, how many employees are passed in Google related certificate
#* give me a summarize version of our data
#* what this application called? i only need the title. Nothing else
#* is preston.lozano exists in the manager_eid column?
#* Can you provide a breakdown of certification progress by employee ID?

# Helper function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This allows us to get dictionary-like rows
    return conn

def get_paginated_query(query, page=1, page_size=10):
    offset = (page - 1) * page_size
    return f"{query} LIMIT {page_size} OFFSET {offset}"

@llm_query_bp.route(f'{LLM_AR}/suggested-questions', methods=['GET'])
def suggested_questions():
    questions = [
        "How many employees are there in the system?",
        "What is the total number of projects?",
        "How many distinct certifications are there?",
        "List all employees with their IDs.",
        "How many certifications have failed?",
        "List all employees who need to retake their exams.",
        "Which certifications are expiring within the next 30 days?",
        "What is the current progress of each employee towards their certifications?",
        "List all certifications that were taken with a voucher.",
        "How many certifications are there for each fiscal year?"
    ]
    return jsonify({"suggested_questions": questions})


@llm_query_bp.route(LLM_AR, methods=[POST_M])
def llm_query():
    data = request.json
    question = data.get("question", "").lower()

    # Generate SQL query using the AI model
    sql_query = generate_sql_query(question)
    
    print("Query:", sql_query)
    
    # Check if the SQL query is valid
    if not sql_query or sql_query == "FAILED":
        # If SQL query generation fails, generate a response indicating data unavailability or relevance
        answer = generate_response(question, "Data not related to the database. Just answer if it is related to our application.")
        return jsonify({"answer": answer})

    # Execute the SQL query if it is valid
    try:
        conn = get_db_connection()  # Define or import this function to get a database connection
        cursor = conn.cursor()
        cursor.execute(sql_query)
        db_data = cursor.fetchall()
        conn.close()
    except Exception as e:
        answer = generate_response(question, "There's no result found in our database or I can't interpret the data that you gave.")
        return jsonify({"answer": answer})

    # Convert the fetched data into a list of dictionaries
    db_data_list = [dict(row) for row in db_data]

    # Generate a response using the retrieved data
    answer = generate_response(question, db_data_list)

    return jsonify({"answer": answer})