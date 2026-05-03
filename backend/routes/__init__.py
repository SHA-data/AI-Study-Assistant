from flask import Flask
from routes.ingest import ingest_bp
from routes.chat import chat_bp
from routes.library import library_bp
from routes.claims import claims_bp

def register_routes(app: Flask):
    app.register_blueprint(ingest_bp, url_prefix="/ingest")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(library_bp, url_prefix="/library")
    app.register_blueprint(claims_bp, url_prefix="/claims")
