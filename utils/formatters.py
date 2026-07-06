from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message
from telegram.ext import ContextTypes
import math
import time
import httpx

WELCOME_STICKER = "CAACAgUAAyEFAATk9pCQAAMZakUfn7xGYNEfdbj585USINvpNooAAg0kAALhryhWuyRu0oy_WyA8BA"
_last_update_timers = {}


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

async def update_progress_ui(status_message: Message, downloaded_bytes: int, total_bytes: int, prefix_text: str = "📥 **Downloading...**"):
    """
    Updates a Telegram message with a scannable progress bar.
    Rate-limits edits to once every 1.5 seconds to prevent FloodWait blocks.
    """
    msg_id = status_message.message_id
    current_time = time.time()
    last_update_time = _last_update_timers.get(msg_id, 0)
    
    # 1. Calculate progress percentages if size is known
    is_complete = (downloaded_bytes >= total_bytes) if total_bytes > 0 else False
    
    # RATE LIMIT: Only edit if 1.5 seconds have passed OR the download is finished
    if (current_time - last_update_time < 1.5) and not is_complete:
        return

    _last_update_timers[msg_id] = current_time

    downloaded_mb = downloaded_bytes / (1024 * 1024)
    
    if total_bytes > 0:
        percent = (downloaded_bytes / total_bytes) * 100
        # Prevent math bounds errors
        percent = min(max(percent, 0.0), 100.0)
        
        # Draw the progress bar [████░░░░░░]
        completed_blocks = math.floor(percent / 10)
        remaining_blocks = 10 - completed_blocks
        progress_bar = "█" * completed_blocks + "░" * remaining_blocks
        
        total_mb = total_bytes / (1024 * 1024)
        progress_text = (
            f"{prefix_text}\n\n"
            f"[{progress_bar}] {percent:.1f}%\n"
            f"📦 `{downloaded_mb:.2f} MB` / `{total_mb:.2f} MB`"
        )
    else:
        # Fallback if server hides file size header
        progress_text = (
            f"{prefix_text}\n\n"
            f"📦 Loaded: `{downloaded_mb:.2f} MB` (Total size unknown)"
        )

    # 3. Fire the update
    try:
        await status_message.edit_text(progress_text, parse_mode="Markdown")
    except Exception:
        # Pass silently if text hasn't changed or message was deleted by user
        pass
        
    # Clean up memory when finished
    if is_complete and msg_id in _last_update_timers:
        del _last_update_timers[msg_id]