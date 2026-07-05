from telegram import Update
from telegram.ext import ContextTypes

async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /weather <city> command."""
    if not context.args:
        await update.message.reply_text("Please provide a city name. Example: /weather Colombo")
        return

    city = " ".join(context.args)
    await update.message.reply_text(f"☀️ Checking weather for {city}...")
    # Fetch data using an async client like httpx here