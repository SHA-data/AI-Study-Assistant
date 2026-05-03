import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # URL of the backend API
    BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5001")
    FLASK_PORT = int(os.getenv("FRONTEND_FLASK_PORT", 5000))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

config = Config()
