from flask import Flask
from flask_cors import CORS
from config import config
from database import init_db
from routes import register_routes

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Initialize Database
    init_db()
    
    # Register Routes
    register_routes(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
