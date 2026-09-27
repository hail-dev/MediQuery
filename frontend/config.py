import os
from dotenv import load_dotenv

load_dotenv()

# FastAPI backend
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("API_KEY", "")

HEADERS = {
    "X-API-Key": API_KEY
}