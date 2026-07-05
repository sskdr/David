from telegram import Update
from telegram.ext import ContextTypes

async def get_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /profile command."""
    user = update.effective_user
    info = (
        f"📋 *User Profile*\n\n"
        f"👤 *Name:* {user.first_name} {user.last_name or ''}\n"
        f"🆔 *User ID:* `{user.id}`\n"
        f"🏷️ *Username:* @{user.username or 'None'}"
    )
    await update.message.reply_text(info, parse_mode="Markdown")