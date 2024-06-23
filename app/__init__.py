from flask import Flask
from flask_socketio import SocketIO
from .routes import auth, main, chat, profile
from pymongo import MongoClient
from .config import Config
import chromadb
import time
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_oauthlib.client import OAuth

def wait_for_chroma_service(client, timeout=60):
    """Wait for the Chroma service to be ready before proceeding."""
    start_time = time.time()
    while True:
        try:
            response = client.heartbeat()
            if response:
                print("Chroma service is up and running.")
                break
        except Exception as e:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                print(f"Timeout waiting for Chroma service to be ready: {e}")
                exit(1)
            print("Waiting for Chroma service to be ready...")
            time.sleep(5)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # allow cross origin requests
    CORS(app)
    jwt = JWTManager(app)
    oauth = OAuth(app)

    google = oauth.remote_app(
        'google',
        consumer_key=Config.GOOGLE_CLIENT_ID,
        consumer_secret=Config.GOOGLE_CLIENT_SECRET,
        request_token_params={
            'scope': 'email profile'
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )
    app.google = google

    chroma_host = Config.CHROMA_HOST
    vectorstore = chromadb.HttpClient(host=chroma_host , port=8000, settings=chromadb.config.Settings(allow_reset=True, anonymized_telemetry=False))

    wait_for_chroma_service(vectorstore)

    app.vectorstore = vectorstore
    if test_config:
        app.config.update(test_config)

    client = MongoClient(Config.MONGO_URI)
    app.db = client.aacharya

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(profile.bp)

    return app
