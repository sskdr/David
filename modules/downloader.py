import re
import requests
import yt_dlp
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ContextTypes

def get_final_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.head(url, allow_redirects=True, timeout=5, headers=headers)
        return response.url
    except Exception:
        return url

def parse_spotify_url(url: str) -> dict:
    pattern = r'(?:https?:\/\/open\.spotify\.com\/|spotify:)(track|album|playlist|artist|episode)[:\/]([a-zA-Z0-9]{22})'
    match = re.search(pattern, url)
    if match:
        return {
            "is_spotify": True,
            "type": match.group(1),
            "id": match.group(2),
            "clean_url": f"https://open.spotify.com/{match.group(1)}/{match.group(2)}"
        }
    return {"is_spotify": False}

def is_supported_by_ytdlp(original_url: str) -> bool:
    if parse_spotify_url(original_url)["is_spotify"]:
        return False
    extractors = yt_dlp.extractor.gen_extractors()
    for extractor in extractors:
        if extractor.suitable(original_url) and extractor.IE_NAME != "generic":
            return True
    return False

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    original_url = update.message.text.strip()
    
    status_message = await update.message.reply_text("🤖 David is resolving the link...")
    final_url = get_final_url(original_url)

    if is_supported_by_ytdlp(final_url):
        await context.bot.delete_message(chat_id=chat_id, message_id=status_message.message_id)
        await update.message.reply_text("✅ Valid URL. It will be handled by yt_dlp!")
        
    elif parse_spotify_url(final_url)["is_spotify"]:
        await context.bot.delete_message(chat_id=chat_id, message_id=status_message.message_id)
        await update.message.reply_text("✅ Valid URL. It will be handled by spotdl!")
        
    else:
        path = urlparse(final_url).path.lower()
        await context.bot.delete_message(chat_id=chat_id, message_id=status_message.message_id)
        if path.endswith(('.mp4', '.mp3', '.pdf', '.zip', '.jpg', '.png')):
            await update.message.reply_text("📁 Detected a direct file link! Downloading directly via raw network stream...")
        else:
            await update.message.reply_text("❌ Unsupported or Invalid URL. Please try another link!")