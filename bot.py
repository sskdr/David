import config
from telegram.ext import Application, CommandHandler, MessageHandler, filters, TypeHandler
from telegram import Update
from config import global_ban_checker
from utils.logger import setup_logger
from modules.downloader import handle_download
from handlers.commands import start, stop, get_profile, get_weather


def main():
    setup_logger()

    application = Application.builder().token(config.BOT_TOKEN).build()

    application.add_handler(TypeHandler(Update, global_ban_checker), group=-1)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("weather", get_weather))
    application.add_handler(CommandHandler("profile", get_profile))
    
    # 4. Global URL parsing routing
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'http[s]?://'), handle_download))

    # 5. Boot sequence
    print("\033[H\033[J", end="")
    print("""

    ███        ██████████                          ███      █████
   ██████     ░░███░░░░███                        ░░░      ░░███ 
  ███░░░       ░███   ░░███  ██████   █████ █████ ████   ███████ 
 ░░█████       ░███    ░███ ░░░░░███ ░░███ ░░███ ░░███  ███░░███ 
  ░░░░███      ░███    ░███  ███████  ░███  ░███  ░███ ░███ ░███ 
  ██████       ░███    ███  ███░░███  ░░███ ███   ░███ ░███ ░███ 
 ░░░███        ██████████  ░░████████  ░░█████    █████░░████████
   ░░░        ░░░░░░░░░░    ░░░░░░░░    ░░░░░    ░░░░░  ░░░░░░░░ 
                                                                 
                                                                 
                          ~$ BOT ALIVE!
          
          """)
    application.run_polling()

if __name__ == "__main__":
    main()