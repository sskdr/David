from telegram import InlineKeyboardButton, InlineKeyboardMarkup

WELCOME_STICKER = "CAACAgUAAyEFAATk9pCQAAMZakUfn7xGYNEfdbj585USINvpNooAAg0kAALhryhWuyRu0oy_WyA8BA"

def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👑 Admin Channel", url="https://t.me/exprometheus"),
            InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/thoughtsofAlb3do")
        ],
        [
            InlineKeyboardButton("❓ Help & Commands", callback_data="help_main"),
            InlineKeyboardButton("📊 System Status", callback_data="system_metrics_callback")
        ]
    ])

def format_welcome_msg(first_name: str, last_name: str = "") -> str:
    name_str = f"{first_name} {last_name}".strip()
    return (
        f"👋 *Hello {name_str}!*\n"
        f"✨ Welcome to your download assistant bot.\n"
        f"I can help you download videos, music, images and more!\n\n"
        f"🎯 *Quick Start:*\n"
        f"• Just send me any link to download\n"
        f"• Use /help to see all commands\n"
        f"• Check /history for past downloads\n\n"
        f"Choose an option below:"
    )