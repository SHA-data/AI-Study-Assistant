import requests
from flask import Flask, render_template, request, redirect, url_for
from config import config

app = Flask(__name__)

# Make backend URL available to all templates
@app.context_processor
def inject_config():
    return dict(BACKEND_URL=config.BACKEND_URL)

@app.route("/")
def index():
    return redirect(url_for("chat"))

@app.route("/chat")
def chat():
    return render_template("chat.html", active_screen="chat")

@app.route("/resource-center")
def upload():
    return render_template("upload.html", active_screen="resource-center")

if __name__ == "__main__":
    app.run(port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
