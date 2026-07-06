import config
from telegram import Update, ReactionTypeEmoji
from telegram.ext import ContextTypes
from config import SUPER_ADMIN_ID, BANNED_USERS
from handlers.restrict import save_bans
import json


from utils.formatters import get_start_keyboard, format_welcome_msg, WELCOME_STICKER

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id

    if update.effective_user.is_bot:
        await update.message.reply_text("We don't do that here!\nYou're banned!")
        return

    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name or ""

    await context.bot.set_message_reaction(
        chat_id=chat_id,
        message_id=message_id,
        reaction=[ReactionTypeEmoji(emoji="❤️")]
    )

    await context.bot.send_sticker(chat_id=chat_id, sticker=WELCOME_STICKER)

    if str(config.SUPER_ADMIN_ID).strip() == str(user_id).strip():
        await update.message.reply_text("Welcome NEO!")

    welcome_text = format_welcome_msg(first_name, last_name)
    inline_keyboard = get_start_keyboard()

    await update.message.reply_text(
        text=welcome_text,
        reply_markup=inline_keyboard,
        parse_mode="Markdown"
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id


    if str(user_id) == str(SUPER_ADMIN_ID):
        await update.message.reply_text("⭕️ *Bot shutting down . . .*", parse_mode="Markdown")
        exit(42)
    else:
        await update.message.reply_text(f"❗️Unauthorized command from user : {user_id}")
        await update.message.reply_text(f"❗️User Banned : {user_id}")
        BANNED_USERS.add(user_id)
        save_bans()


async def get_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    info = (
        f"📋 *User Profile*\n\n"
        f"👤 *Name:* {user.first_name} {user.last_name or ''}\n"
        f"🆔 *User ID:* `{user.id}`\n"
        f"🏷️ *Username:* @{user.username or 'None'}"
    )
    await update.message.reply_text(info, parse_mode="Markdown")

async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a city name. Example: /weather Colombo")
        return

    city = " ".join(context.args)
    await update.message.reply_text(f"☀️ Checking weather for {city}...")