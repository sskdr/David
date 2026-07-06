import os
from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import ContextTypes, TypeHandler, ApplicationHandlerStop
import json

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPER_ADMIN_ID = os.getenv("SUPER_ADMIN_ID")
SUPER_ADMIN_API_ID = os.getenv("SUPER_ADMIN_API_ID")
SUPER_ADMIN_API_HASH = os.getenv("SUPER_ADMIN_API_HASH")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

downloading_users = []

def load_bans() -> set:
    try:
        with open("banned_users.json", "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

BANNED_USERS = load_bans()

if not BOT_TOKEN:
    raise ValueError("❌ ERROR: BOT_TOKEN is missing from the environment or .env file!")

async def global_ban_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Interceptors check every single update before routing to specific handlers."""
    # Ensure there is a user attached to the incoming update (ignore anonymous channel posts etc.)
    if update.effective_user:
        user_id = update.effective_user.id
        
        if user_id in BANNED_USERS:
            # OPTIONAL: Let them know they are blocked if they try clicking an inline button
            if update.callback_query:
                await update.callback_query.answer("🚫 You have been restricted from using this bot.", show_alert=True)
            
            # CRITICAL: This stops python-telegram-bot from sending this specific message 
            # down the pipeline to your download/start handlers. It dies right here.
            raise ApplicationHandlerStop()