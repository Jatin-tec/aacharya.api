import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    # Secret key for signing cookies
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret-key')

    # Flask configurations
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'

    # OpenAI API key
    OPENAI_APIKEY = os.environ.get('OPENAI_APIKEY')
    openai.api_key = OPENAI_APIKEY

    YOUTUBE_API = os.environ.get('YOUTUBE_API')

    # Auth0 configurations
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # ChromaDB / Weaviate configuration
    CHROMA_HOST = os.environ.get('CHROMA_HOST', 'default_host')

    # Hugging Face API key
    HUGGINGFACE_APIKEYS = os.environ.get('HUGGINGFACE_APIKEYS')

    # MongoDB configurations
    MONGO_URI = os.environ.get("MONGO_URI")

    # Client URL
    CLIENT_URL = os.environ.get("CLIENT_URL")
