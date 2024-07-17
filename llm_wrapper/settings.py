from dotenv import load_dotenv
import os

# Get the root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Construct the path to the .env file
dotenv_path = os.path.join(BASE_DIR, '.env')

# Load the .env file
load_dotenv(dotenv_path)

LLM_API_KEY = os.getenv('LLM_API_KEY')
