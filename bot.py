import config
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# 👇 UPDATED IMPORT PATH
from utils.logger import setup_logger
from modules.downloader import handle_download
from handlers.commands import start, stop, get_profile, get_weather

def main():
    # 1. Initialize silent tracking framework from utils
    setup_logger()

    # 2. Build the application mapping engine
    application = Application.builder().token(config.BOT_TOKEN).build()

    # 3. Connect handler routines
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("weather", get_weather))
    application.add_handler(CommandHandler("profile", get_profile))
    
    # 4. Global URL parsing routing
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'http[s]?://'), handle_download))

    # 5. Boot sequence
    print("David is running smoothly! (Console errors disabled, tracing to logs/bot.log)")
    application.run_polling()

if __name__ == "__main__":
    main()