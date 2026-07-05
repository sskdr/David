import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPER_ADMIN_ID = os.getenv("SUPER_ADMIN_ID")
SUPER_ADMIN_API_ID = os.getenv("SUPER_ADMIN_API_ID")
SUPER_ADMIN_API_HASH = os.getenv("SUPER_ADMIN_API_HASH")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not BOT_TOKEN:
    raise ValueError("❌ ERROR: BOT_TOKEN is missing from the environment or .env file!")