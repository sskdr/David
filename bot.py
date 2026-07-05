import logging
from telegram import Update
from telegram.ext import app, CommandHandler, MessageHandler, filters

import config
from modules.download import handle_download
from modules.weather import get_weather
from modules.profile import get_profile

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the user."""
    await update.message.reply_text(
        "Hello! I am David, your multi-utility assistant.\n"
        "Send me a URL to download media, or use /weather or /profile."
    )

def main():
    """Initializes and runs David."""
    # Create the app using your token
    app = app.builder().token(config.BOT_TOKEN).build()

    # Register basic controls
    app.add_handler(CommandHandler("start", start))
    
    # Register core features from separate modules
    app.add_handler(CommandHandler("weather", get_weather))
    app.add_handler(CommandHandler("profile", get_profile))
    
    # Catch-all text filter to detect incoming links for downloading
    # Checks if text looks like a URL
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'http[s]?://'), handle_download))

    # Run the bot until you press Ctrl-C
    print("David is now online and waiting for input...")
    app.run_polling()

if __name__ == "__main__":
    main()