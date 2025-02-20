from flask import Flask
import os
from dotenv import load_dotenv

from api.auth_api import auth_bp
from api.users_api import users_bp
from api.session_api import session_bp
from api.employees_api import employees_bp
from api.llm_query_api import llm_query_bp
from api.ingest_data_api import ingest_data_bp
from api.events_api import events_bp


# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Register API blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(session_bp)
app.register_blueprint(users_bp)
app.register_blueprint(employees_bp)
app.register_blueprint(llm_query_bp)
app.register_blueprint(ingest_data_bp)
app.register_blueprint(events_bp)

if __name__ == '__main__':
    app.run(debug=True)