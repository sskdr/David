from telegram import Update
from telegram.ext import ContextTypes
from config import SUPER_ADMIN_ID, BANNED_USERS
import json

def save_bans():
    with open("banned_users.json", "w") as f:
        json.dump(list(BANNED_USERS), f)

def load_bans():
    try:
        with open("banned_users.json", "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()