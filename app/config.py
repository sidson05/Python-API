import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
CACHE_TTL = int(os.getenv("CACHE_TTL", 60))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
COINGECKO_BASE_URL = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
