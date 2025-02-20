import os

DATABASE_PATH = './data/output/project_database.db'

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
CHAT_COMPLETIONS_DEPLOYMENT_NAME = os.getenv("CHAT_COMPLETIONS_DEPLOYMENT_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
AI_ROLE = "You are a helpful assistant. Your answer is to interpret the data fetched from our database. Reply any excuses or replies if the user asks unrelevant questions"
AI_ROLE_QUERY = "Your job is to convert the question to SQL query to access our database"