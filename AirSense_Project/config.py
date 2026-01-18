# config.py

# API KEYS
import os
from dotenv import load_dotenv

# Load the secret .env file
load_dotenv()

# Read the keys securely
WAQI_API_KEY = os.environ.get("WAQI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# App Settings
CHENNAI_LAT = 13.0827
CHENNAI_LON = 80.2707
USE_REAL_DATA = True


