import os
from dotenv import load_dotenv

API_URL = 'http://127.0.0.1:5000'
APP_NAME = "AccentCert"
SECRET_KEY = os.getenv("SECRET_KEY")
