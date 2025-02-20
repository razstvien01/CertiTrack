import openai
from openai import AzureOpenAI
from constants.config import CHAT_COMPLETIONS_DEPLOYMENT_NAME, OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OPENAI_API_VERSION

client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=OPENAI_API_VERSION,
)

AI_ROLE = "You are a helpful assistant. Your answer is to interpret the data fetched from our database. Reply any excuses or replies if the user asks unrelevant questions"
AI_ROLE_QUERY = "Your job is to convert the question to SQL query to access our database"

def generate_response(question, db_data):
    """
    This function sends a question and database data to the Azure OpenAI service and returns the response.
    """
    try:
        db_data_str = ""
        if isinstance(db_data, list):
            # Convert db_data into a human-readable string or other suitable format
            for row in db_data:
                db_data_str += f"{dict(row)}\n"  # Convert each row to a dictionary and then to a string
        else:
            db_data_str = db_data

        # Prepare the prompt for the LLM
        messages = [
            {"role": "system", "content": AI_ROLE},
            {"role": "user", "content": (
                f"Question: {question}\n\n"
                "Context and Relevant Data:\n"
                f"{db_data_str}\n\n"
                "About Our Application:\n"
                "Our app, called AccentTrack, a certificate tracker app, helps employees track their certification progress.\n\n"
                "If the question seems unrelated to our system, suggest a more relevant question instead.\n\n"
            )}
        ]
        
        # Call the Azure OpenAI service
        completion = client.chat.completions.create(
            model=CHAT_COMPLETIONS_DEPLOYMENT_NAME,
            messages=messages,
            # max_tokens=159,
            temperature=0.7
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        # Check if the error is due to context length exceeding
        if 'context_length_exceeded' in str(e):
            return ("Your message caused our system to load a lot of data because it queried all the information from the database. "
                    "Please try asking a simpler or more specific question to get better results.")
        else:
            # Return a generic error message
            return "Sorry, something went wrong. Please try again later."

def generate_sql_query(question):
    """
    This function generates an SQL query based on the user's question.
    """
    messages = [
        {"role": "system", "content": AI_ROLE_QUERY},
        {"role": "user", "content": (
            "Generate an SQL query based on the following question. Assume the database schema has columns "
            "like EMPLOYEE_ID, FIRST_NAME, LAST_NAME, TARGET_CERTIFICATION, EXPIRATION_DATE, RETAKE_EXAM_DATE, "
            "PROJECT_NAME, MANAGER_EID, TARGET_CERTIFICATION, col_1ST_TARGET_CERTIFIC, CURRENT_PROGRESS, WITH_VOUCHER, "
            "col_1ST_TAKE_RESULT, RETAKE_EXAM_DATE, RETAKE_RESULT, EXPIRATION_DATE, Fiscal_Year, Month, Quarter, and the table name is 'database_table'. Please use only these columns in your query and "
            "do not include any other columns. If the question is not SQL related or cannot be converted, just say 'FAILED'.\n\n"
            f"Question: {question}\n\n"
            "Available columns: ROWID, EMPLOYEE_ID, FIRST_NAME, LAST_NAME, EID, MANAGEMENT_LEVEL, CAPABILITY, "
            "PROJECT_NAME, MANAGER_EID, TARGET_CERTIFICATION, col_1ST_TARGET_CERTIFIC, CURRENT_PROGRESS, WITH_VOUCHER, "
            "col_1ST_TAKE_RESULT, RETAKE_EXAM_DATE, RETAKE_RESULT, EXPIRATION_DATE, Fiscal_Year, Month, Quarter\n\n"
        )}
    ]


    try:
        completion = client.chat.completions.create(
            model=CHAT_COMPLETIONS_DEPLOYMENT_NAME,
            messages=messages,
            temperature=0.5  # Adjust temperature if needed
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating SQL query: {str(e)}"