from flask import Flask
from flask_socketio import SocketIO
from .routes import auth, main, chat, profile
from pymongo import MongoClient
from .config import Config
import chromadb
import time
from flask_cors import CORS


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # allow cross origin requests
    CORS(app)

    chroma_host = Config.CHROMA_HOST
    vectorstore = chromadb.HttpClient(host=chroma_host , port=8000, settings=chromadb.config.Settings(allow_reset=True, anonymized_telemetry=False))

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

    wait_for_chroma_service(vectorstore)


    client = MongoClient(Config.MONGO_URI)

    app.vectorstore = vectorstore

    if test_config:
        app.config.update(test_config)

    app.db = client.aacharya

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(profile.bp)

    return app
