import re
import requests
import yt_dlp
from urllib.parse import urlparse
from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import httpx
import logging
from utils.logger import setup_logger
from typing import Union
import math
from config import downloading_users, SUPER_ADMIN_ID
from utils.formatters import update_progress_ui
from urllib.parse import urlparse, unquote
import mimetypes
import os
import asyncio
import io


setup_logger()
logger = logging.getLogger(__name__)

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

async def is_direct_file_url(url: str) -> bool:
    """
    Checks the URL headers to see if it points to a supported file type 
    without downloading the entire file body.
    """

    ALLOWED_TYPES = ["pdf", "json", "image", "zip", "jpeg", "png", "octet-stream"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(url, follow_redirects=True, timeout=5.0)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '').lower()
            content_length = response.headers.get('Content-Length')
            return any(file_type in content_type for file_type in ALLOWED_TYPES), content_length

        logger.warning(f"URL returned non-200 status code: {response.status_code}")    
        return False

    except httpx.RequestError as e:
        logger.exception(f"Connection breakdown while validating URL: {url}")
        return False

async def stream_direct_file(url: str, status_message: Message):
    # 1. Define real browser headers to bypass 403 blocks
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.google.com/"  # Tricks some hotlink protections
    }

    # 2. Pass the headers into the AsyncClient
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        async with client.stream("GET", url, follow_redirects=True) as response:
            
            # Optional: Raise an exception instantly if the site still rejects it
            response.raise_for_status()
            
            disposition = response.headers.get("Content-Disposition")
            filename = None
            
            if disposition and "filename=" in disposition:
                filename = disposition.split("filename=")[-1].strip().strip('"').strip("'")
            
            if not filename:
                filename = os.path.basename(urlparse(url).path)
                if not filename:
                    filename = "downloaded_file"
            
            filename = unquote(filename)
            
            content_type = response.headers.get("Content-Type", "").split(';')[0]
            extension = mimetypes.guess_extension(content_type) or "" 
            
            if extension and not filename.endswith(extension) and "." not in filename:
                filename += extension

            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            file_payload = bytearray()
            
            async for chunk in response.aiter_bytes(chunk_size=32768):
                file_payload.extend(chunk)
                downloaded += len(chunk)
                
                await update_progress_ui(
                    status_message=status_message,
                    downloaded_bytes=downloaded,
                    total_bytes=total_size,
                    prefix_text=f"📁 **Streaming:** `{filename}`"
                )
                
            return file_payload, filename, content_type, extension

async def ask_save_locally_and_wait(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Sends the inline keyboard, waits for the user's choice, deletes the message, and returns True or False."""
    
    event = asyncio.Event()
    event_key = f"save_choice_{update.effective_user.id}"
    
    context.user_data[event_key] = {"event": event, "choice": None}

    keyboard = [
        [
            InlineKeyboardButton("✅ Yes", callback_data=f"save_yes:{update.effective_user.id}"),
            InlineKeyboardButton("❌ No", callback_data=f"save_no:{update.effective_user.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    inline_msg = await update.message.reply_text(
        text="Do you want to save the file in the local system?",
        reply_markup=reply_markup
    )

    await event.wait()

    result_data = context.user_data.pop(event_key)
    user_choice = result_data["choice"]

    try:
        await inline_msg.delete()
    except Exception:
        pass

    return user_choice

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_message_id = update.message.message_id

    if user_id in downloading_users:
        await update.message.reply_text(
            "⏳ You already have an active download in progress. Please wait until it finishes!",
            reply_to_message_id=user_message_id
        )
        return

    downloading_users.append(user_id)

    try:
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
            is_file = await is_direct_file_url(final_url)
            
            if is_file:
                await status_message.edit_text("📁 File detected! Starting stream...")
                file_payload, filename, file_type, extension = await stream_direct_file(url=final_url, status_message=status_message)
                
                # if str(user_id) == str(SUPER_ADMIN_ID):
                #     should_save = await ask_save_locally_and_wait(update, context)
                # else:
                #     should_save = False

                should_save = False
                
                if should_save:
                    import os
                    os.makedirs("./downloads", exist_ok=True)
                    with open(f"./downloads/{filename}", "wb") as f:
                        f.write(file_payload)
                    await update.message.reply_text("💾 Saved locally to server storage.")

                await status_message.edit_text(f"📤 Uploading `{filename}` to Telegram...")
                
                file_stream = io.BytesIO(file_payload)
                file_stream.name = filename 

                await context.bot.send_document(
                    chat_id=chat_id,
                    document=file_stream,
                    reply_to_message_id=user_message_id,
                    caption=f"✅ **Successfully processed!**\n📄 `{filename}`" if filename else None,
                    parse_mode="Markdown"
                )
                
                await context.bot.delete_message(chat_id=chat_id, message_id=status_message.message_id)

            else:
                # ONLY delete the status message here if the URL is unsupported!
                await context.bot.delete_message(chat_id=chat_id, message_id=status_message.message_id)
                await update.message.reply_text("❌ Unsupported or Invalid URL. Please try another link!")

    except Exception as e:
        logger.exception(f"An unexpected failure hit user {user_id}")
        await update.message.reply_text("❌ Something went wrong during processing.")

    finally:
        if user_id in downloading_users:
            downloading_users.remove(user_id)