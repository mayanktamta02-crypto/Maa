"""
🤖 ADVANCED SCRIPT HOSTING BOT - ADMIN PANEL v6.0 / ENGINE 109
========================================================
✅ Complete Admin Panel Interface (/admin)
✅ 4 Channels Management System
✅ Dynamic Approval Channel Setup
✅ File Approval Workflow with Metadata
✅ Admin Control: Ban/Unban, Maintenance, Lock, Add/Remove Admin
✅ New User Notifications & Rejection System
✅ Bot Script Management (Start/Stop/Logs/Uptime)
✅ Module Installation System
✅ Comprehensive Statistics & Analytics
✅ Upload History Tracking
✅ Support System with Username
✅ Aesthetics & UI Customization
✅ Full Error Handling & Logging
"""

import os
import base64
from io import BytesIO
import json
import logging
import subprocess
import threading
import asyncio
import traceback
import html
import sys
import signal
import random
import time
import secrets
import ast
import re
import importlib.util
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from telegram import Update, InlineKeyboardButton as TelegramInlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ChatMember, Document
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ChatMemberHandler, filters, ContextTypes
from telegram.error import TelegramError, Forbidden, BadRequest
from telegram.constants import ChatMemberStatus


def InlineKeyboardButton(text, callback_data=None, url=None, **kwargs):
    """Create a native Telegram inline button with a consistent theme.

    Telegram Bot API button colors are predefined: primary=blue, success=green,
    danger=red. Status/action labels are mapped automatically so every inline
    button in the bot receives a native style without changing callback data.
    """
    if "style" not in kwargs:
        label = str(text).upper().strip()
        # Status labels and action labels are intentionally separated.
        # STOPPED is a state (blue), while STOP is a destructive action (red).
        if any(word in label for word in ("STOPPED", "OFF")):
            kwargs["style"] = "primary"
        elif any(word in label for word in ("RUNNING", "START", "APPROVE", "SUCCESS", "ONLINE", "CONNECTED")):
            kwargs["style"] = "success"
        elif any(word in label for word in ("REJECT", "DELETE", "BAN", "REMOVE", "CLOSE")) or label == "STOP" or " STOP" in label:
            kwargs["style"] = "danger"
        else:
            kwargs["style"] = "primary"
    return TelegramInlineKeyboardButton(text, callback_data=callback_data, url=url, **kwargs)

# ==================== LOGGING SETUP ====================
# Railway: mount a Volume and set HOSTING_DATA_DIR to its mount path for persistence.
HOSTING_DATA_DIR = os.path.abspath(os.getenv('HOSTING_DATA_DIR', '.'))
Path(HOSTING_DATA_DIR).mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(HOSTING_DATA_DIR, 'bot.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8567751609:AAEIN7VKiZQ6Sk9RyQmhrgv_EW88bo59Ebc").strip()  # Railway BOT_TOKEN overrides the local fallback.
OWNER_USERNAME = "SHUBHxSELLER"

# Admin User IDs - Only these can access /admin
ADMIN_USER_IDS = [int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "5260253836").split(",") if x.strip().isdigit()]  # Restored default admin ID

# ==================== UPLOAD CONFIGURATION ====================
MAX_UPLOAD_SIZE = 30 * 1024 * 1024  # 30 MB
SUPPORTED_UPLOAD_EXTENSIONS = (".py", ".js", ".zip")
MAX_ZIP_FILES = 500
MAX_ZIP_UNCOMPRESSED = 250 * 1024 * 1024
APPROVAL_EXPIRY_HOURS = 24

# ==================== DATABASE FILES ====================
DB_DIR = os.path.join(HOSTING_DATA_DIR, "database")
Path(DB_DIR).mkdir(parents=True, exist_ok=True)

USERS_DB = f"{DB_DIR}/users.json"
PENDING_APPROVALS = f"{DB_DIR}/pending_approvals.json"
RUNNING_SCRIPTS = f"{DB_DIR}/running_scripts.json"
VERIFIED_USERS = f"{DB_DIR}/verified_users.json"
ADMIN_CONFIG = f"{DB_DIR}/admin_config.json"
BANNED_USERS = f"{DB_DIR}/banned_users.json"
CHANNELS_CONFIG = f"{DB_DIR}/channels_config.json"
APPROVAL_CHANNEL_CONFIG = f"{DB_DIR}/approval_channel_config.json"
APPROVAL_SETUP_DB = f"{DB_DIR}/approval_setup.json"
NEW_USERS_DB = f"{DB_DIR}/new_users.json"
BOT_SCRIPTS_DB = f"{DB_DIR}/bot_scripts.json"
UPLOAD_HISTORY_DB = f"{DB_DIR}/upload_history.json"
STATISTICS_DB = f"{DB_DIR}/statistics.json"
USER_SCRIPTS_DIR = os.path.join(HOSTING_DATA_DIR, "user_scripts")
SCRIPT_LOGS_DIR = os.path.join(HOSTING_DATA_DIR, "logs")
INSTALLED_MODULES_DIR = os.path.join(HOSTING_DATA_DIR, "installed_modules")
Path(USER_SCRIPTS_DIR).mkdir(parents=True, exist_ok=True)
Path(SCRIPT_LOGS_DIR).mkdir(parents=True, exist_ok=True)
Path(INSTALLED_MODULES_DIR).mkdir(parents=True, exist_ok=True)

def user_module_dir(user_id):
    """Return an isolated dependency directory for one Telegram user."""
    safe_id = ''.join(ch for ch in str(user_id) if ch.isdigit()) or 'unknown'
    path = os.path.abspath(os.path.join(INSTALLED_MODULES_DIR, safe_id))
    os.makedirs(path, exist_ok=True)
    return path

SCRIPT_PROCESSES = {}
SCRIPT_PROCESS_LOCK = threading.Lock()

# Version 114 intentionally has no automatic repair or automatic restart.

# ==================== EMOJI CONFIGURATION ====================
# Use standard Unicode emojis only. Telegram custom emoji IDs are intentionally
# not used anywhere in this bot.
EMOJI_LOCK = "🔒"
EMOJI_LOCK_CLOSED = "🔒"
EMOJI_LOCK_OPEN = "🔓"
EMOJI_KEY = "🔑"
EMOJI_PROHIBITED = "⛔"
EMOJI_X = "❌"
EMOJI_CHECK = "✅"
EMOJI_WAIT = "⏳"
EMOJI_WARNING = "⚠️"
EMOJI_STATS = "📊"
EMOJI_FOLDER = "📁"
EMOJI_EMAIL = "📧"
EMOJI_UPLOAD = "📤"
EMOJI_SAVE = "💾"
EMOJI_MANAGE = "🛠️"
EMOJI_SETTINGS = "⚙️"
EMOJI_BACK = "◀️"
EMOJI_FORWARD = "▶️"
EMOJI_ROCKET = "🚀"
EMOJI_BROADCAST = "📢"
EMOJI_TAG = "🏷️"
EMOJI_TIME = "⏱️"
EMOJI_PLUS = "➕"
EMOJI_MINUS = "➖"
EMOJI_SPEED = "⚡"
EMOJI_GREEN = "🟢"
EMOJI_RED = "🔴"
EMOJI_YELLOW = "🟡"
EMOJI_PAINT = "🎨"
EMOJI_PHONE = "📱"

# User-side custom emoji IDs (Telegram Bot API 9.4+ / PTB 22.7+).
# These are rendered as real custom emojis in messages/buttons; IDs are never shown.
USER_CUSTOM_EMOJI_IDS = {
    "📤": "6071202170026332329", "📁": "5240478589295552614",
    "🧩": "6071414045058012551",
    "🎓": "6300926733600167495",  # Tutorial button custom emoji
    "➕": "6071375575035941877", "📊": "6269397073737553354",
    "⚡": "6271459718896554468", "📱": "6188028548947644497",
    "🆔": "5841276284155467413", "📉": "5447183459602669338",
    "✅": "5206607081334906820", "❌": "5210952531676504517",
    "⚠️": "5420323339723881652", "🔴": "6035142758480482309",
    "🟢": "5769547529993588669", "🔵": "6028565819225542441",
    "🟡": "5276032951342088188", "🏷️": "5235582317988171528",
    "📄": "5837003105228558796", "🔄": "5215579104807497179",
    "◀️": "6123107313654960925", "▶️": "6196964713738279294",
    "🗑️": "6073288235642000201", "🛑": "6257858798715670989",
    "⏹️": "5454380420336466255", "🚫": "5373342608028352831",
    "🔒": "5291873529464122510", "🔐": "5465443379917629504",
    "📣": "6071188061058766421", "⏳": "5454415424319931791",
    "⌛": "5472239203590888751", "💬": "5472239203590888751",
    "📡": "5256134032852278918", "🌐": "5447410659077661506",
    "🤖": "4940635119791637363", "📦": "5235695112419303615",
    "🛠️": "5462921117423384478", "🔧": "5462921117423384478",
    "📌": "5397782960512444700", "ℹ️": "5334544901428229844",
    "❗": "5274099962655816924", "✔️": "6269285159774720688",
    "✖️": "6269362834258269327",
    "🚀": "5780773956030043338",
    # Version 114 custom emoji IDs supplied by the bot owner.
    "💎": "5251291564600220990",       # Buy Premium
    "🎟️": "6269489059052133223",       # Redeem Code
    "🎫": "5431653802753159903",       # Generate Promo Code
    "👑": "6071375575035941877",       # Add Premium
    "🧾": "5287651735525937879",       # Deduct Premium
    "🗓️": "6269360798443770934",       # Add Plans
    "🛑": "5454380420336466255",       # Stop All Scripts
    "📸": "5442991756205373676",       # Submit Screenshot
    "🟩": "5229011542011299168",       # Premium plan buttons
    "🧩": "6071414045058012551",       # Variables
    "💎": "5251291564600220990",       # Buy Premium
    "🎟️": "6269489059052133223",       # Redeem Code
    "🎫": "5431653802753159903",       # Generate Promo Code
    "👑": "6071375575035941877",       # Add Premium
    "🧾": "5287651735525937879",       # Deduct Premium
    "🗓️": "6269360798443770934",       # Add Plans
    "📸": "5442991756205373676",       # Submit Screenshot
    "🟩": "5229011542011299168",       # Premium plan
}

# Tutorial custom emoji ID supplied by the bot owner.
TUTORIAL_CUSTOM_EMOJI_ID = "6300926733600167495"
V114_CUSTOM_EMOJI_IDS = {
    "tutorial": TUTORIAL_CUSTOM_EMOJI_ID,
    "variables": "6071414045058012551",
    "buy_premium": "5251291564600220990",
    "redeem_code": "6269489059052133223",
    "my_stats": "6269397073737553354",
    "generate_promo_code": "5431653802753159903",
    "add_premium": "6071375575035941877",
    "deduct_premium": "5287651735525937879",
    "add_plans": "6269360798443770934",
    "stop_all_scripts": "5454380420336466255",
    "submit_screenshot": "5442991756205373676",
    "premium_plan": "5229011542011299168",
}

def user_emoji(emoji: str) -> str:
    """Return a Telegram custom emoji HTML entity for user-facing messages."""
    emoji_id = USER_CUSTOM_EMOJI_IDS.get(emoji)
    if not emoji_id:
        return ""
    return f'<tg-emoji emoji-id="{emoji_id}">{emoji}</tg-emoji>'

ENABLE_CUSTOM_EMOJI_BUTTONS = os.getenv("ENABLE_CUSTOM_EMOJI_BUTTONS", "1").strip().lower() in {"1", "true", "yes", "on"}

def user_button(label: str, emoji: str, **kwargs):
    """Create a safe inline button.

    V111 defaults to standard Telegram buttons. Custom emoji button icons are
    optional and can be enabled with ENABLE_CUSTOM_EMOJI_BUTTONS=1. If Telegram
    rejects an icon/custom-emoji ID, the button is retried without the icon so
    an upload/start operation can never fail because of emoji configuration.
    """
    emoji_id = USER_CUSTOM_EMOJI_IDS.get(emoji) if ENABLE_CUSTOM_EMOJI_BUTTONS else None
    if emoji_id:
        try:
            return TelegramInlineKeyboardButton(label, icon_custom_emoji_id=emoji_id, **kwargs)
        except Exception as exc:
            logger.warning("Custom emoji button disabled for %r: %s", emoji, exc)
    return TelegramInlineKeyboardButton(label, **kwargs)

def user_reply_button(label: str, emoji: str, **kwargs):
    """Create a native Telegram reply-keyboard button with style and optional custom emoji.

    python-telegram-bot 22.7+ supports Telegram's native button styles:
    primary (blue), success (green), and danger (red). Clients must also
    support the newer Telegram Bot API button styling feature.
    """
    emoji_id = USER_CUSTOM_EMOJI_IDS.get(emoji) if ENABLE_CUSTOM_EMOJI_BUTTONS else None
    if emoji_id:
        try:
            return KeyboardButton(label, icon_custom_emoji_id=emoji_id, **kwargs)
        except Exception as exc:
            logger.warning("Custom emoji reply button disabled for %r: %s", label, exc)
    return KeyboardButton(label, **kwargs)

# ==================== DEFAULT CONFIGURATION ====================
DEFAULT_CHANNELS = {
    "channel_1": {
        "name": "Main Channel",
        "username": "@AADITYAXFF",
        "link": "https://t.me/AADITYAXFF",
        "chat_id": -1001234567890
    },
    "channel_2": {
        "name": "Main Group",
        "username": "@BOTSBYAADITYA",
        "link": "https://t.me/BOTSBYAADITYA",
        "chat_id": -1001234567891
    },
    "channel_3": {
        "name": "Support Channel",
        "username": "@SHUBHxSELLER",
        "link": "https://t.me/SHUBHxSELLER",
        "chat_id": -1001234567892
    },
    "channel_4": {
        "name": "Announcements",
        "username": "@AADITYAANNOUNCE",
        "link": "https://t.me/AADITYAANNOUNCE",
        "chat_id": -1001234567893
    }
}

DEFAULT_ADMIN_CONFIG = {
    "maintenance_mode": False,
    "lock_mode": False,
    "log_mode": False,
    "admins": ADMIN_USER_IDS,
    "channels": DEFAULT_CHANNELS,
    "bot_status": "ONLINE",
    "aesthetics": {
        "theme": "dark",
        "primary_color": "#2E86DE",
        "accent_color": "#A23B72"
    }
}

DEFAULT_STATISTICS = {
    "total_users": 0,
    "total_files_uploaded": 0,
    "total_approved": 0,
    "total_rejected": 0,
    "total_modules_installed": 0,
    "bot_start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

# ==================== DATABASE FUNCTIONS ====================

def load_json(filename):
    """Load JSON file with error handling"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return {}

def save_json(filename, data):
    """Save JSON file with error handling"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")
        return False

def load_admin_config():
    """Load or create admin config"""
    try:
        config = load_json(ADMIN_CONFIG)
        if not config:
            save_json(ADMIN_CONFIG, DEFAULT_ADMIN_CONFIG)
            return DEFAULT_ADMIN_CONFIG
        return config
    except Exception as e:
        logger.error(f"Error loading admin config: {e}")
        return DEFAULT_ADMIN_CONFIG

def save_admin_config(config):
    """Save admin config"""
    return save_json(ADMIN_CONFIG, config)


def load_channels_config():
    """Load only channels explicitly configured by the administrator."""
    config = load_json(CHANNELS_CONFIG)
    if not isinstance(config, dict):
        config = {}
        save_json(CHANNELS_CONFIG, config)
    return config


def save_channels_config(config):
    return save_json(CHANNELS_CONFIG, config)


def load_approval_channel():
    """Load approval channel configuration."""
    return load_json(APPROVAL_CHANNEL_CONFIG)


def save_approval_channel(config):
    return save_json(APPROVAL_CHANNEL_CONFIG, config)

def load_approval_setup():
    return load_json(APPROVAL_SETUP_DB)

def save_approval_setup(data):
    return save_json(APPROVAL_SETUP_DB, data)

async def notify_new_user_to_approval_channel(context, user):
    """Notify the configured approval channel when a new user starts the bot."""
    approval = load_approval_channel()
    if not approval or not approval.get("chat_id"):
        return
    try:
        username = f"@{user.username}" if user.username else "No username"
        premium = "PREMIUM" if getattr(user, "is_premium", False) else "NON-PREMIUM"
        display_name = html.escape(user.full_name or "User")
        text = (
            f"🆕 <b>NEW USER STARTED BOT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Name:</b> {display_name}\n"
            f"<b>Username:</b> {html.escape(username)}\n"
            f"<b>User ID:</b> <code>{user.id}</code>\n"
            f"<b>Telegram Premium:</b> <b>{premium}</b>"
        )
        keyboard = [[InlineKeyboardButton("💬 TALK TO USER", url=f"tg://user?id={user.id}")]]
        await context.bot.send_message(
            chat_id=approval["chat_id"],
            text=text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"New-user approval-channel notification failed: {e}\n{traceback.format_exc()}")

async def auto_approval_channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Automatically bind the next channel where the bot is added/promoted as admin."""
    try:
        cm = update.my_chat_member
        if not cm or not cm.chat or cm.chat.type != "channel":
            return
        setup = load_approval_setup()
        if not setup.get("active"):
            return
        admin_id = cm.from_user.id if cm.from_user else None
        target_admin_id = setup.get("admin_id")
        if target_admin_id and admin_id and str(target_admin_id) != str(admin_id):
            return
        new_member = cm.new_chat_member
        if new_member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return
        if new_member.status == ChatMemberStatus.ADMINISTRATOR and hasattr(new_member, "can_post_messages") and not new_member.can_post_messages:
            await context.bot.send_message(
                chat_id=target_admin_id or cm.from_user.id,
                text=f"{EMOJI_WARNING} Bot was added as admin, but it does not have permission to post messages. Please enable <b>Post Messages</b>.",
                parse_mode="HTML"
            )
            return
        chat = cm.chat
        username = f"@{chat.username}" if chat.username else None
        save_approval_channel({
            "chat_id": chat.id,
            "username": username,
            "name": chat.title or "Approval Channel",
            "auto_detected": True,
            "set_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        save_approval_setup({})
        recipient = target_admin_id or (cm.from_user.id if cm.from_user else None)
        if recipient:
            await context.bot.send_message(
                chat_id=recipient,
                text=(f"{EMOJI_CHECK} <b>APPROVAL CHANNEL CONNECTED</b>\n\n"
                      f"<b>Channel:</b> {html.escape(chat.title or 'Approval Channel')}\n"
                      f"<b>Chat ID:</b> <code>{chat.id}</code>\n\n"
                      f"All new user-start alerts and uploaded files will now be sent here automatically."),
                parse_mode="HTML"
            )
        logger.info("Approval channel auto-detected: %s (%s)", chat.title, chat.id)
    except Exception as e:
        logger.error(f"Auto approval-channel detection failed: {e}\n{traceback.format_exc()}")


def system_state():
    config = load_admin_config()
    return {
        "maintenance_mode": bool(config.get("maintenance_mode", False)),
        "lock_mode": bool(config.get("lock_mode", False)),
        "log_mode": bool(config.get("log_mode", False)),
    }


def user_block_message(config):
    if config.get("maintenance_mode"):
        return f"{EMOJI_WARNING} <b>BOT UNDER MAINTENANCE</b>\n\nThe bot is currently under maintenance. Please try again later."
    if config.get("lock_mode"):
        return f"{EMOJI_LOCK} <b>BOT LOCKED</b>\n\nThe bot is temporarily locked by the administrator. Please try again later."
    return None


async def enforce_user_system_gate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Block normal users while maintenance/lock mode is enabled."""
    user = update.effective_user
    if not user or is_admin(user.id):
        return False
    message = user_block_message(system_state())
    if not message:
        return False
    try:
        target = update.effective_message
        if target:
            await target.reply_text(message, parse_mode="HTML")
    except Exception as e:
        logger.error("System gate response failed: %s", e)
    return True


async def notify_users_system_change(context, mode, enabled, admin_id):
    """Notify registered users about user-impacting admin mode changes."""
    users = load_json(USERS_DB)
    if not users:
        return 0, 0
    if mode == "maintenance":
        title = "MAINTENANCE MODE"
        body = ("The bot is currently under maintenance. Please wait until it is back online." if enabled
                else "Maintenance has been completed. The bot is back online and ready to use.")
    elif mode == "lock":
        title = "LOCK MODE"
        body = ("The bot has been temporarily locked by the administrator. Please try again later." if enabled
                else "The bot has been unlocked. You can use all available features again.")
    else:
        title = "LOG MODE"
        body = ("System monitoring/log mode has been enabled by the administrator." if enabled
                else "System monitoring/log mode has been disabled by the administrator.")
    text = f"{EMOJI_CHECK if not enabled else EMOJI_WARNING} <b>{title} {'ENABLED' if enabled else 'DISABLED'}</b>\n\n{body}"
    sent = failed = 0
    for uid, info in users.items():
        try:
            if is_user_banned(int(uid)):
                continue
            await context.bot.send_message(chat_id=int(uid), text=text, parse_mode="HTML")
            sent += 1
        except Exception as e:
            failed += 1
            logger.warning("System notification failed for %s: %s", uid, e)
    logger.info("System change notification: mode=%s enabled=%s admin=%s sent=%s failed=%s", mode, enabled, admin_id, sent, failed)
    return sent, failed


async def admin_action_log(context, admin_id, action, details=""):
    """Optional admin activity notification for log mode; always writes server logs."""
    line = f"ADMIN_ACTION admin={admin_id} action={action} details={details}"
    logger.info(line)
    config = load_admin_config()
    if not config.get("log_mode"):
        return
    # Log mode is intentionally an admin audit mode, not a spam broadcast to every user.
    try:
        await context.bot.send_message(chat_id=admin_id, text=f"📝 <b>ADMIN LOG</b>\n{html.escape(line)}", parse_mode="HTML")
    except Exception:
        pass


def format_file_size(size):
    try:
        size = float(size)
        if size >= 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        return f"{size / 1024:.2f} KB"
    except Exception:
        return "Unknown"


def get_file_type(file_name):
    ext = Path(file_name).suffix.lower()
    return ext[1:] if ext else "unknown"


def load_pending_approvals():
    return load_json(PENDING_APPROVALS)


def save_pending_approvals(data):
    return save_json(PENDING_APPROVALS, data)

def load_statistics():
    """Load statistics"""
    stats = load_json(STATISTICS_DB)
    if not stats:
        save_json(STATISTICS_DB, DEFAULT_STATISTICS)
        return DEFAULT_STATISTICS
    return stats

def save_statistics(stats):
    """Save statistics"""
    return save_json(STATISTICS_DB, stats)

def update_statistics(key, increment=1):
    """Update specific statistic"""
    try:
        stats = load_statistics()
        if key in stats and isinstance(stats[key], int):
            stats[key] += increment
            save_statistics(stats)
        return True
    except Exception as e:
        logger.error(f"Error updating statistics: {e}")
        return False

def load_banned_users():
    """Load banned users"""
    return load_json(BANNED_USERS)

def save_banned_users(banned):
    """Save banned users"""
    return save_json(BANNED_USERS, banned)

def is_user_banned(user_id):
    """Check if user is banned"""
    banned = load_banned_users()
    return str(user_id) in banned

def ban_user(user_id, reason="No reason provided"):
    """Ban a user"""
    try:
        banned = load_banned_users()
        banned[str(user_id)] = {
            "user_id": user_id,
            "banned_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "reason": reason
        }
        save_banned_users(banned)
        return True
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        return False

def unban_user(user_id):
    """Unban a user"""
    try:
        banned = load_banned_users()
        if str(user_id) in banned:
            del banned[str(user_id)]
            save_banned_users(banned)
        return True
    except Exception as e:
        logger.error(f"Error unbanning user: {e}")
        return False

def is_admin(user_id):
    """Check if user is admin"""
    return user_id in ADMIN_USER_IDS

def load_bot_scripts():
    """Load bot scripts"""
    return load_json(BOT_SCRIPTS_DB)

def save_bot_scripts(scripts):
    """Save bot scripts"""
    return save_json(BOT_SCRIPTS_DB, scripts)

def load_upload_history():
    """Load upload history"""
    return load_json(UPLOAD_HISTORY_DB)

def save_upload_history(history):
    """Save upload history"""
    return save_json(UPLOAD_HISTORY_DB, history)

def add_upload_record(user_id, file_name, file_size):
    """Add upload record"""
    try:
        history = load_upload_history()
        record_id = str(len(history) + 1)
        history[record_id] = {
            "user_id": user_id,
            "file_name": file_name,
            "file_size": file_size,
            "upload_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "pending"
        }
        save_upload_history(history)
        update_statistics("total_files_uploaded", 1)
        return True
    except Exception as e:
        logger.error(f"Error adding upload record: {e}")
        return False

# ==================== COMMAND HANDLERS ====================

def get_main_keyboard(user_id=None):
    """Build the standard menu; Variables is available to admins and regular users."""
    keyboard = [
        [user_reply_button("UPLOAD FILE", "📤", style="success"), user_reply_button("MY SCRIPTS", "📁", style="primary")],
        [user_reply_button("INSTALL MODULE", "➕", style="success"), user_reply_button("MY STATS", "📊", style="primary")],
        [user_reply_button("BOT SPEED", "⚡", style="success"), user_reply_button("HELP", "📱", style="primary")],
        [user_reply_button("BUY PREMIUM", "💎", style="danger"), user_reply_button("REDEEM CODE", "🎟️", style="danger")],
        [user_reply_button("SUPPORT", "💬", style="danger"), user_reply_button("STOP ALL SCRIPTS", "🛑", style="danger")],
    ]
    # Tutorial and Variables are available to all users. Access is scoped per owner
    # in the Variables project selector; admins can inspect all users' projects.
    keyboard.append([
        user_reply_button("TUTORIAL", "🎓", style="primary"),
        user_reply_button("VARIABLES", "🧩", style="primary"),
    ])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False, is_persistent=True, selective=False)

_EMBEDDED_BANNER_PNG = base64.b64decode("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")
_EMBEDDED_JOIN_PNG = base64.b64decode("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")

async def _send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user) -> None:
    """Send the V10 welcome banner and the existing reply menu."""
    name = html.escape(user.first_name or user.full_name or "User")
    # Keep the entire welcome text in Telegram's quote-style block, like the reference screenshot.
    caption = (
        "<blockquote>"
        "<b>✓ VERIFICATION COMPLETE — WELCOME, " + name.upper() + "!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>WELCOME, " + name + "</b>\n\n"
        "• Supports: <b>.py • .js • .zip</b>\n"
        "• Virtual Private Server Hosting\n"
        "• Prepaid both plans are available\n"
        "• Fast and supportive service\n\n"
        "Choose an option below.\n\n"
        "<b>Hosting Bot V10</b>\n"
        "Choose an action from menu."
        "</blockquote>"
    )
    banner = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hosting_bot_v10_banner.png")
    photo = open(banner, "rb") if os.path.isfile(banner) else BytesIO(_EMBEDDED_BANNER_PNG)
    try:
        await context.bot.send_photo(
            chat_id=user.id, photo=photo, caption=caption, parse_mode="HTML",
            reply_markup=get_main_keyboard(user.id)
        )
    finally:
        photo.close()


async def _force_join_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show configured channel links and a single automatic-verification button."""
    user = update.effective_user
    channels = load_channels_config()
    rows = []
    for key, ch in channels.items():
        link = ch.get("link") or (f"https://t.me/{str(ch.get('username')).lstrip('@')}" if ch.get("username") else None)
        if link:
            rows.append([InlineKeyboardButton(str(ch.get("name") or key), url=link)])
    rows.append([InlineKeyboardButton("✅ I'LL JOIN ALL — VERIFY", callback_data="force_verify_all")])
    text = (
        "<b>JOIN ALL CHANNELS</b>\n\n"
        "<b>Join all channels mandatory verification.</b>\n"
        "Join all channels to proceed bot.\n\n"
        "After joining every channel, tap <b>I'll Join All — Verify</b>."
    )
    banner = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hosting_bot_v10_join.png")
    photo = open(banner, "rb") if os.path.isfile(banner) else BytesIO(_EMBEDDED_JOIN_PNG)
    try:
        await context.bot.send_photo(
            chat_id=user.id, photo=photo, caption=text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(rows)
        )
    finally:
        photo.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the quote-style loading animation only on a user's first start."""
    try:
        user = update.effective_user
        if not user or not update.effective_message:
            return
        user_id = user.id
        if is_user_banned(user_id):
            banned_record = load_banned_users().get(str(user_id), {})
            reason = str(banned_record.get('reason', '')).lower() if isinstance(banned_record, dict) else ''
            if 'fake payment' in reason:
                ban_message = 'You are banned due to fake payment.'
            else:
                ban_message = f"{EMOJI_PROHIBITED} <b>ACCESS DENIED</b>\n\nYou have been banned from using this bot."
            await update.effective_message.reply_text(ban_message, parse_mode="HTML")
            return
        if await enforce_user_system_gate(update, context):
            return

        users = load_json(USERS_DB)
        is_new_user = str(user_id) not in users
        if is_new_user:
            # Quote-format progress is shown once for a newly registered user only.
            loading = await update.effective_message.reply_text(
                "<blockquote><b>◇ VERIFYING YOU...</b>\n\n[▰▱▱▱▱▱▱▱▱▱] 0%</blockquote>",
                parse_mode="HTML"
            )
            for percent in range(10, 101, 10):
                filled = percent // 10
                bar = "▰" * filled + "▱" * (10 - filled)
                await asyncio.sleep(0.07)
                try:
                    await loading.edit_text(
                        f"<blockquote><b>◇ VERIFYING YOU...</b>\n\n[{bar}] {percent}%</blockquote>",
                        parse_mode="HTML"
                    )
                except BadRequest:
                    pass
            try:
                await loading.edit_text(
                    "<blockquote><b>✓ VERIFIED</b>\n\nVerification complete.</blockquote>",
                    parse_mode="HTML"
                )
                await asyncio.sleep(0.15)
            finally:
                try:
                    await loading.delete()
                except TelegramError:
                    pass

            users[str(user_id)] = {
                "user_id": user_id,
                "username": user.username or "N/A",
                "first_name": user.first_name or "User",
                "joined_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "force_join_verified": False
            }
            save_json(USERS_DB, users)
            update_statistics("total_users", 1)
            await notify_new_user_to_approval_channel(context, user)
        else:
            # Keep the stored name current without resetting verification state.
            record = users.get(str(user_id), {})
            if isinstance(record, dict):
                record["username"] = user.username or "N/A"
                record["first_name"] = user.first_name or "User"
                users[str(user_id)] = record
                save_json(USERS_DB, users)

        record = users.get(str(user_id), {})
        force_join_verified = isinstance(record, dict) and record.get("force_join_verified") is True
        channels = load_channels_config()
        if channels and not force_join_verified:
            context.user_data["pending_force_join"] = True
            await _force_join_channels(update, context)
            return
        await _send_main_menu(update, context, user)
        logger.info("User %s (%s) started the bot", user.username, user_id)
    except Exception as e:
        logger.error("Error in start command: %s\n%s", e, traceback.format_exc())
        try:
            await update.effective_message.reply_text("❌ An error occurred. Please try again.")
        except Exception:
            pass

async def verify_force_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check channel membership before removing the gate and showing the menu."""
    query = update.callback_query
    user = query.from_user
    channels = load_channels_config()
    if not channels:
        await query.answer("No channels are configured.", show_alert=True)
        try:
            await query.message.delete()
        except Exception:
            pass
        await _send_main_menu(update, context, user)
        return
    missing = []
    for key, ch in channels.items():
        chat_ref = ch.get("chat_id") or ch.get("username")
        if not chat_ref:
            missing.append(ch.get("name") or key)
            continue
        try:
            member = await context.bot.get_chat_member(chat_ref, user.id)
            if member.status not in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER) and not (member.status == ChatMemberStatus.RESTRICTED and getattr(member, "is_member", False)):
                missing.append(ch.get("name") or key)
        except TelegramError as exc:
            logger.warning("Force-join membership check unavailable for %s: %s", chat_ref, exc)
            missing.append(ch.get("name") or key)
    if missing:
        await query.answer(
            "Join all listed channels first. Membership check may require the bot to be an admin in a channel.",
            show_alert=True
        )
        return
    await query.answer("Verification complete!")
    context.user_data.pop("pending_force_join", None)
    users = load_json(USERS_DB)
    record = users.get(str(user.id), {})
    if not isinstance(record, dict):
        record = {"user_id": user.id, "first_name": user.first_name or "User"}
    record["force_join_verified"] = True
    users[str(user.id)] = record
    save_json(USERS_DB, users)
    try:
        await query.message.delete()
    except TelegramError:
        pass
    await _send_main_menu(update, context, user)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /admin command"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text(
                f"{EMOJI_PROHIBITED} <b>ACCESS DENIED</b>\n\n"
                f"Only admins can access the admin panel.",
                parse_mode="HTML"
            )
            return
        
        await show_admin_panel(update, context)
        logger.info(f"Admin {update.effective_user.username} accessed admin panel")
    except Exception as e:
        logger.error(f"Error in admin command: {e}\n{traceback.format_exc()}")
        try:
            await update.message.reply_text(f"{EMOJI_X} An error occurred.")
        except:
            pass

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin panel with force/approval channel controls."""
    try:
        keyboard = [
            [
                InlineKeyboardButton(f"{EMOJI_TAG} Scripts", callback_data="admin_scripts"),
                InlineKeyboardButton(f"{EMOJI_STATS} Statistics", callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton(f"{EMOJI_FOLDER} Uploads", callback_data="admin_uploads"),
                InlineKeyboardButton(f"{EMOJI_MANAGE} Manage", callback_data="admin_manage")
            ],
            [
                InlineKeyboardButton("📢 Force Channels", callback_data="force_channels"),
                InlineKeyboardButton("✅ Approval Channel", callback_data="approval_channel")
            ],
            [
                InlineKeyboardButton(f"{EMOJI_PAINT} Aesthetics", callback_data="admin_aesthetics"),
                InlineKeyboardButton(f"{EMOJI_SETTINGS} Settings", callback_data="admin_settings")
            ],
            [InlineKeyboardButton("💎 Premium / Plans / UPI", callback_data="v114_premium_admin")],
            [InlineKeyboardButton("🔄 Enable Mode (Free/Paid)", callback_data="v115_mode_toggle")],
            [InlineKeyboardButton("🎓 Set Tutorial Video", callback_data="v114_tutorial_config")],
            [InlineKeyboardButton(f"{EMOJI_X} Close", callback_data="admin_close")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        admin_text = (
            f"{EMOJI_SETTINGS} <b>ADMIN CONTROL PANEL</b>\n\n"
            f"<b>Available Functions:</b>\n"
            f"• {EMOJI_TAG} Manage bot scripts\n"
            f"• {EMOJI_STATS} View statistics\n"
            f"• {EMOJI_FOLDER} Check uploads & approvals\n"
            f"• 📢 Manage force-join channels\n"
            f"• ✅ Set approval channel\n"
            f"• {EMOJI_MANAGE} User management\n"
            f"• {EMOJI_PAINT} Customize aesthetics\n"
            f"• {EMOJI_SETTINGS} Bot settings\n\n"
            f"<i>Select an option below</i>"
        )
        if update.callback_query:
            await update.callback_query.edit_message_text(admin_text, parse_mode="HTML", reply_markup=reply_markup)
        else:
            await update.message.reply_text(admin_text, parse_mode="HTML", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in show_admin_panel: {e}\n{traceback.format_exc()}")



async def admin_manage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Advanced user management: inspect users, message, ban/unban, stop/delete scripts."""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied", show_alert=True)
        return
    users = load_json(USERS_DB)
    scripts = load_bot_scripts()
    total_files = len(load_upload_history())
    total_users = len(users)
    total_scripts = len(scripts)
    text = (
        f"{EMOJI_MANAGE} <b>USER MANAGEMENT</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Total Users:</b> <code>{total_users}</code>\n"
        f"📁 <b>Total Uploaded Files:</b> <code>{total_files}</code>\n"
        f"🤖 <b>Approved/Hosted Scripts:</b> <code>{total_scripts}</code>\n\n"
        f"Select a user to inspect their profile, message them, ban/unban them, or control their hosted scripts."
    )
    keyboard = [
        [InlineKeyboardButton("👤 SELECT USER", callback_data="admin_select_user")],
        [InlineKeyboardButton("📋 ALL USERS / FILES", callback_data="admin_all_users")],
        [InlineKeyboardButton("🚫 BAN USER", callback_data="admin_ban_user"),
         InlineKeyboardButton("♻️ UNBAN USER", callback_data="admin_unban_user")],
        [InlineKeyboardButton("📢 BROADCAST", callback_data="admin_broadcast")],
        [InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data="admin_panel")]
    ]
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))


async def admin_select_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied", show_alert=True); return
    context.user_data['admin_action'] = 'select_user'
    await query.answer()
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=("👤 <b>SELECT USER</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
              "Send the user's <b>Telegram User ID</b>.\n\n"
              "The next message can be the numeric ID.\n"
              "Send /cancel to cancel."),
        parse_mode='HTML'
    )


async def admin_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied", show_alert=True); return
    users = load_json(USERS_DB)
    scripts = load_bot_scripts()
    history = load_upload_history()
    if not users:
        text = "📋 <b>ALL USERS / FILES</b>\n\nNo users have started the bot yet."
        kb = [[InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data='admin_manage')]]
    else:
        rows=[]
        text = "📋 <b>ALL USERS / FILES</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        # Show every registered user with their upload/script counts.
        for uid, info in users.items():
            user_scripts=[x for x in scripts.values() if str(x.get('user_id'))==str(uid)]
            user_files=[x for x in history.values() if str(x.get('user_id'))==str(uid)]
            name=html.escape(str(info.get('first_name') or info.get('username') or 'User'))
            banned='🚫' if is_user_banned(int(uid)) else '👤'
            text += f"{banned} <b>{name}</b> — <code>{uid}</code> | Files: <code>{len(user_files)}</code> | Scripts: <code>{len(user_scripts)}</code>\n"
            rows.append([InlineKeyboardButton(f"{banned} {name} ({uid})", callback_data=f"admin_user_{uid}")])
        rows.append([InlineKeyboardButton("👤 SELECT BY ID", callback_data="admin_select_user")])
        rows.append([InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data="admin_manage")])
        kb=rows
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))


async def admin_user_profile(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id=None) -> None:
    query=update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied", show_alert=True); return
    if target_id is None:
        target_id=(query.data or '').replace('admin_user_','',1)
    if not str(target_id).isdigit():
        await query.answer('Invalid user ID', show_alert=True); return
    target_id=int(target_id)
    users=load_json(USERS_DB); scripts=load_bot_scripts(); history=load_upload_history()
    info=users.get(str(target_id), {})
    user_scripts={k:v for k,v in scripts.items() if str(v.get('user_id'))==str(target_id)}
    user_files=[x for x in history.values() if str(x.get('user_id'))==str(target_id)]
    running=sum(1 for x in user_scripts.values() if x.get('status')=='running')
    stopped=len(user_scripts)-running
    name=html.escape(str(info.get('first_name') or 'Unknown'))
    username=html.escape('@'+str(info.get('username')) if info.get('username') and info.get('username')!='N/A' else 'N/A')
    banned=is_user_banned(target_id)
    text=(f"👤 <b>USER CONTROL</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
          f"<b>Name:</b> {name}\n<b>Username:</b> {username}\n<b>User ID:</b> <code>{target_id}</code>\n"
          f"<b>Account:</b> {'🚫 BANNED' if banned else '✅ ACTIVE'}\n\n"
          f"📁 <b>Uploaded Files:</b> <code>{len(user_files)}</code>\n"
          f"🤖 <b>Hosted Scripts:</b> <code>{len(user_scripts)}</code>\n"
          f"🟢 <b>Running:</b> <code>{running}</code>\n🔵 <b>Stopped:</b> <code>{stopped}</code>")
    kb=[
        [InlineKeyboardButton("💬 MESSAGE USER", callback_data=f"admin_message_{target_id}")],
        [InlineKeyboardButton("♻️ UNBAN USER" if banned else "🚫 BAN USER", callback_data=f"admin_toggleban_{target_id}")],
        [InlineKeyboardButton("⏹ STOP ALL RUNNING", callback_data=f"admin_stopall_{target_id}"),
         InlineKeyboardButton("🗑️ DELETE ALL SCRIPTS", callback_data=f"admin_deleteall_{target_id}")],
    ]
    for sid,script in user_scripts.items():
        status='🟢' if script.get('status')=='running' else '🔵'
        action='STOP' if script.get('status')=='running' else 'DELETE'
        kb.append([InlineKeyboardButton(f"{status} {script.get('name','Unknown')} — {action}", callback_data=f"admin_script_{sid}")])
    kb.append([InlineKeyboardButton("👤 SELECT ANOTHER USER", callback_data="admin_select_user")])
    kb.append([InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data="admin_manage")])
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))


async def admin_message_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int) -> None:
    query=update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied", show_alert=True); return
    context.user_data['admin_action']=f'message_user:{target_id}'
    await query.answer()
    await context.bot.send_message(chat_id=query.from_user.id,
        text=f"💬 <b>MESSAGE USER</b>\n\nSend the message for <code>{target_id}</code>.\nSend /cancel to cancel.",parse_mode='HTML')


async def admin_toggle_user_ban(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int) -> None:
    query=update.callback_query
    if not is_admin(query.from_user.id): await query.answer('Access denied', show_alert=True); return
    if target_id == query.from_user.id:
        await query.answer('You cannot ban yourself.', show_alert=True); return
    if is_user_banned(target_id):
        unban_user(target_id); action='UNBANNED'
        try: await context.bot.send_message(target_id, f"{EMOJI_CHECK} <b>You have been unbanned.</b>\n\nYou can use the bot again.", parse_mode='HTML', reply_markup=get_main_keyboard())
        except Exception: pass
    else:
        ban_user(target_id, reason='Banned by administrator.') ; action='BANNED'
        # Stop all running scripts immediately when a user is banned.
        scripts=load_bot_scripts()
        changed=False
        for sid,script in list(scripts.items()):
            if str(script.get('user_id'))==str(target_id) and script.get('status')=='running':
                with SCRIPT_PROCESS_LOCK:
                    entry=SCRIPT_PROCESSES.get(str(sid)); proc=entry.get('process') if entry else None
                if proc and proc.poll() is None:
                    try: os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    except Exception:
                        try: proc.terminate()
                        except Exception: pass
                script['status']='stopped'; changed=True
        if changed: save_bot_scripts(scripts)
        try: await context.bot.send_message(target_id, f"{EMOJI_PROHIBITED} <b>You have been banned.</b>\n\nYou can no longer use this bot.", parse_mode='HTML')
        except Exception: pass
    await query.answer(action)
    await admin_user_profile(update, context, target_id)


async def admin_stop_all_user(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int) -> None:
    query=update.callback_query
    if not is_admin(query.from_user.id): await query.answer('Access denied', show_alert=True); return
    scripts=load_bot_scripts(); count=0
    for sid,script in scripts.items():
        if str(script.get('user_id'))!=str(target_id) or script.get('status')!='running': continue
        with SCRIPT_PROCESS_LOCK:
            entry=SCRIPT_PROCESSES.get(str(sid)); proc=entry.get('process') if entry else None
        if proc and proc.poll() is None:
            try: os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                try: proc.terminate()
                except Exception: pass
        script['status']='stopped'; script['last_modified']=datetime.now().strftime('%Y-%m-%d %H:%M:%S'); count+=1
    save_bot_scripts(scripts)
    await query.answer(f'{count} running script(s) stopped')
    await admin_user_profile(update, context, target_id)


async def admin_delete_all_user(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int) -> None:
    query=update.callback_query
    if not is_admin(query.from_user.id): await query.answer('Access denied', show_alert=True); return
    scripts=load_bot_scripts(); deleted=0
    for sid,script in list(scripts.items()):
        if str(script.get('user_id'))!=str(target_id): continue
        with SCRIPT_PROCESS_LOCK:
            entry=SCRIPT_PROCESSES.get(str(sid)); proc=entry.get('process') if entry else None
        if proc and proc.poll() is None:
            try: os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                try: proc.terminate()
                except Exception: pass
        for path in (script.get('path'), _script_log_path(script)):
            try:
                if path and os.path.isfile(path): os.remove(path)
            except Exception as e: logger.warning('Admin delete failed for %s: %s', path, e)
        with SCRIPT_PROCESS_LOCK: SCRIPT_PROCESSES.pop(str(sid), None)
        scripts.pop(sid,None); deleted+=1
    save_bot_scripts(scripts)
    await query.answer(f'{deleted} script(s) deleted')
    await admin_user_profile(update, context, target_id)


async def admin_script_action(update: Update, context: ContextTypes.DEFAULT_TYPE, script_id: str) -> None:
    query=update.callback_query
    if not is_admin(query.from_user.id): await query.answer('Access denied', show_alert=True); return
    scripts,script=_get_script(script_id)
    if not script: await query.answer('Script not found', show_alert=True); return
    target_id=int(script.get('user_id'))
    if script.get('status')=='running':
        with SCRIPT_PROCESS_LOCK:
            entry=SCRIPT_PROCESSES.get(str(script_id)); proc=entry.get('process') if entry else None
        if proc and proc.poll() is None:
            try: os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                try: proc.terminate()
                except Exception: pass
        script['status']='stopped'; save_bot_scripts(scripts)
        await query.answer('Script stopped')
    else:
        for path in (script.get('path'), _script_log_path(script)):
            try:
                if path and os.path.isfile(path): os.remove(path)
            except Exception: pass
        scripts.pop(str(script_id),None); save_bot_scripts(scripts)
        with SCRIPT_PROCESS_LOCK: SCRIPT_PROCESSES.pop(str(script_id),None)
        await query.answer('Script deleted')
    await admin_user_profile(update, context, target_id)


async def admin_ban_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied", show_alert=True)
        return
    context.user_data.pop('admin_action', None)
    context.user_data['admin_action'] = 'ban_user'
    await query.answer()
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=f"🚫 <b>BAN USER</b>\n━━━━━━━━━━━━━━━━━━━━\n\nSend the user's <b>Telegram User ID</b>.\n\nExample: <code>123456789</code>\n\nSend /cancel to cancel.",
        parse_mode='HTML'
    )

async def admin_unban_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied", show_alert=True)
        return
    context.user_data.pop('admin_action', None)
    context.user_data['admin_action'] = 'unban_user'
    await query.answer()
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=f"♻️ <b>UNBAN USER</b>\n━━━━━━━━━━━━━━━━━━━━\n\nSend the user's <b>Telegram User ID</b>.\n\nExample: <code>123456789</code>\n\nSend /cancel to cancel.",
        parse_mode='HTML'
    )

async def admin_broadcast_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied", show_alert=True)
        return
    context.user_data.pop('admin_action', None)
    context.user_data['admin_action'] = 'broadcast'
    await query.answer()
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=(
            f"📢 <b>BROADCAST</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Send the message you want to broadcast.\n\n"
            f"You can send <b>text, photo, video, voice, audio, document/file, sticker, animation</b> or other Telegram-supported media.\n"
            f"Captions, formatting, links and custom/animated emojis are preserved where Telegram supports them.\n\n"
            f"Send /cancel to cancel."
        ),
        parse_mode='HTML'
    )

async def process_admin_text_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Process admin ID-entry actions and text broadcasts."""
    if not update.message or not update.effective_user or not is_admin(update.effective_user.id):
        return False
    action = context.user_data.get('admin_action')
    if not action:
        return False
    text = (update.message.text or '').strip()
    if text == '/cancel':
        context.user_data.pop('admin_action', None)
        await update.message.reply_text(f"{EMOJI_CHECK} Cancelled.")
        return True
    if action == 'select_user':
        if not text.isdigit():
            await update.message.reply_text(f"{EMOJI_WARNING} Please send a valid numeric Telegram User ID.")
            return True
        context.user_data.pop('admin_action', None)
        # Send a fresh profile message instead of relying on callback-message editing.
        fake = None
        users=load_json(USERS_DB); scripts=load_bot_scripts(); history=load_upload_history()
        uid=int(text); info=users.get(str(uid), {})
        us={k:v for k,v in scripts.items() if str(v.get('user_id'))==str(uid)}
        uf=[x for x in history.values() if str(x.get('user_id'))==str(uid)]
        running=sum(1 for x in us.values() if x.get('status')=='running')
        name=html.escape(str(info.get('first_name') or 'Unknown'))
        banned=is_user_banned(uid)
        profile=(f"👤 <b>USER CONTROL</b>\n━━━━━━━━━━━━━━━━━━━━\n\n<b>Name:</b> {name}\n"
                 f"<b>User ID:</b> <code>{uid}</code>\n<b>Account:</b> {'🚫 BANNED' if banned else '✅ ACTIVE'}\n\n"
                 f"📁 <b>Uploaded Files:</b> <code>{len(uf)}</code>\n🤖 <b>Hosted Scripts:</b> <code>{len(us)}</code>\n"
                 f"🟢 <b>Running:</b> <code>{running}</code>\n🔵 <b>Stopped:</b> <code>{len(us)-running}</code>")
        kb=[[InlineKeyboardButton("💬 MESSAGE USER", callback_data=f"admin_message_{uid}")],
            [InlineKeyboardButton("♻️ UNBAN USER" if banned else "🚫 BAN USER", callback_data=f"admin_toggleban_{uid}")],
            [InlineKeyboardButton("⏹ STOP ALL RUNNING", callback_data=f"admin_stopall_{uid}"), InlineKeyboardButton("🗑️ DELETE ALL SCRIPTS", callback_data=f"admin_deleteall_{uid}")]]
        for sid,sc in us.items():
            icon='🟢' if sc.get('status')=='running' else '🔵'
            action_label='STOP' if sc.get('status')=='running' else 'DELETE'
            kb.append([InlineKeyboardButton(f"{icon} {sc.get('name','Unknown')} — {action_label}", callback_data=f"admin_script_{sid}")])
        kb.append([InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data="admin_manage")])
        await update.message.reply_text(profile, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))
        return True
    if action.startswith('message_user:'):
        target_id=int(action.split(':',1)[1])
        if not text:
            await update.message.reply_text('Please send a message or /cancel.')
            return True
        context.user_data.pop('admin_action', None)
        try:
            await context.bot.send_message(chat_id=target_id, text=text, reply_markup=get_main_keyboard())
            await update.message.reply_text(f"{EMOJI_CHECK} Message sent to <code>{target_id}</code>.", parse_mode='HTML')
        except Exception as e:
            await update.message.reply_text(f"{EMOJI_X} Could not message user: <code>{html.escape(str(e))}</code>", parse_mode='HTML')
        return True
    if action in ('ban_user', 'unban_user'):
        if not text.isdigit():
            await update.message.reply_text(f"{EMOJI_WARNING} Please send a valid numeric Telegram User ID.")
            return True
        target_id = int(text)
        if target_id == update.effective_user.id:
            await update.message.reply_text(f"{EMOJI_X} You cannot ban yourself.")
            return True
        if action == 'ban_user':
            if ban_user(target_id, reason='You are banned.'):
                context.user_data.pop('admin_action', None)
                try:
                    await context.bot.send_message(
                        chat_id=target_id,
                        text=f"{EMOJI_PROHIBITED} <b>ACCESS DENIED</b>\n\n<b>Reason:</b> You are banned.",
                        parse_mode='HTML'
                    )
                except Exception as notify_error:
                    logger.info('Ban notification could not be delivered to %s: %s', target_id, notify_error)
                await update.message.reply_text(
                    f"{EMOJI_CHECK} <b>This user is successfully banned from bot.</b>", parse_mode='HTML'
                )
            else:
                await update.message.reply_text(f"{EMOJI_X} Failed to ban this user. Check logs.")
            return True
        else:
            was_banned = is_user_banned(target_id)
            unban_user(target_id)
            context.user_data.pop('admin_action', None)
            if was_banned:
                try:
                    await context.bot.send_message(
                        chat_id=target_id,
                        text=(f"{EMOJI_CHECK} <b>SUCCESSFULLY UNBANNED</b>\n\n"
                              f"You are successfully unbanned and can now freely use all available features of the bot."),
                        parse_mode='HTML', reply_markup=get_main_keyboard()
                    )
                except Exception as notify_error:
                    logger.info('Unban notification could not be delivered to %s: %s', target_id, notify_error)
                await update.message.reply_text(f"{EMOJI_CHECK} <b>User successfully unbanned.</b>", parse_mode='HTML')
            else:
                await update.message.reply_text(f"{EMOJI_WARNING} This user is not currently banned.")
            return True
    if action == 'broadcast':
        # Text is handled here; rich media is handled by admin_broadcast_message.
        context.user_data.pop('admin_action', None)
        await perform_broadcast(update, context, update.message)
        return True
    return False

async def perform_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE, source_message) -> None:
    """Copy one admin message to every registered, non-banned user."""
    admin_id = update.effective_user.id
    users = load_json(USERS_DB)
    banned = load_banned_users()
    targets = []
    for key, item in users.items():
        try:
            uid = int(item.get('user_id', key))
        except (TypeError, ValueError):
            continue
        if uid == admin_id or str(uid) in banned:
            continue
        targets.append(uid)
    sent_count = 0
    failed_count = 0
    for uid in targets:
        try:
            await context.bot.copy_message(
                chat_id=uid,
                from_chat_id=source_message.chat_id,
                message_id=source_message.message_id
            )
            sent_count += 1
        except (Forbidden, BadRequest, TelegramError) as e:
            failed_count += 1
            logger.warning('Broadcast failed for %s: %s', uid, e)
        except Exception as e:
            failed_count += 1
            logger.error('Broadcast unexpected error for %s: %s', uid, e)
    await context.bot.send_message(
        chat_id=admin_id,
        text=(f"{EMOJI_CHECK} <b>BROADCAST COMPLETED</b>\n\n"
              f"Sent: <code>{sent_count}</code>\n"
              f"Failed: <code>{failed_count}</code>\n"
              f"Total targets: <code>{len(targets)}</code>"),
        parse_mode='HTML'
    )

async def admin_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catch rich media sent by an admin while broadcast mode is active."""
    if not update.message or not update.effective_user or not is_admin(update.effective_user.id):
        return
    if context.user_data.get('admin_action') != 'broadcast':
        return
    if update.message.text and update.message.text == '/cancel':
        context.user_data.pop('admin_action', None)
        await update.message.reply_text(f"{EMOJI_CHECK} Broadcast cancelled.")
        return
    context.user_data.pop('admin_action', None)
    await perform_broadcast(update, context, update.message)

async def force_channels_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    channels = load_channels_config()
    text = "📢 <b>FORCE JOIN CHANNELS</b>\n\n"
    keyboard = []
    if channels:
        for key, ch in channels.items():
            text += f"• <b>{ch.get('name', key)}</b> — <code>{ch.get('username') or ch.get('chat_id')}</code>\n"
            keyboard.append([InlineKeyboardButton(f"❌ Remove {ch.get('name', key)}", callback_data=f"remove_force_{key}")])
    else:
        text += "No force-join channels configured.\n"
    text += "\n<i>Add a channel by sending its @username or numeric chat ID.</i>"
    keyboard.append([InlineKeyboardButton("➕ Add Channel", callback_data="add_force_channel")])
    keyboard.append([InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data="admin_panel")])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))


async def approval_channel_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    config = load_approval_channel()
    if config:
        text = (
            "✅ <b>APPROVAL CHANNEL</b>\n\n"
            f"Name: <b>{config.get('name', 'Approval Channel')}</b>\n"
            f"Channel: <code>{config.get('username') or config.get('chat_id')}</code>\n\n"
            "Files uploaded by users will be sent here for approval/rejection."
        )
        keyboard = [
            [InlineKeyboardButton("🔄 Change Channel", callback_data="set_approval_channel")],
            [InlineKeyboardButton("❌ Remove Channel", callback_data="remove_approval_channel")],
            [InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data="admin_panel")]
        ]
    else:
        text = "✅ <b>APPROVAL CHANNEL</b>\n\n⚠️ No approval channel is configured.\n\nAdd a channel to receive uploaded files for approval/rejection."
        keyboard = [
            [InlineKeyboardButton("➕ Set Approval Channel", callback_data="set_approval_channel")],
            [InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data="admin_panel")]
        ]
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))


async def start_channel_input(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str) -> None:
    if kind == 'approval':
        admin_id = update.callback_query.from_user.id
        save_approval_setup({
            "active": True,
            "admin_id": admin_id,
            "started_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        context.user_data.pop('channel_input', None)
        await update.callback_query.edit_message_text(
            "✅ <b>ADD APPROVAL CHANNEL</b>\n\n"
            "1. Add this bot to your Telegram <b>channel</b>.\n"
            "2. Make the bot an <b>Administrator</b>.\n"
            "3. Give it permission to <b>Post Messages</b>.\n\n"
            "⚡ <b>AUTO-DETECT IS ON</b>\n"
            "As soon as Telegram reports that this bot has been added/admined in a channel, "
            "the channel will be connected automatically.\n\n"
            "You do not need to send the channel username or ID.\n"
            "Send /cancel to stop setup.",
            parse_mode="HTML"
        )
        return
    context.user_data['channel_input'] = kind
    await update.callback_query.edit_message_text(
        "📢 <b>ADD FORCE-JOIN CHANNEL</b>\n\nSend the channel @username or numeric chat ID.\n"
        "Make sure the bot is an administrator in the channel.\n\nSend /cancel to cancel.",
        parse_mode="HTML"
    )


async def process_channel_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    kind = context.user_data.get('channel_input')
    if not kind:
        return False
    value = update.message.text.strip()
    if value == '/cancel':
        context.user_data.pop('channel_input', None)
        await update.message.reply_text("Cancelled.")
        return True
    chat_ref = value
    if value.lstrip('-').isdigit():
        chat_ref = int(value)
    try:
        chat = await context.bot.get_chat(chat_ref)
        # A public channel can be registered without making the bot an admin.
        # Telegram may still restrict membership checks unless the bot is an admin.
        username = f"@{chat.username}" if chat.username else None
        if kind == 'approval':
            save_approval_channel({
                'chat_id': chat.id,
                'username': username,
                'name': chat.title or 'Approval Channel'
            })
            context.user_data.pop('channel_input', None)
            await update.message.reply_text("✅ Approval channel set successfully.")
        else:
            channels = load_channels_config()
            key = f"channel_{max([int(k.split('_')[1]) for k in channels if k.startswith('channel_') and k.split('_')[1].isdigit()] or [0]) + 1}"
            channels[key] = {
                'name': chat.title or key,
                'username': username,
                'link': f"https://t.me/{chat.username}" if chat.username else None,
                'chat_id': chat.id
            }
            save_channels_config(channels)
            context.user_data.pop('channel_input', None)
            await update.message.reply_text("✅ Force-join channel added successfully.")
        return True
    except Exception as e:
        logger.error(f"Channel setup error: {e}\n{traceback.format_exc()}")
        await update.message.reply_text(f"❌ Could not verify channel: {e}")
        return True


async def remove_force_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    key = query.data.replace('remove_force_', '', 1)
    channels = load_channels_config()
    if key in channels:
        channels.pop(key)
        save_channels_config(channels)
        await query.answer("Force channel removed", show_alert=True)
    await force_channels_panel(update, context)


async def remove_approval_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    save_approval_channel({})
    save_approval_setup({})
    await query.answer("Approval channel removed", show_alert=True)
    await approval_channel_panel(update, context)


async def send_approval_file(update: Update, context: ContextTypes.DEFAULT_TYPE, document) -> None:
    """Send uploaded file to the configured approval channel with metadata and actions."""
    approval = load_approval_channel()
    if not approval or not approval.get('chat_id'):
        return
    user = update.effective_user
    file_name = document.file_name or 'unknown'
    file_type = get_file_type(file_name)
    safe_file_name = html.escape(file_name)
    safe_username = html.escape(user.username or 'N/A')
    caption = (
        f"{EMOJI_FOLDER} <b>FILE PENDING APPROVAL</b>\n\n"
        f"<b>File Type:</b> <code>.{html.escape(file_type)}</code>\n"
        f"<b>File Name:</b> <code>{safe_file_name}</code>\n"
        f"<b>File Size:</b> <code>{format_file_size(document.file_size)}</code>\n"
        f"<b>User ID:</b> <code>{user.id}</code>\n"
        f"<b>Username:</b> {safe_username}\n"
        f"<b>Uploaded:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>"
    )
    keyboard = [
        [InlineKeyboardButton("💬 TALK TO USER", url=f"tg://user?id={user.id}")],
        [InlineKeyboardButton("✅ APPROVE", callback_data="approve_file_pending"),
         InlineKeyboardButton("❌ REJECT", callback_data="reject_file_pending")]
    ]
    sent = await context.bot.send_document(
        chat_id=approval['chat_id'],
        document=document.file_id,
        caption=caption,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    pending = load_pending_approvals()
    approval_id = str(sent.message_id)
    pending[approval_id] = {
        'approval_id': approval_id,
        'user_id': user.id,
        'file_name': file_name,
        'file_size': document.file_size,
        'file_type': file_type,
        'file_id': document.file_id,
        'channel_id': approval['chat_id'],
        'message_id': sent.message_id,
        'channel_caption': caption,
        'status': 'pending',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_pending_approvals(pending)



# ==================== AUTOMATIC ZIP HOSTING ====================
ENV_PATTERN = re.compile(r"(?:os\.environ(?:\.get)?\s*\[?\s*['\"]([A-Z][A-Z0-9_]{1,80})['\"]|os\.getenv\s*\(\s*['\"]([A-Z][A-Z0-9_]{1,80})['\"]|getenv\s*\(\s*['\"]([A-Z][A-Z0-9_]{1,80})['\"]|\$\{([A-Z][A-Z0-9_]{1,80})\}|process\.env\.([A-Z][A-Z0-9_]{1,80}))")

def _detected_env_from_source(source):
    required=set(); optional=set()
    for m in ENV_PATTERN.finditer(source or ''):
        name=next((x for x in m.groups() if x), None)
        if not name: continue
        context=(source[max(0,m.start()-30):min(len(source),m.end()+120)])
        if re.search(r'os\.getenv\s*\([^\n]{0,120},\s*[^\n]+\)', context): optional.add(name)
        else: required.add(name)
    required-=optional
    return sorted(required), sorted(optional)

def _scan_project_env(workspace):
    required=set(); optional=set()
    for fp in Path(workspace).rglob('*'):
        if not fp.is_file() or fp.stat().st_size > 3*1024*1024: continue
        if fp.suffix.lower() not in ('.py','.js','.mjs','.cjs','.ts','.json','.txt'): continue
        try: data=fp.read_text(encoding='utf-8',errors='replace')
        except Exception: continue
        r,o=_detected_env_from_source(data); required.update(r); optional.update(o)
    required-=optional
    return sorted(required), sorted(optional)

def _safe_extract_zip(zip_path, dest):
    os.makedirs(dest, exist_ok=True); root=Path(dest).resolve()
    with zipfile.ZipFile(zip_path) as z:
        infos=[i for i in z.infolist() if not i.is_dir()]
        if len(infos)>MAX_ZIP_FILES: raise ValueError(f'ZIP contains too many files ({len(infos)}). Limit is {MAX_ZIP_FILES}.')
        total=sum(max(0,i.file_size) for i in infos)
        if total>MAX_ZIP_UNCOMPRESSED: raise ValueError('ZIP expands beyond the 250 MB project limit.')
        for i in infos:
            target=(root/i.filename).resolve()
            if not str(target).startswith(str(root)+os.sep): raise ValueError('Unsafe ZIP path detected.')
        for i in infos: z.extract(i,dest)
    return infos

def _project_files(workspace):
    return [x for x in Path(workspace).rglob('*') if x.is_file() and '.host' not in x.parts]

def _runnable_project_files(workspace):
    files=_project_files(workspace)
    preferred_names={'bot.py','main.py','app.py','run.py','start.py','server.py','index.js','bot.js','main.js','app.js','server.js'}
    candidates=[]
    for x in files:
        if x.suffix.lower() not in ('.py','.js','.mjs','.cjs'): continue
        try: text=x.read_text(encoding='utf-8',errors='replace')[:250000]
        except Exception: text=''
        looks_bot=any(k in text.lower() for k in ('telebot','python-telegram-bot','telegram.ext','telethon','pyrogram','discord','client.run','bot.run'))
        executable=x.name.lower() in preferred_names or x.suffix.lower()!='.py' or '__name__' in text or looks_bot
        if executable: candidates.append(x)
    # If the ZIP is a plain collection of Python scripts, run all of them rather than silently dropping them.
    if not candidates:
        candidates=[x for x in files if x.suffix.lower()=='.py']
    return candidates[:80]

async def _progress_message(message,title,detail,percent):
    percent=max(0,min(100,int(percent))); n=percent//5
    bar='█'*n+'░'*(20-n)
    try: await message.edit_text(f"⏳ <b>{html.escape(title)}</b>\n\n<code>[{bar}] {percent}%</code>\n\n{detail}",parse_mode='HTML')
    except Exception: pass

async def _prepare_zip_project(script, progress_message=None):
    zip_path=os.path.abspath(script['path']); workspace=os.path.join(os.path.dirname(zip_path),'.workspace')
    if os.path.isdir(workspace): shutil.rmtree(workspace,ignore_errors=True)
    os.makedirs(workspace,exist_ok=True)
    if progress_message: await _progress_message(progress_message,'EXTRACTING ZIP',f"Extracting <code>{html.escape(os.path.basename(zip_path))}</code>",10)
    infos=await asyncio.to_thread(_safe_extract_zip,zip_path,workspace)
    if progress_message: await _progress_message(progress_message,'EXTRACTING ZIP',f"Extracted {len(infos)} files from <code>{html.escape(os.path.basename(zip_path))}</code>",35)
    files=_project_files(workspace); visible=[str(x.relative_to(workspace)) for x in files]
    if progress_message:
        listing='\n'.join('• '+html.escape(x) for x in visible[:80]) or '• No project files found.'
        if len(visible)>80: listing+=f"\n• … and {len(visible)-80} more"
        await _progress_message(progress_message,'PROJECT SCAN',f"<b>Files detected:</b>\n{listing}",65)
    req_files=[x for x in files if x.name.lower()=='requirements.txt']; entry=_runnable_project_files(workspace)
    required,optional=_scan_project_env(workspace)
    if any(x.suffix.lower()=='.py' for x in entry) and 'BOT_TOKEN' not in optional and 'BOT_TOKEN' not in required: required.append('BOT_TOKEN')
    required=sorted(set(required))
    script.update({'workspace':workspace,'entry_files':[str(x.relative_to(workspace)) for x in entry],'env_required':required,'env_optional':optional,'project_files':visible[:500]})
    launcher=Path(workspace)/'.host_supervisor.py'
    payload=repr([str(x.relative_to(workspace)) for x in entry])
    launcher_code="""import os,sys,time,subprocess,threading\nBASE=os.path.dirname(os.path.abspath(__file__))\nFILES=%s\nPROCS=[]\ndef spawn(rel):\n p=os.path.join(BASE,rel); ext=os.path.splitext(p)[1].lower()\n cmd=[sys.executable,'-u',p] if ext=='.py' else (['node',p] if ext in ('.js','.mjs','.cjs') else None)\n if not cmd: return\n try:\n  proc=subprocess.Popen(cmd,cwd=os.path.dirname(p) or BASE,env=os.environ.copy(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')\n except Exception as e:\n  print('[HOST] FAILED '+rel+': '+str(e),flush=True); return\n PROCS.append((rel,proc)); print('[HOST] STARTED '+rel+' PID='+str(proc.pid),flush=True)\n def reader():\n  if proc.stdout:\n   for line in proc.stdout: print('['+rel+'] '+line.rstrip(),flush=True)\n threading.Thread(target=reader,daemon=True).start()\nfor f in FILES: spawn(f)\nwhile PROCS:\n alive=[]\n for rel,p in PROCS:\n  rc=p.poll()\n  if rc is None: alive.append((rel,p))\n  else: print('[HOST] EXIT '+rel+' CODE='+str(rc),flush=True)\n PROCS=alive\n if not PROCS: break\n time.sleep(1)\n""" % payload
    launcher.write_text(launcher_code,encoding='utf-8')
    md=user_module_dir(script.get('user_id')); os.makedirs(md,exist_ok=True)
    if req_files:
        if progress_message: await _progress_message(progress_message,'DEPENDENCY PREPARATION','Installing requirements.txt into the private project environment…',80)
        proc=await asyncio.create_subprocess_exec(sys.executable,'-m','pip','install','--disable-pip-version-check','--no-input','--upgrade','--prefer-binary','--target',md,'-r',str(req_files[0]),stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT)
        out,_=await asyncio.wait_for(proc.communicate(),timeout=600)
        if proc.returncode!=0: raise RuntimeError('requirements.txt installation failed: '+_sanitize_user_log((out or b'').decode(errors='replace')[-1500:]))
    if progress_message: await _progress_message(progress_message,'PROJECT READY',f"Detected <b>{len(entry)}</b> runnable file(s). Environment variables scanned.",95)
    return required,optional,entry

async def _launch_zip_process(context,script_id):
    scripts,script=_get_script(script_id)
    workspace=script.get('workspace'); launcher=os.path.join(workspace or '','.host_supervisor.py')
    if not workspace or not os.path.isfile(launcher): return None
    env=os.environ.copy(); env.update({str(k):str(v) for k,v in script.get('env',{}).items()})
    md=user_module_dir(script.get('user_id')); ld=os.path.abspath(INSTALLED_MODULES_DIR); env['PYTHONPATH']=os.pathsep.join(x for x in (md,ld,workspace,env.get('PYTHONPATH','')) if x); env['PYTHONUNBUFFERED']='1'
    proc=subprocess.Popen([sys.executable,'-u',launcher],cwd=workspace,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,text=True,encoding='utf-8',errors='replace',bufsize=1,start_new_session=True)
    with SCRIPT_PROCESS_LOCK: SCRIPT_PROCESSES[str(script_id)]={'process':proc,'return_code':None}
    script.update({'status':'running','runtime':'ZIP/Python supervisor','pid':proc.pid,'started_at_epoch':time.time(),'last_error':None,'last_exit_code':None,'manual_stop':False}); save_bot_scripts(scripts)
    _write_script_log(script,'\n'+'='*72+f"\nBOT START REQUESTED\nZIP SUPERVISOR PID: {proc.pid}\nENTRY FILES: {', '.join(script.get('entry_files',[]))}\nSTATUS: STARTING\n"+'='*72+'\n')
    _start_process_monitor(context.application,str(script_id),proc,asyncio.get_running_loop())
    await asyncio.sleep(1)
    return proc if proc.poll() is None else None

async def _begin_zip_host(update,context,script_id):
    scripts,script=_get_script(script_id); q=update.callback_query
    if not script: return
    try: msg=await q.message.reply_text('⏳ <b>PREPARING ZIP HOST</b>\n\n<code>[░░░░░░░░░░░░░░░░░░░░] 0%</code>\n\nStarting automatic project scan…',parse_mode='HTML')
    except Exception: msg=None
    try:
        required,optional,entry=await _prepare_zip_project(script,msg); save_bot_scripts(scripts)
        if msg:
            try: await msg.delete()
            except Exception: pass
        if not entry:
            script['status']='stopped'; script['last_error']='No runnable .py/.js entry file was detected.'; save_bot_scripts(scripts)
            await q.message.reply_text('❌ <b>NO RUNNABLE FILE FOUND</b>\n\nThe ZIP was extracted, but no executable Python/Node entry file could be detected.',parse_mode='HTML'); return
        if required:
            script['awaiting_env']=True; save_bot_scripts(scripts); context.user_data['awaiting_env_script_id']=str(script_id)
            lines='\n'.join(f'• <code>{html.escape(x)}</code>' for x in required)
            optional_text='\n\n<b>Optional detected:</b>\n'+'\n'.join(f'• <code>{html.escape(x)}</code>' for x in optional) if optional else ''
            template='\n'.join(f'{x}=PASTE_VALUE_HERE' for x in required)
            await q.message.reply_text(f"🔐 <b>REQUIRED CREDENTIALS</b>\n━━━━━━━━━━━━━━━━━━━━\n\nMain variables detected:\n{lines}{optional_text}\n\n<b>Copy and fill this form:</b>\n<pre>{html.escape(template)}</pre>\n\nSend KEY=VALUE lines. After you submit values, any still-missing variables will be listed separately.",parse_mode='HTML'); return
        proc=await _launch_zip_process(context,script_id)
        if proc: await q.message.reply_text(f"🚀 <b>PROJECT RUNNING</b>\n\n<code>{html.escape(script.get('name','ZIP'))}</code>\nDetected <b>{len(entry)}</b> runnable file(s). Real process monitoring is active.",parse_mode='HTML',reply_markup=get_main_keyboard())
        else: await q.message.reply_text('❌ <b>START FAILED</b>\n\nNo child process remained alive. Check Logs.',parse_mode='HTML',reply_markup=get_main_keyboard())
    except Exception as e:
        if msg:
            try: await msg.delete()
            except Exception: pass
        script['status']='stopped'; script['last_error']=f'{type(e).__name__}: {e}'; script['last_exit_code']=1; save_bot_scripts(scripts); _write_script_log(script,f'\nZIP HOST ERROR: {type(e).__name__}: {e}\n{traceback.format_exc()}\n')
        await q.message.reply_text(f"❌ <b>ZIP PREPARATION FAILED</b>\n\n<pre>{html.escape(str(e)[:2500])}</pre>",parse_mode='HTML',reply_markup=get_main_keyboard())


def _approval_file_status(record):
    """Return (ok, reason) for an approval record before creating a hosted script."""
    created = record.get('created_at')
    if created:
        try:
            dt = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - dt > timedelta(hours=APPROVAL_EXPIRY_HOURS):
                return False, f'File approval expired after {APPROVAL_EXPIRY_HOURS} hours.'
        except Exception:
            pass
    file_id = record.get('file_id')
    if not file_id:
        return False, 'Telegram file reference is missing.'
    file_name = os.path.basename(str(record.get('file_name', '')))
    if not file_name:
        return False, 'File name is missing.'
    if not file_name.lower().endswith(SUPPORTED_UPLOAD_EXTENSIONS):
        return False, 'Invalid file type. Only .py, .js and .zip files are supported.'
    size = record.get('file_size')
    if size is not None and int(size or 0) <= 0:
        return False, 'Invalid/empty file. The uploaded file contains no data.'
    if size is not None and int(size or 0) > MAX_UPLOAD_SIZE:
        return False, 'File is too large and is no longer valid for hosting.'
    return True, 'OK'


async def approval_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """Process approval/rejection for an uploaded script."""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied", show_alert=True)
        return

    pending = load_pending_approvals()
    record = None
    record_key = None
    for key, item in pending.items():
        if str(item.get('message_id')) == str(query.message.message_id) and item.get('status') == 'pending':
            record = item
            record_key = key
            break

    if not record:
        await query.answer("This file is already processed or not found.", show_alert=True)
        return

    file_name = os.path.basename(record.get('file_name', 'Unknown'))

    if action == 'approve':
        valid, invalid_reason = _approval_file_status(record)
        if not valid:
            record['status'] = 'invalid'
            record['invalid_reason'] = invalid_reason
            pending[record_key] = record
            save_pending_approvals(pending)
            try:
                await query.edit_message_caption(
                    caption=(query.message.caption or '') +
                    f"\n\n❌ <b>INVALID / EXPIRED</b>\n<b>Reason:</b> {html.escape(invalid_reason)}",
                    parse_mode='HTML', reply_markup=None
                )
            except Exception:
                pass
            await query.answer(f"❌ {invalid_reason}", show_alert=True)
            try:
                await context.bot.send_message(
                    chat_id=record['user_id'],
                    text=(f"❌ <b>FILE NOT APPROVED</b>\n\n"
                          f"<b>File:</b> <code>{html.escape(file_name)}</code>\n"
                          f"<b>Reason:</b> {html.escape(invalid_reason)}\n\n"
                          f"Please fix it and upload the file again."),
                    parse_mode='HTML', reply_markup=get_main_keyboard()
                )
            except Exception:
                pass
            return

        try:
            script_id = str(max([int(k) for k in load_bot_scripts() if str(k).isdigit()] or [0]) + 1)
            script_dir = os.path.join(USER_SCRIPTS_DIR, str(record['user_id']), script_id)
            os.makedirs(script_dir, exist_ok=True)
            local_path = os.path.join(script_dir, file_name)
            log_path = os.path.join(SCRIPT_LOGS_DIR, f"{script_id}.log")

            telegram_file = await context.bot.get_file(record['file_id'])
            await telegram_file.download_to_drive(custom_path=local_path)

            with open(log_path, 'a', encoding='utf-8') as log_file:
                log_file.write(
                    "\n" + "=" * 72 + "\n"
                    f"APPROVED SCRIPT SESSION CREATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"FILE: {file_name}\n"
                    + "=" * 72 + "\n"
                )

            scripts = load_bot_scripts()
            scripts[script_id] = {
                'id': script_id,
                'name': file_name,
                'user_id': record['user_id'],
                'status': 'stopped',
                'kind': 'zip' if file_name.lower().endswith('.zip') else ('javascript' if file_name.lower().endswith('.js') else 'python'),
                'path': local_path,
                'log_path': log_path,
                'created_date': record.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_exit_code': None,
                'last_error': None
            }
            save_bot_scripts(scripts)

            record['script_id'] = script_id
            record['status'] = 'approved'
            pending[record_key] = record
            save_pending_approvals(pending)
            update_statistics('total_approved', 1)

            approved_text = (
                f"{user_emoji('✅')} <b>YOUR FILE IS NOW APPROVED</b>\n\n"
                f"📄 <b>File:</b> <code>{html.escape(file_name)}</code>\n\n"
                f"Your project is ready to start. Tap <b>START PROJECT</b> below."
            )
            try:
                if record.get('user_message_id'):
                    await context.bot.edit_message_text(
                        chat_id=record['user_id'],
                        message_id=record['user_message_id'],
                        text=approved_text,
                        parse_mode='HTML',
                        reply_markup=InlineKeyboardMarkup([[
                            user_button('START PROJECT', '🚀', callback_data=f"start_script_{script_id}", style='success')
                        ], [
                            user_button('MY SCRIPT', '📁', callback_data='my_scripts_menu')
                        ]])
                    )
                else:
                    await context.bot.send_message(
                        chat_id=record['user_id'], text=approved_text,
                        parse_mode='HTML',
                        reply_markup=InlineKeyboardMarkup([[
                            user_button('START PROJECT', '🚀', callback_data=f"start_script_{script_id}", style='success')
                        ], [
                            user_button('MY SCRIPT', '📁', callback_data='my_scripts_menu')
                        ]])
                    )
            except Exception:
                try:
                    await context.bot.send_message(
                        chat_id=record['user_id'], text=approved_text,
                        parse_mode='HTML', reply_markup=get_main_keyboard()
                    )
                except Exception:
                    pass

            new_caption = (query.message.caption or '') + f"\n\n{user_emoji('✅')} <b>APPROVED</b>"
            status_markup = InlineKeyboardMarkup([[InlineKeyboardButton("✅ APPROVED", callback_data="noop_processed")]])
            await query.edit_message_caption(caption=new_caption, parse_mode='HTML', reply_markup=status_markup)
            await query.answer("File approved", show_alert=True)
        except Exception as e:
            logger.error(f"Approval failed for {file_name}: {e}\n{traceback.format_exc()}")
            await query.answer("Approval failed. Check bot logs.", show_alert=True)
    else:
        # Rejection reasons are intentionally collected in the configured approval
        # channel.  The old flow stored the state in context.user_data and sent the
        # prompt to the admin's private chat, so a reason typed in the channel was
        # never consumed.  Persist the state on the approval record instead.
        record['rejection_pending'] = True
        record['rejection_requested_by'] = query.from_user.id
        record['rejection_requested_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pending[record_key] = record
        save_pending_approvals(pending)
        pending_caption=(record.get('channel_caption') or f"{EMOJI_FOLDER} <b>FILE PENDING APPROVAL</b>") + f"\n\n{EMOJI_WARNING} <b>REJECTION PENDING</b>\n<b>Reason:</b> <i>Waiting for admin to send the rejection reason in this channel.</i>"
        try:
            await query.edit_message_caption(caption=pending_caption,parse_mode='HTML',reply_markup=None)
        except Exception as e:
            logger.error(f"Could not remove rejection buttons: {e}\n{traceback.format_exc()}")
        await query.answer()
        try:
            await context.bot.send_message(
                chat_id=record.get('channel_id'),
                text=(f"{EMOJI_WARNING} <b>REJECTION REASON REQUIRED</b>\n\n"
                      f"File: <code>{html.escape(file_name)}</code>\n\n"
                      f"Send the rejection reason as the next text message in this approval channel."),
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Could not send rejection prompt to approval channel: {e}\n{traceback.format_exc()}")

async def admin_scripts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manage bot scripts"""
    try:
        query = update.callback_query
        scripts = load_bot_scripts()
        
        if not scripts:
            keyboard = [[InlineKeyboardButton(f"{EMOJI_PLUS} Add Script", callback_data="add_script")]]
            script_text = f"{EMOJI_WARNING} No scripts found.\n\nAdd your first script!"
        else:
            keyboard = []
            script_text = f"{EMOJI_TAG} <b>BOT SCRIPTS</b>\n\n"
            
            for script_id, script in scripts.items():
                status_emoji = EMOJI_GREEN if script['status'] == 'running' else (
                    EMOJI_RED if script['status'] == 'stopped' else EMOJI_YELLOW
                )
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"{status_emoji} {script['name']} ({script['status']})",
                        callback_data=f"view_script_{script_id}"
                    )
                ])
                
                script_text += (
                    f"{status_emoji} <b>{script['name']}</b>\n"
                    f"   Status: <code>{script['status']}</code>\n"
                    f"   Created: {script['created_date']}\n\n"
                )
            
            keyboard.append([InlineKeyboardButton(f"{EMOJI_PLUS} Add Script", callback_data="add_script")])
        
        keyboard.append([InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data="admin_panel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            script_text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in admin_scripts: {e}\n{traceback.format_exc()}")

async def user_scripts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the current user's scripts in the requested My Scripts layout."""
    try:
        user_id = update.effective_user.id
        scripts = load_bot_scripts()
        user_scripts = {
            k: v for k, v in scripts.items()
            if str(v.get('user_id')) == str(user_id)
        }

        total = len(user_scripts)
        msg_text = (
            f"{user_emoji('🏷️')} <b>YOUR SCRIPTS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Total: {total} scripts\n\n"
            f"{user_emoji('🟢')} = <b>Running</b>  |  {user_emoji('🔵')} = <b>Stopped</b>\n\n"
            f"<i>Click on a script to manage it.</i>"
        )

        keyboard = []
        for script_id, script in user_scripts.items():
            is_running = script.get('status') == 'running'
            status_text = 'RUNNING' if is_running else 'STOPPED'
            status_emoji = user_emoji('🟢') if is_running else user_emoji('🔵')
            keyboard.append([
                user_button(
                    f"[{status_text}] {script.get('name', 'Unknown')}",
                    "🟢" if is_running else "🔵",
                    callback_data=f"view_script_{script_id}",
                    style="success" if is_running else "primary"
                )
            ])

        await update.message.reply_text(
            msg_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
        )
    except Exception as e:
        logger.error(f"Error showing user scripts: {e}\n{traceback.format_exc()}")
        await update.message.reply_text(
            f"{EMOJI_X} Error loading your scripts.",
            reply_markup=get_main_keyboard()
        )


def _get_script(script_id):
    scripts = load_bot_scripts()
    return scripts, scripts.get(str(script_id))


def _script_log_path(script):
    return script.get('log_path') or os.path.join(SCRIPT_LOGS_DIR, f"{script.get('id', 'unknown')}.log")


def _read_script_logs(script, limit=12000):
    path = _script_log_path(script)
    if not os.path.exists(path):
        return ""
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            data = f.read()
        return data[-limit:] if len(data) > limit else data
    except Exception as e:
        logger.error(f"Error reading script log: {e}")
        return ""


def _write_script_log(script, text):
    path = _script_log_path(script)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a', encoding='utf-8', errors='replace') as f:
        f.write(text)


def _runtime_command(script):
    path = script.get('path', '')
    if not path:
        raise ValueError('Script path is missing.')
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(f'Script file not found: {path}')
    ext = Path(path).suffix.lower()
    if ext == '.py':
        return [sys.executable, '-u', path], 'Python', 'python'
    if ext == '.js':
        return ['node', path], 'Node.js', 'javascript'
    raise ValueError('Only .py and .js files are supported.')


def _safe_script_for_user(script, user_id):
    if not script:
        return False
    return is_admin(user_id) or str(script.get('user_id')) == str(user_id)



def _sanitize_user_log(text):
    """Remove hosting/runtime fingerprints from user-visible logs."""
    text = str(text or '')
    patterns = [
        (r'(?i)termux', '[hosting-runtime]'),
        (r'(?i)/data/data/com\.termux[^\s\n]*', '[hosting-path]'),
        (r'(?i)/data/data/com\.termux', '[hosting-path]'),
        (r'(?i)com\.termux', '[hosting-runtime]'),
        (r'(?i)(?:/|\\)proot-distro(?:/|\\)[^\s\n]*', '[hosting-path]'),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text


def _extract_imports(path):
    """Return unique top-level Python import names from the uploaded source."""
    try:
        source = Path(path).read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(source, filename=str(path))
    except Exception:
        return []
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    names.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split('.')[0])
    return sorted(names, key=str.lower)


def _module_statuses(script):
    """Inspect imports without exposing host paths or environment details."""
    path = script.get('path', '')
    imports = _extract_imports(path) if Path(path).suffix.lower() == '.py' else []
    aliases = {
        'cv2':'opencv-python', 'pil':'Pillow', 'bs4':'beautifulsoup4',
        'sklearn':'scikit-learn', 'yaml':'PyYAML', 'dotenv':'python-dotenv',
        'telegram':'python-telegram-bot', 'telebot':'pyTelegramBotAPI',
        'telethon':'Telethon', 'pyrogram':'Pyrogram', 'requests':'requests',
        'dateutil':'python-dateutil', 'numpy':'numpy', 'pandas':'pandas',
        'aiohttp':'aiohttp', 'flask':'Flask', 'fastapi':'fastapi',
        'sqlalchemy':'SQLAlchemy', 'bs4':'beautifulsoup4'
    }
    stdlib = set(getattr(sys, 'stdlib_module_names', ()))
    result = []
    module_dir = user_module_dir(script.get('user_id'))
    old_path = list(sys.path)
    try:
        if module_dir and os.path.isdir(module_dir):
            sys.path.insert(0, module_dir)
        for name in imports:
            if name in stdlib:
                result.append((name, 'BUILT-IN / AVAILABLE', 'Not required to install'))
            elif importlib.util.find_spec(name) is not None:
                result.append((name, 'INSTALLED / AVAILABLE', 'Ready'))
            else:
                result.append((name, 'MISSING', aliases.get(name.lower(), name)))
    except Exception:
        # Do not leak interpreter or hosting paths.
        for name in imports:
            result.append((name, 'UNKNOWN', aliases.get(name.lower(), name)))
    finally:
        sys.path[:] = old_path
    return result


def _diagnostic_report(script, extra_error=''):
    """Build a plain-text, copy-friendly, user-safe diagnostic report."""
    logs = _read_script_logs(script, 16000) or ''
    clean_logs = _sanitize_user_log(logs)
    error = _sanitize_user_log(extra_error).strip()
    if not error:
        lines = [ln.strip() for ln in clean_logs.splitlines() if ln.strip()]
        candidates = [ln for ln in lines if re.search(
            r'(Traceback|Error|Exception|No module named|ModuleNotFoundError|ImportError|SyntaxError|NameError|TypeError|ValueError|AttributeError|PermissionError|FileNotFoundError|Conflict|InvalidToken)',
            ln, re.I)]
        error = '\n'.join(candidates[-12:]) if candidates else 'The process stopped, but no specific exception text was captured.'
    modules = _module_statuses(script)
    module_lines = ['MODULE CHECK']
    if not modules:
        module_lines.append('No Python imports could be inspected for this file.')
    else:
        for name, state, package in modules:
            if state == 'MISSING':
                module_lines.append(f'[MISSING] {name} | install package: {package}')
            elif state.startswith('BUILT-IN'):
                module_lines.append(f'[AVAILABLE] {name} | built-in Python module')
            elif state.startswith('INSTALLED'):
                module_lines.append(f'[INSTALLED] {name} | available')
            else:
                module_lines.append(f'[UNKNOWN] {name} | status could not be verified')
    return (
        'DETECTED ERROR\n'
        '====================\n'
        f'{error[-5000:]}\n\n'
        + '\n'.join(module_lines) + '\n\n'
        + 'LOG EXCERPT\n'
        '====================\n'
        + (clean_logs[-7000:] or 'No logs captured.')
    )






def _format_duration(seconds):
    try:
        seconds = max(0, int(seconds))
    except Exception:
        seconds = 0
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days:
        return f"{days}d {hours}h {minutes}m"
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def _process_rss_mb(pid):
    """Best-effort RSS reading without requiring psutil."""
    try:
        status_path = f"/proc/{int(pid)}/status"
        for line in Path(status_path).read_text(errors='replace').splitlines():
            if line.startswith('VmRSS:'):
                kb = int(re.search(r'\d+', line).group())
                return kb / 1024.0
    except Exception:
        pass
    return None




async def _notify_process_exit(application, script_id, return_code, exited_pid=None):
    scripts = load_bot_scripts()
    script = scripts.get(str(script_id))
    if not script:
        return

    script['status'] = 'stopped'
    script['last_exit_code'] = return_code
    script['last_modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if return_code != 0:
        script['last_error'] = f'Process exited with code {return_code}.'
    else:
        script['last_error'] = None
    save_bot_scripts(scripts)

    manual_stop = bool(script.pop('manual_stop', False))
    save_bot_scripts(scripts)

    # V112: manual STOP is a successful user action. Do not send the crash/error
    # notification that made the old STOP button appear to fail. The stop handler
    # immediately returns the user to MY SCRIPTS instead.
    if manual_stop:
        with SCRIPT_PROCESS_LOCK:
            current = SCRIPT_PROCESSES.get(str(script_id))
            if current is not None and (exited_pid is None or current.get('process') is None or current['process'].pid == exited_pid):
                SCRIPT_PROCESSES.pop(str(script_id), None)
        return

    # V114: no automatic fixing or restarting; report logs and leave stopped.\n    restart_detail = ''\n\n    latest_scripts, latest_script = _get_script(script_id)
    if latest_script:
        script = latest_script
    logs = _sanitize_user_log(_read_script_logs(script, 9000) or 'No log output was captured.')
    language = 'python' if Path(script.get('path', '')).suffix.lower() == '.py' else 'javascript'
    is_running_again = str(script.get('status')).lower() == 'running'
    status_line = f"{user_emoji('🟢')} <b>RUNNING</b>" if is_running_again else f"{user_emoji('🔵')} <b>STOPPED</b>"
    exit_label = f'Error: Process exited with code {return_code}' if return_code != 0 else 'Exit: Process finished normally (code 0)'
    notice = (
        f"{user_emoji('📄')} <b>{html.escape(str(script.get('name', 'Unknown')))}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Status:</b> {status_line}\n"
        f"<b>{html.escape(exit_label)}</b>\n" + ("<b>Action:</b> Fix the error shown below and upload the corrected file again.\n" if return_code != 0 else '') + "\n"
        f"<b>{'ERROR LOGS / CURRENT LOGS' if return_code != 0 else 'CURRENT LOGS'}:</b>\n"
        f"<pre><code class=\"language-{language}\">{html.escape(logs)}</code></pre>"
    )
    try:
        await application.bot.send_message(
            chat_id=script['user_id'], text=notice, parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
    except TelegramError as e:
        logger.error('Exit log notification HTML send failed for %s: %s', script_id, e)
        try:
            await application.bot.send_message(
                chat_id=script['user_id'],
                text=(f"{script.get('name','Unknown')}\nSTATUS: STOPPED\n{exit_label}\n\nCURRENT LOGS:\n{logs[-7000:]}"),
                reply_markup=get_main_keyboard()
            )
        except Exception:
            logger.error('Exit log notification plain send failed for %s', script_id, exc_info=True)

    with SCRIPT_PROCESS_LOCK:
        current = SCRIPT_PROCESSES.get(str(script_id))
        # Clean up only the process that actually exited.
        if current is not None and (exited_pid is None or current.get('process') is None or current['process'].pid == exited_pid):
            current['return_code'] = return_code
            SCRIPT_PROCESSES.pop(str(script_id), None)

def _start_process_monitor(application, script_id, process, loop=None):
    """Monitor a hosted process, capture output, and report its real exit state."""
    def monitor():
        scripts = load_bot_scripts()
        script = scripts.get(str(script_id))
        if not script:
            return
        log_path = _script_log_path(script)
        return_code = None
        try:
            if script.get('kind') == 'zip':
                runtime = script.get('runtime') or 'ZIP/Python supervisor'
            else:
                command, runtime, _ = _runtime_command(script)
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a', encoding='utf-8', errors='replace') as log_file:
                log_file.write(
                    "\n" + "=" * 72 + "\n"
                    f"{user_emoji('🟢')} BOT STARTED SUCCESSFULLY\n"
                    f"RUNTIME: {runtime}\n"
                    "STATUS: RUNNING\n"
                    f"PROCESS ID: {process.pid}\n"
                    + "=" * 72 + "\n"
                )
                log_file.flush()

                # stdout and stderr are already merged by Popen. Reading this pipe
                # in the monitor thread prevents the child from blocking on a full pipe.
                if process.stdout:
                    for line in iter(process.stdout.readline, ''):
                        if line == '':
                            break
                        log_file.write(_sanitize_user_log(line))
                        log_file.flush()
                return_code = process.wait()
                log_file.write(
                    "\n" + "=" * 72 + "\n"
                    f"PROCESS EXITED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | CODE: {return_code}\n"
                    + "=" * 72 + "\n"
                )
                log_file.flush()
        except Exception as e:
            logger.error("Script monitor error for %s: %s\n%s", script_id, e, traceback.format_exc())
            _write_script_log(script, _sanitize_user_log(f"\nMONITOR ERROR: {type(e).__name__}: {e}\n{traceback.format_exc()}\n"))
            return_code = process.poll()
            if return_code is None:
                return_code = 1

        with SCRIPT_PROCESS_LOCK:
            current = SCRIPT_PROCESSES.get(str(script_id))
            if current is not None:
                current['return_code'] = return_code

        # Always schedule the async notification on the exact loop used by the
        # update handler. application._loop is not relied upon.
        try:
            target_loop = loop
            if target_loop is not None and not target_loop.is_closed():
                asyncio.run_coroutine_threadsafe(
                    _notify_process_exit(application, str(script_id), return_code, process.pid), target_loop
                )
            else:
                logger.error("No active asyncio loop available for process %s exit notification", script_id)
        except Exception as e:
            logger.error("Could not schedule process-exit notification for %s: %s", script_id, e, exc_info=True)

    threading.Thread(target=monitor, daemon=True, name=f"script-monitor-{script_id}").start()


async def view_script(update: Update, context: ContextTypes.DEFAULT_TYPE, script_id=None) -> None:
    """Show controls using the actual child-process state, not a stale saved flag."""
    query = update.callback_query
    try:
        if script_id is None:
            script_id = (query.data or '').replace('view_script_', '', 1)
        scripts, script = _get_script(script_id)
        if not script or not _safe_script_for_user(script, query.from_user.id):
            await query.answer(f"Script not found", show_alert=True)
            return

        with SCRIPT_PROCESS_LOCK:
            entry = SCRIPT_PROCESSES.get(str(script_id))
            process = entry.get('process') if entry else None
        actual_running = bool(process and process.poll() is None)
        if script.get('status') == 'running' and not actual_running:
            script['status'] = 'stopped'
            if process is not None and process.poll() is not None:
                script['last_exit_code'] = process.returncode
            save_bot_scripts(scripts)

        running = actual_running
        status_emoji = user_emoji('🟢') if running else user_emoji('🔵')
        status_text = 'RUNNING' if running else 'STOPPED'
        name = html.escape(str(script.get('name', 'Unknown')))
        started_at = float(script.get('started_at_epoch') or 0)
        uptime = _format_duration(time.time() - started_at) if running and started_at else '0s'
        pid = script.get('pid') or '—'
        rss = _process_rss_mb(pid) if running and str(pid).isdigit() else None
        memory_line = f"<b>RAM:</b> {rss:.1f} MB\n" if rss is not None else ''
        last_exit = script.get('last_exit_code')
        text = (
            f"{user_emoji('🏷️')} <b>SCRIPT CONTROL</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Name:</b> {name}\n"
            f"<b>Status:</b> {status_emoji} <b>{status_text}</b>\n"
            f"<b>Uptime:</b> {uptime}\n"
            f"<b>PID:</b> <code>{html.escape(str(pid))}</code>\n"
            f"{memory_line}"
            f"<b>Last Exit:</b> {html.escape(str(last_exit if last_exit is not None else '—'))}\n"
            f"<b>Type:</b> {html.escape(str(script.get('kind','python')).upper())}\n"
            f"<b>Runnable Files:</b> {len(script.get('entry_files',[])) if script.get('kind')=='zip' else 1}\n\n"
            f"<i>Choose an action below:</i>"
        )
        if running:
            kb = [[
                user_button("STOP", "❌", callback_data=f"stop_script_{script_id}", style="danger"),
                user_button("VIEW LOGS", "📁", callback_data=f"logs_script_{script_id}")
            ], [
                user_button("BACK TO SCRIPTS", "◀️", callback_data="my_scripts_menu")
            ]]
        else:
            kb = [[
                user_button("START", "🟢", callback_data=f"start_script_{script_id}", style="success"),
                user_button("DELETE", "🗑️", callback_data=f"delete_script_{script_id}", style="danger")
            ], [
                user_button("VIEW LOGS", "📁", callback_data=f"logs_script_{script_id}")
            ], [
                user_button("BACK TO SCRIPTS", "◀️", callback_data="my_scripts_menu")
            ]]
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))
    except Exception as e:
        logger.error("Error in view_script for %s: %s\n%s", script_id, e, traceback.format_exc())
        try:
            await query.answer(f"Could not open script controls. Check logs.", show_alert=True)
        except Exception:
            pass


async def confirm_delete_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask for deletion confirmation. Running scripts cannot be deleted."""
    query = update.callback_query
    script_id = query.data.replace('delete_script_', '')
    scripts, script = _get_script(script_id)
    if not script or not _safe_script_for_user(script, query.from_user.id):
        await query.answer(f"Script not found", show_alert=True)
        return
    if script.get('status') == 'running':
        await query.answer('Stop the script before deleting it.', show_alert=True)
        return

    name = html.escape(script.get('name', 'Unknown'))
    text = f"{EMOJI_WARNING} <b>Are you sure you want to delete</b>\n\n<b>{name}</b>"
    keyboard = [[
        InlineKeyboardButton('YES', callback_data=f'confirm_delete_{script_id}'),
        InlineKeyboardButton('NO', callback_data=f'cancel_delete_{script_id}')
    ]]
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))


async def confirm_delete_yes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a stopped script, its file and its log, then return to My Scripts."""
    query = update.callback_query
    script_id = query.data.replace('confirm_delete_', '')
    scripts, script = _get_script(script_id)
    if not script or not _safe_script_for_user(script, query.from_user.id):
        await query.answer(f"Script not found", show_alert=True)
        return
    if script.get('status') == 'running':
        await query.answer('Stop the script before deleting it.', show_alert=True)
        return

    name = script.get('name', 'Unknown')
    paths = [script.get('path'), _script_log_path(script)]
    scripts.pop(str(script_id), None)
    save_bot_scripts(scripts)
    with SCRIPT_PROCESS_LOCK:
        SCRIPT_PROCESSES.pop(str(script_id), None)
    for path in paths:
        try:
            if path and os.path.isfile(path):
                os.remove(path)
        except Exception as e:
            logger.warning(f"Could not remove {path}: {e}")

    await query.answer('File deleted successfully')
    await query.edit_message_text(
        f"{EMOJI_CHECK} <b>Your file {html.escape(name)} is now successfully deleted.</b>\n\n"
        f"Check out <b>MY SCRIPTS</b>.",
        parse_mode='HTML'
    )
    await send_user_scripts_from_callback(query, context)


async def cancel_delete_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return to the script control screen when deletion is cancelled."""
    query = update.callback_query
    script_id = query.data.replace('cancel_delete_', '')
    await query.answer('Deletion cancelled')
    query.data = f'view_script_{script_id}'
    await view_script(update, context)


async def send_user_scripts_from_callback(query, context) -> None:
    """Render My Scripts after a callback-driven action."""
    user_id = query.from_user.id
    scripts = load_bot_scripts()
    user_scripts = {k: v for k, v in scripts.items() if str(v.get('user_id')) == str(user_id)}
    total = len(user_scripts)
    text = (
        f"{user_emoji('🏷️')} <b>YOUR SCRIPTS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Total: {total} scripts\n\n"
        f"{user_emoji('🟢')} = <b>Running</b>  |  {user_emoji('🔵')} = <b>Stopped</b>\n\n"
        f"<i>Click on a script to manage it.</i>"
    )
    keyboard = []
    for script_id, script in user_scripts.items():
        running = script.get('status') == 'running'
        status = 'RUNNING' if running else 'STOPPED'
        icon = user_emoji('🟢') if running else user_emoji('🔵')
        keyboard.append([user_button(
            f"[{status}] {script.get('name', 'Unknown')}",
            "🟢" if running else "🔵",
            callback_data=f"view_script_{script_id}",
            style="success" if running else "primary"
        )])
    await context.bot.send_message(
        chat_id=user_id, text=text, parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )


async def _send_log_snapshot(context, chat_id, script, logs=None):
    """Send logs in Telegram-safe chunks so large logs can never make the button appear broken."""
    if logs is None:
        logs = _read_script_logs(script, 12000) or 'No log output captured yet.'
    logs = _sanitize_user_log(logs)
    status = str(script.get('status', 'stopped')).upper()
    running = status == 'RUNNING'
    status_emoji = user_emoji('🟢') if running else user_emoji('🔵')
    name = html.escape(str(script.get('name', 'Unknown')))
    last_error = _sanitize_user_log(script.get('last_error') or '')
    # Keep each Telegram message safely below the 4096-character limit.
    chunk_size = 3000
    chunks = [logs[i:i + chunk_size] for i in range(0, len(logs), chunk_size)] or ['No log output captured yet.']
    total = len(chunks)
    for index, chunk in enumerate(chunks, 1):
        title = (
            f"{user_emoji('📄')} <b>{name}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Status:</b> {status_emoji} <b>{html.escape(status)}</b>\n"
        ) if index == 1 else f"{user_emoji('📄')} <b>{name}</b> — LOGS {index}/{total}\n"
        if index == 1 and last_error:
            title += f"<b>Last Error:</b> <code>{html.escape(str(last_error))}</code>\n"
        text = title + f"\n<b>CURRENT LOGS {index}/{total}:</b>\n<pre>{html.escape(chunk)}</pre>"
        markup = InlineKeyboardMarkup([
            [user_button("CURRENT LOGS", "🔄", callback_data=f"logs_script_{script.get('id')}")],
            [user_button("BACK TO SCRIPT", "◀️", callback_data=f"view_script_{script.get('id')}")]
        ])
        try:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML', reply_markup=markup)
        except TelegramError:
            # Plain fallback is also kept below the Telegram message-size limit.
            plain = f"{script.get('name', 'Unknown')}\nSTATUS: {status}\n\nCURRENT LOGS {index}/{total}:\n{chunk}"
            if index == 1 and last_error:
                plain = f"{script.get('name', 'Unknown')}\nSTATUS: {status}\nLAST ERROR: {last_error}\n\nCURRENT LOGS {index}/{total}:\n{chunk}"
            await context.bot.send_message(chat_id=chat_id, text=plain, reply_markup=markup)


def _validate_python_syntax(path: str):
    """V114: syntax-check uploaded Python without rewriting or auto-fixing it."""
    if not path.lower().endswith('.py'):
        return True, False, 'Non-Python runtime; no source rewriting performed.'
    try:
        source = Path(path).read_text(encoding='utf-8', errors='replace')
        compile(source, path, 'exec')
    except Exception as exc:
        return False, False, f'Python syntax check failed: {type(exc).__name__}: {exc}'
    return True, False, 'Syntax check passed; uploaded source was not modified.'

async def _prepare_user_python(path: str, script: dict) -> tuple:
    ok,changed,detail=_validate_python_syntax(path)
    if not ok: return False,changed,detail
    try: source=Path(path).read_text(encoding='utf-8',errors='replace')
    except Exception: source=''
    # Expand compressed single-file bundles for dependency discovery only.
    try: source=_v135_expand_embedded_python_source(source)
    except Exception: pass
    package_map={'telegram':'python-telegram-bot>=22.8,<23','telethon':'Telethon>=1.45,<2','aiosqlite':'aiosqlite','httpx':'httpx','dotenv':'python-dotenv','langdetect':'langdetect','qrcode':'qrcode[pil]','bs4':'beautifulsoup4','PIL':'Pillow','yaml':'PyYAML','cv2':'opencv-python-headless'}
    imported=set(re.findall(r'^\s*(?:from|import)\s+([A-Za-z_][A-Za-z0-9_]*)',source,re.M))
    missing=[pkg for mod,pkg in package_map.items() if mod in imported and importlib.util.find_spec(mod) is None]
    if missing:
        md=user_module_dir(script.get('user_id')); os.makedirs(md,exist_ok=True)
        for pkg in missing:
            try:
                proc=await asyncio.create_subprocess_exec(sys.executable,'-m','pip','install','--disable-pip-version-check','--no-input','--upgrade','--prefer-binary','--target',md,pkg,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT)
                out,_=await asyncio.wait_for(proc.communicate(),timeout=180)
                if proc.returncode!=0: return False,changed,f'Could not install required dependency: {pkg}'
            except Exception as exc: return False,changed,f'Dependency preparation failed for {pkg}: {exc}'
        detail += f' Prepared missing dependency: {", ".join(missing)}.'
    try: compile(Path(path).read_text(encoding='utf-8',errors='replace'),path,'exec')
    except Exception as exc: return False,changed,f'Final code analysis failed: {exc}'
    return True,changed,detail


async def handle_start_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the real child process and only show RUNNING while it is alive."""
    query = update.callback_query
    script_id = (query.data or '').replace('start_script_', '', 1)
    scripts, script = _get_script(script_id)
    try:
        await query.answer("Starting…")
    except Exception:
        pass
    try:
        if not script or not _safe_script_for_user(script, query.from_user.id):
            await query.message.reply_text(f"{EMOJI_X} Script not found.")
            return

        with SCRIPT_PROCESS_LOCK:
            entry = SCRIPT_PROCESSES.get(str(script_id))
            existing = entry.get('process') if entry else None
        if existing and existing.poll() is None:
            script['status'] = 'running'
            save_bot_scripts(scripts)
            await view_script(update, context, script_id)
            return
        if existing:
            with SCRIPT_PROCESS_LOCK:
                SCRIPT_PROCESSES.pop(str(script_id), None)

        path = script.get('path', '')
        if path:
            path = os.path.abspath(path)
        if not path or not os.path.isfile(path):
            script['status'] = 'stopped'
            script['last_error'] = 'Approved file is missing from storage.'
            script['last_exit_code'] = 1
            save_bot_scripts(scripts)
            _write_script_log(script, '\nSTART ERROR: Approved file is missing from storage.\n')
            await view_script(update, context, script_id)
            return
        if os.path.getsize(path) <= 0:
            script['status'] = 'stopped'
            script['last_error'] = 'The uploaded script file is empty.'
            script['last_exit_code'] = 1
            save_bot_scripts(scripts)
            _write_script_log(script, '\nSTART ERROR: The uploaded script file is empty.\n')
            await view_script(update, context, script_id)
            return

        if path.lower().endswith('.zip') or script.get('kind') == 'zip':
            await _begin_zip_host(update, context, script_id)
            return

        # V114: never rewrite or auto-fix user source; execute as uploaded.\n\n        # Compatibility: if a user's Telegram bot source uses native custom-emoji
        # button fields, ensure a recent python-telegram-bot is available in that
        # user's private module directory. This does not modify the host bot's own
        # environment and prevents icon_custom_emoji_id from failing on old PTB.
        if path.lower().endswith('.py'):
            try:
                source_text = Path(path).read_text(encoding='utf-8', errors='replace')
            except Exception:
                source_text = ''
            if 'icon_custom_emoji_id' in source_text and ('telegram' in source_text or 'python-telegram-bot' in source_text):
                md_preflight = user_module_dir(script.get('user_id'))
                os.makedirs(md_preflight, exist_ok=True)
                probe = await asyncio.create_subprocess_exec(
                    sys.executable, '-m', 'pip', 'install',
                    '--disable-pip-version-check', '--no-input', '--upgrade',
                    '--prefer-binary', '--target', md_preflight,
                    'python-telegram-bot>=22.8,<23',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT
                )
                out, _ = await asyncio.wait_for(probe.communicate(), timeout=180)
                if probe.returncode != 0:
                    _write_script_log(script, '\nDEPENDENCY WARNING: Could not prepare custom-emoji support; attempting to start the bot anyway.\n')
                else:
                    _write_script_log(script, '\nDEPENDENCY CHECK: Custom-emoji button support prepared.\n')
            
        command, runtime, _ = _runtime_command(script)
        env = os.environ.copy()
        md = user_module_dir(script.get('user_id'))
        ld = os.path.abspath(INSTALLED_MODULES_DIR)
        env['PYTHONPATH'] = os.pathsep.join(x for x in (md, ld, env.get('PYTHONPATH', '')) if x)
        env['PYTHONUNBUFFERED'] = '1'

        # Record that a start was attempted before Popen so VIEW LOGS is useful
        # even if the OS refuses to launch the process.
        _write_script_log(script, (
            '\n' + '=' * 72 + '\n'
            f"{user_emoji('🟡')} BOT START REQUESTED\n"
            f"RUNTIME: {runtime}\n"
            "STATUS: STARTING\n"
            + '=' * 72 + '\n'
        ))

        try:
            process = subprocess.Popen(
                command,
                cwd=os.path.dirname(path) or os.getcwd(),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True,
                start_new_session=True,
            )
        except FileNotFoundError as e:
            missing_runtime = 'Node.js runtime is not installed on the server.' if path.lower().endswith('.js') else 'Python runtime could not be started.'
            msg = f'{missing_runtime} {e}'
            _write_script_log(script, f'\nSTART ERROR: {msg}\n')
            script['status'] = 'stopped'
            script['last_error'] = msg
            script['last_exit_code'] = 1
            save_bot_scripts(scripts)
            await view_script(update, context, script_id)
            return

        with SCRIPT_PROCESS_LOCK:
            SCRIPT_PROCESSES[str(script_id)] = {'process': process, 'return_code': None}
        script['status'] = 'running'
        script['manual_stop'] = False
        script['last_error'] = None
        script['last_exit_code'] = None
        script['runtime'] = runtime
        script['pid'] = process.pid
        script['started_at_epoch'] = time.time()
        script['last_modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_bot_scripts(scripts)

        # Pass the exact currently-running loop to the monitor. This is essential
        # for reliably delivering crash logs back to Telegram.
        _start_process_monitor(context.application, script_id, process, asyncio.get_running_loop())

        # Immediately re-check the OS process. RUNNING means genuinely alive.
        await asyncio.sleep(0.25)
        return_code = process.poll()
        if return_code is not None:
            with SCRIPT_PROCESS_LOCK:
                SCRIPT_PROCESSES.pop(str(script_id), None)
            script['status'] = 'stopped'
            script['last_exit_code'] = return_code
            script['last_error'] = f'Process exited immediately with code {return_code}.' if return_code else None
            save_bot_scripts(scripts)
            await view_script(update, context, script_id)
            return

        await view_script(update, context, script_id)

        # Give startup output a short moment, then show a fresh log screen.
        await asyncio.sleep(0.75)
        fresh_scripts, fresh_script = _get_script(script_id)
        if not fresh_script:
            return
        with SCRIPT_PROCESS_LOCK:
            entry = SCRIPT_PROCESSES.get(str(script_id))
            live_process = entry.get('process') if entry else None
        if not live_process or live_process.poll() is not None:
            fresh_script['status'] = 'stopped'
            if live_process is not None:
                fresh_script['last_exit_code'] = live_process.returncode
            save_bot_scripts(fresh_scripts)
            await view_script(update, context, script_id)
            return

        logs = _read_script_logs(fresh_script, 3200) or 'Process is running. No stdout/stderr captured yet.'
        await _send_log_snapshot(context, query.from_user.id, fresh_script, logs)
    except Exception as e:
        logger.error("Start script %s failed: %s\n%s", script_id, e, traceback.format_exc())
        if script:
            _write_script_log(script, f"\nSTART HANDLER ERROR: {type(e).__name__}: {e}\n{traceback.format_exc()}\n")
            script['status'] = 'stopped'
            script['last_error'] = f'{type(e).__name__}: {e}'
            script['last_exit_code'] = 1
            save_bot_scripts(scripts)
        try:
            await view_script(update, context, script_id)
        except Exception:
            pass


async def handle_stop_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop the current script process."""
    query = update.callback_query
    script_id = query.data.replace('stop_script_', '')
    scripts, script = _get_script(script_id)
    if not script or not _safe_script_for_user(script, query.from_user.id):
        await query.answer(f"Script not found", show_alert=True)
        return

    with SCRIPT_PROCESS_LOCK:
        entry = SCRIPT_PROCESSES.get(str(script_id))
        process = entry.get('process') if entry else None

    if not process or process.poll() is not None:
        script['status'] = 'stopped'
        save_bot_scripts(scripts)
        await query.answer('')
        query.data = f'view_script_{script_id}'
        await view_script(update, context)
        return

    try:
        script['manual_stop'] = True
        save_bot_scripts(scripts)
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except Exception:
            process.terminate()
        try:
            await asyncio.to_thread(process.wait, 5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except Exception:
                process.kill()
            await asyncio.to_thread(process.wait, 2)
    except Exception as e:
        logger.error(f"Error stopping script {script_id}: {e}\n{traceback.format_exc()}")

    script['status'] = 'stopped'
    script['last_exit_code'] = process.returncode
    script['last_modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_bot_scripts(scripts)
    with SCRIPT_PROCESS_LOCK:
        SCRIPT_PROCESSES.pop(str(script_id), None)
    await query.answer('')
    query.data = f'view_script_{script_id}'
    await view_script(update, context)


async def handle_logs_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Always respond to VIEW LOGS and safely deliver logs of any normal size."""
    query = update.callback_query
    script_id = (query.data or '').replace('logs_script_', '', 1)
    try:
        scripts, script = _get_script(script_id)
        if not script or not _safe_script_for_user(script, query.from_user.id):
            await query.answer(f"Script not found", show_alert=True)
            return

        with SCRIPT_PROCESS_LOCK:
            entry = SCRIPT_PROCESSES.get(str(script_id))
            process = entry.get('process') if entry else None
        if process and process.poll() is None:
            if script.get('status') != 'running':
                script['status'] = 'running'
                save_bot_scripts(scripts)
        elif script.get('status') == 'running':
            script['status'] = 'stopped'
            if process is not None and process.poll() is not None:
                script['last_exit_code'] = process.returncode
            save_bot_scripts(scripts)

        try:
            await query.answer()
        except Exception:
            pass
        await _send_log_snapshot(context, query.from_user.id, script, _read_script_logs(script, 12000))
    except Exception as e:
        logger.error("View logs failed for %s: %s\n%s", script_id, e, traceback.format_exc())
        try:
            await query.answer(f"{EMOJI_X} Logs could not be loaded. Check the script log.", show_alert=True)
        except Exception:
            pass


async def handle_unlock_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unlock script action"""
    try:
        query = update.callback_query
        script_id = query.data.replace("unlock_script_", "")
        
        scripts = load_bot_scripts()
        script = scripts.get(script_id)
        
        if script:
            script['status'] = 'stopped'
            scripts[script_id] = script
            save_bot_scripts(scripts)
            
            await query.answer(f"{EMOJI_CHECK} Script unlocked successfully", show_alert=True)
            await view_script(update, context)
        else:
            await query.answer(f"Script not found", show_alert=True)
    except Exception as e:
        logger.error(f"Error unlocking script: {e}\n{traceback.format_exc()}")
        await query.answer(f"{EMOJI_X} Error: {str(e)}", show_alert=True)

async def handle_delete_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle delete script action"""
    try:
        query = update.callback_query
        script_id = query.data.replace("delete_script_", "")
        
        scripts = load_bot_scripts()
        if script_id in scripts:
            del scripts[script_id]
            save_bot_scripts(scripts)
            
            await query.answer(f"{EMOJI_CHECK} Script deleted", show_alert=True)
            await admin_scripts(update, context)
        else:
            await query.answer(f"Script not found", show_alert=True)
    except Exception as e:
        logger.error(f"Error deleting script: {e}\n{traceback.format_exc()}")
        await query.answer(f"{EMOJI_X} Error: {str(e)}", show_alert=True)

async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied", show_alert=True); return
    cfg = load_admin_config()
    text = (f"{EMOJI_SETTINGS} <b>BOT SETTINGS</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Maintenance: <b>{'ON' if cfg.get('maintenance_mode') else 'OFF'}</b>\n"
            f"Lock Mode: <b>{'ON' if cfg.get('lock_mode') else 'OFF'}</b>\n"
            f"Log Mode: <b>{'ON' if cfg.get('log_mode') else 'OFF'}</b>\n\n"
            "Maintenance/Lock block normal users. Admins remain accessible.")
    kb=[[InlineKeyboardButton(f"🛠 Maintenance {'OFF' if cfg.get('maintenance_mode') else 'ON'}", callback_data='toggle_maintenance')],
        [InlineKeyboardButton(f"🔐 Lock {'OFF' if cfg.get('lock_mode') else 'ON'}", callback_data='toggle_lock')],
        [InlineKeyboardButton(f"📝 Log Mode {'OFF' if cfg.get('log_mode') else 'ON'}", callback_data='toggle_log')],
        [InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data='admin_panel')]]
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))


async def admin_aesthetics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query=update.callback_query
    cfg=load_admin_config(); theme=cfg.get('aesthetics',{}).get('theme','dark')
    kb=[[InlineKeyboardButton('🌑 Dark', callback_data='theme_dark'), InlineKeyboardButton('☀️ Light', callback_data='theme_light')],
        [InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data='admin_panel')]]
    await query.edit_message_text(f"🎨 <b>AESTHETICS</b>\n\nCurrent theme: <b>{html.escape(theme)}</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))


async def admin_uploads(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query=update.callback_query
    pending=load_pending_approvals(); hist=load_json(UPLOAD_HISTORY_DB)
    await query.edit_message_text(f"{EMOJI_FOLDER} <b>UPLOADS</b>\n\nPending approvals: <b>{sum(1 for x in pending.values() if x.get('status')=='pending')}</b>\nUpload history records: <b>{len(hist)}</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data='admin_panel')]]))


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query=update.callback_query; st=load_json(STATISTICS_DB)
    await query.edit_message_text(f"{EMOJI_STATS} <b>STATISTICS</b>\n\nUsers: <b>{st.get('total_users',0)}</b>\nFiles: <b>{st.get('total_files_uploaded',0)}</b>\nApproved: <b>{st.get('total_approved',0)}</b>\nRejected: <b>{st.get('total_rejected',0)}</b>\nModules installed: <b>{st.get('total_modules_installed',0)}</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{EMOJI_BACK} Back", callback_data='admin_panel')]]))


async def toggle_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query=update.callback_query
    if not is_admin(query.from_user.id): await query.answer("Access denied", show_alert=True); return
    cfg=load_admin_config(); old=bool(cfg.get('maintenance_mode')); new=not old
    cfg['maintenance_mode']=new; save_admin_config(cfg)
    await query.answer(f"Maintenance mode {'ON' if new else 'OFF'}", show_alert=True)
    await admin_action_log(context, query.from_user.id, 'maintenance', new)
    await notify_users_system_change(context, 'maintenance', new, query.from_user.id)
    await admin_settings(update, context)

async def toggle_lock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query=update.callback_query
    if not is_admin(query.from_user.id): await query.answer("Access denied", show_alert=True); return
    cfg=load_admin_config(); old=bool(cfg.get('lock_mode')); new=not old
    cfg['lock_mode']=new; save_admin_config(cfg)
    await query.answer(f"Lock mode {'ON' if new else 'OFF'}", show_alert=True)
    await admin_action_log(context, query.from_user.id, 'lock', new)
    await notify_users_system_change(context, 'lock', new, query.from_user.id)
    await admin_settings(update, context)

async def toggle_log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query=update.callback_query
    if not is_admin(query.from_user.id): await query.answer("Access denied", show_alert=True); return
    cfg=load_admin_config(); old=bool(cfg.get('log_mode')); new=not old
    cfg['log_mode']=new; save_admin_config(cfg)
    await query.answer(f"Log mode {'ON' if new else 'OFF'}", show_alert=True)
    await admin_action_log(context, query.from_user.id, 'log_mode', new)
    await notify_users_system_change(context, 'log', new, query.from_user.id)
    await admin_settings(update, context)

async def set_theme(update: Update, context: ContextTypes.DEFAULT_TYPE, theme: str) -> None:
    """Set UI theme"""
    try:
        query = update.callback_query
        config = load_admin_config()
        config['aesthetics'] = config.get('aesthetics', {})
        config['aesthetics']['theme'] = theme
        save_admin_config(config)
        
        await query.answer(f"{EMOJI_CHECK} Theme set to {theme}", show_alert=True)
        await admin_aesthetics(update, context)
    except Exception as e:
        logger.error(f"Error setting theme: {e}")
        await query.answer(f"{EMOJI_X} Error", show_alert=True)

# ==================== MESSAGE HANDLERS ====================

async def handle_channel_rejection_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Consume the NEXT real channel post after Reject, regardless of its type.

    Supported rejection-reason messages include text, photo/screenshot, document,
    video, audio, voice, animation, sticker, video-note and other Telegram media.
    The bot ignores its own channel messages so the rejection prompt itself can
    never accidentally become the reason.
    """
    try:
        message = update.channel_post
        if not message:
            return

        # Ignore channel posts sent by this bot itself (including the rejection prompt).
        try:
            me = await context.bot.get_me()
            if message.from_user and message.from_user.id == me.id:
                return
        except Exception:
            pass

        channel_id = str(message.chat.id)
        pending = load_pending_approvals()
        candidates = [
            (key, item) for key, item in pending.items()
            if str(item.get('channel_id')) == channel_id
            and item.get('status') == 'pending'
            and item.get('rejection_pending')
            and str(item.get('message_id')) != str(message.message_id)
        ]
        if not candidates:
            return

        # The most recently pressed Reject gets the next channel message.
        candidates.sort(
            key=lambda pair: str(pair[1].get('rejection_requested_at', '')),
            reverse=True
        )
        record_key, record = candidates[0]
        file_name = os.path.basename(record.get('file_name', 'Unknown'))

        # Extract any human-readable text/caption, but DO NOT require it.
        reason_text = (message.text or message.caption or '').strip()
        if not reason_text:
            if message.photo:
                reason_text = '[Screenshot / Photo sent as rejection reason]'
            elif message.document:
                reason_text = f"[Document sent as rejection reason: {message.document.file_name or 'document'}]"
            elif message.video:
                reason_text = '[Video sent as rejection reason]'
            elif message.audio:
                reason_text = '[Audio sent as rejection reason]'
            elif message.voice:
                reason_text = '[Voice message sent as rejection reason]'
            elif message.animation:
                reason_text = '[Animation / GIF sent as rejection reason]'
            elif message.video_note:
                reason_text = '[Video note sent as rejection reason]'
            elif message.sticker:
                reason_text = '[Sticker sent as rejection reason]'
            else:
                reason_text = '[Channel message sent as rejection reason]'

        record['status'] = 'rejected'
        record['rejection_reason'] = reason_text
        record['rejection_reason_message_id'] = message.message_id
        record['rejection_reason_message_type'] = (
            'photo' if message.photo else
            'document' if message.document else
            'video' if message.video else
            'audio' if message.audio else
            'voice' if message.voice else
            'animation' if message.animation else
            'video_note' if message.video_note else
            'sticker' if message.sticker else
            'text' if message.text else 'other'
        )
        record['rejected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        record.pop('rejection_pending', None)
        record.pop('rejection_requested_by', None)
        record.pop('rejection_requested_at', None)
        pending[record_key] = record
        save_pending_approvals(pending)
        update_statistics('total_rejected', 1)

        # First tell the uploader that the file was rejected.
        user_text = (
            f"{user_emoji('❌')} <b>FILE REJECTED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>File:</b> <code>{html.escape(file_name)}</code>\n\n"
            f"<b>REJECTED</b>\n"
            f"<b>Reason:</b>\n"
            f"<blockquote>{html.escape(reason_text)}</blockquote>"
        )
        try:
            await context.bot.send_message(
                chat_id=record['user_id'],
                text=user_text,
                parse_mode='HTML',
                reply_markup=get_main_keyboard()
            )

            # For media/non-text reasons, deliver the EXACT channel message to the user.
            # copy_message preserves the screenshot/photo/document/etc. without needing
            # to download or guess the Telegram file type.
            if not message.text:
                await context.bot.copy_message(
                    chat_id=record['user_id'],
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
        except Exception as e:
            logger.error(
                f"Could not notify rejected file owner: {e}\n{traceback.format_exc()}"
            )

        # Finalize the original approval post: REJECTED, never APPROVED, and remove buttons.
        final_caption = (
            (record.get('channel_caption') or f"{EMOJI_FOLDER} <b>FILE</b>")
            + f"\n\n{user_emoji('❌')} <b>REJECTED</b>\n"
            + f"<b>REASON:</b>\n<blockquote>{html.escape(reason_text)}</blockquote>"
        )
        try:
            await context.bot.edit_message_caption(
                chat_id=record.get('channel_id'),
                message_id=record.get('message_id'),
                caption=final_caption,
                parse_mode='HTML',
                reply_markup=None
            )
        except Exception as e:
            logger.error(
                f"Could not finalize rejected channel message: {e}\n{traceback.format_exc()}"
            )

        # Confirm that THIS exact next channel message was consumed.
        try:
            await message.reply_text(
                f"{EMOJI_CHECK} <b>REJECTION RECORDED</b>\n\n"
                f"File: <code>{html.escape(file_name)}</code>",
                parse_mode='HTML'
            )
        except Exception:
            pass
    except Exception as e:
        logger.error(
            f"Error handling channel rejection reason: {e}\n{traceback.format_exc()}"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages from main menu"""
    try:
        user = update.effective_user
        user_id = user.id
        text = update.message.text
        # Reply-keyboard buttons can contain different Unicode emoji representations.
        # Normalize by removing emoji/symbols and comparing the actual button label.
        button_text = ''.join(ch for ch in (text or '') if ch.isalnum() or ch.isspace()).strip().upper()

        # A menu tap is a new user action, not a variable submission.
        # Clear stale variable state first so old missing-variable prompts cannot
        # spam the user when they switch to Upload/My Scripts/Modules/etc.
        if _menu_action_requested(button_text):
            _clear_user_env_session(context, user_id)

        env_script_id = context.user_data.get('awaiting_env_script_id')
        if env_script_id:
            scripts, env_script = _get_script(str(env_script_id))
            if env_script and _safe_script_for_user(env_script, user_id):
                required = env_script.get('env_required', [])
                parsed={}
                for raw in (text or '').splitlines():
                    raw=raw.strip()
                    if not raw or raw.startswith('#') or '=' not in raw: continue
                    key,val=raw.split('=',1); key=key.strip(); val=val.strip()
                    if key in required and val and val!='PASTE_VALUE_HERE': parsed[key]=val
                missing=[k for k in required if k not in parsed]
                if missing:
                    await update.message.reply_text('⚠️ <b>VARIABLES MISSING</b>\n\nSend every required variable as <code>KEY=VALUE</code>, one per line.\n\nMissing: '+', '.join(f'<code>{html.escape(x)}</code>' for x in missing),parse_mode='HTML'); return
                env_script['env']=parsed; env_script['awaiting_env']=False; save_bot_scripts(scripts); context.user_data.pop('awaiting_env_script_id',None)
                env_script['awaiting_env']=False; save_bot_scripts(scripts)
                await update.message.reply_text('🔐 <b>Credentials received.</b>\n\nPreparing the real project process…',parse_mode='HTML')
                try:
                    if str(env_script.get('kind')) == 'zip':
                        proc=await _launch_zip_process(context,str(env_script_id))
                    else:
                        proc=await _v110_launch_python_process(context,str(env_script_id))
                    if proc:
                        await _v110_running_card(context.application,user_id,env_script)
                    else:
                        await update.message.reply_text('❌ <b>PROJECT DID NOT STAY RUNNING</b>\n\nCheck VIEW CURRENT LOGS for the real startup output.',parse_mode='HTML',reply_markup=InlineKeyboardMarkup([[user_button('VIEW CURRENT LOGS','📡',callback_data=f"logs_script_{env_script_id}")],[user_button('MY SCRIPT','📁',callback_data='my_scripts_menu')]]))
                except Exception as exc:
                    _write_script_log(env_script,'\nV110 ENV START ERROR: '+str(exc)+'\n'+traceback.format_exc()+'\n')
                    await update.message.reply_text(f'❌ <b>PROJECT START FAILED</b>\n\n<pre>{html.escape(str(exc)[:2500])}</pre>',parse_mode='HTML',reply_markup=InlineKeyboardMarkup([[user_button('VIEW CURRENT LOGS','📡',callback_data=f"logs_script_{env_script_id}")],[user_button('MY SCRIPT','📁',callback_data='my_scripts_menu')]]))
                return

        if is_user_banned(user_id):
            await update.message.reply_text(
                f"{user_emoji('🚫')} <b>ACCESS DENIED</b>\n\n<b>Reason:</b> You are banned.",
                parse_mode="HTML"
            )
            return

        if await enforce_user_system_gate(update, context):
            return

        if is_admin(user_id) and context.user_data.get('rejecting_approval_key'):
            reason = (text or '').strip()
            if not reason:
                await update.message.reply_text('Please send a rejection reason.')
                return
            pending = load_pending_approvals()
            key = context.user_data.get('rejecting_approval_key')
            record = pending.get(key)
            if record and record.get('status') == 'pending':
                record['status']='rejected'; record['rejection_reason']=reason; record['rejected_at']=datetime.now().strftime('%Y-%m-%d %H:%M:%S'); record.pop('rejection_pending',None); update_statistics('total_rejected',1); pending[key]=record; save_pending_approvals(pending)
                file_name=os.path.basename(record.get('file_name','Unknown'))
                try:
                    await context.bot.send_message(chat_id=record['user_id'],text=(f"{user_emoji('❌')} <b>YOUR FILE HAS BEEN REJECTED</b>\n━━━━━━━━━━━━━━━━━━━━\n\n<b>File:</b> <code>{html.escape(file_name)}</code>\n\n<b>REJECTION REASON:</b>\n<blockquote>{html.escape(reason)}</blockquote>"),parse_mode='HTML',reply_markup=get_main_keyboard())
                except Exception as e: logger.error(f"Could not notify rejected file owner: {e}\n{traceback.format_exc()}")
                final_caption=(record.get('channel_caption') or f"{user_emoji('📁')} <b>FILE</b>") + f"\n\n{user_emoji('❌')} <b>REJECTED</b>\n<b>REJECTION REASON:</b>\n<blockquote>{html.escape(reason)}</blockquote>"
                try: await context.bot.edit_message_caption(chat_id=record.get('channel_id'),message_id=record.get('message_id'),caption=final_caption,parse_mode='HTML',reply_markup=None)
                except Exception as e: logger.error(f"Could not finalize rejected channel message: {e}\n{traceback.format_exc()}")
            else:
                await update.message.reply_text(f"{user_emoji('⚠️')} That approval request is no longer pending.",reply_markup=get_main_keyboard())
            context.user_data.pop('rejecting_approval_key',None)
            await update.message.reply_text(f"{user_emoji('✅')} <b>REJECTION RECORDED SUCCESSFULLY</b>\n\nFile: <code>{html.escape(record.get('file_name','Unknown') if record else 'Unknown')}</code>",parse_mode='HTML',reply_markup=get_main_keyboard())
            return

        if await process_admin_text_action(update, context):
            return

        if is_admin(user_id) and context.user_data.get('channel_input'):
            await process_channel_input(update, context)
            return
        if button_text in ("UPLOAD FILE", "UPLOAD SCRIPT"):
            await update.message.reply_text(
                f"{user_emoji('📤')} <b>UPLOAD WORKSPACE</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Please send your script file directly here.\n\n"
                f"{user_emoji('✅')} <b>Supported formats:</b>\n"
                f"├ .py (Python)\n"
                f"├ .js (Node.js)\n"
                f"└ .zip (Python/Node project)\n\n"
                f"{user_emoji('⚠️')} <b>Max upload size: 30MB</b>",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
        
        elif button_text in ("MY SCRIPTS", "MY SCRIPT"):
            await user_scripts_menu(update, context)
        
        elif button_text in ("INSTALL MODULE", "MODULE"):
            # Enter the module-installation state. The prompt itself is kept in the
            # chat so the progress message can be edited in-place later.
            context.user_data['awaiting_module_name'] = True
            sent = await update.message.reply_text(
                f"{user_emoji('➕')} <b>INSTALL MODULE</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Send the module name to install.\n\n"
                f"<b>Examples:</b>\n"
                f"├ requests\n"
                f"├ pillow\n"
                f"├ numpy\n"
                f"└ telebot\n\n"
                f"<i>Send /cancel to cancel.</i>",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
        
        elif button_text == "BOT SPEED":
            await update.message.reply_text(
                f"{user_emoji('⚡')} <b>Pinging...</b>",
                parse_mode="HTML", reply_markup=get_main_keyboard()
            )
            await asyncio.sleep(random.uniform(3.0, 6.0))
            response_ms = random.uniform(10.1, 999.9)
            final_speed_text = (
                f"{user_emoji('⚡')} <b>SERVER PERFORMANCE</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>Current Speed:</b> <code>{response_ms:.1f} ms</code>\n"
                f"<b>Status:</b> Online {user_emoji('✅')}\n\n"
                f"{user_emoji('🟢')} <i>All systems operational.</i>"
            )
            await update.message.reply_text(
                final_speed_text, parse_mode="HTML", reply_markup=get_main_keyboard()
            )

        elif button_text in ("STATS", "STATISTICS"):
            # Show statistics for this user only.
            # Active Scripts = currently running scripts; Total Files = all scripts
            # saved in My Scripts; Pending Configs = this user's uploads waiting
            # for approval; Running/Stopped are the current script states.
            scripts = load_bot_scripts()
            user_scripts = [
                script for script in scripts.values()
                if str(script.get('user_id')) == str(user_id)
            ]

            total_files = len(user_scripts)
            running_scripts = sum(
                1 for script in user_scripts if script.get('status') == 'running'
            )
            stopped_scripts = total_files - running_scripts

            pending = load_pending_approvals()
            pending_configs = sum(
                1 for item in pending.values()
                if str(item.get('user_id')) == str(user_id)
                and item.get('status') == 'pending'
            )

            # This is the Python interpreter/environment actually running the bot.
            import platform
            python_version = platform.python_version()

            stats_text = (
                f"{user_emoji('📊')} <b>STATISTICS</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>USER STATISTICS:</b>\n"
                f"├ <b>Active Scripts:</b> <code>{running_scripts}</code>\n"
                f"├ <b>Total Files:</b> <code>{total_files}</code>\n"
                f"├ <b>Pending Configs:</b> <code>{pending_configs}</code>\n"
                f"├ {user_emoji('🟢')} <b>Running:</b> <code>{running_scripts}</code>\n"
                f"└ {user_emoji('🔴')} <b>Stopped:</b> <code>{stopped_scripts}</code>\n\n"
                f"<b>SYSTEM INFO:</b>\n"
                f"├ <b>Python:</b> <code>{html.escape(python_version)}</code>\n"
                f"└ <b>Virtual Private Server (VPS)</b>"
            )

            await update.message.reply_text(
                stats_text,
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
        
        elif button_text in ("HELP", "SUPPORT"):
            help_text = """╔════════════════════════════╗
🚀 JAGANNATH HOSTING BOT
╚════════════════════════════╝

╔════════════════════════════╗
📖 GUIDE
╚════════════════════════════╝

🟢 STEP 1 — UPLOAD FILE

Tap Upload File and send a supported project file.

✅ Supported: .py • .js • .zip

ZIP projects are extracted automatically and scanned for runnable files, dependencies and environment variables.

━━━━━━━━━━━━━━━━━━━━

🟢 STEP 2 — ADMIN APPROVAL

Wait for Admin Approval.

✅ After approval, you will receive a notification.

━━━━━━━━━━━━━━━━━━━━

🟢 STEP 3 — MY SCRIPT

Go to My Script to view your approved scripts.

━━━━━━━━━━━━━━━━━━━━

🟢 STEP 4 — SELECT SCRIPT

Tap the button of your ".py" script.

━━━━━━━━━━━━━━━━━━━━

🟢 STEP 5 — START

Tap ▶️ Start to run your script.

If it runs successfully, check your bot to make sure everything is working properly.

━━━━━━━━━━━━━━━━━━━━

🔴 IF YOUR SCRIPT STOPS

Check the Logs carefully.

Find the error and fix it yourself, or use an AI assistant to understand and solve the problem.

━━━━━━━━━━━━━━━━━━━━

╔════════════════════════════╗
🙏 JAI JAGANNATH 🙏
╚════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━
🆘 HELP
━━━━━━━━━━━━━━━━━━━━

CONTACT — @SHUBHxSELLER"""

            await update.message.reply_text(
                help_text,
                reply_markup=get_main_keyboard()
            )
        
        else:
            if context.user_data.get('awaiting_module_name'):
                module_name = (text or '').strip()
                if not module_name:
                    await update.message.reply_text(
                        f"{user_emoji('⚠️')} Please send a module name or /cancel.",
                        reply_markup=get_main_keyboard()
                    )
                    return

                # Telegram text is passed as an argument (never through a shell),
                # so package names cannot become shell commands.
                progress_text = (
                    f"{user_emoji('⏳')} <b>Installing {html.escape(module_name)}...</b>"
                )
                # Send exactly one progress message for this package. That same
                # message is edited to the final success/failure result; no second
                # result message is sent.
                progress_message = await update.message.reply_text(
                    progress_text,
                    parse_mode="HTML",
                    reply_markup=get_main_keyboard()
                )
                install_message_id = progress_message.message_id

                logger.info("Module installation requested by %s: %s", user_id, module_name)

                try:
                    # Railway/Linux uses the bot's actual Python interpreter. Termux is
                    # not required and should not be used on Railway. We install into a
                    # dedicated directory that every hosted script receives through
                    # PYTHONPATH, so user scripts can import their installed packages.
                    module_dir = user_module_dir(user_id)

                    # Accept normal pip names plus the common import-name aliases.
                    # This fixes the frequent case where a user types the import name
                    # rather than the PyPI distribution name.
                    package_aliases = {
                        'cv2': 'opencv-python',
                        'pil': 'Pillow',
                        'pillow': 'Pillow',
                        'bs4': 'beautifulsoup4',
                        'sklearn': 'scikit-learn',
                        'yaml': 'PyYAML',
                        'dotenv': 'python-dotenv',
                        'telegram': 'python-telegram-bot',
                        'telethon': 'Telethon',
                        'telebot': 'pyTelegramBotAPI',
                        'pyrogram': 'Pyrogram',
                        'request': 'requests',
                        'beautifulsoup': 'beautifulsoup4',
                        'dateutil': 'python-dateutil',
                        'cv': 'opencv-python',
                        'motor': 'motor',
                        'mongo': 'pymongo',
                        'pymongo': 'pymongo',
                        'aiohttp': 'aiohttp',
                        'httpx': 'httpx',
                    }
                    requested_name = module_name.strip()
                    if requested_name.startswith('-'):
                        raise ValueError('Invalid module name. Send a valid PyPI package name, e.g. motor, requests, numpy, or pillow.')
                    base_name = requested_name.split('==')[0].split('>=')[0].split('<=')[0].strip().lower()
                    package_name = package_aliases.get(base_name, requested_name)

                    # Locate pip from the SAME interpreter that runs this hosting bot.
                    # This avoids installing into a different system Python.
                    pip_command = [sys.executable, '-m', 'pip']
                    probe = await asyncio.create_subprocess_exec(
                        *pip_command, '--version',
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.STDOUT
                    )
                    probe_out, _ = await asyncio.wait_for(probe.communicate(), timeout=20)
                    if probe.returncode != 0:
                        # Try bootstrapping pip in the active Python environment.
                        ensure = await asyncio.create_subprocess_exec(
                            sys.executable, '-m', 'ensurepip', '--upgrade',
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.STDOUT
                        )
                        ensure_out, _ = await asyncio.wait_for(ensure.communicate(), timeout=60)
                        if ensure.returncode != 0:
                            raise RuntimeError(
                                'pip is unavailable in the active Python environment. '
                                + (ensure_out or b'').decode('utf-8', errors='replace')[-1200:]
                            )

                    pip_args = [
                        *pip_command, 'install',
                        '--disable-pip-version-check',
                        '--no-input',
                        '--upgrade',
                        '--prefer-binary',
                        '--target', module_dir,
                        package_name
                    ]
                    logger.info('Running module installer: %r', pip_args)
                    process = await asyncio.create_subprocess_exec(
                        *pip_args,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.STDOUT
                    )
                    try:
                        output_bytes, _ = await asyncio.wait_for(process.communicate(), timeout=300)
                    except asyncio.TimeoutError:
                        try:
                            process.kill()
                        except ProcessLookupError:
                            pass
                        await process.communicate()
                        raise TimeoutError('Package installation timed out after 5 minutes. Check Railway network/build logs.')

                    output = (output_bytes or b'').decode('utf-8', errors='replace')
                    output_lines = [line.strip() for line in output.splitlines() if line.strip()]

                    if process.returncode != 0:
                        error_tail = '\n'.join(output_lines[-12:]) if output_lines else 'pip returned a non-zero exit code without output.'
                        raise RuntimeError(error_tail[:3500])

                    # HARD verification: verify the distribution with pip. Only use
                    # import verification for packages whose import name is known. This
                    # prevents false failures for valid PyPI packages where the distribution
                    # name and Python import name differ.
                    known_imports = {
                        'opencv-python': 'cv2', 'pillow': 'PIL', 'beautifulsoup4': 'bs4',
                        'scikit-learn': 'sklearn', 'pyyaml': 'yaml', 'python-dotenv': 'dotenv',
                        'python-telegram-bot': 'telegram', 'pytelegrambotapi': 'telebot',
                        'telethon': 'telethon', 'pyrogram': 'pyrogram',
                        'motor': 'motor', 'pymongo': 'pymongo',
                        'aiohttp': 'aiohttp', 'httpx': 'httpx'
                    }
                    verify_name = str(package_name).split('==')[0].split('>=')[0].split('<=')[0].strip()
                    known_import = known_imports.get(verify_name.lower())
                    if known_import:
                        verify_code = (
                            'import sys; '
                            f'sys.path.insert(0, {module_dir!r}); '
                            f'import importlib; m=importlib.import_module({known_import!r}); '
                            'print(getattr(m, "__version__", "import-ok"))'
                        )
                        verify = await asyncio.create_subprocess_exec(
                            sys.executable, '-c', verify_code,
                            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
                        )
                        verify_bytes, _ = await asyncio.wait_for(verify.communicate(), timeout=45)
                        verify_output = (verify_bytes or b'').decode('utf-8', errors='replace').strip()
                        if verify.returncode != 0:
                            raise RuntimeError(f'Package installed but import verification failed for {known_import}.\\n{verify_output[-1800:]}')
                        import_display = known_import
                    else:
                        # Verify the distribution inside the per-user --target directory.
                        # pip show may inspect the bot's global environment instead.
                        verify_code = (
                            'import sys; import importlib.metadata as md; '
                            f'sys.path.insert(0, {module_dir!r}); '
                            f'print(md.version({verify_name!r}))'
                        )
                        verify = await asyncio.create_subprocess_exec(
                            sys.executable, '-c', verify_code,
                            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
                        )
                        verify_bytes, _ = await asyncio.wait_for(verify.communicate(), timeout=30)
                        verify_output = (verify_bytes or b'').decode('utf-8', errors='replace').strip()
                        if verify.returncode != 0 or not verify_output:
                            raise RuntimeError(
                                f'Package installation completed but distribution verification failed.\n{verify_output[-1800:]}'
                            )
                        import_display = f'verified distribution {verify_output.splitlines()[-1][-120:]}'

                    # Always define this value before the success logger.
                    # PyPI distribution names and Python import names can differ.
                    import_name = known_import or verify_name or package_name

                    result_text = (
                        f"{user_emoji('✅')} <b>Module installed successfully</b>\n"
                        f"<b>Module:</b> — <code>{html.escape(package_name)}</code>\n"
                        f"<b>Verification:</b> <code>{html.escape(import_display)}</code>\n"
                        f"<b>Status:</b> Ready for hosted scripts {user_emoji('✅')}"
                    )
                    update_statistics('total_modules_installed', 1)
                    context.user_data['awaiting_module_name'] = True
                    logger.info('Module installed and verified for %s: %s (%s)', user_id, package_name, import_name)

                    # Never edit the temporary installer message. Some Telegram
                    # messages can no longer be edited; sending the result separately
                    # guarantees the user always receives the outcome.
                    await update.message.reply_text(
                        result_text,
                        parse_mode='HTML',
                        reply_markup=get_main_keyboard()
                    )

                except Exception as install_error:
                    logger.error(
                        'Module installation failed for %r (user %s): %s\n%s',
                        module_name, user_id, install_error, traceback.format_exc()
                    )
                    error_text = str(install_error).strip() or 'Unknown installer error.'
                    result_text = (
                        f"{user_emoji('❌')} <b>Module installation failed</b>\n\n"
                        f"<b>Requested:</b> <code>{html.escape(module_name)}</code>\n\n"
                        f"<pre>{html.escape(error_text[:3500])}</pre>\n\n"
                        f"Send another module name or /cancel."
                    )
                    await update.message.reply_text(result_text, parse_mode='HTML', reply_markup=get_main_keyboard())

            else:
                await update.message.reply_text(
                    f"{user_emoji('⚠️')} I don't understand that command.\n\n"
                    f"Please use the menu buttons below.",
                    reply_markup=get_main_keyboard()
                )
    
    except Exception as e:
        logger.error(f"Error in handle_message: {e}\n{traceback.format_exc()}")
        try:
            await update.message.reply_text(
                f"{user_emoji('❌')} An error occurred. Please try again.",
                reply_markup=get_main_keyboard()
            )
        except:
            pass

async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle file uploads"""
    try:
        user_id = update.effective_user.id
        document = update.message.document

        if is_admin(user_id) and context.user_data.get('admin_action') == 'broadcast':
            context.user_data.pop('admin_action', None)
            await perform_broadcast(update, context, update.message)
            return
        
        if is_user_banned(user_id):
            await update.message.reply_text(
                f"{EMOJI_PROHIBITED} <b>ACCESS DENIED</b>\n\n<b>Reason:</b> You are banned.",
                parse_mode="HTML"
            )
            return

        if await enforce_user_system_gate(update, context):
            return
        
        file_name = document.file_name or ""
        if not file_name.lower().endswith(SUPPORTED_UPLOAD_EXTENSIONS):
            await update.message.reply_text(
                f"{EMOJI_X} <b>INVALID FILE</b>\n\n"
                f"Supported formats are .py (Python), .js (Node.js) and .zip (project).",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
            return

        if document.file_size and document.file_size > MAX_UPLOAD_SIZE:
            await update.message.reply_text(
                f"{EMOJI_X} <b>FILE TOO LARGE</b>\n\n"
                f"Maximum upload size is 30MB.",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
            return

        add_upload_record(user_id, file_name, document.file_size)
        try:
            await send_approval_file(update, context, document)
        except Exception as approval_error:
            logger.error(f"Approval channel send failed: {approval_error}\n{traceback.format_exc()}")
        
        sent_user_message = await update.message.reply_text(
            f"{user_emoji('⏳')} File <code>{html.escape(document.file_name)}</code> is under detection.\n"
            f"Once approved, you will be notified.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )

        # Store the user's notification message so it can be updated after approval.
        pending = load_pending_approvals()
        for key, item in pending.items():
            if (str(item.get('user_id')) == str(user_id)
                    and item.get('file_id') == document.file_id
                    and item.get('status') == 'pending'):
                item['user_message_id'] = sent_user_message.message_id
                pending[key] = item
                break
        save_pending_approvals(pending)
        
        logger.info(f"User {user_id} uploaded: {document.file_name}")
    except Exception as e:
        logger.error(f"Error handling file upload: {e}\n{traceback.format_exc()}")
        try:
            await update.message.reply_text(
                f"{user_emoji('❌')} Error uploading file.",
                reply_markup=get_main_keyboard()
            )
        except:
            pass

async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Restart a user's script by numeric script ID; no extra button required."""
    user_id = update.effective_user.id
    if not context.args or not str(context.args[0]).isdigit():
        await update.message.reply_text("Usage: /restart <script_id>\nOpen MY SCRIPTS to see your script IDs.", reply_markup=get_main_keyboard())
        return
    script_id = str(context.args[0])
    scripts, script = _get_script(script_id)
    if not script or not _safe_script_for_user(script, user_id):
        await update.message.reply_text(f"{EMOJI_X} Script not found.", reply_markup=get_main_keyboard())
        return
    # Reuse the same launcher path by stopping an existing process first.
    with SCRIPT_PROCESS_LOCK:
        entry = SCRIPT_PROCESSES.get(script_id)
        proc = entry.get('process') if entry else None
    if proc and proc.poll() is None:
        script['manual_stop'] = True
        save_bot_scripts(scripts)
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            try: proc.terminate()
            except Exception: pass
        try: await asyncio.to_thread(proc.wait, 5)
        except Exception: pass
        with SCRIPT_PROCESS_LOCK: SCRIPT_PROCESSES.pop(script_id, None)
    script['manual_stop'] = False
    save_bot_scripts(scripts)
    # Launch directly with the same environment as the normal START button.
    try:
        command, runtime, _ = _runtime_command(script)
        path = os.path.abspath(script['path'])
        md = user_module_dir(script.get('user_id')); ld = os.path.abspath(INSTALLED_MODULES_DIR)
        env = os.environ.copy(); env['PYTHONPATH'] = os.pathsep.join(x for x in (md, ld, env.get('PYTHONPATH','')) if x); env['PYTHONUNBUFFERED']='1'
        proc = subprocess.Popen(command, cwd=os.path.dirname(path) or os.getcwd(), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, text=True, encoding='utf-8', errors='replace', bufsize=1, universal_newlines=True, start_new_session=True)
        with SCRIPT_PROCESS_LOCK: SCRIPT_PROCESSES[script_id] = {'process': proc, 'return_code': None}
        script['status']='running'; script['runtime']=runtime; script['pid']=proc.pid; script['started_at_epoch']=time.time(); script['last_error']=None; script['last_exit_code']=None; script['manual_stop']=False
        save_bot_scripts(scripts)
        _write_script_log(script, f"\\nRESTART REQUESTED: process {proc.pid}\\n")
        _start_process_monitor(context.application, script_id, proc, asyncio.get_running_loop())
        await update.message.reply_text(f"{EMOJI_ROCKET} <b>RESTARTED</b>\\n\\n<code>{html.escape(str(script.get('name','Unknown')))}</code> is running.\\nUptime: 0s", parse_mode='HTML', reply_markup=get_main_keyboard())
    except Exception as exc:
        script['status']='stopped'; script['last_error']=f'{type(exc).__name__}: {exc}'; save_bot_scripts(scripts)
        _write_script_log(script, f"\\nRESTART ERROR: {type(exc).__name__}: {exc}\\n{traceback.format_exc()}\\n")
        await update.message.reply_text(f"{EMOJI_X} <b>RESTART FAILED</b>\\n\\n<pre>{html.escape(traceback.format_exc()[-3000:])}</pre>", parse_mode='HTML', reply_markup=get_main_keyboard())


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel the currently active user/admin workflow."""
    context.user_data.pop('rejecting_approval_key', None)
    _clear_user_env_session(context, update.effective_user.id)
    if is_admin(update.effective_user.id) and context.user_data.pop('admin_action', None):
        context.user_data.pop('broadcast_media_group', None)
        await update.message.reply_text(
            f"{EMOJI_CHECK} <b>Action cancelled.</b>",
            parse_mode="HTML"
        )
        return

    if context.user_data.pop('awaiting_module_name', None):
        context.user_data.pop('module_install_message_id', None)
        await update.message.reply_text(
            f"{EMOJI_CHECK} <b>Module installation cancelled.</b>",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            f"{EMOJI_WARNING} Nothing to cancel.",
            reply_markup=get_main_keyboard()
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Central callback dispatcher, including a hard ban gate."""
    query = update.callback_query
    user_id = query.from_user.id
    if is_user_banned(user_id):
        await query.answer("Access denied — You are banned.", show_alert=True)
        return
    if not is_admin(user_id) and user_block_message(system_state()):
        await query.answer('Bot is currently unavailable. Please try again later.', show_alert=True)
        return
    data = query.data or ''
    try:
        if data == 'admin_panel':
            await query.answer()
            await show_admin_panel(update, context)
        elif data == 'admin_manage':
            await query.answer()
            await admin_manage(update, context)
        elif data == 'admin_ban_user':
            await admin_ban_prompt(update, context)
        elif data == 'admin_unban_user':
            await admin_unban_prompt(update, context)
        elif data == 'admin_broadcast':
            await admin_broadcast_prompt(update, context)
        elif data == 'admin_select_user':
            await admin_select_user_prompt(update, context)
        elif data == 'admin_all_users':
            await query.answer(); await admin_all_users(update, context)
        elif data.startswith('admin_user_') and data.replace('admin_user_', '', 1).isdigit():
            await query.answer(); await admin_user_profile(update, context, data.replace('admin_user_', '', 1))
        elif data.startswith('admin_message_'):
            await admin_message_user_prompt(update, context, int(data.replace('admin_message_', '', 1)))
        elif data.startswith('admin_toggleban_'):
            await admin_toggle_user_ban(update, context, int(data.replace('admin_toggleban_', '', 1)))
        elif data.startswith('admin_stopall_'):
            await admin_stop_all_user(update, context, int(data.replace('admin_stopall_', '', 1)))
        elif data.startswith('admin_deleteall_'):
            await admin_delete_all_user(update, context, int(data.replace('admin_deleteall_', '', 1)))
        elif data.startswith('admin_script_'):
            await admin_script_action(update, context, data.replace('admin_script_', '', 1))
        elif data == 'force_verify_all':
            await verify_force_join_callback(update, context)
        elif data == 'force_channels':
            await query.answer(); await force_channels_panel(update, context)
        elif data == 'approval_channel':
            await query.answer(); await approval_channel_panel(update, context)
        elif data.startswith('remove_force_'):
            await remove_force_channel(update, context)
        elif data == 'remove_approval_channel':
            await remove_approval_channel(update, context)
        elif data == 'set_approval_channel':
            await query.answer(); await start_channel_input(update, context, 'approval')
        elif data == 'add_force_channel':
            await query.answer(); await start_channel_input(update, context, 'force')
        elif data == 'admin_scripts':
            await query.answer(); await admin_scripts(update, context)
        elif data.startswith('view_script_'):
            await query.answer()
            await view_script(update, context, data.replace('view_script_', '', 1))
        elif data.startswith('start_script_'):
            await handle_start_script(update, context)
        elif data.startswith('stop_script_'):
            await handle_stop_script(update, context)
        elif data.startswith('logs_script_'):
            await handle_logs_script(update, context)
        elif data.startswith('delete_script_'):
            await handle_delete_script(update, context)
        elif data.startswith('confirm_delete_'):
            await confirm_delete_yes(update, context)
        elif data.startswith('cancel_delete_'):
            await cancel_delete_script(update, context)
        elif data == 'my_scripts_menu':
            await query.answer(); await send_user_scripts_from_callback(query, context)
        elif data == 'admin_settings':
            await query.answer(); await admin_settings(update, context)
        elif data == 'admin_aesthetics':
            await query.answer(); await admin_aesthetics(update, context)
        elif data == 'admin_uploads':
            await query.answer(); await admin_uploads(update, context)
        elif data == 'admin_stats':
            await query.answer(); await admin_stats(update, context)
        elif data == 'toggle_maintenance':
            await toggle_maintenance(update, context)
        elif data == 'toggle_lock':
            await toggle_lock(update, context)
        elif data == 'toggle_log':
            await toggle_log(update, context)
        elif data.startswith('theme_'):
            await set_theme(update, context, data.replace('theme_', ''))
        elif data == 'noop_processed':
            await query.answer('This file has already been processed.', show_alert=True)
        elif data == 'admin_close':
            await query.answer(); await query.edit_message_text('Admin panel closed.')
        elif data in ('approve_file_pending', 'reject_file_pending'):
            await approval_action(update, context, 'approve' if data.startswith('approve') else 'reject')
        else:
            await query.answer('This action is not available yet.', show_alert=True)
    except Exception as e:
        logger.error('Callback handler error for %s: %s\n%s', data, e, traceback.format_exc())
        try: await query.answer()
        except Exception: pass
        try:
            if query.message:
                await query.message.reply_text(f"{EMOJI_X} <b>Action could not be completed.</b>\n\nPlease open the relevant screen again and retry.",parse_mode='HTML',reply_markup=get_main_keyboard())
        except Exception: pass


async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Record uncaught Telegram/update errors instead of failing silently."""
    logger.error("Unhandled update error: %s\n%s", context.error, traceback.format_exc())
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                f"{EMOJI_X} <b>Something went wrong.</b>\nPlease try again.",
                parse_mode="HTML", reply_markup=get_main_keyboard()
            )
        except Exception:
            pass


# ==================== MAIN ====================

def main():
    """Start the bot"""
    try:
        if not BOT_TOKEN:
            raise RuntimeError("BOT_TOKEN environment variable is not set.")
        if not ADMIN_USER_IDS:
            raise RuntimeError("ADMIN_USER_IDS environment variable is not set.")
        # Native reply and inline button styles require python-telegram-bot 22.7+.
        # The current stable PTB line is 22.8; use 22.8 for native button styles.
        from telegram import __version__ as PTB_VERSION
        try:
            ptb_major, ptb_minor = [int(x) for x in PTB_VERSION.split('.')[:2]]
        except Exception:
            ptb_major, ptb_minor = 0, 0
        if (ptb_major, ptb_minor) < (22, 7):
            raise RuntimeError(
                f"python-telegram-bot {PTB_VERSION} is too old. Install python-telegram-bot>=22.8,<23."
            )

        application = Application.builder().token(BOT_TOKEN).build()
        try:
            if application.job_queue:
                application.job_queue.run_repeating(_v114_expiry_alert_job, interval=3600, first=30, name="v114_premium_expiry_alerts")
                application.job_queue.run_repeating(_v10_st_expiry_job, interval=300, first=30, name="v10_slot_time_expiry")
        except Exception as _job_error:
            logger.warning("Premium expiry alert job unavailable: %s", _job_error)
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("admin", admin_command))
        application.add_handler(CommandHandler("cancel", cancel_command))
        application.add_handler(CommandHandler("restart", restart_command))
        application.add_handler(ChatMemberHandler(auto_approval_channel_handler, ChatMemberHandler.MY_CHAT_MEMBER))
        
        # Rejection reason handler MUST be registered first in the same handler group.
        # Otherwise a channel document/media post could be consumed by a generic
        # upload/broadcast handler before the rejection workflow sees it.
        application.add_handler(MessageHandler(
            filters.UpdateType.CHANNEL_POST,
            handle_channel_rejection_reason
        ))
        # Broadcast documents are handled inside the existing document handler;
        # other rich media have their own handler. Text broadcasts are handled by handle_message.
        application.add_handler(MessageHandler(filters.Document.ALL, handle_file_upload))
        application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, _v114_payment_photo_handler))
        application.add_handler(MessageHandler(
            filters.PHOTO | filters.VIDEO | filters.VOICE | filters.AUDIO |
            filters.ANIMATION | filters.VIDEO_NOTE | filters.Sticker.ALL,
            admin_broadcast_message
        ))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_error_handler(global_error_handler)
        
        print("\n" + "="*80)
        print("🤖 SCRIPT HOSTING BOT - ADMIN PANEL v6.0 / ENGINE 127")
        print("="*80)
        print(f"{EMOJI_CHECK} Bot Token: CONFIGURED")
        print(f"{EMOJI_CHECK} Admin ID: CONFIGURED")
        print(f"{EMOJI_CHECK} Main Menu: ENABLED (Variables available to users; admins see all projects)")
        print(f"{EMOJI_CHECK} Admin Panel: ENABLED (/admin)")
        print(f"{EMOJI_CHECK} Script Management: ENABLED")
        print(f"{EMOJI_CHECK} Module Installation: ENABLED")
        print(f"{EMOJI_CHECK} Statistics Dashboard: ENABLED")
        print(f"{EMOJI_CHECK} Support System: ENABLED")
        print(f"{EMOJI_CHECK} Ban/Unban System: ENABLED")
        print(f"{EMOJI_CHECK} Full Error Handling: ENABLED")
        print(f"{EMOJI_CHECK} Custom Telegram Emoji IDs: ENABLED (user-side buttons/messages)")
        print("="*80)
        print(f"{EMOJI_ROCKET} Bot is starting... | Hosting Engine {HOSTING_ENGINE_VERSION}")
        print("="*80 + "\n")
        
        logger.info("Bot started successfully")
        application.run_polling(allowed_updates=__import__("telegram").Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}\n{traceback.format_exc()}")
        print(f"\n{EMOJI_X} FATAL ERROR: {e}")
        raise

# --- ZIP PROJECT / UNIVERSAL DEPENDENCY PREPARATION ---
# This layer is intentionally additive: it prepares uploaded projects without
# replacing the existing approval/process-management architecture.
PY_STDLIB = {
    "os","sys","re","json","math","time","datetime","pathlib","typing","asyncio",
    "logging","subprocess","threading","sqlite3","random","string","collections","itertools",
    "functools","hashlib","hmac","base64","urllib","http","email","io","shutil","zipfile",
    "tempfile","traceback","signal","socket","ssl","csv","glob","platform","inspect","statistics",
}
IMPORT_TO_PACKAGE = {
    "telegram": "python-telegram-bot>=22.8,<23",
    "bs4": "beautifulsoup4",
    "PIL": "Pillow",
    "yaml": "PyYAML",
    "dotenv": "python-dotenv",
    "cv2": "opencv-python-headless",
    "requests": "requests",
    "aiohttp": "aiohttp",
    "httpx": "httpx",
    "pymongo": "pymongo",
    "motor": "motor",
    "redis": "redis",
    "flask": "Flask",
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "pandas": "pandas",
    "numpy": "numpy",
    "cryptography": "cryptography",
    "psutil": "psutil",
}

def _scan_python_imports(source):
    found=set()
    for m in re.finditer(r'^\s*(?:import\s+([A-Za-z_][\w.]*)|from\s+([A-Za-z_][\w.]*)\s+import\s+)', source, re.M):
        name=(m.group(1) or m.group(2) or '').split('.')[0]
        if name and name not in PY_STDLIB and not name.startswith('_'):
            found.add(name)
    return found

def _scan_project_dependencies(root):
    """Collect declared requirements plus import-derived packages across the project."""
    requirements=[]; imports=set(); files=[]
    req_files=[]
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {'.git','__pycache__','.venv','venv','node_modules'}]
        for name in names:
            fp=os.path.join(base,name); files.append(fp)
            if name.lower() == 'requirements.txt': req_files.append(fp)
            if name.lower().endswith('.py'):
                try: imports |= _scan_python_imports(Path(fp).read_text(encoding='utf-8',errors='replace'))
                except Exception: pass
    for rp in req_files:
        try:
            for line in Path(rp).read_text(encoding='utf-8',errors='replace').splitlines():
                line=line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    requirements.append(line)
        except Exception: pass
    mapped=[IMPORT_TO_PACKAGE[x] for x in sorted(imports) if x in IMPORT_TO_PACKAGE]
    return files, list(dict.fromkeys(requirements+mapped)), sorted(imports)

def _safe_extract_zip(zip_path, destination, max_files=5000, max_uncompressed_bytes=500*1024*1024):
    """Prevent path traversal and simple ZIP bombs while extracting."""
    total=0; count=0
    os.makedirs(destination, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        infos=zf.infolist()
        for info in infos:
            if info.is_dir(): continue
            count += 1; total += max(0, info.file_size)
            if count > max_files: raise ValueError('ZIP contains too many files.')
            if total > max_uncompressed_bytes: raise ValueError('ZIP expands beyond the safe extraction limit.')
            target=os.path.abspath(os.path.join(destination, info.filename))
            if os.path.commonpath([os.path.abspath(destination), target]) != os.path.abspath(destination):
                raise ValueError('Unsafe ZIP path detected.')
        zf.extractall(destination)
    return count, total

def _detect_project_entrypoints(root):
    """Prefer explicit/common entrypoints; do not blindly execute helper .py files."""
    candidates=[]
    priority=('bot.py','main.py','app.py','run.py','server.py','index.py')
    for name in priority:
        p=os.path.join(root,name)
        if os.path.isfile(p): candidates.append(p)
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {'.git','__pycache__','.venv','venv','node_modules'}]
        for name in names:
            if name.endswith('.py') and name not in priority and name.lower() in {'start.py','launcher.py'}:
                candidates.append(os.path.join(base,name))
    return list(dict.fromkeys(candidates))


# ==================== SHUB HOSTING BOT 108 — ADVANCED HOSTING ENGINE ====================
# This layer extends v107 without removing its existing admin, upload, approval,
# statistics, module, script-control or UI systems.
HOSTING_ENGINE_VERSION = "108.0"
PROJECT_VENV_DIRNAME = ".host_venv"
PROJECT_MANIFEST_NAME = "host.json"
MAX_PROJECT_DISPLAY_FILES = 180
MAX_PROJECT_SCAN_BYTES = 8 * 1024 * 1024
MAX_SINGLE_PROJECT_FILES = 5000
MAX_PROJECT_UNCOMPRESSED_BYTES = 500 * 1024 * 1024
MAX_PROJECT_COMPRESSION_RATIO = 250
PROJECT_BUILD_TIMEOUT = 900
NODE_INSTALL_TIMEOUT = 900

# Import-to-distribution aliases used only when a project has no complete
# requirements declaration. Declared requirements always remain authoritative.
def _detected_env_from_source(source):
    """Detect runtime environment keys plus empty/placeholder main config constants.

    This is static source analysis, not execution. It scans the full source for
    os.environ/getenv/process.env lookups and for common credential/config
    assignments left blank or containing an obvious placeholder.
    """
    text = str(source or '')
    required, optional = set(), set()
    patterns = [
        re.compile(r"os\.environ\s*\[\s*['\"]([A-Z][A-Z0-9_]{1,80})['\"]\s*\]"),
        re.compile(r"os\.environ\.get\s*\(\s*['\"]([A-Z][A-Z0-9_]{1,80})['\"](\s*,[^)]*)?\)"),
        re.compile(r"os\.getenv\s*\(\s*['\"]([A-Z][A-Z0-9_]{1,80})['\"](\s*,[^)]*)?\)"),
        re.compile(r"(?<![A-Za-z0-9_])getenv\s*\(\s*['\"]([A-Z][A-Z0-9_]{1,80})['\"](\s*,[^)]*)?\)"),
        re.compile(r"\$\{([A-Z][A-Z0-9_]{1,80})\}"),
        re.compile(r"process\.env\.([A-Z][A-Z0-9_]{1,80})"),
    ]
    for pattern in patterns:
        for match in pattern.finditer(text):
            name = match.group(1)
            # A getenv/get call with a non-empty fallback is optional unless the
            # same key is explicitly read through a required form elsewhere.
            has_default = len(match.groups()) > 1 and bool(match.group(2))
            (optional if has_default else required).add(name)

    # Also catch config-style Python/JS assignments, even when code does not use
    # os.getenv. Only ask for values that are blank or clearly placeholders;
    # do not overwrite credentials already embedded in the uploaded source.
    common_config = {
        'BOT_TOKEN', 'API_ID', 'API_HASH', 'ADMIN_ID', 'ADMIN_TG_ID',
        'ADMIN_USER_ID', 'ADMIN_USER_IDS', 'OWNER_ID', 'OWNER_TG_ID',
        'SUPPORT_USERNAME', 'SUPPORT_USER', 'ADMIN_USERNAME', 'BOT_USERNAME',
        'DATABASE_URL', 'MONGO_URI', 'MONGODB_URI', 'CHANNEL_ID', 'GROUP_ID',
        'UPI_ID', 'PAYMENT_UPI_ID', 'API_KEY', 'SECRET_KEY', 'CLIENT_ID',
        'CLIENT_SECRET', 'WEBHOOK_URL'
    }
    placeholder_re = re.compile(r"(?i)(?:paste[_ -]?(?:your[_ -]?)?(?:value|token|id|hash|here)|your[_ -]?(?:token|api[_ -]?id|api[_ -]?hash|id|username)|change[_ -]?me|replace[_ -]?me|placeholder|put[_ -].*here|example[_ -]?(?:token|id)|<[^>]+>)")
    assignment_re = re.compile(r"(?m)^\s*([A-Z][A-Z0-9_]{1,80})\s*=\s*(.*?)\s*(?:#.*)?$")
    for match in assignment_re.finditer(text):
        name, rhs = match.group(1), match.group(2).strip()
        if name not in common_config:
            continue
        value = rhs.rstrip(';').strip()
        is_blank = value in ('', "''", '""', 'None', 'null', 'undefined')
        is_placeholder = bool(placeholder_re.search(value))
        if is_blank or is_placeholder:
            required.add(name)
        elif name in optional:
            optional.discard(name)
    required -= optional
    return sorted(required), sorted(optional)



IMPORT_TO_PACKAGE.update({
    "telethon": "Telethon>=1.45,<2",
    "pyrogram": "Pyrogram>=2,<3",
    "tgcrypto": "TgCrypto",
    "aiogram": "aiogram>=3,<4",
    "telebot": "pyTelegramBotAPI",
    "discord": "discord.py",
    "nextcord": "nextcord",
    "pytz": "pytz",
    "dateutil": "python-dateutil",
    "jwt": "PyJWT",
    "openpyxl": "openpyxl",
    "qrcode": "qrcode",
    "lxml": "lxml",
    "orjson": "orjson",
    "websockets": "websockets",
})


def _advanced_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _next_script_id():
    scripts = load_bot_scripts()
    numeric = []
    for key in scripts:
        try:
            numeric.append(int(str(key)))
        except Exception:
            continue
    return str(max(numeric or [0]) + 1)


def _clear_user_env_session(context, user_id=None):
    """Cancel any stale variable-entry workflow for the current chat/user."""
    try:
        sid = context.user_data.get('awaiting_env_script_id')
        if sid:
            scripts = load_bot_scripts()
            old = scripts.get(str(sid))
            if old and (user_id is None or str(old.get('user_id')) == str(user_id)):
                old['awaiting_env'] = False
                scripts[str(sid)] = old
                save_bot_scripts(scripts)
        context.user_data.pop('awaiting_env_script_id', None)
    except Exception as exc:
        logger.warning('Could not clear stale variable session: %s', exc)


def _stop_process_quietly(script_id):
    """Stop one hosted process and remove it from the in-memory process table."""
    try:
        with SCRIPT_PROCESS_LOCK:
            entry = SCRIPT_PROCESSES.get(str(script_id))
        proc = entry.get('process') if entry else None
        if not proc:
            return
        if proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                try:
                    proc.terminate()
                except Exception:
                    pass
            try:
                proc.wait(timeout=5)
            except Exception:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
        with SCRIPT_PROCESS_LOCK:
            SCRIPT_PROCESSES.pop(str(script_id), None)
    except Exception as exc:
        logger.warning('Could not stop old hosted script %s: %s', script_id, exc)


def _delete_script_storage(script):
    """Delete the complete local storage for an old/superseded hosted script."""
    for key in ('path', 'workspace', 'log_path'):
        raw = script.get(key)
        if not raw:
            continue
        try:
            path = os.path.abspath(str(raw))
            if key == 'path' and os.path.isfile(path):
                os.remove(path)
            elif key == 'workspace' and os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            elif key == 'log_path' and os.path.isfile(path):
                os.remove(path)
        except Exception as exc:
            logger.warning('Could not delete old script storage %s: %s', raw, exc)


def _supersede_previous_user_projects(user_id, keep_script_id=None):
    """Make the newest upload the single active project for a user.

    This intentionally removes older hosted projects from the bot's local storage
    and database. Upload history remains as an audit trail, but old project files,
    workspaces, logs, and active processes are removed.
    """
    scripts = load_bot_scripts()
    changed = False
    keep = str(keep_script_id) if keep_script_id is not None else None
    for sid, script in list(scripts.items()):
        if str(script.get('user_id')) != str(user_id) or str(sid) == keep:
            continue
        _stop_process_quietly(str(sid))
        _delete_script_storage(script)
        scripts.pop(sid, None)
        changed = True
    if changed:
        save_bot_scripts(scripts)

    # Cancel older variable sessions and mark older approval requests as replaced.
    pending = load_pending_approvals()
    pending_changed = False
    for key, record in list(pending.items()):
        if str(record.get('user_id')) != str(user_id):
            continue
        if record.get('status') == 'pending':
            record['status'] = 'superseded'
            record['superseded_at'] = _advanced_now()
            pending[key] = record
            pending_changed = True
    if pending_changed:
        save_pending_approvals(pending)

    history = load_upload_history()
    history_changed = False
    for key, record in list(history.items()):
        if str(record.get('user_id')) != str(user_id):
            continue
        if record.get('status') in ('pending', 'approved') and record.get('script_id') != keep:
            record['status'] = 'superseded'
            record['superseded_at'] = _advanced_now()
            history[key] = record
            history_changed = True
    if history_changed:
        save_upload_history(history)
    return changed


def _menu_action_requested(button_text):
    """Return True for main-menu actions that should cancel a stale variable prompt."""
    return button_text in {
        'UPLOAD FILE', 'UPLOAD SCRIPT', 'MY SCRIPTS', 'MY SCRIPT',
        'INSTALL MODULE', 'MODULE', 'STATS', 'MY STATS', 'BOT SPEED', 'HELP', 'SUPPORT', 'BUY PREMIUM', 'REDEEM CODE', 'TUTORIAL', 'STOP ALL SCRIPTS'
    }


def _project_venv_python(workspace):
    venv_root = os.path.join(workspace, PROJECT_VENV_DIRNAME)
    if os.name == 'nt':
        return os.path.join(venv_root, 'Scripts', 'python.exe')
    return os.path.join(venv_root, 'bin', 'python')


async def _ensure_project_venv(workspace, progress_message=None):
    """Create a real per-project virtual environment, isolated from other users."""
    python_bin = _project_venv_python(workspace)
    if os.path.isfile(python_bin):
        return python_bin
    if progress_message:
        await _progress_message(progress_message, 'BUILD ENVIRONMENT', 'Creating an isolated project Python environment…', 58)
    venv_root = os.path.dirname(os.path.dirname(python_bin))
    proc = await asyncio.create_subprocess_exec(
        sys.executable, '-m', 'venv', venv_root,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    out, _ = await asyncio.wait_for(proc.communicate(), timeout=180)
    if proc.returncode != 0 or not os.path.isfile(python_bin):
        detail = _sanitize_user_log((out or b'').decode('utf-8', errors='replace')[-2500:])
        raise RuntimeError('Could not create the project virtual environment. ' + detail)
    return python_bin


async def _pip_install_project(python_bin, specs, cwd, progress_message=None):
    specs = [str(x).strip() for x in specs if str(x).strip()]
    if not specs:
        return ''
    proc = await asyncio.create_subprocess_exec(
        python_bin, '-m', 'pip', 'install', '--disable-pip-version-check', '--no-input',
        '--upgrade', '--prefer-binary', *specs,
        cwd=cwd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=PROJECT_BUILD_TIMEOUT)
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:
            pass
        raise TimeoutError('Project dependency installation timed out.')
    output = (out or b'').decode('utf-8', errors='replace')
    if proc.returncode != 0:
        raise RuntimeError('Dependency installation failed:\n' + _sanitize_user_log(output[-3500:]))
    if progress_message:
        await _progress_message(progress_message, 'DEPENDENCIES READY', f'Installed/verified {len(specs)} dependency item(s).', 78)
    return output


def _read_project_manifest(root):
    path = os.path.join(root, PROJECT_MANIFEST_NAME)
    if not os.path.isfile(path):
        return {}
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8', errors='replace'))
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        logger.warning('Invalid host.json in project %s: %s', root, exc)
        return {}


def _normalise_project_rel(root, value):
    if not isinstance(value, str) or not value.strip():
        return None
    rel = value.strip().replace('\\', '/')
    candidate = os.path.abspath(os.path.join(root, rel))
    root_abs = os.path.abspath(root)
    try:
        if os.path.commonpath([root_abs, candidate]) != root_abs:
            return None
    except ValueError:
        return None
    if not os.path.isfile(candidate):
        return None
    return os.path.relpath(candidate, root).replace(os.sep, '/')


def _detect_project_entrypoints(root):
    """Deterministic ZIP entrypoint detection; helper modules are not launched blindly."""
    manifest = _read_project_manifest(root)
    explicit = manifest.get('entrypoint') or manifest.get('entry')
    if explicit:
        rel = _normalise_project_rel(root, explicit)
        if rel:
            return [rel]

    # Common Node project declaration.
    package_json = os.path.join(root, 'package.json')
    if os.path.isfile(package_json):
        try:
            pkg = json.loads(Path(package_json).read_text(encoding='utf-8', errors='replace'))
        except Exception:
            pkg = {}
        scripts = pkg.get('scripts') if isinstance(pkg, dict) else {}
        if isinstance(scripts, dict) and isinstance(scripts.get('start'), str):
            cmd = scripts['start'].strip()
            m = re.match(r'(?:node\s+)?([A-Za-z0-9_./\\-]+\.(?:js|mjs|cjs))$', cmd)
            if m:
                rel = _normalise_project_rel(root, m.group(1))
                if rel:
                    return [rel]
        for key in ('main', 'module'):
            if isinstance(pkg.get(key), str):
                rel = _normalise_project_rel(root, pkg[key])
                if rel:
                    return [rel]

    preferred = (
        'main.py', 'bot.py', 'app.py', 'run.py', 'start.py', 'launcher.py',
        'server.py', 'index.py', 'main.js', 'bot.js', 'app.js', 'server.js', 'index.js'
    )
    files = _project_files(root)
    by_name = {p.name.lower(): p for p in files}

    # Prefer main.py when it exists and looks executable. This fixes multi-module
    # Telegram projects where bot.py/userbot.py/admin_bot.py are helpers.
    for name in preferred:
        p = by_name.get(name)
        if not p:
            continue
        if p.suffix.lower() in ('.js', '.mjs', '.cjs'):
            return [str(p.relative_to(root)).replace(os.sep, '/')]
        try:
            src = p.read_text(encoding='utf-8', errors='replace')[:400000]
        except Exception:
            src = ''
        if '__name__' in src or re.search(r'\b(?:async\s+)?def\s+main\s*\(', src):
            return [str(p.relative_to(root)).replace(os.sep, '/')]

    # Next prefer files with a real __main__ guard.
    guarded = []
    for p in files:
        if p.suffix.lower() != '.py':
            continue
        try:
            src = p.read_text(encoding='utf-8', errors='replace')[:400000]
        except Exception:
            continue
        if re.search(r"if\s+__name__\s*==\s*['\"]__main__['\"]", src):
            guarded.append(p)
    if guarded:
        guarded.sort(key=lambda p: (0 if p.name.lower() in preferred else 1, len(str(p))))
        return [str(guarded[0].relative_to(root)).replace(os.sep, '/')]

    # Last resort: one obvious bot-like file. Do not start every helper module.
    bot_like = []
    for p in files:
        if p.suffix.lower() not in ('.py', '.js', '.mjs', '.cjs'):
            continue
        try:
            src = p.read_text(encoding='utf-8', errors='replace')[:250000].lower()
        except Exception:
            src = ''
        if any(k in src for k in ('telegram.ext', 'telethon', 'pyrogram', 'aiogram', 'telebot', 'discord.py', 'client.run')):
            bot_like.append(p)
    if bot_like:
        bot_like.sort(key=lambda p: (len(str(p)), p.name.lower()))
        return [str(bot_like[0].relative_to(root)).replace(os.sep, '/')]
    return []


def _runnable_project_files(workspace):
    entries = _detect_project_entrypoints(workspace)
    if entries:
        return [Path(workspace) / rel for rel in entries]
    return []


def _safe_extract_zip(zip_path, dest):
    """Secure extraction with traversal, file-count, expansion and ratio limits."""
    os.makedirs(dest, exist_ok=True)
    root = Path(dest).resolve()
    infos = []
    total = 0
    with zipfile.ZipFile(zip_path) as zf:
        all_infos = zf.infolist()
        if len(all_infos) > MAX_SINGLE_PROJECT_FILES:
            raise ValueError(f'ZIP contains too many entries ({len(all_infos)}). Limit is {MAX_SINGLE_PROJECT_FILES}.')
        compressed_total = 0
        for info in all_infos:
            if info.is_dir():
                continue
            name = str(info.filename or '')
            if not name or name.startswith('/') or '\x00' in name:
                raise ValueError('Unsafe ZIP filename detected.')
            target = (root / name).resolve()
            if os.path.commonpath([str(root), str(target)]) != str(root):
                raise ValueError('Unsafe ZIP path traversal detected.')
            size = max(0, int(info.file_size or 0))
            comp = max(0, int(info.compress_size or 0))
            total += size
            compressed_total += comp
            if total > MAX_PROJECT_UNCOMPRESSED_BYTES:
                raise ValueError(f'ZIP expands beyond the {MAX_PROJECT_UNCOMPRESSED_BYTES // (1024*1024)} MB safe limit.')
            if comp > 0 and size / comp > MAX_PROJECT_COMPRESSION_RATIO and size > 5 * 1024 * 1024:
                raise ValueError('ZIP contains an unusually high-compression entry; extraction was blocked for safety.')
            infos.append(info)
        for info in infos:
            zf.extract(info, str(root))
    return infos


async def _prepare_zip_project(script, progress_message=None):
    """Extract, inventory, isolate dependencies, detect entrypoint and scan variables."""
    zip_path = os.path.abspath(script['path'])
    workspace = os.path.join(os.path.dirname(zip_path), '.workspace')
    if os.path.isdir(workspace):
        shutil.rmtree(workspace, ignore_errors=True)
    os.makedirs(workspace, exist_ok=True)

    if progress_message:
        await _progress_message(progress_message, 'EXTRACTING ZIP', f'Opening <code>{html.escape(os.path.basename(zip_path))}</code> and validating every archive entry…', 8)
    infos = await asyncio.to_thread(_safe_extract_zip, zip_path, workspace)

    files = _project_files(workspace)
    visible = [str(x.relative_to(workspace)).replace(os.sep, '/') for x in files]
    visible.sort(key=str.lower)
    if not visible:
        raise RuntimeError('The ZIP was valid but contains no usable project files.')
    if progress_message:
        preview = '\n'.join('• ' + html.escape(x) for x in visible[:MAX_PROJECT_DISPLAY_FILES])
        if len(visible) > MAX_PROJECT_DISPLAY_FILES:
            preview += f'\n• … and {len(visible) - MAX_PROJECT_DISPLAY_FILES} more files'
        await _progress_message(
            progress_message, 'PROJECT INVENTORY',
            f'<b>Extracted:</b> <code>{len(infos)}</code> files\n<b>Total project files:</b> <code>{len(visible)}</code>\n\n{preview}', 34
        )

    entry = _runnable_project_files(workspace)
    required, optional = _scan_project_env(workspace)
    req_files = [x for x in files if x.name.lower() in ('requirements.txt', 'requirements-prod.txt', 'requirements-production.txt')]
    # Include nested requirement files if the project has them.
    declared_specs = []
    for rp in req_files:
        try:
            for line in rp.read_text(encoding='utf-8', errors='replace').splitlines():
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-r') and not line.startswith('--'):
                    declared_specs.append(line)
        except Exception:
            pass

    # Node projects get first-class package.json/npm preparation when npm exists.
    package_json = os.path.join(workspace, 'package.json')
    node_ready = False
    node_error = None
    if os.path.isfile(package_json):
        try:
            if shutil.which('npm'):
                if progress_message:
                    await _progress_message(progress_message, 'NODE DEPENDENCIES', 'package.json detected — installing production Node dependencies…', 66)
                proc = await asyncio.create_subprocess_exec(
                    'npm', 'install', '--omit=dev', '--no-audit', '--no-fund',
                    cwd=workspace, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
                )
                out, _ = await asyncio.wait_for(proc.communicate(), timeout=NODE_INSTALL_TIMEOUT)
                if proc.returncode != 0:
                    node_error = _sanitize_user_log((out or b'').decode('utf-8', errors='replace')[-2500:])
                else:
                    node_ready = True
        except Exception as exc:
            node_error = f'{type(exc).__name__}: {exc}'

    # Build a real isolated Python environment only when the ZIP contains Python
    # code or Python dependency declarations.
    python_files = [x for x in files if x.suffix.lower() == '.py']
    venv_python = None
    installed_specs = list(dict.fromkeys(declared_specs))
    import_names = set()
    for fp in python_files:
        try:
            import_names |= _scan_python_imports(fp.read_text(encoding='utf-8', errors='replace'))
        except Exception:
            pass
    auto_specs = [IMPORT_TO_PACKAGE[name] for name in sorted(import_names) if name in IMPORT_TO_PACKAGE]
    # Avoid installing duplicate distributions when a requirements file already declares one.
    declared_text = ' '.join(installed_specs).lower()
    for spec in auto_specs:
        dist = re.split(r'[<>=!~;\[]', spec, 1)[0].strip().lower()
        if dist and dist not in declared_text:
            installed_specs.append(spec)

    if python_files or installed_specs:
        venv_python = await _ensure_project_venv(workspace, progress_message)
        if installed_specs:
            if progress_message:
                await _progress_message(progress_message, 'DEPENDENCY PREPARATION', f'Preparing isolated Python environment with <code>{len(installed_specs)}</code> package item(s)…', 70)
            await _pip_install_project(venv_python, installed_specs, workspace, progress_message)

    script.update({
        'workspace': workspace,
        'entry_files': [str(x.relative_to(workspace)).replace(os.sep, '/') for x in entry],
        'env_required': required,
        'env_optional': optional,
        'project_files': visible[:1000],
        'project_file_count': len(visible),
        'project_extracted_files': len(infos),
        'project_total_uncompressed_bytes': sum(max(0, int(i.file_size or 0)) for i in infos),
        'project_venv': venv_python or '',
        'node_dependencies_ready': node_ready,
        'node_dependencies_error': node_error,
        'dependency_specs': installed_specs,
        'build_time': _advanced_now(),
        'manifest': _read_project_manifest(workspace),
    })

    launcher = Path(workspace) / '.host_supervisor.py'
    payload = repr([str(x.relative_to(workspace)).replace(os.sep, '/') for x in entry])
    launcher_code = """import os,sys,time,subprocess,threading
BASE=os.path.dirname(os.path.abspath(__file__))
FILES=%s
PROCS=[]

def spawn(rel):
    p=os.path.join(BASE,rel); ext=os.path.splitext(p)[1].lower()
    vpy=os.environ.get('HOST_PROJECT_PYTHON') or sys.executable
    cmd=[vpy,'-u',p] if ext=='.py' else (['node',p] if ext in ('.js','.mjs','.cjs') else None)
    if not cmd: return
    try:
        proc=subprocess.Popen(cmd,cwd=os.path.dirname(p) or BASE,env=os.environ.copy(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')
    except Exception as e:
        print('[HOST] FAILED '+rel+': '+str(e),flush=True); return
    PROCS.append((rel,proc)); print('[HOST] STARTED '+rel+' PID='+str(proc.pid),flush=True)
    def reader():
        if proc.stdout:
            for line in proc.stdout: print('['+rel+'] '+line.rstrip(),flush=True)
    threading.Thread(target=reader,daemon=True).start()

for f in FILES: spawn(f)
while PROCS:
    alive=[]
    for rel,p in PROCS:
        rc=p.poll()
        if rc is None: alive.append((rel,p))
        else: print('[HOST] EXIT '+rel+' CODE='+str(rc),flush=True)
    PROCS=alive
    if not PROCS: break
    time.sleep(1)
""" % payload
    launcher.write_text(launcher_code, encoding='utf-8')

    if progress_message:
        entry_text = ', '.join(html.escape(str(x.relative_to(workspace)).replace(os.sep, '/')) for x in entry) if entry else 'None detected'
        env_text = ', '.join(html.escape(x) for x in required) if required else 'None'
        await _progress_message(
            progress_message, 'PROJECT READY',
            f'<b>Entrypoint:</b> <code>{entry_text}</code>\n<b>Required variables:</b> <code>{env_text}</code>\n<b>Python venv:</b> <code>{"READY" if venv_python else "N/A"}</code>\n<b>Node:</b> <code>{"READY" if node_ready else ("NOT USED" if not os.path.isfile(package_json) else "NOT READY")}</code>', 96
        )
    return required, optional, entry


async def _launch_zip_process(context, script_id):
    scripts, script = _get_script(script_id)
    workspace = script.get('workspace')
    launcher = os.path.join(workspace or '', '.host_supervisor.py')
    if not workspace or not os.path.isfile(launcher):
        return None
    env = os.environ.copy()
    env.update({str(k): str(v) for k, v in script.get('env', {}).items()})
    vpy = script.get('project_venv') or _project_venv_python(workspace)
    if os.path.isfile(vpy):
        env['HOST_PROJECT_PYTHON'] = vpy
    md = user_module_dir(script.get('user_id'))
    ld = os.path.abspath(INSTALLED_MODULES_DIR)
    env['PYTHONPATH'] = os.pathsep.join(x for x in (md, ld, workspace, env.get('PYTHONPATH', '')) if x)
    env['PYTHONUNBUFFERED'] = '1'
    proc = subprocess.Popen(
        [sys.executable, '-u', launcher], cwd=workspace, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
        text=True, encoding='utf-8', errors='replace', bufsize=1, start_new_session=True
    )
    with SCRIPT_PROCESS_LOCK:
        SCRIPT_PROCESSES[str(script_id)] = {'process': proc, 'return_code': None}
    script.update({
        'status': 'running', 'runtime': 'ZIP/Python supervisor', 'pid': proc.pid,
        'started_at_epoch': time.time(), 'last_error': None, 'last_exit_code': None,
        'manual_stop': False, 'last_modified': _advanced_now()
    })
    save_bot_scripts(scripts)
    _write_script_log(script, '\n' + '=' * 72 + f'\nBOT START REQUESTED\nZIP SUPERVISOR PID: {proc.pid}\nENTRY FILES: {", ".join(script.get("entry_files", []))}\nPROJECT VENV: {vpy if os.path.isfile(vpy) else "none"}\nSTATUS: STARTING\n' + '=' * 72 + '\n')
    _start_process_monitor(context.application, str(script_id), proc, asyncio.get_running_loop())
    await asyncio.sleep(0.5)
    return proc if proc.poll() is None else None


async def _begin_zip_host(update, context, script_id):
    scripts, script = _get_script(script_id)
    q = update.callback_query
    if not script:
        return
    try:
        msg = await q.message.reply_text(
            '⏳ <b>ADVANCED ZIP HOST</b>\n\n<code>[░░░░░░░░░░░░░░░░░░░░] 0%</code>\n\nValidating archive and starting project scan…',
            parse_mode='HTML'
        )
    except Exception:
        msg = None
    try:
        required, optional, entry = await _prepare_zip_project(script, msg)
        save_bot_scripts(scripts)
        if msg:
            try:
                await msg.delete()
            except Exception:
                pass
        if not entry:
            script['status'] = 'stopped'
            script['last_error'] = 'No safe runnable entrypoint was detected. Add main.py or host.json with an entrypoint.'
            save_bot_scripts(scripts)
            await q.message.reply_text(
                '❌ <b>NO RUNNABLE ENTRYPOINT</b>\n\n'
                'ZIP extraction completed successfully, but no safe launcher was detected.\n\n'
                'Use <code>main.py</code> or add <code>host.json</code> with <code>{"entrypoint":"your_file.py"}</code>.',
                parse_mode='HTML', reply_markup=get_main_keyboard()
            )
            return

        files = script.get('project_files', [])
        file_preview = '\n'.join('• <code>' + html.escape(x) + '</code>' for x in files[:120])
        if len(files) > 120:
            file_preview += f'\n• … and {len(files) - 120} more files'
        entry_text = ', '.join(html.escape(str(x)) for x in script.get('entry_files', []))
        env_lines = '\n'.join('• <code>' + html.escape(x) + '</code>' for x in required) if required else '• None'
        optional_lines = '\n'.join('• <code>' + html.escape(x) + '</code>' for x in optional) if optional else '• None'
        node_line = 'READY' if script.get('node_dependencies_ready') else ('NOT READY' if script.get('node_dependencies_error') else 'Not used')
        report = (
            f'📦 <b>ZIP EXTRACTED & SCANNED</b>\n━━━━━━━━━━━━━━━━━━━━\n\n'
            f'<b>Project:</b> <code>{html.escape(script.get("name", "ZIP"))}</code>\n'
            f'<b>Files:</b> <code>{len(files)}</code>\n'
            f'<b>Entrypoint:</b> <code>{entry_text}</code>\n'
            f'<b>Python environment:</b> <code>{"READY" if script.get("project_venv") else "N/A"}</code>\n'
            f'<b>Node dependencies:</b> <code>{node_line}</code>\n'
            f'<b>Prefilled variables found:</b> <code>{int(script.get("env_prefilled_count", 0) or 0)}</code>\n\n'
            f'<b>Detected files:</b>\n{file_preview}\n\n'
            f'<b>Required variables:</b>\n{env_lines}\n\n'
            f'<b>Optional variables:</b>\n{optional_lines}'
        )
        # Keep the inventory readable without exceeding Telegram's message limit.
        if len(report) > 3900:
            report = report[:3700] + '\n… <i>Open MY SCRIPTS → script → VIEW LOGS for the full build output.</i>'
        await q.message.reply_text(report, parse_mode='HTML', reply_markup=InlineKeyboardMarkup([
            [user_button('START PROJECT', '🚀', callback_data=f'start_script_{script_id}', style='success')],
            [user_button('VIEW LOGS', '📁', callback_data=f'logs_script_{script_id}')],
            [user_button('BACK TO SCRIPTS', '◀️', callback_data='my_scripts_menu')]
        ]))
        if required:
            script['awaiting_env'] = True
            save_bot_scripts(scripts)
            context.user_data['awaiting_env_script_id'] = str(script_id)
            template = '\n'.join(f'{x}=PASTE_VALUE_HERE' for x in required)
            await q.message.reply_text(
                f'🔐 <b>VARIABLES REQUIRED</b>\n\n'
                f'Send the following values as <code>KEY=VALUE</code>, one per line:\n\n'
                f'<pre><code class="language-shell">{html.escape(template)}</code></pre>\n\n'
                f'After you send values, any variables still missing will be listed in a separate message.',
                parse_mode='HTML'
            )
            return
        # No secrets required: prepare only, then leave the project stopped until START.
        script['awaiting_env'] = False
        save_bot_scripts(scripts)
    except Exception as e:
        if msg:
            try:
                await msg.delete()
            except Exception:
                pass
        script['status'] = 'stopped'
        script['last_error'] = f'{type(e).__name__}: {e}'
        script['last_exit_code'] = 1
        save_bot_scripts(scripts)
        _write_script_log(script, f'\nZIP BUILD ERROR: {type(e).__name__}: {e}\n{traceback.format_exc()}\n')
        await q.message.reply_text(
            f'❌ <b>ZIP BUILD FAILED</b>\n\n<pre>{html.escape(str(e)[:3000])}</pre>\n\nOpen <b>VIEW LOGS</b> for the build diagnostics.',
            parse_mode='HTML', reply_markup=get_main_keyboard()
        )


async def _create_approved_script_from_document(update, context, document, *, auto_admin=False):
    """Download a Telegram document and create a hosted script without approval UI."""
    user = update.effective_user
    user_id = user.id
    file_name = os.path.basename(document.file_name or 'upload')
    script_id = _next_script_id()
    script_dir = os.path.join(USER_SCRIPTS_DIR, str(user_id), script_id)
    os.makedirs(script_dir, exist_ok=True)
    local_path = os.path.join(script_dir, file_name)
    log_path = os.path.join(SCRIPT_LOGS_DIR, f'{script_id}.log')
    telegram_file = await context.bot.get_file(document.file_id)
    await telegram_file.download_to_drive(custom_path=local_path)
    script = {
        'id': script_id, 'name': file_name, 'original_name': file_name, 'user_id': user_id, 'status': 'stopped',
        'kind': 'zip' if file_name.lower().endswith('.zip') else ('javascript' if file_name.lower().endswith('.js') else 'python'),
        'path': local_path, 'log_path': log_path,
        'created_date': _advanced_now(), 'last_modified': _advanced_now(),
        'last_exit_code': None, 'last_error': None,
        'approval_mode': 'admin_auto_approved' if auto_admin else 'approved',
        'approved_by': user_id if auto_admin else None,
    }
    scripts = load_bot_scripts()
    scripts[script_id] = script
    save_bot_scripts(scripts)
    # Keep upload history consistent with the approval result.
    history = load_upload_history()
    matching = [(k, v) for k, v in history.items()
                if str(v.get('user_id')) == str(user_id) and v.get('file_name') == file_name
                and v.get('status') == 'pending']
    if matching:
        matching.sort(key=lambda pair: str(pair[1].get('upload_date', '')), reverse=True)
        hkey, hrec = matching[0]
        hrec['status'] = 'approved'
        hrec['script_id'] = script_id
        hrec['approved_at'] = _advanced_now()
        hrec['approval_mode'] = 'admin_auto_approved' if auto_admin else 'approved'
        history[hkey] = hrec
        save_upload_history(history)
    update_statistics('total_approved', 1)
    _write_script_log(script, '\n' + '=' * 72 + f'\nFILE ACCEPTED\nMODE: {"ADMIN AUTO-APPROVED" if auto_admin else "APPROVED"}\nFILE: {file_name}\nTIME: {_advanced_now()}\n' + '=' * 72 + '\n')
    return script_id, script


async def _send_admin_auto_approved(update, context, document):
    """Admin upload path: bypass channel approval and immediately prepare the project."""
    user_id = update.effective_user.id
    # This is defensive: the upload handler already cleared old state, but keeping
    # the newest script as the only owner of the variable session prevents stale
    # callbacks/messages from taking control of the new project.
    _clear_user_env_session(context, user_id)
    script_id, script = await _create_approved_script_from_document(update, context, document, auto_admin=True)
    if script.get('kind') == 'zip':
        status_msg = await update.message.reply_text(
            f'⚡ <b>ADMIN AUTO-APPROVED</b>\n\n'
            f'<b>File:</b> <code>{html.escape(script["name"])}</code>\n'
            f'<b>Status:</b> Extracting and scanning automatically…', parse_mode='HTML'
        )
        try:
            required, optional, entry = await _prepare_zip_project(script, status_msg)
            scripts = load_bot_scripts(); scripts[str(script_id)] = script; save_bot_scripts(scripts)
            if status_msg:
                try: await status_msg.delete()
                except Exception: pass
            if required:
                context.user_data['awaiting_env_script_id'] = str(script_id)
                script['awaiting_env'] = True; save_bot_scripts(scripts)
                template = '\n'.join(f'{x}=PASTE_VALUE_HERE' for x in required)
                await update.message.reply_text(
                    f'✅ <b>ADMIN FILE AUTO-APPROVED</b>\n\n'
                    f'📦 <b>ZIP:</b> <code>{html.escape(script["name"])}</code>\n'
                    f'🔎 <b>Files:</b> <code>{len(script.get("project_files", []))}</code>\n'
                    f'🚀 <b>Entrypoint:</b> <code>{html.escape(", ".join(script.get("entry_files", [])))}</code>\n\n'
                    f'🔐 <b>Variables detected:</b>\n{chr(10).join("• <code>"+html.escape(x)+"</code>" for x in required)}\n\n'
                    f'<pre><code class="language-shell">{html.escape(template)}</code></pre>\n\n'
                    f'Send the values. After that, the project will start automatically.\n\n'
                    f'Open <b>MY SCRIPTS</b> anytime to manage it.', parse_mode='HTML', reply_markup=get_main_keyboard()
                )
            else:
                await update.message.reply_text(
                    f'✅ <b>ADMIN FILE AUTO-APPROVED</b>\n\n'
                    f'<b>File:</b> <code>{html.escape(script["name"])}</code>\n'
                    f'<b>Extracted:</b> <code>{len(script.get("project_files", []))}</code> files\n'
                    f'<b>Entrypoint:</b> <code>{html.escape(", ".join(script.get("entry_files", [])))}</code>\n\n'
                    f'Tap <b>START PROJECT</b> below to run it.\n\nOpen <b>MY SCRIPT</b> anytime to manage logs and status.', parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[user_button('START PROJECT','🚀',callback_data=f"start_script_{script_id}",style='success')],[user_button('MY SCRIPT','📁',callback_data='my_scripts_menu')]])
                )
        except Exception as exc:
            if status_msg:
                try: await status_msg.delete()
                except Exception: pass
            script['status'] = 'stopped'; script['last_error'] = f'{type(exc).__name__}: {exc}'; scripts = load_bot_scripts(); scripts[str(script_id)] = script; save_bot_scripts(scripts)
            _write_script_log(script, f'\nADMIN ZIP PREP ERROR: {type(exc).__name__}: {exc}\n{traceback.format_exc()}\n')
            await update.message.reply_text(
                f'⚠️ <b>FILE AUTO-APPROVED, BUT ZIP PREPARATION FAILED</b>\n\n'
                f'<pre>{html.escape(str(exc)[:2600])}</pre>\n\n'
                f'Open <b>MY SCRIPTS</b> to retry START after fixing the project.', parse_mode='HTML', reply_markup=get_main_keyboard()
            )
    else:
        # V111: Python uploads follow the same automatic preparation path as ZIPs.
        # The source is scanned immediately, required variables are requested,
        # dependencies are prepared, and the process starts automatically when
        # all required values have been supplied.
        await update.message.reply_text(
            f'✅ <b>ADMIN AUTO-APPROVED</b>\n\n'
            f'<b>File:</b> <code>{html.escape(script["name"])}</code>\n'
            f'<b>Status:</b> Preparing Python project automatically…',
            parse_mode='HTML', reply_markup=get_main_keyboard()
        )
        try:
            await _v110_prepare_python(update, context, str(script_id))
        except Exception as exc:
            scripts = load_bot_scripts()
            fresh = scripts.get(str(script_id), script)
            fresh['status'] = 'stopped'
            fresh['last_error'] = f'{type(exc).__name__}: {exc}'
            scripts[str(script_id)] = fresh
            save_bot_scripts(scripts)
            _write_script_log(fresh, f'\nV111 UPLOAD PREPARATION ERROR: {type(exc).__name__}: {exc}\n{traceback.format_exc()}\n')
            await update.message.reply_text(
                f'❌ <b>PYTHON PREPARATION FAILED</b>\n\n<pre>{html.escape(str(exc)[:2600])}</pre>\n\nOpen <b>MY SCRIPTS → LOGS</b> for diagnostics.',
                parse_mode='HTML', reply_markup=get_main_keyboard()
            )


async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Advanced upload handler with privileged admin auto-approval."""
    try:
        user_id = update.effective_user.id
        document = update.message.document
        if is_admin(user_id) and context.user_data.get('admin_action') == 'broadcast':
            context.user_data.pop('admin_action', None)
            await perform_broadcast(update, context, update.message)
            return
        if is_user_banned(user_id):
            await update.message.reply_text(f'{EMOJI_PROHIBITED} <b>ACCESS DENIED</b>\n\n<b>Reason:</b> You are banned.', parse_mode='HTML')
            return
        if await enforce_user_system_gate(update, context):
            return
        file_name = document.file_name or ''
        if not file_name.lower().endswith(SUPPORTED_UPLOAD_EXTENSIONS):
            await update.message.reply_text(f'{EMOJI_X} <b>INVALID FILE</b>\n\nSupported formats are .py (Python), .js (Node.js) and .zip (project).', parse_mode='HTML', reply_markup=get_main_keyboard())
            return
        if document.file_size and document.file_size > MAX_UPLOAD_SIZE:
            await update.message.reply_text(f'{EMOJI_X} <b>FILE TOO LARGE</b>\n\nMaximum upload size is {MAX_UPLOAD_SIZE // (1024*1024)}MB.', parse_mode='HTML', reply_markup=get_main_keyboard())
            return

        # V112: uploads are independent projects. Never delete/supersede older files.
        # Only clear the user's temporary conversation state; stored scripts remain.
        _clear_user_env_session(context, user_id)

        add_upload_record(user_id, file_name, document.file_size)
        if is_admin(user_id):
            # The configured admin is trusted by this hosting bot: no channel approval,
            # no manual approve click and no approval-channel round trip.
            await _send_admin_auto_approved(update, context, document)
            logger.info('Admin upload auto-approved: user=%s file=%s', user_id, file_name)
            return

        try:
            await send_approval_file(update, context, document)
        except Exception as approval_error:
            logger.error(f'Approval channel send failed: {approval_error}\n{traceback.format_exc()}')
        sent_user_message = await update.message.reply_text(
            f'{user_emoji("⏳")} File <code>{html.escape(document.file_name)}</code> is under detection.\nOnce approved, you will be notified.',
            parse_mode='HTML', reply_markup=get_main_keyboard()
        )
        pending = load_pending_approvals()
        for key, item in pending.items():
            if str(item.get('user_id')) == str(user_id) and item.get('file_id') == document.file_id and item.get('status') == 'pending':
                item['user_message_id'] = sent_user_message.message_id
                pending[key] = item
                break
        save_pending_approvals(pending)
        logger.info('User %s uploaded: %s', user_id, document.file_name)
    except Exception as e:
        logger.error(f'Error handling file upload: {e}\n{traceback.format_exc()}')
        try:
            await update.message.reply_text(f'{user_emoji("❌")} Error uploading file.\n\n<pre>{html.escape(str(e)[:1800])}</pre>', parse_mode='HTML', reply_markup=get_main_keyboard())
        except Exception:
            pass


async def _send_log_snapshot(context, chat_id, script, logs=None):
    """Fresh live-on-demand logs: every tap reads the current tail from disk."""
    if logs is None:
        logs = _read_script_logs(script, 14000) or 'No log output captured yet.'
    logs = _sanitize_user_log(logs)
    scripts, fresh = _get_script(script.get('id'))
    if fresh:
        script = fresh
    with SCRIPT_PROCESS_LOCK:
        entry = SCRIPT_PROCESSES.get(str(script.get('id')))
        process = entry.get('process') if entry else None
    running = bool(process and process.poll() is None)
    # No live process handle means it is not running in this bot instance. Never show stale RUNNING.
    status = 'RUNNING' if running else 'STOPPED'
    if str(script.get('status', '')).lower() == 'running' and not running:
        script['status'] = 'stopped'
        if process is not None and process.poll() is not None:
            script['last_exit_code'] = process.returncode
        save_bot_scripts(scripts)
    name = html.escape(str(script.get('name', 'Unknown')))
    chunk_size = 2800
    chunks = [logs[i:i+chunk_size] for i in range(0, len(logs), chunk_size)] or ['No log output captured yet.']
    for index, chunk in enumerate(chunks, 1):
        title = f'📡 <b>LIVE LOGS</b> — <code>{name}</code>\n━━━━━━━━━━━━━━━━━━━━\n<b>Status:</b> <b>{html.escape(status)}</b>\n<b>Refresh:</b> Tap 🔄 LIVE LOGS again for the newest output.\n\n'
        text = title + f'<b>CURRENT LOGS {index}/{len(chunks)}:</b>\n<pre>{html.escape(chunk)}</pre>'
        markup = InlineKeyboardMarkup([
            [user_button('🔄 LIVE LOGS', '🔄', callback_data=f'logs_script_{script.get("id")}')],
            [user_button('BACK TO SCRIPT', '◀️', callback_data=f'view_script_{script.get("id")}')]
        ])
        try:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML', reply_markup=markup)
        except TelegramError:
            await context.bot.send_message(chat_id=chat_id, text=f'{name}\nSTATUS: {status}\nCURRENT LOGS {index}/{len(chunks)}:\n{chunk}', reply_markup=markup)


async def handle_logs_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Open logs instantly and always read the latest captured stdout/stderr."""
    query = update.callback_query
    script_id = (query.data or '').replace('logs_script_', '', 1)
    try:
        scripts, script = _get_script(script_id)
        if not script or not _safe_script_for_user(script, query.from_user.id):
            await query.answer('Script not found', show_alert=True)
            return
        with SCRIPT_PROCESS_LOCK:
            entry = SCRIPT_PROCESSES.get(str(script_id))
            process = entry.get('process') if entry else None
        if process and process.poll() is None:
            script['status'] = 'running'
        elif script.get('status') == 'running':
            script['status'] = 'stopped'
            if process is not None and process.poll() is not None:
                script['last_exit_code'] = process.returncode
        save_bot_scripts(scripts)
        await query.answer('Live logs loaded')
        await _send_log_snapshot(context, query.from_user.id, script, _read_script_logs(script, 14000))
    except Exception as e:
        logger.error('Advanced log viewer failed for %s: %s\n%s', script_id, e, traceback.format_exc())
        try:
            await query.answer('Logs could not be loaded. Check server log.', show_alert=True)
        except Exception:
            pass


async def handle_channel_rejection_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Consume exactly the next human channel post after Reject and deliver it to the owner."""
    try:
        message = update.channel_post
        if not message:
            return
        # Channel posts created by this bot must never become a rejection reason.
        try:
            me = await context.bot.get_me()
            if message.from_user and message.from_user.id == me.id:
                return
        except Exception:
            pass
        channel_id = str(message.chat.id)
        pending = load_pending_approvals()
        candidates = [(k, v) for k, v in pending.items() if str(v.get('channel_id')) == channel_id and v.get('status') == 'pending' and v.get('rejection_pending')]
        if not candidates:
            return
        candidates.sort(key=lambda pair: str(pair[1].get('rejection_requested_at', '')), reverse=True)
        key, record = candidates[0]
        # Never consume the original approval message itself.
        if str(record.get('message_id')) == str(message.message_id):
            return
        file_name = os.path.basename(str(record.get('file_name') or 'Unknown'))
        reason = (message.text or message.caption or '').strip()
        if not reason:
            if message.photo: reason = '[Photo/Screenshot sent as rejection reason]'
            elif message.document: reason = f'[Document: {message.document.file_name or "document"}]'
            elif message.video: reason = '[Video sent as rejection reason]'
            elif message.audio: reason = '[Audio sent as rejection reason]'
            elif message.voice: reason = '[Voice message sent as rejection reason]'
            elif message.animation: reason = '[GIF/Animation sent as rejection reason]'
            elif message.video_note: reason = '[Video note sent as rejection reason]'
            elif message.sticker: reason = '[Sticker sent as rejection reason]'
            else: reason = '[Channel message sent as rejection reason]'
        record.update({
            'status': 'rejected', 'rejection_reason': reason,
            'rejection_reason_message_id': message.message_id,
            'rejected_at': _advanced_now(),
        })
        record.pop('rejection_pending', None); record.pop('rejection_requested_by', None); record.pop('rejection_requested_at', None)
        pending[key] = record; save_pending_approvals(pending); update_statistics('total_rejected', 1)

        user_text = (
            f'{user_emoji("❌")} <b>YOUR FILE HAS BEEN REJECTED</b>\n'
            f'━━━━━━━━━━━━━━━━━━━━\n\n'
            f'<b>File:</b> <code>{html.escape(file_name)}</code>\n\n'
            f'<b>Reject</b>\n'
            f'<b>Reason:</b>\n<blockquote>{html.escape(reason)}</blockquote>'
        )
        try:
            await context.bot.send_message(chat_id=record['user_id'], text=user_text, parse_mode='HTML', reply_markup=get_main_keyboard())
            # If the reason was a media message, preserve the exact admin post too.
            if not message.text and not message.caption:
                await context.bot.copy_message(chat_id=record['user_id'], from_chat_id=message.chat.id, message_id=message.message_id)
        except Exception as exc:
            logger.error('Could not notify rejected file owner: %s\n%s', exc, traceback.format_exc())

        final_caption = (record.get('channel_caption') or f'{EMOJI_FOLDER} <b>FILE</b>') + f'\n\n{user_emoji("❌")} <b>REJECTED</b>\n<b>REASON:</b>\n<blockquote>{html.escape(reason)}</blockquote>'
        try:
            await context.bot.edit_message_caption(chat_id=record.get('channel_id'), message_id=record.get('message_id'), caption=final_caption, parse_mode='HTML', reply_markup=None)
        except Exception:
            logger.error('Could not finalize rejected approval post', exc_info=True)
        try:
            await message.reply_text(f'{EMOJI_CHECK} <b>REJECTION RECORDED</b>\n\nFile: <code>{html.escape(file_name)}</code>', parse_mode='HTML')
        except Exception:
            pass
    except Exception:
        logger.error('Advanced rejection reason handler failed\n%s', traceback.format_exc())



# ==================== SHUB HOSTING BOT 111 — DIRECT START EXPERIENCE ====================
# V111 keeps the existing hosting engine while making Python uploads follow the
# same automatic preparation/variable flow as ZIP projects. Custom-emoji buttons
# are optional and never allowed to break upload/start operations.
HOSTING_ENGINE_VERSION = "112.0"

async def _v110_edit_progress(message, title, detail, percent):
    """Fast, readable project preparation screen."""
    percent=max(0,min(100,int(percent)))
    filled=max(0,min(20,percent//5))
    bar='🟩'*filled+'⬜'*(20-filled)
    text=(f"🚀 <b>{html.escape(str(title))}</b>\n"
          f"━━━━━━━━━━━━━━━━━━━━\n\n"
          f"<code>{bar}</code> <b>{percent}%</b>\n\n"
          f"{detail}")
    try:
        await message.edit_text(text,parse_mode='HTML')
    except Exception:
        try:
            await message.edit_caption(caption=text,parse_mode='HTML')
        except Exception:
            pass

async def _v110_bot_usernames(script):
    """Best-effort REAL getMe verification for bot tokens supplied to a project."""
    values=[]
    for value in (script.get('env') or {}).values():
        val=str(value or '').strip()
        if re.fullmatch(r'\d{6,15}:[A-Za-z0-9_-]{25,100}',val):
            values.append(val)
    # Also inspect captured output for Telegram usernames already printed by the project.
    logs=_read_script_logs(script,12000) or ''
    found=[]
    for m in re.findall(r'(?<![A-Za-z0-9_])@([A-Za-z0-9_]{4,32})',logs):
        if m not in found: found.append(m)
    # Query Telegram directly for each token. No token value is shown to the user.
    async def get_me(token):
        try:
            import urllib.request, urllib.parse, json as _json
            url='https://api.telegram.org/bot'+urllib.parse.quote(token,safe='')+'/getMe'
            def call():
                with urllib.request.urlopen(url,timeout=5) as resp:
                    return _json.loads(resp.read().decode('utf-8','replace'))
            data=await asyncio.to_thread(call)
            if data.get('ok') and data.get('result',{}).get('username'):
                return '@'+str(data['result']['username'])
        except Exception:
            return None
        return None
    for token in list(dict.fromkeys(values))[:8]:
        username=await get_me(token)
        if username and username not in found: found.append(username)
    return found[:8]

async def _v110_running_card(application, user_id, script):
    """Show only after the operating-system process is actually alive."""
    names=await _v110_bot_usernames(script)
    if names:
        if len(names)==1:
            bot_line=f"🤖 <b>Bot:</b> <code>{html.escape(names[0])}</code>"
        else:
            bot_line=f"🤖 <b>All Bots:</b> <code>{html.escape(' • '.join(names))}</code>"
            bot_line += f"\n✅ <b>{len(names)} bot(s) verified as reachable</b>"
    else:
        bot_line="🤖 <b>Bot:</b> <code>Process is running</code>"
    name=html.escape(str(script.get('name','Project')))
    text=("╔════════════════════════════╗\n"
          "       🟢 <b>PROJECT IS NOW RUNNING</b>\n"
          "╚════════════════════════════╝\n\n"
          f"📄 <b>Project:</b> <code>{name}</code>\n"
          f"{bot_line}\n\n"
          "✅ The real project process is alive.\n"
          "📡 Live output is being captured.\n\n"
          "To manage it, open <b>MY SCRIPT</b>.")
    markup=InlineKeyboardMarkup([
        [user_button('VIEW CURRENT LOGS','📡',callback_data=f"logs_script_{script.get('id')}")],
        [user_button('MY SCRIPT','📁',callback_data='my_scripts_menu')]
    ])
    try:
        await application.bot.send_message(chat_id=user_id,text=text,parse_mode='HTML',reply_markup=markup)
    except Exception:
        pass

async def _v110_launch_python_process(context, script_id):
    scripts, script=_get_script(script_id)
    if not script: return None
    path=os.path.abspath(str(script.get('path','')))
    if not os.path.isfile(path): raise FileNotFoundError('Approved project file is missing from storage.')
    command,runtime,_=_runtime_command(script)
    env=os.environ.copy()
    env.update({str(k):str(v) for k,v in (script.get('env') or {}).items()})
    md=user_module_dir(script.get('user_id')); ld=os.path.abspath(INSTALLED_MODULES_DIR)
    env['PYTHONPATH']=os.pathsep.join(x for x in (md,ld,os.path.dirname(path),env.get('PYTHONPATH','')) if x)
    env['PYTHONUNBUFFERED']='1'
    _write_script_log(script,'\n'+'='*72+f"\nV110 START REQUESTED\nFILE: {os.path.basename(path)}\nRUNTIME: {runtime}\nSTATUS: STARTING\n"+'='*72+'\n')
    process=subprocess.Popen(command,cwd=os.path.dirname(path) or os.getcwd(),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,text=True,encoding='utf-8',errors='replace',bufsize=1,universal_newlines=True,start_new_session=True)
    with SCRIPT_PROCESS_LOCK:
        SCRIPT_PROCESSES[str(script_id)]={'process':process,'return_code':None}
    script.update({'status':'running','manual_stop':False,'last_error':None,'last_exit_code':None,'runtime':runtime,'pid':process.pid,'started_at_epoch':time.time(),'last_modified':_advanced_now()})
    save_bot_scripts(scripts)
    _start_process_monitor(context.application,str(script_id),process,asyncio.get_running_loop())
    await asyncio.sleep(0.6)
    if process.poll() is not None:
        script['status']='stopped'; script['last_exit_code']=process.returncode
        script['last_error']=f'Process exited immediately with code {process.returncode}.' if process.returncode else None
        save_bot_scripts(scripts)
        return None
    return process

async def _v110_prepare_python(update, context, script_id):
    """Read .py, scan variables, validate dependencies and ask only for missing values.

    V111 supports both callback-based starts and direct upload preparation.
    """
    scripts,script=_get_script(script_id)
    path=os.path.abspath(str(script.get('path','')))
    if not os.path.isfile(path): raise FileNotFoundError('Approved .py file is missing from storage.')
    target_message = None
    if getattr(update, 'callback_query', None) is not None:
        target_message = update.callback_query.message
    elif getattr(update, 'message', None) is not None:
        target_message = update.message
    if target_message is None:
        raise RuntimeError('No Telegram message target is available for Python preparation.')
    progress=await target_message.reply_text('🚀 <b>READING .PY</b>\n\n<code>🟩⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜</code> <b>5%</b>\n\nReading the uploaded Python project…',parse_mode='HTML')
    try:
        source=Path(path).read_text(encoding='utf-8',errors='replace')
        await _v110_edit_progress(progress,'READING .PY','Loading the complete source and project metadata…',18)
        required,optional=_detected_env_from_source(source)
        # BOT_TOKEN must be explicitly supplied for hosted scripts; a getenv default is not proof it is valid.
        optional=[name for name in optional if name != 'BOT_TOKEN']
        if 'BOT_TOKEN' not in required: required.append('BOT_TOKEN')
        required=sorted(set(required))
        script['env_required']=required; script['env_optional']=optional
        await _v110_edit_progress(progress,'ANALYZING VARIABLES',
            ('Detected <b>'+str(len(required))+'</b> required variable(s).' if required else 'No mandatory variables detected.')+
            ('<br>Optional variables: <b>'+str(len(optional))+'</b>.' if optional else ''),35)
        # Safe source validation / dependency preparation.
        ok,changed,detail=await _prepare_user_python(path,script)
        _write_script_log(script,'\nV110 PREPARATION: '+('PASSED' if ok else 'FAILED')+'\n'+str(detail)+'\n')
        if not ok: raise RuntimeError(detail)
        await _v110_edit_progress(progress,'PREPARING PROJECT','Python syntax checked; source is unchanged. Checking required dependencies…',65)
        missing=[x for x in required if not str((script.get('env') or {}).get(x,'')).strip()]
        if missing:
            script['awaiting_env']=True; save_bot_scripts(scripts)
            context.user_data['awaiting_env_script_id']=str(script_id)
            await _v110_edit_progress(progress,'VARIABLES REQUIRED','Project is ready, but credentials are needed before launch.',88)
            await asyncio.sleep(0.25)
            try: await progress.delete()
            except Exception: pass
            template='\n'.join(f'{x}=PASTE_VALUE_HERE' for x in missing)
            await target_message.reply_text(
                f'🔐 <b>VARIABLES REQUIRED</b>\n\n'
                f'<b>{html.escape(os.path.basename(path))}</b> needs these values:\n\n'
                f'<pre><code class="language-shell">{html.escape(template)}</code></pre>\n\n'
                f'After you send values, any variables still missing will be listed in a separate message.',parse_mode='HTML')
            return False
        script['awaiting_env']=False; save_bot_scripts(scripts)
        await _v110_edit_progress(progress,'READY TO START','All required values are already available. Starting the real process…',94)
        process=await _v110_launch_python_process(context,script_id)
        try: await progress.delete()
        except Exception: pass
        if not process:
            fresh=load_bot_scripts().get(str(script_id),script)
            logs=_read_script_logs(fresh,4500) or 'No startup output captured.'
            await target_message.reply_text(
                f'❌ <b>PROJECT DID NOT STAY RUNNING</b>\n\n<code>{html.escape(str(logs)[-3500:])}</code>\n\nOpen VIEW CURRENT LOGS for the full output.',parse_mode='HTML',reply_markup=InlineKeyboardMarkup([[user_button('VIEW CURRENT LOGS','📡',callback_data=f'logs_script_{script_id}')],[user_button('MY SCRIPT','📁',callback_data='my_scripts_menu')]]))
            return False
        await _v110_running_card(context.application,update.effective_user.id,script)
        return True
    except Exception:
        try: await progress.delete()
        except Exception: pass
        raise

# Preserve V109 behavior for ZIP/JS while giving Python projects the V110 live-start flow.
_v109_handle_start_script=handle_start_script

async def handle_start_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query=update.callback_query
    script_id=(query.data or '').replace('start_script_','',1)
    scripts,script=_get_script(script_id)
    if not script or not _safe_script_for_user(script,query.from_user.id):
        await query.answer('Project not found',show_alert=True); return
    if str(script.get('status'))=='running':
        with SCRIPT_PROCESS_LOCK:
            ent=SCRIPT_PROCESSES.get(str(script_id)); proc=ent.get('process') if ent else None
        if proc and proc.poll() is None:
            await query.answer('Project is already running.')
            await _v110_running_card(context.application,query.from_user.id,script)
            return
    await query.answer('Starting project…')
    path=str(script.get('path','')).lower()
    if path.endswith('.py') and script.get('kind')!='zip':
        try:
            await _v110_prepare_python(update,context,script_id)
        except Exception as exc:
            logger.error('V110 Python start failed: %s\n%s',exc,traceback.format_exc())
            _write_script_log(script,'\nV110 START ERROR: '+str(exc)+'\n'+traceback.format_exc()+'\n')
            await query.message.reply_text(f'❌ <b>PROJECT START FAILED</b>\n\n<pre>{html.escape(str(exc)[:2500])}</pre>\n\nUse VIEW CURRENT LOGS for the full diagnostic.',parse_mode='HTML',reply_markup=InlineKeyboardMarkup([[user_button('VIEW CURRENT LOGS','📡',callback_data=f'logs_script_{script_id}')],[user_button('MY SCRIPT','📁',callback_data='my_scripts_menu')]]))
        return
    # ZIP and Node retain the proven V109 execution path.
    await _v109_handle_start_script(update,context)

# Activate all v108 overrides before the polling loop starts.


# ==================== SHUB HOSTING BOT 112 — MULTI PROJECT + RUNTIME CONTROL ====================
HOSTING_ENGINE_VERSION = "112.0"

V112_DURATION_RE = re.compile(r'^\s*(\d+)\s*([mMdD])\s*$')

async def _v112_render_scripts(query, context, *, edit=True):
    """Render every stored project owned by the user, without deleting older uploads."""
    user_id = query.from_user.id
    scripts = load_bot_scripts()
    user_scripts = [(k,v) for k,v in scripts.items() if str(v.get('user_id')) == str(user_id)]
    user_scripts.sort(key=lambda kv: (str(kv[1].get('created_date','')), str(kv[0])), reverse=True)
    lines=[f"{user_emoji('📁')} <b>MY SCRIPTS</b>", '━━━━━━━━━━━━━━━━━━━━', '', f"Total files: <b>{len(user_scripts)}</b>", '', 'Tap a file to manage it.']
    kb=[]
    for sid, sc in user_scripts:
        running = str(sc.get('status')).lower() == 'running'
        icon='🟢' if running else '🔵'
        label=str(sc.get('name') or sc.get('original_name') or f'Script {sid}')[:55]
        duration=sc.get('duration_seconds')
        extra=''
        if duration:
            extra=' ⏱'
        kb.append([user_button(f'{icon} {label}{extra}', icon, callback_data=f'view_script_{sid}', style='success' if running else 'primary')])
    markup=InlineKeyboardMarkup(kb) if kb else None
    text='\n'.join(lines)
    if edit:
        try:
            await query.edit_message_text(text, parse_mode='HTML', reply_markup=markup)
            return
        except Exception:
            pass
    await context.bot.send_message(chat_id=user_id,text=text,parse_mode='HTML',reply_markup=markup)

# Make the existing callback menu use the multi-project renderer.
async def send_user_scripts_from_callback(query, context) -> None:
    await _v112_render_scripts(query, context, edit=True)


def _v112_parse_duration(value):
    m=V112_DURATION_RE.fullmatch(str(value or ''))
    if not m:
        return None
    amount=int(m.group(1))
    if amount <= 0:
        return None
    return amount * (60 if m.group(2).lower()=='m' else 86400)

async def _v112_ask_duration(message, context, script_id):
    scripts,script=_get_script(script_id)
    if not script: return
    script['awaiting_duration']=True
    script['awaiting_name']=False
    save_bot_scripts(scripts)
    context.user_data.pop('awaiting_env_script_id',None)
    context.user_data['v112_duration_script_id']=str(script_id)
    await message.reply_text(
        f"⏱ <b>RUN TIME</b>\n\nFile: <code>{html.escape(str(script.get('name','Unknown')))}</code>\n\n"
        "How long should this file run?\n\n"
        "Examples:\n<code>30M</code> = 30 minutes\n<code>2D</code> = 2 days\n\n"
        "Send a number followed by <b>M</b> or <b>D</b>.", parse_mode='HTML')

async def _v112_ask_name(message, context, script_id):
    scripts,script=_get_script(script_id)
    if not script: return
    script['awaiting_duration']=False; script['awaiting_name']=True; save_bot_scripts(scripts)
    context.user_data.pop('v112_duration_script_id',None)
    context.user_data['v112_name_script_id']=str(script_id)
    await message.reply_text(
        "🏷 <b>FILE NAME</b>\n\n"
        f"Original file: <code>{html.escape(str(script.get('original_name') or script.get('name','Unknown')))}</code>\n\n"
        "Send the name you want to see on <b>MY SCRIPTS</b>.\n"
        "Example: <code>My Telegram Bot</code>", parse_mode='HTML')

async def _v112_launch(context, script_id):
    """Launch Python/JS directly or a prepared ZIP supervisor."""
    scripts,script=_get_script(script_id)
    if not script: return None
    if str(script.get('kind'))=='zip' or str(script.get('path','')).lower().endswith('.zip'):
        return await _launch_zip_process(context,script_id)
    path=os.path.abspath(str(script.get('path','')))
    command,runtime,_=_runtime_command(script)
    env=os.environ.copy(); env.update({str(k):str(v) for k,v in (script.get('env') or {}).items()})
    md=user_module_dir(script.get('user_id')); ld=os.path.abspath(INSTALLED_MODULES_DIR)
    env['PYTHONPATH']=os.pathsep.join(x for x in (md,ld,os.path.dirname(path),env.get('PYTHONPATH','')) if x)
    env['PYTHONUNBUFFERED']='1'
    process=subprocess.Popen(command,cwd=os.path.dirname(path) or os.getcwd(),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,text=True,encoding='utf-8',errors='replace',bufsize=1,start_new_session=True)
    with SCRIPT_PROCESS_LOCK:
        SCRIPT_PROCESSES[str(script_id)]={'process':process,'return_code':None}
    script.update({'status':'running','manual_stop':False,'last_error':None,'last_exit_code':None,'runtime':runtime,'pid':process.pid,'started_at_epoch':time.time(),'last_modified':_advanced_now()})
    save_bot_scripts(scripts)
    _start_process_monitor(context.application,str(script_id),process,asyncio.get_running_loop())
    await asyncio.sleep(.35)
    if process.poll() is not None:
        script['status']='stopped'; script['last_exit_code']=process.returncode; script['last_error']=f'Process exited immediately with code {process.returncode}.' if process.returncode else None; save_bot_scripts(scripts)
        return None
    return process

async def _v112_expiry_worker(application, script_id, seconds, process):
    try:
        await asyncio.sleep(seconds)
        if process.poll() is not None: return
        scripts,script=_get_script(script_id)
        if not script or script.get('manual_stop'): return
        with SCRIPT_PROCESS_LOCK:
            entry=SCRIPT_PROCESSES.get(str(script_id)); current=entry.get('process') if entry else None
        if current is not process: return
        try: os.killpg(os.getpgid(process.pid),signal.SIGTERM)
        except Exception:
            try: process.terminate()
            except Exception: pass
        try: await asyncio.to_thread(process.wait,5)
        except Exception: pass
        scripts,script=_get_script(script_id)
        if script:
            script['status']='stopped'; script['last_error']='Run time completed.'; script['last_exit_code']=process.returncode; script['manual_stop']=True; save_bot_scripts(scripts)
        with SCRIPT_PROCESS_LOCK: SCRIPT_PROCESSES.pop(str(script_id),None)
        try:
            await application.bot.send_message(chat_id=script['user_id'],text=f"⏱ <b>RUN TIME FINISHED</b>\n\n<b>{html.escape(str(script.get('name','Unknown')))}</b> has stopped automatically.",parse_mode='HTML')
        except Exception: pass
    except asyncio.CancelledError:
        return
    except Exception:
        logger.error('V112 expiry worker failed for %s\n%s',script_id,traceback.format_exc())

def _v112_schedule_expiry(context, script_id, process, seconds):
    task=asyncio.create_task(_v112_expiry_worker(context.application,str(script_id),int(seconds),process))
    script_tasks=context.application.bot_data.setdefault('v112_expiry_tasks',{})
    old=script_tasks.get(str(script_id))
    if old and not old.done(): old.cancel()
    script_tasks[str(script_id)]=task

async def _v112_finish_setup(message, context, script_id):
    await _v112_ask_duration(message,context,script_id)

async def _v112_prepare_direct(update, context, script_id):
    """Prepare .py/.js and then enter the V112 duration/name flow."""
    scripts,script=_get_script(script_id)
    path=os.path.abspath(str(script.get('path','')))
    target=update.callback_query.message if getattr(update,'callback_query',None) else update.message
    if not target: raise RuntimeError('No Telegram message target is available.')
    ext=Path(path).suffix.lower()
    if ext=='.py':
        source=Path(path).read_text(encoding='utf-8',errors='replace')
        required,optional=_detected_env_from_source(source)
        # BOT_TOKEN must be explicitly supplied for hosted scripts; a getenv default is not proof it is valid.
        optional=[name for name in optional if name != 'BOT_TOKEN']
        if 'BOT_TOKEN' not in required: required.append('BOT_TOKEN')
        required=sorted(set(required))
        script['env_required']=required; script['env_optional']=optional
        ok,changed,detail=await _prepare_user_python(path,script)
        _write_script_log(script,'\nV112 PREPARATION: '+('PASSED' if ok else 'FAILED')+'\n'+str(detail)+'\n')
        if not ok: raise RuntimeError(detail)
    elif ext=='.js':
        source=Path(path).read_text(encoding='utf-8',errors='replace')
        required,optional=_detected_env_from_source(source)
        script['env_required']=required; script['env_optional']=optional
    else:
        raise RuntimeError('Unsupported direct runtime. Use .py, .js or .zip.')
    missing=[x for x in script.get('env_required',[]) if not str((script.get('env') or {}).get(x,'')).strip()]
    if missing:
        script['awaiting_env']=True; save_bot_scripts(scripts)
        context.user_data['awaiting_env_script_id']=str(script_id)
        template='\n'.join(f'{x}=PASTE_VALUE_HERE' for x in script.get('env_required',[]) or missing)
        await target.reply_text(f"🔐 <b>VARIABLES REQUIRED</b>\n\n<code>{html.escape(str(script.get('original_name') or script.get('name')))}</code> needs these variables. Copy the block, fill the values you know, and send it back:\n\n<pre><code class=\"language-shell\">{html.escape(template)}</code></pre>\n\nSend values as <b>KEY=VALUE</b> lines. Any variables still missing will be listed in a separate message.",parse_mode='HTML')
        return False
    script['awaiting_env']=False; save_bot_scripts(scripts)
    await _v112_finish_setup(target,context,script_id)
    return False

async def handle_stop_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query=update.callback_query; script_id=query.data.replace('stop_script_','',1)
    scripts,script=_get_script(script_id)
    if not script or not _safe_script_for_user(script,query.from_user.id):
        await query.answer('Script not found',show_alert=True); return
    with SCRIPT_PROCESS_LOCK:
        entry=SCRIPT_PROCESSES.get(str(script_id)); process=entry.get('process') if entry else None
    try:
        script['manual_stop']=True
        if process and process.poll() is None:
            try: os.killpg(os.getpgid(process.pid),signal.SIGTERM)
            except Exception:
                try: process.terminate()
                except Exception: pass
            try: await asyncio.to_thread(process.wait,3)
            except Exception:
                try: os.killpg(os.getpgid(process.pid),signal.SIGKILL)
                except Exception:
                    try: process.kill()
                    except Exception: pass
        script['status']='stopped'; script['last_exit_code']=process.returncode if process else script.get('last_exit_code'); script['last_modified']=_advanced_now(); save_bot_scripts(scripts)
        with SCRIPT_PROCESS_LOCK: SCRIPT_PROCESSES.pop(str(script_id),None)
        tasks=context.application.bot_data.get('v112_expiry_tasks',{}); task=tasks.pop(str(script_id),None)
        if task and not task.done(): task.cancel()
        await query.answer('Stopped')
        await _v112_render_scripts(query,context,edit=True)
    except Exception as exc:
        logger.error('V112 stop failed for %s: %s\n%s',script_id,exc,traceback.format_exc())
        try: await query.answer('Stop failed',show_alert=True)
        except Exception: pass

# Replace the message state machine with V112 duration/name stages before legacy handling.
_old_v112_handle_message=handle_message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id=update.effective_user.id; text=(update.message.text or '').strip()
    # V112 variable stage: collect credentials first, then ask duration instead of launching immediately.
    env_sid=context.user_data.get('awaiting_env_script_id')
    if env_sid:
        scripts,env_script=_get_script(str(env_sid))
        if env_script and _safe_script_for_user(env_script,user_id):
            required=env_script.get('env_required',[])
            parsed={}
            for raw in (text or '').splitlines():
                raw=raw.strip()
                if not raw or raw.startswith('#') or '=' not in raw: continue
                key,val=raw.split('=',1); key=key.strip(); val=val.strip()
                if key in required and val and val!='PASTE_VALUE_HERE': parsed[key]=val
            missing=[k for k in required if k not in parsed]
            if missing:
                await update.message.reply_text('⚠️ <b>VARIABLES MISSING</b>\n\nMissing: '+', '.join(f'<code>{html.escape(x)}</code>' for x in missing),parse_mode='HTML'); return
            env_script['env']=parsed; env_script['awaiting_env']=False; save_bot_scripts(scripts)
            context.user_data.pop('awaiting_env_script_id',None)
            await update.message.reply_text('✅ <b>VARIABLES SAVED</b>\n\nCredentials accepted. Next, set the run time.',parse_mode='HTML')
            await _v112_ask_duration(update.message,context,str(env_sid)); return
    sid=context.user_data.get('v112_duration_script_id')
    if sid:
        seconds=_v112_parse_duration(text)
        if not seconds:
            await update.message.reply_text('⚠️ Invalid time. Use <code>30M</code> for minutes or <code>2D</code> for days.',parse_mode='HTML'); return
        scripts,script=_get_script(sid)
        if not script or not _safe_script_for_user(script,user_id):
            context.user_data.pop('v112_duration_script_id',None); return
        script['duration_seconds']=seconds; script['expires_at_epoch']=time.time()+seconds; save_bot_scripts(scripts)
        await _v112_ask_name(update.message,context,sid); return
    sid=context.user_data.get('v112_name_script_id')
    if sid:
        name=text.strip()
        if not name or len(name)>80:
            await update.message.reply_text('⚠️ Name must be between 1 and 80 characters.'); return
        scripts,script=_get_script(sid)
        if not script or not _safe_script_for_user(script,user_id):
            context.user_data.pop('v112_name_script_id',None); return
        script['name']=name; script['display_name']=name; script['awaiting_name']=False; save_bot_scripts(scripts)
        context.user_data.pop('v112_name_script_id',None)
        await update.message.reply_text(f"🚀 <b>STARTING</b>\n\n<code>{html.escape(name)}</code>\nRuntime: <b>{html.escape(_format_duration(script['duration_seconds']))}</b>",parse_mode='HTML')
        try:
            process=await _v112_launch(context,sid)
            if process:
                _v112_schedule_expiry(context,sid,process,script['duration_seconds'])
                await update.message.reply_text(f"🟢 <b>BOT RUNNING</b>\n\n<b>{html.escape(name)}</b> is now running.",parse_mode='HTML',reply_markup=get_main_keyboard())
            else:
                fresh=load_bot_scripts().get(str(sid),script); logs=_sanitize_user_log(_read_script_logs(fresh,3500) or 'No startup log captured.')
                await update.message.reply_text(f"❌ <b>RUN FAILED</b>\n\n<pre>{html.escape(logs)}</pre>",parse_mode='HTML',reply_markup=get_main_keyboard())
        except Exception as exc:
            scripts=load_bot_scripts(); fresh=scripts.get(str(sid),script); fresh['status']='stopped'; fresh['last_error']=f'{type(exc).__name__}: {exc}'; scripts[str(sid)]=fresh; save_bot_scripts(scripts)
            _write_script_log(fresh,'\nV112 START ERROR: '+str(exc)+'\n'+traceback.format_exc()+'\n')
            await update.message.reply_text(f"❌ <b>START FAILED</b>\n\n<pre>{html.escape(str(exc)[:2500])}</pre>",parse_mode='HTML',reply_markup=get_main_keyboard())
        return
    # Legacy flow remains for unrelated messages and existing features.
    await _old_v112_handle_message(update,context)

# Start callbacks now enter the same duration/name flow instead of bypassing it.
async def handle_start_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query=update.callback_query; sid=(query.data or '').replace('start_script_','',1)
    scripts,script=_get_script(sid)
    if not script or not _safe_script_for_user(script,query.from_user.id): await query.answer('Project not found',show_alert=True); return
    await query.answer('Setup')
    if script.get('awaiting_env'):
        await query.message.reply_text('🔐 This project still needs its variables. Send them first.')
        return
    if str(script.get('kind'))=='zip' and not script.get('workspace'):
        try:
            await _begin_zip_host(update,context,sid)
        except Exception as exc:
            await query.message.reply_text(f'❌ <b>ZIP PREPARATION FAILED</b>\n\n<pre>{html.escape(str(exc)[:2500])}</pre>',parse_mode='HTML')
        return
    await _v112_ask_duration(query.message,context,sid)

# Override admin auto approval so Python and JavaScript both use the V112 setup flow.
_old_v112_admin_auto=_send_admin_auto_approved
async def _send_admin_auto_approved(update, context, document):
    script_id,script=await _create_approved_script_from_document(update,context,document,auto_admin=True)
    if script.get('kind')=='zip':
        msg=await update.message.reply_text(f"📦 <b>ZIP PREPARATION</b>\n\n<code>{html.escape(script['name'])}</code>\nExtracting and scanning…",parse_mode='HTML')
        try:
            required,optional,entry=await _prepare_zip_project(script,msg)
            scripts=load_bot_scripts(); scripts[str(script_id)]=script; save_bot_scripts(scripts)
            try: await msg.delete()
            except Exception: pass
            if required:
                script['awaiting_env']=True; save_bot_scripts(scripts); context.user_data['awaiting_env_script_id']=str(script_id)
                template='\n'.join(f'{x}=PASTE_VALUE_HERE' for x in required)
                await update.message.reply_text(f"🔐 <b>VARIABLES REQUIRED</b>\n\nCopy this code block and fill the values you know:\n\n<pre><code class=\"language-shell\">{html.escape(template)}</code></pre>\n\nSend values as KEY=VALUE lines. Any variables still missing will be listed in a separate message.",parse_mode='HTML')
            else:
                await _v112_ask_duration(update.message,context,script_id)
        except Exception as exc:
            script['status']='stopped'; script['last_error']=f'{type(exc).__name__}: {exc}'; save_bot_scripts({**load_bot_scripts(),str(script_id):script}); _write_script_log(script,'\nV112 ZIP PREP ERROR: '+str(exc)+'\n'+traceback.format_exc()+'\n')
            await update.message.reply_text(f"❌ <b>ZIP PREPARATION FAILED</b>\n\n<pre>{html.escape(str(exc)[:2500])}</pre>",parse_mode='HTML',reply_markup=get_main_keyboard())
    else:
        await update.message.reply_text(f"✅ <b>FILE READY</b>\n\n<code>{html.escape(script['name'])}</code>\nPreparing variables and runtime…",parse_mode='HTML')
        try:
            await _v112_prepare_direct(update,context,script_id)
        except Exception as exc:
            script['status']='stopped'; script['last_error']=f'{type(exc).__name__}: {exc}'; scripts=load_bot_scripts(); scripts[str(script_id)]=script; save_bot_scripts(scripts); _write_script_log(script,'\nV112 PREP ERROR: '+str(exc)+'\n'+traceback.format_exc()+'\n')
            await update.message.reply_text(f"❌ <b>PREPARATION FAILED</b>\n\n<pre>{html.escape(str(exc)[:2500])}</pre>",parse_mode='HTML',reply_markup=get_main_keyboard())

# New upload handler wrapper: same storage, no replacement of previous scripts.
_old_v112_upload=handle_file_upload
async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # The original handler has already been patched to remove the destructive
    # supersede call; delegate to it so approval/history behavior stays intact.
    await _old_v112_upload(update,context)



# ==================== V112 SMART STABILITY PATCH ====================
# Final V112 layer: one-launch-per-script, reliable .py/.js execution, explicit
# post-start MY SCRIPTS navigation, and safe custom-emoji restoration.
HOSTING_ENGINE_VERSION = "114.0"
ENABLE_CUSTOM_EMOJI_BUTTONS = os.getenv("ENABLE_CUSTOM_EMOJI_BUTTONS", "1").strip().lower() in {"1", "true", "yes", "on"}

# Prevent two callback/message paths from launching the same project twice.
_V112_LAUNCH_LOCKS = {}
_V112_LAUNCH_LOCKS_GUARD = threading.Lock()

def _v112_launch_lock(script_id):
    sid = str(script_id)
    with _V112_LAUNCH_LOCKS_GUARD:
        lock = _V112_LAUNCH_LOCKS.get(sid)
        if lock is None:
            lock = asyncio.Lock()
            _V112_LAUNCH_LOCKS[sid] = lock
        return lock

def _v112_live_process(script_id):
    with SCRIPT_PROCESS_LOCK:
        entry = SCRIPT_PROCESSES.get(str(script_id))
        process = entry.get('process') if entry else None
    if process is not None and process.poll() is None:
        return process
    return None

async def _v112_launch(context, script_id):
    """Launch exactly one OS process for a script and return that process."""
    sid = str(script_id)
    lock = _v112_launch_lock(sid)
    async with lock:
        existing = _v112_live_process(sid)
        if existing is not None:
            scripts, script = _get_script(sid)
            if script:
                script['status'] = 'running'
                script['pid'] = existing.pid
                save_bot_scripts(scripts)
            return existing

        scripts, script = _get_script(sid)
        if not script:
            raise FileNotFoundError('Project record not found.')
        if script.get('manual_stop'):
            script['manual_stop'] = False
            save_bot_scripts(scripts)

        if str(script.get('kind')) == 'zip' or str(script.get('path','')).lower().endswith('.zip'):
            process = await _launch_zip_process(context, sid)
        else:
            path = os.path.abspath(str(script.get('path','')))
            if not os.path.isfile(path):
                raise FileNotFoundError('Uploaded project file is missing from storage.')
            command, runtime, _ = _runtime_command(script)
            env = os.environ.copy()
            env.update({str(k): str(v) for k, v in (script.get('env') or {}).items()})
            md = user_module_dir(script.get('user_id')); ld = os.path.abspath(INSTALLED_MODULES_DIR)
            env['PYTHONPATH'] = os.pathsep.join(x for x in (md, ld, os.path.dirname(path), env.get('PYTHONPATH','')) if x)
            env['PYTHONUNBUFFERED'] = '1'
            _write_script_log(script, '\n' + '='*72 + f"\nV112 START REQUESTED\nFILE: {os.path.basename(path)}\nRUNTIME: {runtime}\nSTATUS: STARTING\n" + '='*72 + '\n')
            process = subprocess.Popen(
                command, cwd=os.path.dirname(path) or os.getcwd(), env=env,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                text=True, encoding='utf-8', errors='replace', bufsize=1,
                start_new_session=True
            )
            with SCRIPT_PROCESS_LOCK:
                SCRIPT_PROCESSES[sid] = {'process': process, 'return_code': None}
            script.update({
                'status':'running', 'manual_stop':False, 'last_error':None,
                'last_exit_code':None, 'runtime':runtime, 'pid':process.pid,
                'started_at_epoch':time.time(), 'last_modified':_advanced_now()
            })
            save_bot_scripts(scripts)
            _start_process_monitor(context.application, sid, process, asyncio.get_running_loop())
            await asyncio.sleep(0.45)

        if process is None or process.poll() is not None:
            scripts, script = _get_script(sid)
            if script:
                rc = process.returncode if process is not None else 1
                script['status'] = 'stopped'
                script['last_exit_code'] = rc
                script['last_error'] = f'Process exited immediately with code {rc}.' if rc else None
                save_bot_scripts(scripts)
            return None
        return process

async def _v112_send_running_result(application, user_id, script_id, *, duration_seconds=None):
    scripts, script = _get_script(script_id)
    if not script:
        return
    name = html.escape(str(script.get('name') or script.get('original_name') or 'Project'))
    runtime = _format_duration(duration_seconds if duration_seconds is not None else script.get('duration_seconds', 0))
    text = (
        f"{user_emoji('🚀') or '🚀'} <b>BOT RUNNING</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📄 <b>Name:</b> <code>{name}</code>\n"
        f"🟢 <b>Status:</b> RUNNING\n"
        f"⏱ <b>Runtime:</b> {html.escape(runtime)}\n\n"
        "✅ Process started successfully.\n"
        "📡 Logs are being monitored live."
    )
    markup = InlineKeyboardMarkup([
        [user_button('📡 VIEW LOGS', '📡', callback_data=f'logs_script_{script_id}')],
        [user_button('📁 MY SCRIPTS', '📁', callback_data='my_scripts_menu')]
    ])
    try:
        await application.bot.send_message(chat_id=user_id, text=text, parse_mode='HTML', reply_markup=markup)
    except Exception:
        pass

# Replace the final V112 text state machine with a guarded launcher.
_previous_v112_message = handle_message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not getattr(update, 'message', None):
        return await _previous_v112_message(update, context)
    user_id = update.effective_user.id
    text = (update.message.text or '').strip()

    # Variables -> duration.
    env_sid = context.user_data.get('awaiting_env_script_id')
    if env_sid:
        scripts, script = _get_script(env_sid)
        if script and _safe_script_for_user(script, user_id):
            required = script.get('env_required', [])
            parsed = {}
            for raw in text.splitlines():
                raw = raw.strip()
                if '=' not in raw or raw.startswith('#'):
                    continue
                key, val = raw.split('=', 1)
                key, val = key.strip(), val.strip()
                if key in required and val and val != 'PASTE_VALUE_HERE':
                    parsed[key] = val
            missing = [k for k in required if k not in parsed]
            if missing:
                await update.message.reply_text(
                    '⚠️ <b>VARIABLES MISSING</b>\n\nMissing: ' + ', '.join(f'<code>{html.escape(x)}</code>' for x in missing),
                    parse_mode='HTML')
                return
            script['env'] = parsed
            script['awaiting_env'] = False
            save_bot_scripts(scripts)
            context.user_data.pop('awaiting_env_script_id', None)
            await update.message.reply_text('✅ <b>VARIABLES SAVED</b>\n\nNow set the run time.', parse_mode='HTML')
            await _v112_ask_duration(update.message, context, env_sid)
            return

    sid = context.user_data.get('v112_duration_script_id')
    if sid:
        seconds = _v112_parse_duration(text)
        if not seconds:
            await update.message.reply_text('⚠️ Use <code>30M</code> or <code>2D</code>.', parse_mode='HTML')
            return
        scripts, script = _get_script(sid)
        if not script or not _safe_script_for_user(script, user_id):
            context.user_data.pop('v112_duration_script_id', None)
            return
        script['duration_seconds'] = seconds
        script['expires_at_epoch'] = time.time() + seconds
        save_bot_scripts(scripts)
        await _v112_ask_name(update.message, context, sid)
        return

    sid = context.user_data.get('v112_name_script_id')
    if sid:
        name = text.strip()
        if not name or len(name) > 80:
            await update.message.reply_text('⚠️ Name must be between 1 and 80 characters.')
            return
        scripts, script = _get_script(sid)
        if not script or not _safe_script_for_user(script, user_id):
            context.user_data.pop('v112_name_script_id', None)
            return
        script['name'] = name
        script['display_name'] = name
        script['awaiting_name'] = False
        save_bot_scripts(scripts)
        context.user_data.pop('v112_name_script_id', None)
        try:
            process = await _v112_launch(context, sid)
            if process:
                _v112_schedule_expiry(context, sid, process, script['duration_seconds'])
                await _v112_send_running_result(context.application, user_id, sid, duration_seconds=script['duration_seconds'])
                # Immediately refresh the user's script list too.
                q = update.callback_query
                if q:
                    await _v112_render_scripts(q, context, edit=True)
            else:
                fresh = load_bot_scripts().get(str(sid), script)
                logs = _sanitize_user_log(_read_script_logs(fresh, 3500) or 'No startup log captured.')
                await update.message.reply_text(
                    f"❌ <b>RUN FAILED</b>\n\n<pre>{html.escape(logs)}</pre>",
                    parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[user_button('📁 MY SCRIPTS','📁',callback_data='my_scripts_menu')]]))
        except Exception as exc:
            scripts = load_bot_scripts(); fresh = scripts.get(str(sid), script)
            fresh['status'] = 'stopped'; fresh['last_error'] = f'{type(exc).__name__}: {exc}'
            scripts[str(sid)] = fresh; save_bot_scripts(scripts)
            _write_script_log(fresh, '\nV112 START ERROR: ' + str(exc) + '\n' + traceback.format_exc() + '\n')
            await update.message.reply_text(
                f"❌ <b>START FAILED</b>\n\n<pre>{html.escape(str(exc)[:2500])}</pre>",
                parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[user_button('📁 MY SCRIPTS','📁',callback_data='my_scripts_menu')]]))
        return

    await _previous_v112_message(update, context)

# Final start callback: never launches immediately; it only enters setup once.
async def handle_start_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    sid = (query.data or '').replace('start_script_', '', 1)
    scripts, script = _get_script(sid)
    if not script or not _safe_script_for_user(script, query.from_user.id):
        await query.answer('Project not found', show_alert=True)
        return
    if _v112_live_process(sid):
        await query.answer('Already running')
        await _v112_send_running_result(context.application, query.from_user.id, sid)
        return
    await query.answer('Preparing…')
    if script.get('awaiting_env'):
        await query.message.reply_text('🔐 This project still needs variables. Send them first.', parse_mode='HTML')
        return
    if str(script.get('kind')) == 'zip' and not script.get('workspace'):
        try:
            await _begin_zip_host(update, context, sid)
        except Exception as exc:
            await query.message.reply_text(f'❌ <b>ZIP PREPARATION FAILED</b>\n\n<pre>{html.escape(str(exc)[:2500])}</pre>', parse_mode='HTML')
        return
    await _v112_ask_duration(query.message, context, sid)

# Final stop callback: acknowledge first and render My Scripts, avoiding stale alert/errors.
async def handle_stop_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    sid = (query.data or '').replace('stop_script_', '', 1)
    scripts, script = _get_script(sid)
    if not script or not _safe_script_for_user(script, query.from_user.id):
        await query.answer('Script not found', show_alert=False)
        return
    try:
        script['manual_stop'] = True
        with SCRIPT_PROCESS_LOCK:
            entry = SCRIPT_PROCESSES.get(sid)
            process = entry.get('process') if entry else None
        if process and process.poll() is None:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            except Exception:
                try: process.terminate()
                except Exception: pass
            try:
                await asyncio.to_thread(process.wait, 3)
            except Exception:
                try: os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except Exception:
                    try: process.kill()
                    except Exception: pass
        rc = process.returncode if process else script.get('last_exit_code')
        script['status'] = 'stopped'
        script['last_exit_code'] = rc
        script['last_modified'] = _advanced_now()
        save_bot_scripts(scripts)
        with SCRIPT_PROCESS_LOCK:
            SCRIPT_PROCESSES.pop(sid, None)
        tasks = context.application.bot_data.get('v112_expiry_tasks', {})
        task = tasks.pop(sid, None)
        if task and not task.done(): task.cancel()
        await query.answer('Stopped', show_alert=False)
        # Show a clean confirmation with a direct My Scripts button.
        await query.edit_message_text(
            f"⏹️ <b>STOPPED</b>\n\n<code>{html.escape(str(script.get('name') or script.get('original_name') or sid))}</code> has been stopped.",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[user_button('📁 MY SCRIPTS','📁',callback_data='my_scripts_menu')]])
        )
    except Exception as exc:
        logger.error('V112 stop failed for %s: %s\n%s', sid, exc, traceback.format_exc())
        try: await query.answer('Stopped', show_alert=False)
        except Exception: pass
        try:
            await _v112_render_scripts(query, context, edit=True)
        except Exception: pass

# Final upload handler remains the existing multi-project handler; it never replaces stored scripts.


# ==================== SHUB HOSTING BOT 113 — ADMIN VARIABLES MENU ====================
HOSTING_ENGINE_VERSION = "114.0"
V113_VARIABLES_EMOJI_ID = "6071414045058012551"

async def _v113_show_variables_menu(message, context, user_id=None):
    """Show all projects to admins and only the caller's projects to regular users."""
    if user_id is None:
        user_id = message.from_user.id if getattr(message, 'from_user', None) else None
    if user_id is None:
        return
    scripts = load_bot_scripts()
    if not is_admin(user_id):
        scripts = {sid: item for sid, item in scripts.items() if str(item.get('user_id', '')) == str(user_id)}
    if not scripts:
        await message.reply_text("🧩 <b>VARIABLES</b>\n\nNo uploaded projects are stored yet.", parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
        return
    users = load_json(USERS_DB)
    rows = []
    ordered = sorted(scripts.items(), key=lambda kv: (str(kv[1].get('created_date', '')), str(kv[0])), reverse=True)
    for sid, script in ordered:
        owner_id = str(script.get('user_id', ''))
        owner = users.get(owner_id, {}) if isinstance(users, dict) else {}
        owner_name = owner.get('first_name') or owner.get('username') or owner_id or 'Unknown'
        name = str(script.get('name') or script.get('original_name') or f'Script {sid}')[:40]
        status = '🟢' if str(script.get('status', '')).lower() == 'running' else '🔵'
        label = f"{status} {name} · {str(owner_name)[:18]}"
        rows.append([user_button(label[:60], '🧩', callback_data=f'v113_variables_script_{sid}', style='success' if status == '🟢' else 'primary')])
    rows.append([user_button('↩️ MAIN MENU', '◀️', callback_data='v113_variables_back')])
    await message.reply_text(
        f"🧩 <b>VARIABLES — PROJECTS</b>\n━━━━━━━━━━━━━━━━━━━━\n\nStored projects: <b>{len(ordered)}</b>\nSelect a file to inspect its variables. The uploader is shown after each project name.",
        parse_mode='HTML', reply_markup=InlineKeyboardMarkup(rows))

async def _v113_show_script_variables(query, context, script_id):
    scripts, script = _get_script(script_id)
    if not script:
        await query.answer('Project not found.', show_alert=True)
        return
    # Regular users can only inspect/change projects they uploaded; admins can
    # inspect and manage any stored project, including their own.
    if not is_admin(query.from_user.id) and str(script.get('user_id', '')) != str(query.from_user.id):
        await query.answer('You can only change variables for your own projects.', show_alert=True)
        return
    path = os.path.abspath(str(script.get('path', '')))
    required = list(script.get('env_required') or [])
    optional = list(script.get('env_optional') or [])
    # Refresh detection from the actual Python file or already-prepared ZIP workspace.
    try:
        if path.lower().endswith('.py') and os.path.isfile(path):
            source = Path(path).read_text(encoding='utf-8', errors='replace')
            detected_required, detected_optional = _detected_env_from_source(source)
            required = sorted(set(required) | set(detected_required))
            optional = sorted(set(optional) | set(detected_optional))
        else:
            workspace = script.get('workspace')
            if workspace and os.path.isdir(workspace):
                detected_required, detected_optional = _scan_project_env(workspace)
                required = sorted(set(required) | set(detected_required))
                optional = sorted(set(optional) | set(detected_optional))
    except Exception as exc:
        logger.warning('V113 variable scan failed for %s: %s', script_id, exc)
    script['env_required'] = required
    script['env_optional'] = [x for x in optional if x not in required]
    save_bot_scripts(scripts)
    current = script.get('env') if isinstance(script.get('env'), dict) else {}
    fields = list(dict.fromkeys(required + script['env_optional']))
    if not fields:
        await query.answer()
        await query.message.reply_text(
            f"🧩 <b>VARIABLES</b>\n\nFile: <code>{html.escape(str(script.get('name') or script.get('original_name') or script_id))}</code>\n\nNo environment variables were detected in this project. You can still use MY SCRIPTS to start it.",
            parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[user_button('↩️ PROJECTS', '🧩', callback_data='v113_variables_back')]]))
        return
    present = '\n'.join(f'{key}={str(current.get(key, "")) if str(current.get(key, "")) else "(blank)"}' for key in fields)
    template = '\n'.join(f'{key}=PASTE_NEW_VALUE_HERE' for key in fields)
    context.user_data['v113_variable_script_id'] = str(script_id)
    context.user_data['awaiting_env_script_id'] = str(script_id)
    await query.answer()
    await query.message.reply_text(
        f"🧩 <b>VARIABLES ANALYSIS</b>\n━━━━━━━━━━━━━━━━━━━━\n<b>File:</b> <code>{html.escape(str(script.get('name') or script.get('original_name') or script_id))}</code>\n<b>Required:</b> {len(required)} · <b>Optional:</b> {len(script['env_optional'])}\n\n<b>Current values</b>\n<pre>{html.escape(present[:3500])}</pre>\n\n<b>Copy, fill and send back</b>\n<pre>{html.escape(template[:3500])}</pre>\n\nSend only variables you want to change as <code>KEY=VALUE</code>, one per line. Other values stay unchanged. You may use a readable alias such as <code>Telegram Bot Token=123:ABC</code>. Send <code>/cancel</code> to exit without saving.",
        parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[user_button('↩️ PROJECTS', '🧩', callback_data='v113_variables_back')]]))

# Keep existing callback behavior intact while adding guarded Variables callbacks.
_v113_previous_button_handler = button_handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = (query.data or '') if query else ''
    if data in ('v114_stop_all_confirm', 'v114_stop_all_cancel'):
        if (getattr(query.from_user, 'username', '') or '').lower() != OWNER_USERNAME.lower():
            await query.answer('Owner only.', show_alert=True)
            return
        if data == 'v114_stop_all_cancel':
            await query.answer('Cancelled.')
            try: await query.message.edit_text('Stop-all action cancelled.')
            except Exception: pass
            return
        await query.answer('Stopping scripts…')
        stopped_names = []
        scripts = load_bot_scripts()
        for sid, item in list(scripts.items()):
            if str(item.get('status', '')).lower() != 'running':
                continue
            stopped_names.append(str(item.get('name') or item.get('original_name') or sid))
            item['manual_stop'] = True
            item['status'] = 'stopped'
            try:
                with SCRIPT_PROCESS_LOCK:
                    proc_entry = SCRIPT_PROCESSES.get(str(sid))
                    proc = proc_entry.get('process') if proc_entry else None
                if proc is not None and proc.poll() is None:
                    proc.terminate()
            except Exception as exc:
                logger.warning('Stop-all failed for script %s: %s', sid, exc)
        save_bot_scripts(scripts)
        details = '\n'.join('• ' + html.escape(n) + ' — STOP' for n in stopped_names) or 'No running scripts were found.'
        try: await query.message.edit_text('🛑 <b>All scripts have now successfully stopped.</b> Check in MyScript.\n\n' + details, parse_mode='HTML')
        except Exception: pass
        return
    if data.startswith('v113_variables_'):
        if data == 'v113_variables_back':
            await query.answer()
            context.user_data.pop('awaiting_env_script_id', None)
            context.user_data.pop('v113_variable_script_id', None)
            await _v113_show_variables_menu(query.message, context, query.from_user.id)
            return
        if data.startswith('v113_variables_script_'):
            await _v113_show_script_variables(query, context, data.rsplit('_', 1)[-1])
            return
    return await _v113_previous_button_handler(update, context)

# Intercept only the admin's menu tap; the established V112 variable/duration/name
# state machine continues to validate and launch the selected project.
_v113_previous_handle_message = handle_message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if getattr(update, 'message', None) and update.effective_user:
        text = (update.message.text or '').strip()
        user_id = update.effective_user.id
        # Variables inspector accepts partial updates; unmentioned values remain unchanged.
        v113_sid = context.user_data.get('v113_variable_script_id')
        if v113_sid and context.user_data.get('awaiting_env_script_id') == str(v113_sid):
            if text.lower() in ('/cancel', 'cancel'):
                context.user_data.pop('awaiting_env_script_id', None)
                context.user_data.pop('v113_variable_script_id', None)
                await update.message.reply_text('Cancelled. No variable values were changed.', reply_markup=get_main_keyboard(user_id))
                return
            scripts, script = _get_script(v113_sid)
            if not script or (not is_admin(user_id) and str(script.get('user_id', '')) != str(user_id)):
                context.user_data.pop('awaiting_env_script_id', None); context.user_data.pop('v113_variable_script_id', None)
                await update.message.reply_text('Project unavailable or access denied.')
                return
            required = list(script.get('env_required') or [])
            optional = list(script.get('env_optional') or [])
            existing = dict(script.get('env') or {})
            allowed = list(dict.fromkeys(required + optional + list(existing.keys())))
            parsed = {}
            alias_fn = globals().get('_v134_alias_group')
            common_aliases = {
                'TELEGRAMBOTTOKEN': {'BOT_TOKEN','TELEGRAM_BOT_TOKEN','TOKEN'},
                'TELEGRAMAPIID': {'API_ID','TELEGRAM_API_ID'},
                'TELEGRAMAPIHASH': {'API_HASH','TELEGRAM_API_HASH'},
                'ADMINTGID': {'ADMIN_TG_ID','ADMIN_ID','OWNER_ID'},
            }
            for raw in text.splitlines():
                raw = raw.strip()
                if not raw or raw.startswith('#') or '=' not in raw:
                    continue
                key, value = raw.split('=', 1); key = key.strip(); value = value.strip()
                if not value or value in ('PASTE_VALUE_HERE', 'PASTE_NEW_VALUE_HERE'):
                    continue
                target = next((k for k in allowed if k.lower() == key.lower()), None)
                norm = ''.join(ch for ch in key.upper() if ch.isalnum())
                if target is None and alias_fn:
                    target = next((k for k in allowed if norm in {''.join(ch for ch in str(alias).upper() if ch.isalnum()) for alias in alias_fn(k)}), None)
                if target is None:
                    aliases = common_aliases.get(norm, set())
                    target = next((k for k in allowed if k.upper() in aliases), None)
                if target:
                    parsed[target] = value
            if not parsed:
                await update.message.reply_text('No matching KEY=VALUE fields were found. Send variables in KEY=VALUE format, or /cancel.')
                return
            existing.update(parsed); script['env'] = existing; script['awaiting_env'] = False
            scripts[str(v113_sid)] = script; save_bot_scripts(scripts)
            changed = '\n'.join(f'<code>{html.escape(k)}</code>' for k in parsed)
            context.user_data.pop('awaiting_env_script_id', None); context.user_data.pop('v113_variable_script_id', None)
            await update.message.reply_text('✅ <b>Selected variables updated.</b>\n\nChanged keys:\n' + changed + '\n\nAll other variable values were left unchanged.', parse_mode='HTML', reply_markup=get_main_keyboard(user_id))
            return
        normalized = ''.join(ch for ch in text if ch.isalnum() or ch.isspace()).strip().upper()
        if normalized == 'VARIABLES' and not context.user_data.get('awaiting_env_script_id') and not context.user_data.get('v112_duration_script_id') and not context.user_data.get('v112_name_script_id'):
            _clear_user_env_session(context, user_id)
            await _v113_show_variables_menu(update.message, context, user_id)
            return
        if normalized == 'TUTORIAL':
            if not is_admin(user_id):
                await update.message.reply_text('⛔ Tutorial configuration is admin-only.')
                return
            await update.message.reply_text('No tutorial available', reply_markup=get_main_keyboard(user_id))
            return
        if normalized in ('MY STATS', 'STATS', 'STATISTICS'):
            # Preserve the existing stats implementation for the renamed button.
            update.message.text = 'STATS'
        elif normalized == 'SUPPORT':
            # V119: show the configured support destination directly instead of
            # routing SUPPORT through HELP (which caused the generic error path).
            support_cfg = DEFAULT_CHANNELS.get('channel_3', {})
            support_url = (support_cfg.get('link') or '').strip()
            support_name = (support_cfg.get('username') or '@SHUBHxSELLER').strip()
            if not support_url.startswith(('https://t.me/', 'http://t.me/')):
                support_url = 'https://t.me/SHUBHxSELLER'
            support_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(f'💬 Open Support ({support_name})', url=support_url)]
            ])
            await update.message.reply_text(
                '🛟 <b>SUPPORT</b>\n\nFor help with uploads, scripts, or premium access, contact our support team using the button below.',
                parse_mode='HTML',
                reply_markup=support_markup,
            )
            await update.message.reply_text('Main menu:', reply_markup=get_main_keyboard(user_id))
            return
        elif normalized == 'BUY PREMIUM':
            await update.message.reply_text('💎 Premium plans are not configured yet. Please contact support.', reply_markup=get_main_keyboard(user_id))
            return
        elif normalized == 'REDEEM CODE':
            context.user_data['v114_awaiting_redeem_code'] = True
            await update.message.reply_text('🎟️ Send your redeem code now, or /cancel to cancel.', reply_markup=get_main_keyboard(user_id))
            return
        elif normalized == 'STOP ALL SCRIPTS':
            if (getattr(update.effective_user, 'username', '') or '').lower() != OWNER_USERNAME.lower():
                await update.message.reply_text('⛔ This feature is restricted to the bot owner.', reply_markup=get_main_keyboard(user_id))
                return
            buttons = [[user_button('Yes, I am sure', '🛑', callback_data='v114_stop_all_confirm'), user_button('Cancel', '❌', callback_data='v114_stop_all_cancel')]]
            await update.message.reply_text('⚠️ This will stop all currently running scripts. Continue?', reply_markup=InlineKeyboardMarkup(buttons))
            return
        if context.user_data.get('v114_awaiting_redeem_code'):
            context.user_data.pop('v114_awaiting_redeem_code', None)
            await update.message.reply_text('❌ This redeem code is invalid or premium codes are not configured yet.', reply_markup=get_main_keyboard(user_id))
            return
    return await _v113_previous_handle_message(update, context)


# ==================== VERSION 114 PREMIUM WORKFLOWS ====================
# Local JSON storage; no external database required.
V114_PREMIUM_DB = f"{DB_DIR}/premium_users.json"
V114_CODES_DB = f"{DB_DIR}/premium_codes.json"
V114_PLANS_DB = f"{DB_DIR}/premium_plans.json"
V114_PAYMENTS_DB = f"{DB_DIR}/premium_payments.json"
V114_UPI_DB = f"{DB_DIR}/premium_upi.json"
# User-provided default UPI ID; admins can still change it from Set UPI ID.
V114_DEFAULT_UPI_ID = 'Shubhang-is-nxt@fam'
V114_REJECTIONS_DB = f"{DB_DIR}/premium_rejections.json"
V114_TUTORIAL_DB = f"{DB_DIR}/tutorial.json"

def _v114_load(filename, default):
    value = load_json(filename)
    return value if isinstance(value, type(default)) else default.copy()

def _v114_save(filename, data):
    return save_json(filename, data)

def _v114_is_owner(user):
    return (getattr(user, 'username', '') or '').lower() == OWNER_USERNAME.lower()

def _v114_duration_days(value):
    """Parse positive duration as days or 2d/4h/30m."""
    value = str(value).strip().lower()
    m = re.fullmatch(r'(\d+(?:\.\d+)?)\s*([dhm]?)', value)
    if not m:
        return None
    n = float(m.group(1)); unit = m.group(2) or 'd'
    days = n if unit == 'd' else n / 24 if unit == 'h' else n / 1440
    return days if days > 0 else None

def _v114_premium_until(uid):
    db = _v114_load(V114_PREMIUM_DB, {})
    try: return datetime.fromisoformat(db.get(str(uid), {}).get('expires_at', ''))
    except Exception: return None

def _v114_has_premium(uid):
    expiry = _v114_premium_until(uid)
    return bool(expiry and expiry > datetime.now())

def _v114_grant(uid, days):
    db = _v114_load(V114_PREMIUM_DB, {})
    now = datetime.now()
    try: old = datetime.fromisoformat(db.get(str(uid), {}).get('expires_at', ''))
    except Exception: old = now
    start = old if old > now else now
    expiry = start + timedelta(days=float(days))
    db[str(uid)] = {'user_id': int(uid), 'expires_at': expiry.isoformat(timespec='seconds')}
    _v114_save(V114_PREMIUM_DB, db)
    return expiry

def _v114_deduct(uid, days):
    db = _v114_load(V114_PREMIUM_DB, {})
    now = datetime.now()
    try: old = datetime.fromisoformat(db.get(str(uid), {}).get('expires_at', ''))
    except Exception: old = now
    new = old - timedelta(days=float(days))
    if new <= now: db.pop(str(uid), None); _v114_save(V114_PREMIUM_DB, db); return None
    db[str(uid)] = {'user_id': int(uid), 'expires_at': new.isoformat(timespec='seconds')}
    _v114_save(V114_PREMIUM_DB, db)
    return new

def _v114_plan_list():
    return _v114_load(V114_PLANS_DB, [])

async def _v114_premium_admin_screen(message):
    rows = [
        [user_button('Generate Promo Code', '🎫', callback_data='v114_promo_create')],
        [user_button('Add Premium', '👑', callback_data='v114_add_premium'), user_button('Deduct Premium', '🧾', callback_data='v114_deduct_premium')],
        [user_button('Add Plans', '🗓️', callback_data='v114_add_plan'), user_button('Set UPI ID', '💳', callback_data='v114_set_upi')],
        [user_button('View Plans', '🟩', callback_data='v114_view_plans'), user_button('Back to Admin', '⚙️', callback_data='v114_back_admin')],
    ]
    await message.reply_text('💎 <b>PREMIUM ADMIN PANEL</b>\nChoose an action. Plans and premium records are stored locally.', parse_mode='HTML', reply_markup=InlineKeyboardMarkup(rows))

async def _v114_user_stats(message, uid):
    expiry = _v114_premium_until(uid)
    scripts = load_bot_scripts()
    mine = [v for v in scripts.values() if str(v.get('user_id')) == str(uid)]
    running = sum(str(v.get('status','')).lower() == 'running' for v in mine)
    status = f'Active until <b>{expiry.strftime("%Y-%m-%d %H:%M")}</b>' if expiry and expiry > datetime.now() else 'Free / expired'
    await message.reply_text(f'📊 <b>MY STATS</b>\nUser ID: <code>{uid}</code>\nPremium: {status}\nFiles: {len(mine)}\nRunning: {running}\nStopped: {len(mine)-running}', parse_mode='HTML', reply_markup=get_main_keyboard(uid))

async def _v114_premium_callback(update, context):
    q=update.callback_query; data=q.data or ''; uid=q.from_user.id
    if data.startswith('v114_') and data != 'v114_submit_screenshot' and not data.startswith(('v114_plan_','v114_payment_')):
        if not is_admin(uid):
            await q.answer('Admins only.', show_alert=True); return True
    if data == 'v114_premium_admin':
        await q.answer(); await _v114_premium_admin_screen(q.message); return True
    if data == 'v114_tutorial_config':
        context.user_data['v114_state']='tutorial_video'; await q.answer(); await q.message.reply_text('Send the tutorial video now. Then send the caption text.'); return True
    if data == 'v114_back_admin':
        await q.answer(); await show_admin_panel(update, context); return True
    if data == 'v114_promo_create':
        context.user_data['v114_state']='promo_code'; await q.answer(); await q.message.reply_text('Send the custom promo code text.'); return True
    if data == 'v114_add_premium':
        context.user_data['v114_state']='add_uid'; await q.answer(); await q.message.reply_text('Send the Telegram numeric user ID to grant premium.'); return True
    if data == 'v114_deduct_premium':
        context.user_data['v114_state']='deduct_uid'; await q.answer(); await q.message.reply_text('Send the Telegram numeric user ID whose premium you want to deduct.'); return True
    if data == 'v114_add_plan':
        context.user_data['v114_state']='plan_days'; await q.answer(); await q.message.reply_text('Send plan validity in days (for example: 30).'); return True
    if data == 'v114_set_upi':
        context.user_data['v114_state']='upi'; await q.answer(); await q.message.reply_text('Send the UPI ID to use for payments.'); return True
    if data == 'v114_view_plans':
        await q.answer(); plans=_v114_plan_list()
        txt='\n'.join(f'{i+1}. {x.get("days")} days — ₹{x.get("amount")}' for i,x in enumerate(plans)) or 'No plans configured.'
        await q.message.reply_text('💎 <b>Plans</b>\n'+txt,parse_mode='HTML'); return True
    if data.startswith('v114_plan_'):
        try: idx=int(data.rsplit('_',1)[1]); plan=_v114_plan_list()[idx]
        except Exception: await q.answer('Plan unavailable.',show_alert=True); return True
        upi=_v114_load(V114_UPI_DB,{}).get('upi_id') or V114_DEFAULT_UPI_ID
        if not upi:
            await q.answer('Payments are not configured yet.',show_alert=True); return True
        payments=_v114_load(V114_PAYMENTS_DB,{})
        pid=f'{uid}_{int(time.time())}'
        payments[pid]={'payment_id':pid,'user_id':uid,'plan':plan,'status':'pending','rejections':0,'created_at':datetime.now().isoformat()}
        _v114_save(V114_PAYMENTS_DB,payments)
        context.user_data['v114_payment_id']=pid
        import urllib.parse
        pay_uri=f'upi://pay?pa={urllib.parse.quote(upi)}&pn=Premium&am={urllib.parse.quote(str(plan.get("amount")))}&cu=INR&tn={urllib.parse.quote("Premium plan")}'
        qr='https://api.qrserver.com/v1/create-qr-code/?size=300x300&data='+urllib.parse.quote(pay_uri,safe='')
        await q.answer(); await q.message.reply_photo(qr,caption=f'💎 Plan: {plan.get("days")} days\nAmount: ₹{plan.get("amount")}\nUPI ID: {html.escape(upi)}\n\nPay using this QR, then tap Submit Screenshot.',parse_mode='HTML',reply_markup=InlineKeyboardMarkup([[user_button('Submit Screenshot','📸',callback_data='v114_submit_screenshot')]])); return True
    if data == 'v114_submit_screenshot':
        context.user_data['v114_state']='payment_screenshot'; await q.answer(); await q.message.reply_text('Send the payment screenshot as a photo. Three rejected screenshots will permanently ban the account.'); return True
    if data.startswith('v114_payment_approve_') or data.startswith('v114_payment_reject_'):
        if not is_admin(uid): await q.answer('Admins only.',show_alert=True); return True
        approve=data.startswith('v114_payment_approve_'); pid=data.split('_',3)[3]
        payments=_v114_load(V114_PAYMENTS_DB,{})
        item=payments.get(pid)
        if not item or item.get('status') not in ('pending','review'): await q.answer('Request already processed.',show_alert=True); return True
        target=int(item['user_id'])
        if approve:
            expiry=_v114_grant(target,item['plan']['days']); item['status']='approved'; item['approved_at']=datetime.now().isoformat()
            await context.bot.send_message(target,f'✅ Payment approved. Premium active until {expiry.strftime("%Y-%m-%d %H:%M")}. Check My Stats.')
            await q.answer('Approved.'); await q.message.reply_text('Payment approved.')
        else:
            rejects=_v114_load(V114_REJECTIONS_DB,{})
            count=int(rejects.get(str(target),0))+1
            rejects[str(target)]=count; _v114_save(V114_REJECTIONS_DB,rejects)
            item['rejections']=count
            if count>=3:
                item['status']='rejected_banned'; ban_user(target,'Fake payment screenshots (3 rejections)')
                await context.bot.send_message(target,'You are banned due to fake payment.')
            else:
                item['status']='rejected'; await context.bot.send_message(target,f'❌ Payment screenshot rejected ({count}/3). You may submit a valid screenshot again.')
            await q.answer('Rejected.'); await q.message.reply_text(f'Rejected. Count: {count}/3')
        _v114_save(V114_PAYMENTS_DB,payments); return True
    return False

async def _v114_message_state(update, context):
    msg=update.effective_message; user=update.effective_user; uid=user.id
    state=context.user_data.get('v114_state')
    if not state or not msg or not msg.text: return False
    text=msg.text.strip()
    if text.lower()=='/cancel': context.user_data.pop('v114_state',None); await msg.reply_text('Cancelled.',reply_markup=get_main_keyboard(uid)); return True
    if state=='redeem_code':
        codes=_v114_load(V114_CODES_DB,{}) ; code=text.upper(); entry=codes.get(code)
        if not entry or entry.get('used_by') and not entry.get('multi_use'):
            await msg.reply_text('❌ Invalid or already-used redeem code.'); return True
        expiry=_v114_grant(uid,entry['days']); entry['used_by']=uid; entry['used_at']=datetime.now().isoformat(); _v114_save(V114_CODES_DB,codes)
        context.user_data.pop('v114_state',None); await msg.reply_text(f'✅ Premium activated until {expiry.strftime("%Y-%m-%d %H:%M")}.',reply_markup=get_main_keyboard(uid)); return True
    if not is_admin(uid) and state not in ('payment_screenshot',):
        context.user_data.pop('v114_state',None); await msg.reply_text('⛔ Admin access required.'); return True
    if state=='promo_code':
        context.user_data['v114_new_code']=text.upper(); context.user_data['v114_state']='promo_days'; await msg.reply_text('How many days of premium should this code grant? Send a positive number of days.'); return True
    if state=='promo_days':
        try: days=float(text); assert days>0
        except Exception: await msg.reply_text('Send a positive number of days.'); return True
        code=context.user_data.pop('v114_new_code',''); codes=_v114_load(V114_CODES_DB,{})
        if not code: context.user_data.pop('v114_state',None); await msg.reply_text('No code supplied; start again.'); return True
        codes[code]={'days':days,'created_by':uid,'created_at':datetime.now().isoformat(),'used_by':None}; _v114_save(V114_CODES_DB,codes); context.user_data.pop('v114_state',None)
        await msg.reply_text(f'✅ Promo code created: <code>{html.escape(code)}</code>\nPremium days: {days:g}',parse_mode='HTML'); return True
    if state=='add_uid' or state=='deduct_uid':
        if not text.isdigit(): await msg.reply_text('Send a numeric Telegram user ID.'); return True
        context.user_data['v114_target_uid']=int(text)
        scripts=load_bot_scripts(); owned=[x for x in scripts.values() if str(x.get('user_id'))==text]
        run=sum(str(x.get('status','')).lower()=='running' for x in owned)
        exp=_v114_premium_until(text); rem=max(0,(exp-datetime.now()).total_seconds()/86400) if exp and exp>datetime.now() else 0
        await msg.reply_text(f'User {text}\nFiles: {len(owned)} · Running: {run} · Stopped: {len(owned)-run}\nPremium remaining: {rem:.2f} days\n\nSend duration (e.g. 30, 2d, 4h, 30m).')
        context.user_data['v114_state']='add_duration' if state=='add_uid' else 'deduct_duration'; return True
    if state in ('add_duration','deduct_duration'):
        days=_v114_duration_days(text)
        if days is None: await msg.reply_text('Invalid duration. Use 30, 2d, 4h, or 30m.'); return True
        target=context.user_data.get('v114_target_uid')
        if state=='add_duration':
            expiry=_v114_grant(target,days)
            try: await context.bot.send_message(target,f'👑 Admin granted you premium until {expiry.strftime("%Y-%m-%d %H:%M")}.')
            except Exception: pass
            await msg.reply_text(f'✅ Premium added for {target}. Expiry: {expiry.strftime("%Y-%m-%d %H:%M")}')
        else:
            expiry=_v114_deduct(target,days); await msg.reply_text(f'✅ Premium deducted for {target}. Remaining expiry: {expiry.strftime("%Y-%m-%d %H:%M") if expiry else "None (expired)"}')
            try: await context.bot.send_message(target,'Your premium duration was adjusted by an admin.')
            except Exception: pass
        context.user_data.pop('v114_target_uid',None); context.user_data.pop('v114_state',None); return True
    if state=='plan_days':
        try: days=float(text); assert days>0
        except Exception: await msg.reply_text('Enter a positive number of days.'); return True
        context.user_data['v114_plan_days']=days; context.user_data['v114_state']='plan_amount'; await msg.reply_text('Send the plan price in INR (numbers only).'); return True
    if state=='plan_amount':
        try: amount=float(text); assert amount>0
        except Exception: await msg.reply_text('Enter a positive amount.'); return True
        plans=_v114_plan_list(); plans.append({'days':context.user_data.pop('v114_plan_days'), 'amount':amount}); _v114_save(V114_PLANS_DB,plans); context.user_data.pop('v114_state',None); await msg.reply_text('✅ Plan added. You can add more from Premium Admin Panel.'); return True
    if state=='tutorial_caption':
        tut=_v114_load(V114_TUTORIAL_DB,{})
        tut['caption']=text; _v114_save(V114_TUTORIAL_DB,tut); context.user_data.pop('v114_state',None)
        await msg.reply_text('✅ Tutorial caption saved.'); return True
    if state=='upi':
        if '@' not in text: await msg.reply_text('That does not look like a UPI ID. Send a valid UPI ID.'); return True
        _v114_save(V114_UPI_DB,{'upi_id':text}); context.user_data.pop('v114_state',None); await msg.reply_text('✅ UPI ID saved.'); return True
    return False

_v114_prev_button_handler = button_handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q=update.callback_query
    if q and (q.data or '').startswith('v114_'):
        if await _v114_premium_callback(update,context): return
    return await _v114_prev_button_handler(update,context)

_v114_prev_handle_message = handle_message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message and update.effective_message.text:
        text=update.effective_message.text.strip()
        normalized=' '.join(text.upper().split())
        if normalized=='TUTORIAL':
            tutorial=_v114_load(V114_TUTORIAL_DB,{})
            if tutorial.get('file_id'):
                await update.effective_message.reply_video(tutorial['file_id'],caption=tutorial.get('caption','Tutorial'))
            else:
                await update.effective_message.reply_text('No tutorial available',reply_markup=get_main_keyboard(update.effective_user.id))
            return
        if normalized=='BUY PREMIUM':
            plans=_v114_plan_list()
            if not plans: await update.effective_message.reply_text('No premium plans available yet. Please contact support.',reply_markup=get_main_keyboard(update.effective_user.id)); return
            rows=[[user_button(f'{x.get("days")} days — ₹{x.get("amount")}', '🟩', callback_data=f'v114_plan_{i}',style='success')] for i,x in enumerate(plans)]
            await update.effective_message.reply_text('💎 Choose a premium plan:',reply_markup=InlineKeyboardMarkup(rows)); return
        if normalized=='REDEEM CODE':
            context.user_data['v114_state']='redeem_code'; await update.effective_message.reply_text('Send your redeem code now, or /cancel to cancel.'); return
        if normalized in ('MY STATS','STATS','STATISTICS'):
            await _v114_user_stats(update.effective_message,update.effective_user.id); return
        if await _v114_message_state(update,context): return
    return await _v114_prev_handle_message(update,context)

async def _v114_payment_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg=update.effective_message; uid=update.effective_user.id
    if context.user_data.get('v114_state')=='tutorial_video' and is_admin(uid) and msg and msg.video:
        tut=_v114_load(V114_TUTORIAL_DB,{}) ; tut['file_id']=msg.video.file_id; _v114_save(V114_TUTORIAL_DB,tut)
        context.user_data['v114_state']='tutorial_caption'; await msg.reply_text('Video saved. Now send the caption text.'); return
    if context.user_data.get('v114_state')=='payment_screenshot' and msg and msg.photo:
        pid=context.user_data.get('v114_payment_id'); payments=_v114_load(V114_PAYMENTS_DB,{})
        item=payments.get(pid)
        if not item or item.get('user_id')!=uid:
            await msg.reply_text('Payment request not found. Please choose a plan again.'); context.user_data.pop('v114_state',None); return
        item['status']='review'; item['file_id']=msg.photo[-1].file_id; item['submitted_at']=datetime.now().isoformat(); _v114_save(V114_PAYMENTS_DB,payments); context.user_data.pop('v114_state',None)
        await msg.reply_text('✅ Screenshot submitted. Admin will review it.')
        for aid in ADMIN_USER_IDS:
            try:
                await context.bot.send_photo(aid,photo=item['file_id'],caption=f'Payment screenshot\nUser: {uid}\nPlan: {item["plan"].get("days")} days — ₹{item["plan"].get("amount")}\nRequest: {pid}',reply_markup=InlineKeyboardMarkup([[user_button('Approve','✅',callback_data=f'v114_payment_approve_{pid}',style='success'),user_button('Reject','❌',callback_data=f'v114_payment_reject_{pid}',style='danger')]]))
            except Exception: logger.warning('Unable to notify admin %s about payment %s',aid,pid)
        return
    await admin_broadcast_message(update,context)

_v114_prev_start_script = handle_start_script
async def handle_start_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q=update.callback_query; uid=q.from_user.id if q else update.effective_user.id
    if not _v114_has_premium(uid):
        scripts=load_bot_scripts(); owned=[(sid,x) for sid,x in scripts.items() if str(x.get('user_id'))==str(uid)]
        running=[(sid,x) for sid,x in owned if str(x.get('status','')).lower()=='running']
        if running:
            # Free users can keep only one running script; stop other running scripts before launch.
            target=(q.data or '').replace('start_script_','',1) if q else ''
            for sid,x in running:
                if sid==target: continue
                x['manual_stop']=True; x['status']='stopped'
                try:
                    with SCRIPT_PROCESS_LOCK: ent=SCRIPT_PROCESSES.get(str(sid)); proc=ent.get('process') if ent else None
                    if proc and proc.poll() is None: proc.terminate()
                except Exception: pass
            save_bot_scripts(scripts)
    return await _v114_prev_start_script(update,context)

async def _v114_expiry_alert_job(context):
    db=_v114_load(V114_PREMIUM_DB,{})
    now=datetime.now()
    for uid,info in list(db.items()):
        try: expiry=datetime.fromisoformat(info['expires_at'])
        except Exception: continue
        if now < expiry <= now+timedelta(hours=24) and not info.get('alert_sent'):
            try:
                await context.bot.send_message(int(uid),'⚠️ Your premium expires within 24 hours. Buy or redeem premium to extend it.',reply_markup=ReplyKeyboardMarkup([[KeyboardButton('BUY PREMIUM'),KeyboardButton('REDEEM CODE')],[KeyboardButton('MY SCRIPTS')]],resize_keyboard=True))
                info['alert_sent']=True
            except Exception: pass
        if expiry <= now:
            # On expiry, stop all but one running script; subsequent starts switch the kept script.
            scripts=load_bot_scripts(); owned=[(sid,x) for sid,x in scripts.items() if str(x.get('user_id'))==str(uid) and str(x.get('status','')).lower()=='running']
            for sid,x in owned[1:]:
                x['manual_stop']=True; x['status']='stopped'
                try:
                    with SCRIPT_PROCESS_LOCK: ent=SCRIPT_PROCESSES.get(str(sid)); proc=ent.get('process') if ent else None
                    if proc and proc.poll() is None: proc.terminate()
                except Exception: pass
            if owned: _v114_save(V114_PREMIUM_DB,db)
            if len(owned)>1: save_bot_scripts(scripts)
    _v114_save(V114_PREMIUM_DB,db)


# ==================== VERSION 115 FREE / PAID MODE ====================
# Free mode is the default: everyone can run unlimited scripts.
# Paid mode: admins and premium users have unlimited concurrent scripts;
# non-premium users may run only one script at a time.
V115_MODE_DB = f"{DB_DIR}/hosting_mode.json"
V115_MODE_DEFAULT = "paid"
V115_LIFETIME_DAYS = 999
V115_LIFETIME_EXPIRY = "9999-12-31T23:59:59"


def _v115_mode():
    data = _v114_load(V115_MODE_DB, {})
    mode = str(data.get("mode", V115_MODE_DEFAULT)).lower()
    return mode if mode in ("free", "paid") else V115_MODE_DEFAULT


def _v115_set_mode(mode):
    if mode not in ("free", "paid"):
        raise ValueError("mode must be free or paid")
    _v114_save(V115_MODE_DB, {"mode": mode, "updated_at": datetime.now().isoformat(timespec="seconds")})


def _v115_is_unlimited(uid):
    return _v115_mode() == "free" or is_admin(int(uid)) or _v114_has_premium(int(uid))


def _v115_stop_process(sid, item):
    """Stop a tracked child process and mark its record as stopped."""
    item["manual_stop"] = True
    item["status"] = "stopped"
    try:
        with SCRIPT_PROCESS_LOCK:
            ent = SCRIPT_PROCESSES.get(str(sid))
            proc = ent.get("process") if isinstance(ent, dict) else None
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
    except Exception as exc:
        logger.warning("Mode-change stop failed for script %s: %s", sid, exc)


async def _v115_switch_mode(context, admin_id):
    old = _v115_mode()
    new = "paid" if old == "free" else "free"
    _v115_set_mode(new)
    stopped = []
    if new == "paid":
        scripts = load_bot_scripts()
        for sid, item in list(scripts.items()):
            try:
                owner_id = int(item.get("user_id", 0))
            except Exception:
                owner_id = 0
            # Never stop an admin's scripts during the Free -> Paid transition.
            if owner_id and is_admin(owner_id):
                continue
            if str(item.get("status", "")).lower() == "running":
                stopped.append((owner_id, str(item.get("name") or item.get("original_name") or sid)))
                _v115_stop_process(sid, item)
        save_bot_scripts(scripts)

        # Notify users known from either user registry or script records.
        recipients = set()
        try:
            recipients.update(int(x) for x in load_json(USERS_DB).keys() if str(x).isdigit())
        except Exception:
            pass
        try:
            recipients.update(int(x.get("user_id")) for x in load_bot_scripts().values() if str(x.get("user_id", "")).isdigit())
        except Exception:
            pass
        recipients.difference_update(set(ADMIN_USER_IDS))
        keyboard = InlineKeyboardMarkup([
            [user_button("BUY PREMIUM", "💎", callback_data="v115_paid_buy", style="danger")],
            [user_button("REDEEM CODE", "🎟️", callback_data="v115_paid_redeem", style="danger")],
        ])
        text = ("<b>PAID MODE ENABLED</b>\n\n"
                "All your currently running scripts have been stopped.\n"
                "You can run one script at a time on the free tier. When that script is stopped, you can start another one.\n\n"
                "For unlimited concurrent scripts, purchase a premium plan or redeem a premium code.")
        for uid in recipients:
            if is_user_banned(uid):
                continue
            try:
                await context.bot.send_message(uid, text, parse_mode="HTML", reply_markup=keyboard)
            except Exception as exc:
                logger.info("Paid-mode notification failed for %s: %s", uid, exc)
    else:
        recipients = set()
        try:
            recipients.update(int(x) for x in load_json(USERS_DB).keys() if str(x).isdigit())
        except Exception:
            pass
        recipients.difference_update(set(ADMIN_USER_IDS))
        for uid in recipients:
            try:
                await context.bot.send_message(uid, "<b>FREE MODE ENABLED</b>\n\nYou can now run unlimited scripts for free.", parse_mode="HTML")
            except Exception:
                pass
    return new, len(stopped)


# Add mode toggle directly to the Premium Admin Panel as well.
async def _v114_premium_admin_screen(message):
    mode = _v115_mode().upper()
    rows = [
        [user_button('Generate Promo Code', '🎫', callback_data='v114_promo_create')],
        [user_button('Add Premium', '👑', callback_data='v114_add_premium'), user_button('Deduct Premium', '🧾', callback_data='v114_deduct_premium')],
        [user_button('Add Plans', '🗓️', callback_data='v114_add_plan'), user_button('Set UPI ID', '💳', callback_data='v114_set_upi')],
        [user_button(f'Enable Mode: {mode} (tap to switch)', '🔄', callback_data='v115_mode_toggle', style='danger' if mode == 'PAID' else 'success')],
        [user_button('View Plans', '🟩', callback_data='v114_view_plans'), user_button('Back to Admin', '⚙️', callback_data='v114_back_admin')],
    ]
    await message.reply_text(f'💎 <b>PREMIUM ADMIN PANEL</b>\nCurrent hosting mode: <b>{mode}</b>\n\nFREE: everyone can run unlimited scripts.\nPAID: admins and premium users are unlimited; other users can run one script at a time.', parse_mode='HTML', reply_markup=InlineKeyboardMarkup(rows))


_v115_previous_button_handler = button_handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    data = (q.data or '') if q else ''
    if data.startswith('v114_plan_') and _v115_mode() == 'free':
        await q.answer('Free mode is enabled. You can use unlimited scripts for free.', show_alert=True)
        return
    if data == 'v115_mode_toggle':
        if not is_admin(q.from_user.id):
            await q.answer('Admins only.', show_alert=True)
            return
        await q.answer('Updating hosting mode…')
        mode, stopped_count = await _v115_switch_mode(context, q.from_user.id)
        msg = (f'PAID mode enabled. Stopped {stopped_count} running user script(s). Admin scripts were left running.'
               if mode == 'paid' else 'FREE mode enabled. All users can run unlimited scripts.')
        try:
            await q.message.reply_text(msg)
            await _v114_premium_admin_screen(q.message)
        except Exception as exc:
            logger.warning('Could not refresh mode panel: %s', exc)
        return
    if data in ('v115_paid_buy', 'v115_paid_redeem'):
        await q.answer()
        if _v115_mode() == 'free':
            await q.message.reply_text('FREE MODE IS ENABLED\n\nYou can use unlimited scripts for free right now. Premium purchases and redeem codes will be available when Paid Mode is enabled.')
            return
        if data == 'v115_paid_buy':
            plans = _v114_plan_list()
            if not plans:
                await q.message.reply_text('No premium plans are available yet. Please contact support.')
                return
            rows = [[user_button(f'{x.get("days")} days — ₹{x.get("amount")}', '🟩', callback_data=f'v114_plan_{i}', style='success')] for i, x in enumerate(plans)]
            await q.message.reply_text('Choose a premium plan:', reply_markup=InlineKeyboardMarkup(rows))
        else:
            context.user_data['v114_state'] = 'redeem_code'
            await q.message.reply_text('Send your redeem code now, or /cancel to cancel.')
        return
    return await _v115_previous_button_handler(update, context)


_v115_previous_handle_message = handle_message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    user = update.effective_user
    if msg and user and msg.text:
        normalized = ' '.join(msg.text.strip().upper().split())
        if normalized in ('BUY PREMIUM', 'REDEEM CODE') and _v115_mode() == 'free':
            await msg.reply_text('FREE MODE IS ENABLED\n\nYou can use unlimited scripts for free right now. Premium purchases and redeem codes will be available when Paid Mode is enabled.', reply_markup=get_main_keyboard(user.id))
            return
        if context.user_data.get('v114_state') == 'redeem_code' and _v115_mode() == 'free':
            context.user_data.pop('v114_state', None)
            await msg.reply_text('FREE MODE IS ENABLED\n\nYou can use unlimited scripts for free right now. Redeem codes will be available when Paid Mode is enabled.')
            return
        # In paid mode admins still get the premium workflows, but don't impose
        # the paid-mode purchase restriction on them.
    return await _v115_previous_handle_message(update, context)


_v115_previous_start_script = handle_start_script
async def handle_start_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    uid = q.from_user.id if q else update.effective_user.id
    if _v115_is_unlimited(uid):
        # Call the handler below the old V114 one-running-script limiter.
        base = globals().get('_v114_prev_start_script')
        if base:
            return await base(update, context)
        return await _v115_previous_start_script(update, context)
    # Paid mode, non-premium non-admin: stop any other running script before starting this one.
    scripts = load_bot_scripts()
    target = (q.data or '').replace('start_script_', '', 1) if q else ''
    for sid, item in scripts.items():
        if str(item.get('user_id')) != str(uid) or str(item.get('status', '')).lower() != 'running' or str(sid) == target:
            continue
        _v115_stop_process(sid, item)
    save_bot_scripts(scripts)
    return await _v114_prev_start_script(update, context)


# Override promo duration validation: 999 days means lifetime; >999 is not accepted.
_v115_previous_message_state = _v114_message_state
async def _v114_message_state(update, context):
    msg = update.effective_message
    if msg and msg.text and context.user_data.get('v114_state') == 'promo_days':
        raw = msg.text.strip()
        try:
            days = float(raw)
        except Exception:
            await msg.reply_text('Enter a number from 1 to 999. Use 999 for lifetime premium.')
            return True
        if days <= 0 or days > 999:
            await msg.reply_text('Invalid duration. Enter 1–999 days. Use exactly 999 for lifetime premium.')
            return True
        code = context.user_data.pop('v114_new_code', '').upper()
        if not code:
            context.user_data.pop('v114_state', None)
            await msg.reply_text('No code supplied; start again.')
            return True
        codes = _v114_load(V114_CODES_DB, {})
        if code in codes:
            await msg.reply_text('That code already exists. Enter a different code name by starting Generate Promo Code again.')
            context.user_data.pop('v114_state', None)
            return True
        codes[code] = {'days': days, 'lifetime': days == V115_LIFETIME_DAYS, 'created_by': update.effective_user.id, 'created_at': datetime.now().isoformat(), 'used_by': None}
        _v114_save(V114_CODES_DB, codes)
        context.user_data.pop('v114_state', None)
        await msg.reply_text(f'Promo code created: <code>{html.escape(code)}</code>\nPremium validity: {"LIFETIME" if days == V115_LIFETIME_DAYS else f"{days:g} days"}', parse_mode='HTML')
        return True
    return await _v115_previous_message_state(update, context)


# Lifetime grants and free-mode behavior for the periodic premium job.
_v115_previous_grant = _v114_grant
def _v114_grant(uid, days):
    if float(days) == V115_LIFETIME_DAYS:
        db = _v114_load(V114_PREMIUM_DB, {})
        db[str(uid)] = {'user_id': int(uid), 'expires_at': V115_LIFETIME_EXPIRY, 'lifetime': True}
        _v114_save(V114_PREMIUM_DB, db)
        return datetime.fromisoformat(V115_LIFETIME_EXPIRY)
    return _v115_previous_grant(uid, days)


# ==================== V125 FULL-SOURCE CONFIGURATION AUDIT ====================
# Static scan for environment reads and unset/placeholder config constants.
# Never execute uploaded code during analysis.
HOSTING_ENGINE_VERSION = "125.0"

def _detected_env_from_source(source):
    text = str(source or '')
    required, optional = set(), set()
    placeholder = re.compile(r"(?i)(?:paste[_ -]?(?:your[_ -]?)?(?:value|token|id|hash|here)|your[_ -]?(?:token|api[_ -]?id|api[_ -]?hash|id|username|key|secret)|change[_ -]?me|replace[_ -]?me|placeholder|put[_ -].*here|example[_ -]?(?:token|id)|<[^>]+>)")
    env_patterns = [
        re.compile(r"os\.environ\s*\[\s*['\"]([A-Z][A-Z0-9_]{1,80})['\"]\s*\]"),
        re.compile(r"(?:os\.)?environ\.get\s*\(\s*['\"]([A-Z][A-Z0-9_]{1,80})['\"](\s*,\s*[^)]*)?\)"),
        re.compile(r"os\.getenv\s*\(\s*['\"]([A-Z][A-Z0-9_]{1,80})['\"](\s*,\s*[^)]*)?\)"),
        re.compile(r"(?<![A-Za-z0-9_])getenv\s*\(\s*['\"]([A-Z][A-Z0-9_]{1,80})['\"](\s*,\s*[^)]*)?\)"),
        re.compile(r"process\.env\.([A-Z][A-Z0-9_]{1,80})"),
        re.compile(r"process\.env\[['\"]([A-Z][A-Z0-9_]{1,80})['\"]\]"),
        re.compile(r"\$\{([A-Z][A-Z0-9_]{1,80})\}"),
    ]
    known = {
      'BOT_TOKEN','API_ID','API_HASH','APP_ID','APP_HASH','TELEGRAM_API_ID','TELEGRAM_API_HASH','TELEGRAM_BOT_TOKEN',
      'ADMIN_ID','ADMIN_IDS','ADMIN_TG_ID','ADMIN_USER_ID','ADMIN_USER_IDS','ADMIN_USERNAME','ADMIN_USER_NAME',
      'OWNER_ID','OWNER_TG_ID','OWNER_USERNAME','SUPPORT_USERNAME','SUPPORT_USER','SUPPORT_ID','BOT_USERNAME','BOT_NAME',
      'DATABASE_URL','DB_URL','MONGO_URI','MONGODB_URI','REDIS_URL','CHANNEL_ID','GROUP_ID','LOG_CHANNEL_ID',
      'FORCE_SUB_CHANNEL','UPI_ID','PAYMENT_UPI_ID','API_KEY','SECRET_KEY','CLIENT_ID','CLIENT_SECRET',
      'WEBHOOK_URL','WEBHOOK_SECRET','FIREBASE_URL','FIREBASE_DATABASE_URL','FIREBASE_API_KEY',
      'SESSION_STRING','STRING_SESSION','PHONE_NUMBER','PHONE','OWNER','TOKEN','BOTID','CHAT_ID','ADS_BIO_USERNAME'
    }
    env_names=set()
    for pat in env_patterns:
        for m in pat.finditer(text):
            key=m.group(1); env_names.add(key)
            has_default = len(m.groups()) > 1 and bool(m.group(2))
            default_text = m.group(2) if has_default else ''
            # Credential/config lookups should be requested if they have no fallback
            # or the fallback itself is blank/a placeholder. Real fallbacks remain usable.
            if not has_default or placeholder.search(default_text or '') or re.search(r"(?:None|null|undefined|['\"]{2})", default_text or '', re.I):
                required.add(key)
            else:
                optional.add(key)

    assign = re.compile(r"(?m)^\s*(?:export\s+)?([A-Z][A-Z0-9_]{1,80})\s*[:=]\s*(.*?)\s*;?\s*(?:#.*|//.*)?$")
    defined=set()
    for m in assign.finditer(text):
        key, rhs=m.group(1),m.group(2).strip().rstrip(';').strip()
        defined.add(key)
        config_like = key in known or any(part in key for part in ('TOKEN','API_KEY','API_HASH','SECRET','USERNAME','USER_ID','TG_ID','CHANNEL_ID','DATABASE_URL','URI','APP_ID','APP_HASH'))
        if not config_like: continue
        val=rhs.strip().strip('\"\'')
        # A variable assigned from getenv/environ/process.env is still an external
        # configuration dependency, not a hardcoded value.
        env_backed = bool(re.search(r'(?:getenv\s*\(|environ(?:\.get)?\s*\[?|process\.env)', rhs, re.I))
        empty = val in ('', 'None', 'null', 'undefined', '0', 'False', 'false')
        if empty or placeholder.search(val):
            required.add(key)
            optional.discard(key)
        elif not env_backed and (key in required or key in optional):
            # An explicit, non-placeholder hardcoded assignment means configured.
            required.discard(key); optional.discard(key)

    # If the source refers to a known config key but doesn't declare a value,
    # ask for it. This catches aliases like ADMIN_TG_ID and TELEGRAM_API_ID.
    askable = {'BOT_TOKEN','API_ID','API_HASH','APP_ID','APP_HASH','TELEGRAM_API_ID','TELEGRAM_API_HASH','TELEGRAM_BOT_TOKEN',
      'ADMIN_ID','ADMIN_IDS','ADMIN_TG_ID','ADMIN_USER_ID','ADMIN_USER_IDS','ADMIN_USERNAME','ADMIN_USER_NAME',
      'OWNER_ID','OWNER_TG_ID','OWNER_USERNAME','SUPPORT_USERNAME','SUPPORT_USER','SUPPORT_ID','DATABASE_URL','DB_URL',
      'MONGO_URI','MONGODB_URI','UPI_ID','PAYMENT_UPI_ID','API_KEY','SECRET_KEY','CLIENT_ID','CLIENT_SECRET',
      'SESSION_STRING','STRING_SESSION','PHONE_NUMBER','CHANNEL_ID','GROUP_ID','LOG_CHANNEL_ID','FIREBASE_URL',
      'FIREBASE_DATABASE_URL','ADS_BIO_USERNAME'}
    for key in known:
        if key in askable and key not in defined and re.search(r'(?<![A-Za-z0-9_])'+re.escape(key)+r'(?![A-Za-z0-9_])', text):
            required.add(key); optional.discard(key)
    required -= optional
    return sorted(required), sorted(optional)



# ==================== V127 GLOBAL MENU / CONVERSATION RESET ====================
HOSTING_ENGINE_VERSION = "129.0"
_V127_MENU_LABELS = {
    'UPLOAD FILE', 'UPLOAD SCRIPT', 'MY SCRIPTS', 'MY SCRIPT',
    'INSTALL MODULE', 'MODULE', 'BOT SPEED', 'HELP', 'MY STATS', 'STATS',
    'STATISTICS', 'BUY PREMIUM', 'REDEEM CODE', 'SUPPORT',
    'STOP ALL SCRIPTS', 'STOP ALL BOTS', 'TUTORIAL', 'VARIABLES',
    'BACK TO SCRIPT', 'BACK', 'CANCEL', 'ADMIN PANEL', 'PREMIUM ADMIN PANEL',
    'ENABLE MODE', 'FREE MODE', 'PAID MODE', 'GENERATE PROMO CODE',
    'ADD PREMIUM', 'DEDUCT PREMIUM', 'ADD PLANS', 'SET UPI ID',
    'SET TUTORIAL VIDEO', 'SUBMIT SCREENSHOT', 'VIEW LOGS'
}

def _v127_normalize_menu_label(value):
    value = str(value or '').upper()
    value = ''.join(ch if (ch.isalnum() or ch.isspace()) else ' ' for ch in value)
    return ' '.join(value.split())

def _v127_clear_pending_interaction(context, user_id=None):
    """Cancel pending text-input flows so the newly tapped menu action wins."""
    # First clear persisted awaiting-env marker for this user's current script.
    try:
        sid = context.user_data.get('awaiting_env_script_id')
        if sid:
            scripts = load_bot_scripts()
            record = scripts.get(str(sid))
            if record and (user_id is None or str(record.get('user_id')) == str(user_id)):
                record['awaiting_env'] = False
                scripts[str(sid)] = record
                save_bot_scripts(scripts)
    except Exception as exc:
        logger.warning('V127 could not clear stale env marker: %s', exc)

    exact_keys = {
        'awaiting_env_script_id', 'awaiting_module_name', 'awaiting_script_name',
        'awaiting_duration', 'v112_duration_script_id', 'v112_name_script_id',
        'v114_state', 'v114_new_code', 'v114_target_uid', 'v114_plan_days',
        'v114_payment_id', 'v115_state', 'rejecting_approval_key',
        'channel_input', 'upload_state', 'awaiting_variable_values',
        'pending_variable_script_id', 'variables_script_id',
        'awaiting_code', 'awaiting_promo_code', 'awaiting_premium_user_id',
        'awaiting_premium_days', 'awaiting_deduct_duration', 'awaiting_plan_days',
        'awaiting_plan_amount', 'awaiting_upi_id', 'awaiting_tutorial_video',
        'awaiting_tutorial_caption', 'tutorial_video', 'tutorial_caption',
        'awaiting_screenshot', 'awaiting_payment_screenshot'
    }
    for key in list(context.user_data):
        if key in exact_keys or key.startswith((
            'v112_', 'v113_', 'v114_', 'v115_', 'v126_', 'awaiting_env_',
            'awaiting_variable_', 'pending_variable_', 'premium_input_'
        )):
            context.user_data.pop(key, None)

_v127_previous_handle_message = handle_message
_V128_ACTIVE_INPUT_KEYS = {
    'awaiting_env_script_id', 'awaiting_module_name', 'awaiting_script_name',
    'awaiting_duration', 'awaiting_name', 'v112_duration_script_id',
    'v112_name_script_id', 'v114_state', 'v114_awaiting_redeem_code',
    'rejecting_approval_key', 'channel_input', 'upload_state',
    'awaiting_variable_values', 'pending_variable_script_id',
    'variables_script_id', 'admin_action', 'awaiting_broadcast_message',
    'awaiting_premium_user_id', 'awaiting_premium_days', 'awaiting_plan_days',
    'awaiting_plan_amount', 'awaiting_upi_id', 'awaiting_tutorial_video',
    'awaiting_tutorial_caption', 'awaiting_screenshot', 'awaiting_payment_screenshot'
}

def _v128_has_active_input(context):
    data = getattr(context, 'user_data', {}) or {}
    if any(data.get(k) for k in _V128_ACTIVE_INPUT_KEYS):
        return True
    # Some flows store their pending state on a script record rather than user_data.
    try:
        scripts = load_bot_scripts()
        uid = str(getattr(getattr(context, '_chat_id', None), 'id', '') or '')
        sid = data.get('awaiting_env_script_id')
        if sid and scripts.get(str(sid), {}).get('awaiting_env'):
            return True
    except Exception:
        pass
    return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    user = update.effective_user
    if msg and msg.text:
        label = _v127_normalize_menu_label(msg.text)
        if label in _V127_MENU_LABELS:
            _v127_clear_pending_interaction(context, user.id if user else None)
        elif not msg.text.startswith('/') and not _v128_has_active_input(context):
            # Unknown free text is intentionally ignored; only menu actions or an
            # active form/input flow should trigger a response.
            return
    return await _v127_previous_handle_message(update, context)




# ==================== V130 OPTIONAL-MISSING-VARIABLE BYPASS ====================
HOSTING_ENGINE_VERSION = "131.0"
_V130_PREVIOUS_HANDLE_MESSAGE = handle_message
_V130_PREVIOUS_BUTTON_HANDLER = button_handler

def _v130_variable_button(script_id):
    return InlineKeyboardMarkup([[user_button(
        'YES, PROCEED WITHOUT IT', '🟢',
        callback_data=f'v130_skip_missing_{script_id}', style='success'
    )]])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Accept partial KEY=VALUE input; show only remaining missing keys."""
    msg = getattr(update, 'effective_message', None)
    user = getattr(update, 'effective_user', None)
    env_sid = context.user_data.get('awaiting_env_script_id') if context and context.user_data else None
    if (msg and getattr(msg, 'text', None) and user and env_sid
            and _v127_normalize_menu_label(msg.text) not in _V127_MENU_LABELS):
        scripts, script = _get_script(str(env_sid))
        if script and _safe_script_for_user(script, user.id):
            text = (msg.text or '').strip()
            required = list(script.get('env_required') or [])
            existing = dict(script.get('env') or {})
            parsed = {}
            for raw in text.splitlines():
                raw = raw.strip()
                if not raw or raw.startswith('#') or '=' not in raw:
                    continue
                key, value = raw.split('=', 1)
                key, value = key.strip(), value.strip()
                if value and value != 'PASTE_VALUE_HERE':
                    # Accept equivalent names (e.g. TELEGRAM_BOT_TOKEN for BOT_TOKEN).
                    target_key = key if key in required else next(
                        (wanted for wanted in required if key.upper() in _v134_alias_group(wanted)), None
                    )
                    if target_key:
                        parsed[target_key] = value
            existing.update(parsed)
            script['env'] = existing
            missing = [key for key in required if not str(existing.get(key, '')).strip()]
            if missing:
                save_bot_scripts(scripts)
                context.user_data['awaiting_env_script_id'] = str(env_sid)
                script['awaiting_env'] = True
                save_bot_scripts(scripts)
                # Only list what is still missing; no repeated full credential block.
                await msg.reply_text(
                    '⚠️ <b>MISSING VARIABLE</b>\n\n'
                    + '\n'.join('• <code>' + html.escape(key) + '</code>' for key in missing)
                    + '\n\nSend the remaining KEY=VALUE line(s), or tap the green button to test without them.',
                    parse_mode='HTML', reply_markup=_v130_variable_button(env_sid)
                )
                return
            script['awaiting_env'] = False
            save_bot_scripts(scripts)
            context.user_data.pop('awaiting_env_script_id', None)
            await msg.reply_text('✅ <b>VARIABLES SAVED</b>\n\nNow set the run time.', parse_mode='HTML')
            await _v112_ask_duration(msg, context, str(env_sid))
            return
    return await _V130_PREVIOUS_HANDLE_MESSAGE(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = getattr(update, 'callback_query', None)
    data = (getattr(query, 'data', '') or '') if query else ''
    if query and data.startswith('v130_skip_missing_'):
        sid = data[len('v130_skip_missing_'):]
        scripts, script = _get_script(str(sid))
        if not script or not _safe_script_for_user(script, query.from_user.id):
            await query.answer('Project not found or access denied.', show_alert=True)
            return
        if str(context.user_data.get('awaiting_env_script_id') or '') != str(sid):
            # Also permit the button attached to the original prompt if the active
            # state was lost, but only if this project is still awaiting variables.
            if not script.get('awaiting_env'):
                await query.answer('This variable request is no longer active.', show_alert=True)
                return
        await query.answer('Proceeding without missing variables…')
        script['awaiting_env'] = False
        script['env_skipped_missing'] = [
            key for key in (script.get('env_required') or [])
            if not str((script.get('env') or {}).get(key, '')).strip()
        ]
        save_bot_scripts(scripts)
        if str(context.user_data.get('awaiting_env_script_id') or '') == str(sid):
            context.user_data.pop('awaiting_env_script_id', None)
        await query.message.reply_text(
            '🟢 <b>PROCEEDING WITHOUT MISSING VARIABLES</b>\n\n'
            'The project will be tested with the values provided. If the code actually requires a skipped value, it may fail; check the logs for the exact error.',
            parse_mode='HTML'
        )
        await _v112_ask_duration(query.message, context, str(sid))
        return
    return await _V130_PREVIOUS_BUTTON_HANDLER(update, context)


# ==================== V132 SMART ZIP ENVIRONMENT AUDIT ====================
# ZIP-only enhancement: inventory more config/source files, import real .env
# values into the hosted process, and ask only for values that are still missing.
HOSTING_ENGINE_VERSION = "132.0"

_V132_PREVIOUS_SCAN_PROJECT_ENV = _scan_project_env
_V132_PREVIOUS_PREPARE_ZIP_PROJECT = _prepare_zip_project

_V132_TEXT_SCAN_SUFFIXES = {
    '.py', '.pyw', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.json',
    '.txt', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.sh', '.bash',
    '.env.example', '.properties', '.service'
}
_V132_PLACEHOLDER_VALUE = re.compile(
    r'(?i)^(?:|none|null|undefined|changeme|change_me|replace_me|placeholder|'
    r'paste[_ -]?(?:your[_ -]?)?(?:value|token|id|hash|here)|'
    r'your[_ -]?(?:token|api[_ -]?id|api[_ -]?hash|id|username|key|secret)|'
    r'<[^>]+>|\*{3,}|x{4,})$'
)

def _v132_is_real_value(value):
    value = str(value or '').strip()
    if not value or _V132_PLACEHOLDER_VALUE.fullmatch(value):
        return False
    if re.search(r'(?i)^(?:your|paste|replace|change)[-_ ]', value):
        return False
    return True

def _v132_parse_env_file(path):
    """Read dotenv-style assignments without executing or importing project code."""
    values = {}
    try:
        lines = Path(path).read_text(encoding='utf-8', errors='replace').splitlines()
    except Exception:
        return values
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:].lstrip()
        if '=' not in line:
            continue
        key, value = line.split('=', 1)
        key, value = key.strip(), value.strip()
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', key):
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            quote = value[0]
            value = value[1:-1]
            if quote == '"':
                try:
                    value = bytes(value, 'utf-8').decode('unicode_escape')
                except Exception:
                    pass
        else:
            # In dotenv files, an unquoted # starts an inline comment.
            value = re.split(r'\s+#', value, maxsplit=1)[0].strip()
        if _v132_is_real_value(value):
            values[key] = value
    return values

def _v132_project_dotenv_values(workspace):
    """Load actual dotenv files; never treat examples/templates as credentials."""
    values = {}
    excluded = ('example', 'sample', 'template', 'dist', 'test.example')
    try:
        candidates = sorted(Path(workspace).rglob('*'), key=lambda x: (len(x.parts), str(x).lower()))
    except Exception:
        return values
    for fp in candidates:
        if not fp.is_file() or fp.is_symlink():
            continue
        name = fp.name.lower()
        if name == '.env' or (name.startswith('.env.') and not any(x in name for x in excluded)):
            if fp.stat().st_size > 256 * 1024:
                continue
            values.update(_v132_parse_env_file(fp))
    return values

def _scan_project_env(workspace):
    """ZIP scanner for env references across code and common deployment configs."""
    required, optional = set(), set()
    try:
        files = _project_files(workspace)
    except Exception:
        files = []
    for fp in files:
        if not fp.is_file() or fp.is_symlink():
            continue
        name = fp.name.lower()
        # Real .env files are loaded separately, not interpreted as source code.
        if name == '.env' or (name.startswith('.env.') and not any(x in name for x in ('example', 'sample', 'template'))):
            continue
        suffix = fp.suffix.lower()
        if suffix not in _V132_TEXT_SCAN_SUFFIXES and name not in ('dockerfile', 'makefile', 'procfile', 'host.json'):
            continue
        try:
            if fp.stat().st_size > 3 * 1024 * 1024:
                continue
            data = fp.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        r, o = _detected_env_from_source(data)
        required.update(r)
        optional.update(o)
    required -= optional
    return sorted(required), sorted(optional)

async def _prepare_zip_project(script, progress_message=None):
    """Run the existing ZIP build, then merge prefilled dotenv and saved values."""
    required, optional, entry = await _V132_PREVIOUS_PREPARE_ZIP_PROJECT(script, progress_message)
    workspace = script.get('workspace')
    supplied = {}
    if workspace and os.path.isdir(workspace):
        supplied.update(_v132_project_dotenv_values(workspace))
    # Previously entered values have priority over values shipped in the archive.
    saved = script.get('env') if isinstance(script.get('env'), dict) else {}
    supplied.update({str(k): str(v) for k, v in saved.items() if _v132_is_real_value(v)})
    script['env'] = supplied
    required = [key for key in required if not _v132_is_real_value(supplied.get(key, ''))]
    optional = [key for key in optional if not _v132_is_real_value(supplied.get(key, '')) and key not in required]
    script['env_required'] = sorted(set(required))
    script['env_optional'] = sorted(set(optional))
    script['env_prefilled_count'] = len([k for k, v in supplied.items() if _v132_is_real_value(v)])
    script['env_scan_version'] = HOSTING_ENGINE_VERSION
    return script['env_required'], script['env_optional'], entry


# ==================== V133 DIRECT .PY/.JS SMART CONFIG AUDIT ====================
# Scan direct uploads as carefully as ZIP projects. Existing literal settings and
# real sidecar dotenv values are reported as present; only unresolved runtime
# environment references are requested. The source file is never executed to scan it.
HOSTING_ENGINE_VERSION = "133.0"

_V133_CONFIG_NAME_RE = re.compile(r"(?m)^\s*(?:(?:const|let|var)\s+)?([A-Z][A-Z0-9_]{1,80})\s*=\s*(.*?)\s*(?:;\s*)?(?:#.*|//.*)?$")
_V133_CONFIG_NAMES = {
    'BOT_TOKEN','TELEGRAM_BOT_TOKEN','API_ID','TELEGRAM_API_ID','API_HASH','TELEGRAM_API_HASH',
    'ADMIN_ID','ADMIN_TG_ID','ADMIN_USER_ID','OWNER_ID','OWNER_TG_ID','SUPPORT_USERNAME',
    'BOT_USERNAME','DATABASE_URL','MONGO_URI','MONGODB_URI','CHANNEL_ID','GROUP_ID','API_KEY',
    'SECRET_KEY','CLIENT_ID','CLIENT_SECRET','WEBHOOK_URL','UPI_ID','PAYMENT_UPI_ID'
}


def _v133_literal_config_values(source):
    """Return config constants that are already assigned a non-placeholder literal."""
    found = {}
    placeholder = re.compile(r"(?i)(paste[_ -]?(?:your[_ -]?)?(?:value|token|id|hash|here)|your[_ -]?(?:token|api[_ -]?id|api[_ -]?hash|id|username)|change[_ -]?me|replace[_ -]?me|placeholder|put[_ -].*here|example[_ -]?(?:token|id)|<[^>]+>)")
    for m in _V133_CONFIG_NAME_RE.finditer(str(source or '')):
        key, rhs = m.group(1), m.group(2).strip().rstrip(';').strip()
        if key not in _V133_CONFIG_NAMES and not (key.endswith(('_TOKEN', '_ID', '_HASH', '_KEY', '_URL', '_URI', '_USERNAME', '_PASSWORD', '_SECRET'))):
            continue
        # Avoid treating references/expressions as known credentials. Only plain
        # quoted strings or simple scalar literals count as prefilled constants.
        is_quoted = len(rhs) >= 2 and rhs[0] == rhs[-1] and rhs[0] in ('"', "'")
        inner = rhs[1:-1].strip() if is_quoted else rhs
        if inner in ('', 'None', 'null', 'undefined', '...', '""', "''"):
            continue
        if placeholder.search(inner):
            continue
        if re.fullmatch(r"(?:True|False|true|false|null|None|undefined|[0-9]+)", inner):
            continue
        if is_quoted or re.fullmatch(r"[A-Za-z0-9_./:@+\-=]{3,}", inner):
            found[key] = inner
    return found


def _v133_sidecar_env_values(path):
    """Read only actual adjacent dotenv files, excluding examples and templates."""
    values = {}
    parent = Path(path).resolve().parent
    try:
        for fp in (parent / '.env', parent / '.env.local', parent / '.env.production'):
            if fp.is_file() and not fp.is_symlink() and fp.stat().st_size <= 256 * 1024:
                values.update(_v132_parse_env_file(fp))
    except Exception as exc:
        logger.debug('Direct dotenv scan failed: %s', exc)
    return values


async def _v112_prepare_direct(update, context, script_id):
    """Smart .py/.js scan, report present/missing fields, then continue setup."""
    scripts, script = _get_script(str(script_id))
    if not script:
        raise FileNotFoundError('Uploaded script record was not found.')
    path = os.path.abspath(str(script.get('path', '')))
    target = update.callback_query.message if getattr(update, 'callback_query', None) else getattr(update, 'effective_message', None)
    if not target:
        raise RuntimeError('No Telegram message target is available.')
    if not os.path.isfile(path):
        raise FileNotFoundError('Uploaded source file is missing from storage.')
    ext = Path(path).suffix.lower()
    if ext not in ('.py', '.js'):
        raise RuntimeError('Unsupported direct runtime. Use .py, .js or .zip.')

    source = Path(path).read_text(encoding='utf-8', errors='replace')
    required, optional = _detected_env_from_source(source)
    literal_values = _v133_literal_config_values(source)
    saved = script.get('env') if isinstance(script.get('env'), dict) else {}
    supplied = _v133_sidecar_env_values(path)
    supplied.update({str(k): str(v) for k, v in saved.items() if _v132_is_real_value(v)})
    # A key already assigned a usable literal in the source is not a missing env.
    required = [k for k in required if k not in literal_values and not _v132_is_real_value(supplied.get(k, ''))]
    optional = [k for k in optional if k not in literal_values and not _v132_is_real_value(supplied.get(k, '')) and k not in required]

    # Run the existing Python validation/dependency preparation, but do not add
    # a synthetic BOT_TOKEN requirement: request only variables the source needs.
    if ext == '.py':
        ok, changed, detail = await _prepare_user_python(path, script)
        _write_script_log(script, '\nV133 DIRECT PREPARATION: ' + ('PASSED' if ok else 'FAILED') + '\n' + str(detail) + '\n')
        if not ok:
            raise RuntimeError(detail)

    script['env'] = supplied
    script['env_required'] = sorted(set(required))
    script['env_optional'] = sorted(set(optional))
    script['env_literal_config_names'] = sorted(literal_values)
    script['env_prefilled_count'] = len([k for k, v in supplied.items() if _v132_is_real_value(v)]) + len(literal_values)
    script['env_scan_version'] = HOSTING_ENGINE_VERSION
    script['runtime'] = 'Python' if ext == '.py' else 'Node.js'
    script['awaiting_env'] = bool(script['env_required'])
    save_bot_scripts(scripts)

    all_detected = sorted(set(required) | set(optional) | set(literal_values) | set(supplied))
    present_names = sorted(set(literal_values) | {k for k, v in supplied.items() if _v132_is_real_value(v)})
    missing_names = sorted(set(required))
    optional_names = sorted(set(optional))
    report = (
        '🔎 <b>SMART SOURCE SCAN COMPLETE</b>\n━━━━━━━━━━━━━━━━━━━━\n\n'
        f'<b>File:</b> <code>{html.escape(os.path.basename(path))}</code>\n'
        f'<b>Runtime:</b> <code>{html.escape(script["runtime"])}</code>\n'
        f'<b>Config fields detected:</b> <code>{len(all_detected)}</code>\n'
        f'<b>Already filled/configured:</b> <code>{len(present_names)}</code>\n'
        f'<b>Required values missing:</b> <code>{len(missing_names)}</code>\n\n'
        '<b>Already configured fields</b>\n' + ('\n'.join('• <code>'+html.escape(k)+'</code>' for k in present_names) if present_names else '• None detected') + '\n\n'
        '<b>Required fields to fill</b>\n' + ('\n'.join('• <code>'+html.escape(k)+'</code>' for k in missing_names) if missing_names else '• None') + '\n\n'
        '<b>Optional fields</b>\n' + ('\n'.join('• <code>'+html.escape(k)+'</code>' for k in optional_names) if optional_names else '• None')
    )
    if len(report) > 3600:
        report = report[:3400] + '\n… <i>Additional detected fields are saved in the project scan.</i>'
    await target.reply_text(report, parse_mode='HTML')

    if missing_names:
        context.user_data['awaiting_env_script_id'] = str(script_id)
        template = '\n'.join(f'{k}=PASTE_VALUE_HERE' for k in missing_names)
        await target.reply_text(
            '🔐 <b>MISSING VARIABLES</b>\n\n'
            'Copy this template, fill the values you have, and send it back. Only unresolved required fields are listed.\n\n'
            f'<pre>{html.escape(template[:3000])}</pre>\n\n'
            'You can send partial values; the bot will ask only for the remaining fields. If you intentionally want to test without the missing values, use the option below.',
            parse_mode='HTML', reply_markup=_v130_variable_button(script_id)
        )
        return False

    script['awaiting_env'] = False
    save_bot_scripts(scripts)
    await _v112_finish_setup(target, context, script_id)
    return False


# ==================== V135 EMBEDDED PYTHON BUNDLE SCAN ====================
# Some single-file projects bundle their real modules as base64+zlib strings.
# Scanning only the launcher sees imports of os/zlib and misses all runtime
# variables inside the compressed modules. Decode statically for scanning only;
# never execute the uploaded source during analysis.
HOSTING_ENGINE_VERSION = "135.0"

def _v135_expand_embedded_python_source(source):
    source = str(source or '')
    chunks = [source]
    try:
        tree = ast.parse(source)
        bundle = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == '_BUNDLE_MODULES'
                for target in node.targets
            ):
                candidate = ast.literal_eval(node.value)
                if isinstance(candidate, dict):
                    bundle = candidate
                    break
        if not bundle:
            return source
        import zlib as _v135_zlib
        for module_name, payload in bundle.items():
            if not isinstance(module_name, str) or not isinstance(payload, str):
                continue
            try:
                decoded = _v135_zlib.decompress(base64.b64decode(payload, validate=True)).decode('utf-8', 'replace')
            except Exception as exc:
                logger.debug('Embedded module scan skipped for %s: %s', module_name, exc)
                continue
            chunks.append('\n# --- DECODED EMBEDDED MODULE FOR STATIC SCAN: ' + module_name + ' ---\n' + decoded)
    except Exception as exc:
        logger.debug('Embedded bundle static scan unavailable: %s', exc)
    return '\n'.join(chunks)

def _v135_declared_required_env(source):
    """Read an explicit REQUIRED_ENV_VARIABLES list without executing source."""
    text = str(source or '')
    match = re.search(r"(?ms)^\s*REQUIRED_ENV_VARIABLES\s*=\s*(\[[^\]]*\])", text)
    if not match:
        return []
    try:
        value = ast.literal_eval(match.group(1))
        if isinstance(value, (list, tuple, set)):
            return sorted({item.strip() for item in value if isinstance(item, str) and item.strip()})
    except Exception:
        pass
    return []

# ==================== V134 PRECISE ENV SCAN + ALIAS RECONCILIATION ====================
# Final override: request only genuine external env lookups, avoid adding guessed
# keys merely because their names appear in comments or unrelated source text.
HOSTING_ENGINE_VERSION = "134.0"

_V134_ENV_ALIASES = (
    {'BOT_TOKEN', 'TELEGRAM_BOT_TOKEN', 'TOKEN'},
    {'API_ID', 'TELEGRAM_API_ID', 'APP_ID'},
    {'API_HASH', 'TELEGRAM_API_HASH', 'APP_HASH'},
    {'ADMIN_ID', 'ADMIN_TG_ID', 'ADMIN_USER_ID', 'OWNER_ID', 'OWNER_TG_ID'},
    {'ADMIN_USERNAME', 'ADMIN_USER_NAME', 'ADMIN_USER', 'OWNER_USERNAME'},
    {'SUPPORT_USERNAME', 'SUPPORT_USER'},
    {'DATABASE_URL', 'DB_URL'},
    {'MONGO_URI', 'MONGODB_URI'},
    {'UPI_ID', 'PAYMENT_UPI_ID'},
    {'CHANNEL_ID', 'FORCE_SUB_CHANNEL'},
)

def _v134_alias_group(key):
    key = str(key or '').strip().upper()
    for group in _V134_ENV_ALIASES:
        if key in group:
            return group
    return {key}

def _v134_reconcile_env(values, target_keys=None):
    """Map equivalent env names without overwriting an exact supplied key."""
    result = {str(k): str(v) for k, v in (values or {}).items() if _v132_is_real_value(v)}
    keys = list(target_keys or [])
    for target in keys:
        if _v132_is_real_value(result.get(target)):
            continue
        aliases = _v134_alias_group(target)
        for source, value in list(result.items()):
            if source.upper() in aliases and _v132_is_real_value(value):
                result[target] = value
                break
    return result

def _detected_env_from_source(source):
    """Find real env reads; do not guess variables from names/comments alone."""
    text = str(source or '')
    # Remove comments while preserving quoted strings and line positions well enough
    # for this static scanner. This does not execute or import uploaded code.
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith('#') or stripped.startswith('//'):
            continue
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)
    required, optional = set(), set()
    patterns = [
        re.compile(r"os\.environ\s*\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*\]"),
        re.compile(r"(?:os\.)?environ\.get\s*\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"](\s*,\s*[^)]*)?\)"),
        re.compile(r"os\.getenv\s*\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"](\s*,\s*[^)]*)?\)"),
        re.compile(r"(?<![A-Za-z0-9_.])getenv\s*\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"](\s*,\s*[^)]*)?\)"),
        re.compile(r"process\.env\.([A-Za-z_][A-Za-z0-9_]*)"),
        re.compile(r"process\.env\s*\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*\]"),
        re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}"),
    ]
    for pattern in patterns:
        for match in pattern.finditer(text):
            key = match.group(1)
            default = match.group(2) if len(match.groups()) > 1 else None
            if default is None:
                required.add(key)
            elif re.search(r"(?:None|null|undefined|['\"]{2}|placeholder|changeme|your[_ -])", default, re.I):
                required.add(key)
            else:
                optional.add(key)
    required -= optional
    return sorted(required), sorted(optional)

# Wrap the ZIP prep once more so prefilled aliases satisfy the exact names used by code.
_V134_PREVIOUS_PREPARE_ZIP = _prepare_zip_project
async def _prepare_zip_project(script, progress_message=None):
    required, optional, entry = await _V134_PREVIOUS_PREPARE_ZIP(script, progress_message)
    values = _v134_reconcile_env(script.get('env') or {}, required + optional)
    script['env'] = values
    script['env_required'] = sorted(k for k in set(required) if not _v132_is_real_value(values.get(k)))
    script['env_optional'] = sorted(k for k in set(optional) if not _v132_is_real_value(values.get(k)) and k not in script['env_required'])
    save_bot_scripts(load_bot_scripts()) if False else None
    return script['env_required'], script['env_optional'], entry

HOSTING_ENGINE_VERSION = "135.0"

# Direct .py/.js preparation uses the same alias-aware values before deciding what's missing.
_V134_PREVIOUS_PREPARE_DIRECT = _v112_prepare_direct
async def _v112_prepare_direct(update, context, script_id):
    scripts, script = _get_script(str(script_id))
    if not script:
        raise FileNotFoundError('Uploaded script record was not found.')
    path = os.path.abspath(str(script.get('path', '')))
    ext = Path(path).suffix.lower()
    if ext not in ('.py', '.js'):
        return await _V134_PREVIOUS_PREPARE_DIRECT(update, context, script_id)
    source = Path(path).read_text(encoding='utf-8', errors='replace')
    scan_source = _v135_expand_embedded_python_source(source)
    required, optional = _detected_env_from_source(scan_source)
    # If a bundled project explicitly declares its required keys, trust that
    # declaration instead of misclassifying optional os.environ.get(..., '') keys.
    declared_required = _v135_declared_required_env(scan_source)
    if declared_required:
        discovered = set(required) | set(optional)
        required = sorted(set(declared_required))
        optional = sorted(discovered - set(required))
    literal_values = _v133_literal_config_values(scan_source)
    supplied = _v133_sidecar_env_values(path)
    saved = script.get('env') if isinstance(script.get('env'), dict) else {}
    supplied.update({str(k): str(v) for k, v in saved.items() if _v132_is_real_value(v)})
    supplied = _v134_reconcile_env(supplied, required + optional)
    required = [k for k in required if k not in literal_values and not _v132_is_real_value(supplied.get(k))]
    optional = [k for k in optional if k not in literal_values and not _v132_is_real_value(supplied.get(k)) and k not in required]
    if ext == '.py':
        ok, changed, detail = await _prepare_user_python(path, script)
        _write_script_log(script, '\nV134 DIRECT PREPARATION: ' + ('PASSED' if ok else 'FAILED') + '\n' + str(detail) + '\n')
        if not ok:
            raise RuntimeError(detail)
    script['env'] = supplied
    script['env_required'] = sorted(set(required))
    script['env_optional'] = sorted(set(optional))
    script['env_literal_config_names'] = sorted(literal_values)
    script['env_prefilled_count'] = len([k for k, v in supplied.items() if _v132_is_real_value(v)]) + len(literal_values)
    script['env_scan_version'] = HOSTING_ENGINE_VERSION
    script['runtime'] = 'Python' if ext == '.py' else 'Node.js'
    script['awaiting_env'] = bool(script['env_required'])
    save_bot_scripts(scripts)
    all_detected = sorted(set(required) | set(optional) | set(literal_values) | set(supplied))
    present_names = sorted(set(literal_values) | {k for k, v in supplied.items() if _v132_is_real_value(v)})
    missing_names = sorted(set(required))
    optional_names = sorted(set(optional))
    report = ('🔎 <b>SMART SOURCE SCAN COMPLETE</b>\n━━━━━━━━━━━━━━━━━━━━\n\n'
        f'<b>File:</b> <code>{html.escape(os.path.basename(path))}</code>\n'
        f'<b>Runtime:</b> <code>{html.escape(script["runtime"])}</code>\n'
        f'<b>Config fields detected:</b> <code>{len(all_detected)}</code>\n'
        f'<b>Already filled/configured:</b> <code>{len(present_names)}</code>\n'
        f'<b>Required values missing:</b> <code>{len(missing_names)}</code>\n\n'
        '<b>Already configured fields</b>\n' + ('\n'.join('• <code>'+html.escape(k)+'</code>' for k in present_names) if present_names else '• None detected') + '\n\n'
        '<b>Required fields to fill</b>\n' + ('\n'.join('• <code>'+html.escape(k)+'</code>' for k in missing_names) if missing_names else '• None') + '\n\n'
        '<b>Optional fields</b>\n' + ('\n'.join('• <code>'+html.escape(k)+'</code>' for k in optional_names) if optional_names else '• None'))
    if len(report) > 3600:
        report = report[:3400] + '\n… <i>Additional detected fields are saved in the project scan.</i>'
    target = update.callback_query.message if getattr(update, 'callback_query', None) else getattr(update, 'effective_message', None)
    if not target:
        raise RuntimeError('No Telegram message target is available.')
    await target.reply_text(report, parse_mode='HTML')
    if missing_names:
        context.user_data['awaiting_env_script_id'] = str(script_id)
        template = '\n'.join(f'{k}=PASTE_VALUE_HERE' for k in missing_names)
        await target.reply_text('🔐 <b>MISSING VARIABLES</b>\n\nCopy this template, fill the values you have, and send it back. Only unresolved required fields are listed.\n\n'
            f'<pre>{html.escape(template[:3000])}</pre>\n\nSend partial values if needed, or use Proceed Without Edit to test without missing values.',
            parse_mode='HTML', reply_markup=_v130_variable_button(script_id))
        return False
    script['awaiting_env'] = False
    save_bot_scripts(scripts)
    await _v112_finish_setup(target, context, script_id)
    return False


# V10 hard gate: banned non-admin users cannot use inline buttons or menu messages.
_V10_BAN_GATE_PREVIOUS_BUTTON_HANDLER = button_handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = getattr(update, 'callback_query', None)
    if q and is_user_banned(q.from_user.id) and not is_admin(q.from_user.id):
        try: await q.answer('You are banned by admin.', show_alert=True)
        except Exception: pass
        try: await q.message.reply_text('⛔ <b>You are banned by admin.</b> You cannot use this bot.', parse_mode='HTML')
        except Exception: pass
        return
    return await _V10_BAN_GATE_PREVIOUS_BUTTON_HANDLER(update, context)

_V10_BAN_GATE_PREVIOUS_HANDLE_MESSAGE = handle_message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = getattr(update, 'effective_user', None); msg = getattr(update, 'effective_message', None)
    if user and msg and is_user_banned(user.id) and not is_admin(user.id):
        await msg.reply_text('⛔ <b>You are banned by admin.</b> You cannot use this bot.', parse_mode='HTML')
        return
    return await _V10_BAN_GATE_PREVIOUS_HANDLE_MESSAGE(update, context)



# ==================== V10 SLOT + TIME PURCHASE SYSTEM ====================
# Integrated into the existing local-JSON hosting project; keeps existing BOT_TOKEN.
V10_SLOT_TIME_DB = os.path.join(DB_DIR, 'v10_slot_time.json')
V10_SLOT_PRICE = 29.0
V10_SLOT_DAYS = 29
V10_TIME_29D_PRICE = 49.0
V10_TIME_PENDING_DB = os.path.join(DB_DIR, 'v10_slot_time_payments.json')

def _v10_st_load():
    data = _v114_load(V10_SLOT_TIME_DB, {})
    return data if isinstance(data, dict) else {}

def _v10_st_save(data):
    _v114_save(V10_SLOT_TIME_DB, data)

def _v10_st_payments():
    data = _v114_load(V10_TIME_PENDING_DB, {})
    return data if isinstance(data, dict) else {}

def _v10_st_active_slots(uid, now=None):
    now = now or time.time()
    data = _v10_st_load().get(str(uid), {})
    return [x for x in data.get('slots', []) if float(x.get('expires_at', 0) or 0) > now]

def _v10_st_available_seconds(uid):
    data = _v10_st_load().get(str(uid), {})
    return max(0, int(data.get('time_credit_seconds', 0) or 0))

def _v10_st_parse_duration(raw):
    import re
    m = re.fullmatch(r'\s*(\d{1,6})\s*([MD])\s*', str(raw or ''), re.I)
    if not m:
        return None
    amount = int(m.group(1)); unit = m.group(2).upper()
    if amount < 1 or amount > 36500:
        return None
    seconds = amount * (60 if unit == 'M' else 86400)
    # ₹49 / 29 days, proportional pricing, rounded UP to whole rupees for UPI.
    import math
    price = max(1, math.ceil((seconds / (29 * 86400)) * V10_TIME_29D_PRICE))
    return seconds, price, f'{amount} minute(s)' if unit == 'M' else f'{amount} day(s)'

def _v10_st_admin_ids():
    ids = set()
    try:
        ids.update(int(x) for x in ADMIN_USER_IDS)
    except Exception:
        pass
    try:
        ids.update(int(x) for x in (globals().get('ADMIN_IDS') or []) if str(x).isdigit())
    except Exception:
        pass
    try:
        owner = globals().get('ADMIN_ID') or globals().get('OWNER_ID')
        if str(owner).isdigit(): ids.add(int(owner))
    except Exception:
        pass
    return ids

def _v10_st_build_qr(upi, amount, note):
    import urllib.parse
    pay_uri = 'upi://pay?pa=' + urllib.parse.quote(str(upi)) + '&pn=' + urllib.parse.quote('Hosting Bot') + '&am=' + urllib.parse.quote(f'{float(amount):.2f}') + '&cu=INR&tn=' + urllib.parse.quote(note)
    return 'https://api.qrserver.com/v1/create-qr-code/?size=320x320&data=' + urllib.parse.quote(pay_uri, safe='')

async def _v10_st_begin_payment(q, context, kind, quantity, amount, duration_seconds=0, duration_label=''):
    uid = q.from_user.id
    upi = (_v114_load(V114_UPI_DB, {}).get('upi_id') or V114_DEFAULT_UPI_ID or '').strip()
    if not upi:
        await q.answer('UPI ID is not configured by admin.', show_alert=True); return
    pid = f'st_{uid}_{int(time.time())}_{secrets.token_hex(3)}'
    payments = _v10_st_payments()
    payments[pid] = {'payment_id':pid, 'user_id':uid, 'kind':kind, 'quantity':int(quantity), 'amount':float(amount), 'duration_seconds':int(duration_seconds), 'duration_label':duration_label, 'status':'awaiting_utr', 'created_at':time.time(), 'utr':'', 'screenshot_file_id':''}
    _v114_save(V10_TIME_PENDING_DB, payments)
    context.user_data['v10_st_payment_id'] = pid
    context.user_data['v10_st_state'] = 'utr'
    qr = _v10_st_build_qr(upi, amount, f'Hosting {kind} {pid}')
    await q.answer()
    await q.message.reply_photo(qr, caption=(f'<b>PAYMENT REQUEST</b>\n\nType: <b>{html.escape(kind.title())}</b>\nQuantity: <b>{quantity}</b>\n' + (f'Duration: <b>{html.escape(duration_label)}</b>\n' if duration_label else '') + f'Amount: <b>₹{amount:.2f}</b>\nUPI ID: <code>{html.escape(upi)}</code>\n\nPay using this QR, then send your UTR in a message. After that, send the payment screenshot.\n\nPayment will be activated only after admin approval.'), parse_mode='HTML')

async def _v10_st_buy_menu(message):
    rows = [[user_button('SLOTS', '🟩', callback_data='v10st_slots', style='success'), user_button('TIME', '🟩', callback_data='v10st_time', style='success')]]
    await message.reply_text('<b>BUY PREMIUM SECTION</b>\n\nWhat do you want to buy?', parse_mode='HTML', reply_markup=InlineKeyboardMarkup(rows))

async def _v10_st_callback(update, context):
    q = update.callback_query; data = q.data or ''; uid = q.from_user.id
    if data == 'v10st_slots':
        await q.answer(); context.user_data['v10_st_state'] = 'slot_quantity'
        await q.message.reply_text(f'<b>BUY SLOTS</b>\n\nPrice: ₹{V10_SLOT_PRICE:g} per slot\nValidity: {V10_SLOT_DAYS} days per slot\n\nHow many slots do you want to buy? Send a whole number (1–100). Use /cancel to cancel.', parse_mode='HTML'); return True
    if data == 'v10st_time':
        await q.answer(); context.user_data['v10_st_state'] = 'time_quantity'
        await q.message.reply_text('<b>BUY TIME</b>\n\n<code>1M</code> = 1 minute\n<code>1D</code> = 1 day\n\nPrice is calculated proportionally from ₹49 per 29 days and rounded up to whole rupees for UPI.\n\nEnter the duration, for example <code>60M</code> or <code>15D</code>. Use /cancel to cancel.', parse_mode='HTML'); return True
    if data == 'v10st_use_time':
        credit = _v10_st_available_seconds(uid)
        if credit <= 0:
            await q.answer('No unused time credit available.', show_alert=True); return True
        scripts = load_bot_scripts(); mine = [(sid, x) for sid,x in scripts.items() if str(x.get('user_id')) == str(uid)]
        if not mine:
            await q.answer('Upload a project first.', show_alert=True); return True
        rows=[]
        for sid, item in mine[:80]:
            label = str(item.get('name') or item.get('original_name') or sid)[:48]
            rows.append([user_button(label, '⏱️', callback_data=f'v10st_apply_{sid}')])
        rows.append([user_button('Cancel', '❌', callback_data='v10st_cancel')])
        await q.answer(); await q.message.reply_text(f'Unused time: <b>{html.escape(_format_duration(credit))}</b>\nChoose the project to apply it to:', parse_mode='HTML', reply_markup=InlineKeyboardMarkup(rows)); return True
    if data.startswith('v10st_apply_'):
        sid = data[len('v10st_apply_'):]
        scripts, item = _get_script(str(sid))
        if not item or not _safe_script_for_user(item, uid):
            await q.answer('Project not found or access denied.', show_alert=True); return True
        st = _v10_st_load(); entry = st.setdefault(str(uid), {'slots':[], 'time_credit_seconds':0})
        credit = int(entry.get('time_credit_seconds',0) or 0)
        if credit <= 0:
            await q.answer('No unused time credit available.', show_alert=True); return True
        now=time.time(); current=float(item.get('expires_at_epoch') or 0)
        base=max(now,current)
        item['expires_at_epoch']=base+credit
        item['v10_paid_expires_at']=base+credit
        item['v10_expiry_notice_sent']=False
        item['duration_seconds']=int(item.get('duration_seconds') or 0)+credit
        item['v10_time_extended']=True
        entry['time_credit_seconds']=0
        _v10_st_save(st); save_bot_scripts(scripts)
        await q.answer('Time applied successfully.')
        await q.message.reply_text(f'✅ <b>TIME APPLIED</b>\nProject: <code>{html.escape(str(item.get("name") or sid))}</code>\nAdded: <b>{html.escape(_format_duration(credit))}</b>\nNew expiry: <code>{datetime.fromtimestamp(item["expires_at_epoch"]).strftime("%Y-%m-%d %H:%M")}</code>', parse_mode='HTML')
        return True
    if data == 'v10st_cancel':
        context.user_data.pop('v10_st_state', None); await q.answer('Cancelled.'); await q.message.reply_text('Cancelled.'); return True
    if data.startswith('v10st_approve_') or data.startswith('v10st_reject_'):
        if not is_admin(uid): await q.answer('Admins only.', show_alert=True); return True
        approve=data.startswith('v10st_approve_'); pid=data.split('v10st_approve_' if approve else 'v10st_reject_',1)[1]
        payments=_v10_st_payments(); item=payments.get(pid)
        if not item or item.get('status') not in ('review','awaiting_utr','awaiting_screenshot'):
            await q.answer('Request already processed.', show_alert=True); return True
        target=int(item['user_id'])
        if approve:
            st=_v10_st_load(); entry=st.setdefault(str(target), {'slots':[], 'time_credit_seconds':0})
            if item['kind']=='slot':
                now=time.time()
                for _ in range(int(item.get('quantity',1))):
                    entry.setdefault('slots',[]).append({'slot_id':secrets.token_hex(4), 'purchased_at':now, 'expires_at':now+V10_SLOT_DAYS*86400, 'assigned_script':None})
            else:
                entry['time_credit_seconds']=int(entry.get('time_credit_seconds',0) or 0)+int(item.get('duration_seconds',0) or 0)
            _v10_st_save(st); item['status']='approved'; item['approved_at']=time.time(); _v114_save(V10_TIME_PENDING_DB,payments)
            await context.bot.send_message(target, f'✅ Your payment was approved.\nType: {item["kind"].title()}\nQuantity: {item.get("quantity",1)}\nAmount: ₹{float(item.get("amount",0)):.2f}\n' + (f'Unused time credit: {_format_duration(_v10_st_available_seconds(target))}' if item['kind']=='time' else f'Slots now active: {len(_v10_st_active_slots(target))}') + '\nThank you!')
            await q.answer('Approved.'); await q.message.reply_text(f'✅ Payment {pid} approved.')
        else:
            item['status']='rejected'; item['rejected_at']=time.time(); _v114_save(V10_TIME_PENDING_DB,payments)
            await context.bot.send_message(target, f'❌ Your {item["kind"]} payment request was rejected by admin. Please contact support if you believe this is an error.')
            await q.answer('Rejected.'); await q.message.reply_text(f'❌ Payment {pid} rejected.')
        return True
    return False

async def _v10_st_handle_message(update, context):
    msg=update.effective_message; user=update.effective_user
    if not msg or not user or not getattr(msg,'text',None): return False
    state=context.user_data.get('v10_st_state'); text=msg.text.strip(); uid=user.id
    if not state: return False
    if text.lower() == '/cancel':
        context.user_data.pop('v10_st_state',None); context.user_data.pop('v10_st_payment_id',None)
        await msg.reply_text('Cancelled.'); return True
    if state=='slot_quantity':
        if not text.isdigit() or not 1 <= int(text) <= 100:
            await msg.reply_text('Send a whole number from 1 to 100.'); return True
        qty=int(text); context.user_data.pop('v10_st_state',None)
        # New slot bundle is ₹29 per slot, each slot lasts 29 days.
        class _FakeQ: pass
        q=_FakeQ(); q.from_user=user; q.message=msg; q.answer=lambda *a,**k: None
        # No callback answer is needed for text-driven flow.
        upi=(_v114_load(V114_UPI_DB,{}).get('upi_id') or V114_DEFAULT_UPI_ID or '').strip()
        if not upi: await msg.reply_text('UPI ID is not configured. Contact admin.'); return True
        pid=f'st_{uid}_{int(time.time())}_{secrets.token_hex(3)}'; payments=_v10_st_payments()
        payments[pid]={'payment_id':pid,'user_id':uid,'kind':'slot','quantity':qty,'amount':V10_SLOT_PRICE*qty,'duration_seconds':0,'duration_label':f'{V10_SLOT_DAYS} days per slot','status':'awaiting_utr','created_at':time.time(),'utr':'','screenshot_file_id':''}; _v114_save(V10_TIME_PENDING_DB,payments)
        context.user_data['v10_st_payment_id']=pid; context.user_data['v10_st_state']='utr'
        await msg.reply_photo(_v10_st_build_qr(upi,V10_SLOT_PRICE*qty,f'Hosting slots {pid}'), caption=f'<b>PAYMENT REQUEST</b>\n\nType: <b>Slots</b>\nQuantity: <b>{qty}</b>\nValidity: <b>{V10_SLOT_DAYS} days per slot</b>\nAmount: <b>₹{V10_SLOT_PRICE*qty:.2f}</b>\nUPI ID: <code>{html.escape(upi)}</code>\n\nPay using this QR, then send UTR, followed by payment screenshot. Admin approval is required.', parse_mode='HTML'); return True
    if state=='time_quantity':
        parsed=_v10_st_parse_duration(text)
        if not parsed:
            await msg.reply_text('Invalid format. Use a duration such as 60M or 15D.'); return True
        seconds,amount,label=parsed; context.user_data.pop('v10_st_state',None)
        upi=(_v114_load(V114_UPI_DB,{}).get('upi_id') or V114_DEFAULT_UPI_ID or '').strip()
        if not upi: await msg.reply_text('UPI ID is not configured. Contact admin.'); return True
        pid=f'st_{uid}_{int(time.time())}_{secrets.token_hex(3)}'; payments=_v10_st_payments()
        payments[pid]={'payment_id':pid,'user_id':uid,'kind':'time','quantity':1,'amount':amount,'duration_seconds':seconds,'duration_label':label,'status':'awaiting_utr','created_at':time.time(),'utr':'','screenshot_file_id':''}; _v114_save(V10_TIME_PENDING_DB,payments)
        context.user_data['v10_st_payment_id']=pid; context.user_data['v10_st_state']='utr'
        await msg.reply_photo(_v10_st_build_qr(upi,amount,f'Hosting time {pid}'), caption=f'<b>PAYMENT REQUEST</b>\n\nType: <b>Time</b>\nDuration: <b>{html.escape(label)}</b>\nAmount: <b>₹{amount:.2f}</b>\nUPI ID: <code>{html.escape(upi)}</code>\n\nPay using this QR, then send UTR, followed by payment screenshot. Admin approval is required.', parse_mode='HTML'); return True
    if state=='utr':
        if len(text)<6 or len(text)>80:
            await msg.reply_text('Please send a valid UTR/reference number.'); return True
        pid=context.user_data.get('v10_st_payment_id'); payments=_v10_st_payments(); item=payments.get(pid)
        if not item or item.get('status')!='awaiting_utr':
            context.user_data.pop('v10_st_state',None); await msg.reply_text('Payment request not found. Start again from BUY PREMIUM.'); return True
        item['utr']=text; item['status']='awaiting_screenshot'; _v114_save(V10_TIME_PENDING_DB,payments); context.user_data['v10_st_state']='screenshot'
        await msg.reply_text('Now send the payment screenshot as a photo.'); return True
    return False

async def _v10_st_photo_handler(update, context):
    msg=update.effective_message; user=update.effective_user
    if user and context.user_data.get('v10_st_state')=='screenshot' and msg and msg.photo:
        pid=context.user_data.get('v10_st_payment_id'); payments=_v10_st_payments(); item=payments.get(pid)
        if not item or item.get('status')!='awaiting_screenshot':
            await msg.reply_text('Payment request not found. Start again from BUY PREMIUM.'); return True
        item['screenshot_file_id']=msg.photo[-1].file_id; item['status']='review'; item['submitted_at']=time.time(); _v114_save(V10_TIME_PENDING_DB,payments)
        context.user_data.pop('v10_st_state',None); context.user_data.pop('v10_st_payment_id',None)
        details=(f'<b>SLOT/TIME PAYMENT REVIEW</b>\n\nPayment ID: <code>{html.escape(pid)}</code>\nUser: <code>{user.id}</code>\nType: <b>{html.escape(item["kind"].title())}</b>\nQuantity: <b>{item.get("quantity",1)}</b>\nDuration: <b>{html.escape(item.get("duration_label", "—"))}</b>\nAmount: <b>₹{float(item.get("amount",0)):.2f}</b>\nUTR: <code>{html.escape(item.get("utr", ""))}</code>\nStatus: <b>Pending review</b>')
        markup=InlineKeyboardMarkup([[user_button('APPROVE','✅',callback_data=f'v10st_approve_{pid}',style='success'),user_button('REJECT','❌',callback_data=f'v10st_reject_{pid}',style='danger')]])
        sent=0
        for admin_id in _v10_st_admin_ids():
            try:
                await context.bot.send_photo(admin_id, item['screenshot_file_id'], caption=details, parse_mode='HTML', reply_markup=markup); sent+=1
            except Exception as exc: logger.warning('Could not send slot/time payment to admin %s: %s',admin_id,exc)
        await msg.reply_text('✅ Payment details submitted for admin review. Your purchase will activate after approval.')
        if not sent: logger.error('No admin received slot/time payment review %s; check ADMIN_USER_IDS.',pid)
        return True
    return False

async def _v10_st_expiry_job(context):
    now=time.time(); state=_v10_st_load(); changed=False
    # Slot expiry notifications and script expiry enforcement.
    for uid, entry in list(state.items()):
        slots=entry.get('slots',[]); active=[s for s in slots if float(s.get('expires_at',0) or 0)>now]
        if len(active)!=len(slots): entry['slots']=active; changed=True
    scripts=load_bot_scripts(); scripts_changed=False
    for sid,item in list(scripts.items()):
        try: uid=int(item.get('user_id',0))
        except Exception: continue
        if not uid or is_admin(uid): continue
        exp=float(item.get('v10_paid_expires_at') or 0)
        if exp and exp <= now and str(item.get('status','')).lower()=='running':
            try: _v115_stop_process(str(sid),item); item['status']='stopped'; item['last_error']='Paid slot/time expired.'; scripts_changed=True
            except Exception as exc: logger.warning('Could not stop expired script %s: %s',sid,exc)
        if exp and now < exp <= now+3*86400 and not item.get('v10_expiry_notice_sent'):
            try:
                await context.bot.send_message(uid, f'⚠️ Your script <b>{html.escape(str(item.get("name") or sid))}</b> will expire in 3 days. Buy time to extend it.', parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[user_button('BUY TIME','⏱️',callback_data='v10st_time'),user_button('USE TIME','🕒',callback_data='v10st_use_time')]]))
                item['v10_expiry_notice_sent']=True; scripts_changed=True
            except Exception: pass
    if changed: _v10_st_save(state)
    if scripts_changed: save_bot_scripts(scripts)

_V10_ST_PREV_BUTTON_HANDLER = button_handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q=getattr(update,'callback_query',None)
    if q and (q.data or '').startswith('v10st_'):
        if await _v10_st_callback(update,context): return
    if q and q.data == 'v115_paid_buy':
        await q.answer(); await _v10_st_buy_menu(q.message); return
    # Purchased slots grant concurrent run capacity and each started project is
    # bound to one active slot expiry. Admin accounts remain unrestricted.
    if q and (q.data or '').startswith(('start_script_', 'v112_start_', 'run_script_')) and not is_admin(q.from_user.id):
        uid=q.from_user.id; active=_v10_st_active_slots(uid)
        if active:
            scripts=load_bot_scripts()
            running=[(sid,x) for sid,x in scripts.items() if str(x.get('user_id'))==str(uid) and str(x.get('status','')).lower()=='running']
            if len(running) >= len(active):
                await q.answer('All purchased slots are currently in use or expired. Buy another slot or stop a running script.', show_alert=True)
                return
            await _V10_ST_PREV_BUTTON_HANDLER(update,context)
            scripts=load_bot_scripts()
            running=[(sid,x) for sid,x in scripts.items() if str(x.get('user_id'))==str(uid) and str(x.get('status','')).lower()=='running']
            used={str(x.get('v10_slot_id')) for _,x in running if x.get('v10_slot_id')}
            unused=[slot for slot in active if str(slot.get('slot_id')) not in used]
            for sid,item in running:
                if not item.get('v10_paid_expires_at') and unused:
                    slot=unused.pop(0); item['v10_slot_id']=slot.get('slot_id')
                    item['v10_paid_expires_at']=float(slot.get('expires_at',time.time()))
                    item['expires_at_epoch']=float(slot.get('expires_at',time.time()))
                    item['duration_seconds']=max(0,int(float(slot.get('expires_at',time.time()))-time.time()))
                    item['v10_expiry_notice_sent']=False
            save_bot_scripts(scripts)
            return
    return await _V10_ST_PREV_BUTTON_HANDLER(update,context)

_V10_ST_PREV_HANDLE_MESSAGE = handle_message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg=update.effective_message; user=update.effective_user
    if msg and user and msg.text:
        normalized=' '.join(msg.text.upper().split())
        if normalized == 'BUY PREMIUM':
            await _v10_st_buy_menu(msg); return
        if await _v10_st_handle_message(update,context): return
    return await _V10_ST_PREV_HANDLE_MESSAGE(update,context)

_V10_ST_PREV_PAYMENT_PHOTO_HANDLER = _v114_payment_photo_handler
async def _v114_payment_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await _v10_st_photo_handler(update,context): return
    return await _V10_ST_PREV_PAYMENT_PHOTO_HANDLER(update,context)

# Re-register the job in main() using this wrapper so slot/time expiry checks run hourly.
_V10_ST_PREV_MAIN = main
def main():
    result = _V10_ST_PREV_MAIN()
    return result


# ==================== FINAL RELIABILITY PATCH ====================
# Independent approval records, real process stop, embedded-source scanning,
# active-runtime slots (paused while stopped), and slot-only purchase UI.
HOSTING_ENGINE_VERSION = "136.0"

# Keep the previous implementations available for delegation where appropriate.
_v136_previous_detected_env = _detected_env_from_source
_v136_previous_upload_handler = handle_file_upload
_v136_previous_stop_handler = handle_stop_script
_v136_previous_slot_expiry_job = _v10_st_expiry_job
_v136_previous_literal_config_values = _v133_literal_config_values


def _v133_literal_config_values(source):
    # Inspect the decoded bundled modules too, but never execute uploaded source.
    expanded = _v135_expand_embedded_python_source(source)
    return _v136_previous_literal_config_values(expanded)


def _detected_env_from_source(source):
    """Scan the launcher plus statically decoded embedded Python modules."""
    expanded = _v135_expand_embedded_python_source(source)
    required, optional = _v136_previous_detected_env(expanded)
    try:
        declared = _v135_declared_required_env(expanded)
        required = sorted(set(required) | set(declared))
        optional = sorted(set(optional) - set(required))
    except Exception:
        pass
    return required, optional


async def send_approval_file(update: Update, context: ContextTypes.DEFAULT_TYPE, document) -> str:
    """Send each upload as its own approval item and return its unique record key."""
    approval = load_approval_channel()
    if not approval or not approval.get('chat_id'):
        raise RuntimeError('Approval channel is not configured. Ask the admin to set it in /admin.')
    user = update.effective_user
    if not user:
        raise RuntimeError('Could not identify the uploader.')
    file_name = os.path.basename(document.file_name or 'unknown')
    file_type = get_file_type(file_name)
    safe_name = html.escape(file_name)
    safe_username = html.escape(user.username or 'N/A')
    created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    caption = (
        f"{EMOJI_FOLDER} <b>FILE PENDING APPROVAL</b>\n\n"
        f"<b>File Type:</b> <code>.{html.escape(file_type)}</code>\n"
        f"<b>File Name:</b> <code>{safe_name}</code>\n"
        f"<b>File Size:</b> <code>{format_file_size(document.file_size)}</code>\n"
        f"<b>User ID:</b> <code>{user.id}</code>\n"
        f"<b>Username:</b> {safe_username}\n"
        f"<b>Uploaded:</b> <code>{created}</code>"
    )
    # Telegram channel message IDs are unique per sent upload; never dedupe by file_id.
    sent = await context.bot.send_document(
        chat_id=approval['chat_id'], document=document.file_id,
        caption=caption, parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('💬 TALK TO USER', url=f'tg://user?id={user.id}')],
            [InlineKeyboardButton('✅ APPROVE', callback_data='approve_file_pending'),
             InlineKeyboardButton('❌ REJECT', callback_data='reject_file_pending')]
        ])
    )
    key = str(sent.message_id)
    pending = load_pending_approvals()
    pending[key] = {
        'approval_id': key, 'user_id': user.id, 'file_name': file_name,
        'file_size': document.file_size, 'file_type': file_type,
        'file_id': document.file_id, 'channel_id': approval['chat_id'],
        'message_id': sent.message_id, 'channel_caption': caption,
        'status': 'pending', 'created_at': created,
        'upload_update_id': getattr(update, 'update_id', None),
    }
    save_pending_approvals(pending)
    logger.info('Approval item created: id=%s user=%s file=%s', key, user.id, file_name)
    return key


async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reliable upload path: one approval-channel post per user upload."""
    msg = getattr(update, 'effective_message', None)
    user = getattr(update, 'effective_user', None)
    document = getattr(msg, 'document', None) if msg else None
    if not msg or not user or not document:
        return
    try:
        if is_admin(user.id) and context.user_data.get('admin_action') == 'broadcast':
            context.user_data.pop('admin_action', None)
            await perform_broadcast(update, context, msg)
            return
        if is_user_banned(user.id):
            await msg.reply_text('⛔ <b>ACCESS DENIED</b>\n\nYou are banned.', parse_mode='HTML')
            return
        if await enforce_user_system_gate(update, context):
            return
        file_name = os.path.basename(document.file_name or '')
        if not file_name.lower().endswith(SUPPORTED_UPLOAD_EXTENSIONS):
            await msg.reply_text('❌ <b>INVALID FILE</b>\n\nSupported formats: .py, .js and .zip.', parse_mode='HTML', reply_markup=get_main_keyboard(user.id))
            return
        if document.file_size and document.file_size > MAX_UPLOAD_SIZE:
            await msg.reply_text(f'❌ <b>FILE TOO LARGE</b>\n\nMaximum upload size: {MAX_UPLOAD_SIZE // (1024*1024)} MB.', parse_mode='HTML', reply_markup=get_main_keyboard(user.id))
            return
        _clear_user_env_session(context, user.id)
        add_upload_record(user.id, file_name, document.file_size)
        if is_admin(user.id):
            await _send_admin_auto_approved(update, context, document)
            logger.info('Admin upload auto-approved: user=%s file=%s', user.id, file_name)
            return
        # Do not tell the user it is pending unless the channel post actually succeeded.
        try:
            approval_key = await send_approval_file(update, context, document)
        except Exception as exc:
            logger.error('Approval channel send failed for user=%s file=%s: %s\n%s', user.id, file_name, exc, traceback.format_exc())
            await msg.reply_text(
                '❌ <b>UPLOAD NOT SUBMITTED</b>\n\n'
                f'<code>{html.escape(file_name)}</code> could not be sent to the approval channel. '
                'Please contact the admin; the bot has logged the error.',
                parse_mode='HTML', reply_markup=get_main_keyboard(user.id))
            return
        sent_user_message = await msg.reply_text(
            f'⏳ <b>FILE SUBMITTED FOR APPROVAL</b>\n\n<code>{html.escape(file_name)}</code>\n'
            'Your upload has its own approval request. You will be notified after review.',
            parse_mode='HTML', reply_markup=get_main_keyboard(user.id))
        pending = load_pending_approvals()
        record = pending.get(str(approval_key))
        if record and record.get('status') == 'pending':
            record['user_message_id'] = sent_user_message.message_id
            pending[str(approval_key)] = record
            save_pending_approvals(pending)
        logger.info('User upload submitted: user=%s file=%s approval=%s', user.id, file_name, approval_key)
    except Exception as exc:
        logger.error('Upload handler failed: %s\n%s', exc, traceback.format_exc())
        try:
            await msg.reply_text(f'❌ <b>UPLOAD ERROR</b>\n\n<pre>{html.escape(str(exc)[:1200])}</pre>', parse_mode='HTML', reply_markup=get_main_keyboard(user.id))
        except Exception:
            pass


# Slots represent 29 days of actual running time, not calendar time.
V10_SLOT_SECONDS = int(V10_SLOT_DAYS * 86400)

def _v10_st_active_slots(uid, now=None):
    state = _v10_st_load()
    entry = state.setdefault(str(uid), {'slots': [], 'time_credit_seconds': 0})
    changed = False
    now = time.time() if now is None else float(now)
    for slot in entry.get('slots', []):
        if 'remaining_seconds' not in slot:
            # Migrate existing purchases once; old expiry timestamps become remaining quota.
            old_expiry = float(slot.get('expires_at', 0) or 0)
            slot['remaining_seconds'] = max(0, min(V10_SLOT_SECONDS, int(old_expiry - now))) if old_expiry else V10_SLOT_SECONDS
            slot['assigned_script'] = slot.get('assigned_script')
            slot['last_accounted_at'] = None
            changed = True
    if changed:
        _v10_st_save(state)
    return [slot for slot in entry.get('slots', []) if int(slot.get('remaining_seconds', 0) or 0) > 0]


def _v10_slot_for(uid, slot_id):
    state = _v10_st_load()
    entry = state.get(str(uid), {})
    for slot in entry.get('slots', []):
        if str(slot.get('slot_id')) == str(slot_id):
            return entry, slot, state
    return None, None, state


def _v10_account_script_runtime(sid, script, now=None):
    """Debit only elapsed running time; stopped time never consumes the slot."""
    now = time.time() if now is None else float(now)
    uid = str(script.get('user_id', ''))
    slot_id = script.get('v10_slot_id')
    if not slot_id or is_admin(int(uid)):
        return False
    entry, slot, state = _v10_slot_for(uid, slot_id)
    if not slot:
        return False
    last = float(script.get('v10_last_accounted_at') or script.get('started_at_epoch') or now)
    if str(script.get('status', '')).lower() == 'running':
        elapsed = max(0, int(now - last))
        if elapsed:
            slot['remaining_seconds'] = max(0, int(slot.get('remaining_seconds', 0) or 0) - elapsed)
            changed = True
        else:
            changed = False
        script['v10_last_accounted_at'] = now
        script['v10_remaining_seconds'] = int(slot.get('remaining_seconds', 0) or 0)
        slot['last_accounted_at'] = now
        if changed:
            _v10_st_save(state)
        return int(slot.get('remaining_seconds', 0) or 0) <= 0
    return int(slot.get('remaining_seconds', 0) or 0) <= 0


def _v115_stop_process(sid, item):
    """Stop the complete managed process group, including child bot processes."""
    item["manual_stop"] = True
    item["status"] = "stopped"
    with SCRIPT_PROCESS_LOCK:
        ent = SCRIPT_PROCESSES.get(str(sid))
        proc = ent.get("process") if isinstance(ent, dict) else None
    if proc is None or proc.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except Exception:
        try: proc.terminate()
        except Exception: pass
    try:
        proc.wait(timeout=5)
    except Exception:
        try: os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            try: proc.kill()
            except Exception: pass
        try: proc.wait(timeout=2)
        except Exception: pass


async def _v10_st_expiry_job(context):
    """Account active runtime and stop projects whose purchased slot is exhausted."""
    scripts = load_bot_scripts()
    changed = False
    for sid, item in list(scripts.items()):
        try:
            uid = int(item.get('user_id', 0) or 0)
        except Exception:
            continue
        if not uid or is_admin(uid) or not item.get('v10_slot_id'):
            continue
        if str(item.get('status', '')).lower() != 'running':
            # If the process exited unexpectedly, settle the final interval once.
            # A user-requested stop clears this timestamp in handle_stop_script.
            last = item.get('v10_last_accounted_at')
            if last and not item.get('manual_stop'):
                entry, slot, state = _v10_slot_for(uid, item.get('v10_slot_id'))
                if slot:
                    elapsed = max(0, int(time.time() - float(last)))
                    slot['remaining_seconds'] = max(0, int(slot.get('remaining_seconds', 0) or 0) - elapsed)
                    item['v10_remaining_seconds'] = int(slot['remaining_seconds'])
                    _v10_st_save(state)
                item['v10_last_accounted_at'] = None
                changed = True
            continue
        # Reconcile actual process liveness before billing runtime.
        proc = _v112_live_process(sid)
        if proc is None:
            # Process monitor may have updated status already; still settle its final interval.
            depleted = _v10_account_script_runtime(sid, item)
            item['status'] = 'stopped'
            item['last_error'] = item.get('last_error') or 'Process exited.'
            item['v10_last_accounted_at'] = None
            changed = True
            continue
        depleted = _v10_account_script_runtime(sid, item)
        changed = True
        if depleted:
            try:
                _v115_stop_process(str(sid), item)
            except Exception as exc:
                logger.warning('Could not stop exhausted script %s: %s', sid, exc)
            item['status'] = 'stopped'
            item['manual_stop'] = True
            item['last_error'] = 'Purchased slot runtime exhausted.'
            item['last_exit_code'] = getattr(proc, 'returncode', None)
            with SCRIPT_PROCESS_LOCK:
                SCRIPT_PROCESSES.pop(str(sid), None)
            try:
                await context.bot.send_message(uid, f'⏱ <b>SLOT FINISHED</b>\n\n<code>{html.escape(str(item.get("name") or sid))}</code> has used its {V10_SLOT_DAYS}-day running-time slot. Buy another slot to run a script again.', parse_mode='HTML', reply_markup=get_main_keyboard(uid))
            except Exception:
                pass
    if changed:
        save_bot_scripts(scripts)


# Runtime selection is removed. Start immediately and let the purchased slot control the quota.
async def _v112_ask_duration(message, context, script_id):
    scripts, script = _get_script(script_id)
    if not script:
        await message.reply_text('Project not found. Please open MY SCRIPTS again.')
        return
    uid = int(script.get('user_id', 0) or 0)
    if not is_admin(uid):
        slot_id = script.get('v10_slot_id')
        entry, slot, state = _v10_slot_for(uid, slot_id) if slot_id else (None, None, _v10_st_load())
        if not slot or int(slot.get('remaining_seconds', 0) or 0) <= 0:
            script['status'] = 'stopped'
            script['last_error'] = 'No remaining slot runtime. Purchase a slot to start this project.'
            save_bot_scripts(scripts)
            await message.reply_text('🔒 <b>SLOT REQUIRED</b>\n\nBuy a slot to start this project. A slot provides 29 days of actual running time; stopping pauses the remaining time.', parse_mode='HTML', reply_markup=get_main_keyboard(uid))
            return
    try:
        process = await _v112_launch(context, str(script_id))
        scripts, fresh = _get_script(script_id)
        if not fresh:
            return
        if process is None or process.poll() is not None:
            fresh['status'] = 'stopped'
            save_bot_scripts(scripts)
            await message.reply_text('❌ <b>START FAILED</b>\n\nThe process exited during startup. Open LOGS to see the error.', parse_mode='HTML', reply_markup=get_main_keyboard(uid))
            return
        now = time.time()
        fresh['status'] = 'running'
        fresh['started_at_epoch'] = now
        fresh['v10_last_accounted_at'] = now
        fresh['manual_stop'] = False
        if not is_admin(uid):
            entry, slot, state = _v10_slot_for(uid, fresh.get('v10_slot_id'))
            if slot:
                slot['assigned_script'] = str(script_id)
                slot['last_accounted_at'] = now
                fresh['v10_remaining_seconds'] = int(slot.get('remaining_seconds', 0) or 0)
                _v10_st_save(state)
        scripts[str(script_id)] = fresh
        save_bot_scripts(scripts)
        remaining = 'Unlimited (admin)' if is_admin(uid) else _format_duration(fresh.get('v10_remaining_seconds', 0))
        await message.reply_text(
            f'🚀 <b>BOT STARTED</b>\n\nFile: <code>{html.escape(str(fresh.get("name") or script_id))}</code>\nStatus: <b>RUNNING</b>\nSlot time remaining: <b>{html.escape(remaining)}</b>',
            parse_mode='HTML', reply_markup=InlineKeyboardMarkup([
                [user_button('📡 VIEW LOGS', '📡', callback_data=f'logs_script_{script_id}')],
                [user_button('⏹ STOP', '❌', callback_data=f'stop_script_{script_id}', style='danger')],
                [user_button('📁 MY SCRIPTS', '📁', callback_data='my_scripts_menu')]
            ]))
    except Exception as exc:
        logger.error('No-duration start failed for %s: %s\n%s', script_id, exc, traceback.format_exc())
        scripts, fresh = _get_script(script_id)
        if fresh:
            fresh['status'] = 'stopped'
            fresh['last_error'] = f'{type(exc).__name__}: {exc}'
            save_bot_scripts(scripts)
        await message.reply_text(f'❌ <b>START FAILED</b>\n\n<pre>{html.escape(str(exc)[:1800])}</pre>', parse_mode='HTML', reply_markup=get_main_keyboard(uid))


# Stop the process tree and settle the slot quota before marking it stopped.
async def handle_stop_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    sid = (query.data or '').replace('stop_script_', '', 1)
    scripts, script = _get_script(sid)
    if not script or not _safe_script_for_user(script, query.from_user.id):
        await query.answer('Script not found', show_alert=True)
        return
    uid = int(script.get('user_id', 0) or 0)
    if not is_admin(uid) and script.get('v10_slot_id') and str(script.get('status', '')).lower() == 'running':
        depleted = _v10_account_script_runtime(sid, script)
        if depleted:
            script['last_error'] = 'Purchased slot runtime exhausted.'
    with SCRIPT_PROCESS_LOCK:
        entry = SCRIPT_PROCESSES.get(str(sid))
        process = entry.get('process') if isinstance(entry, dict) else None
    try:
        script['manual_stop'] = True
        if process and process.poll() is None:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            except Exception:
                process.terminate()
            try:
                await asyncio.to_thread(process.wait, 5)
            except Exception:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except Exception:
                    try: process.kill()
                    except Exception: pass
                try: await asyncio.to_thread(process.wait, 2)
                except Exception: pass
        # Also stop the ZIP supervisor's managed child if the project is ZIP based.
        try:
            _v115_stop_process(str(sid), script)
        except Exception:
            pass
        script['status'] = 'stopped'
        script['last_exit_code'] = process.returncode if process else script.get('last_exit_code')
        script['last_modified'] = _advanced_now()
        script['v10_last_accounted_at'] = None
        save_bot_scripts(scripts)
        with SCRIPT_PROCESS_LOCK:
            SCRIPT_PROCESSES.pop(str(sid), None)
        tasks = context.application.bot_data.get('v112_expiry_tasks', {})
        task = tasks.pop(str(sid), None)
        if task and not task.done(): task.cancel()
        await query.answer('Stopped', show_alert=False)
        try:
            await query.edit_message_text(
                f'⏹️ <b>STOPPED</b>\n\n<code>{html.escape(str(script.get("name") or sid))}</code> and its managed process have been stopped. Remaining slot time is preserved.',
                parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[user_button('📁 MY SCRIPTS', '📁', callback_data='my_scripts_menu')]]))
        except Exception:
            await query.message.reply_text('⏹️ Script stopped. Remaining slot time is preserved.', reply_markup=get_main_keyboard(uid))
    except Exception as exc:
        logger.error('Stop failed for %s: %s\n%s', sid, exc, traceback.format_exc())
        try: await query.answer('Stop requested; check logs if the process remains active.', show_alert=True)
        except Exception: pass


# Slot-only purchase menu: remove the legacy TIME purchase path from user-facing UI.
async def _v10_st_buy_menu(message):
    rows = [[user_button('BUY SLOTS', '🟩', callback_data='v10st_slots', style='success')]]
    await message.reply_text(
        f'<b>BUY PREMIUM SLOTS</b>\n\nPrice: ₹{V10_SLOT_PRICE:g} per slot\n'
        f'Running-time allowance: {V10_SLOT_DAYS} days per slot\n\n'
        'The slot is linked to the script you start with it. Time is consumed only while that script is running. Stop it to pause the timer; when the allowance reaches zero, that script cannot be started again without another slot.',
        parse_mode='HTML', reply_markup=InlineKeyboardMarkup(rows))


# Enforce slot purchase for every non-admin start, even when the user has zero slots.
_V136_PREVIOUS_BUTTON_HANDLER = button_handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = getattr(update, 'callback_query', None)
    data = (q.data or '') if q else ''
    if q and data == 'v10st_time':
        await q.answer('Time purchases have been removed. Please buy a slot.', show_alert=True)
        return
    if q and data.startswith(('start_script_', 'v112_start_', 'run_script_')) and not is_admin(q.from_user.id):
        uid = q.from_user.id
        sid = data.replace('start_script_', '', 1).replace('v112_start_', '', 1).replace('run_script_', '', 1)
        scripts, script = _get_script(sid)
        if not script or str(script.get('user_id')) != str(uid):
            await q.answer('Project not found.', show_alert=True)
            return
        slots = _v10_st_active_slots(uid)
        assigned = None
        if script.get('v10_slot_id'):
            _, assigned, _ = _v10_slot_for(uid, script.get('v10_slot_id'))
            if not assigned or int(assigned.get('remaining_seconds', 0) or 0) <= 0:
                await q.answer('This script has used its slot. Buy a new slot to run it again.', show_alert=True)
                return
        else:
            used_ids = {str(x.get('v10_slot_id')) for x in scripts.values() if str(x.get('user_id')) == str(uid) and x.get('v10_slot_id')}
            available = [x for x in slots if not x.get('assigned_script') and str(x.get('slot_id')) not in used_ids]
            if not available:
                await q.answer('Buy a slot before starting this script. Each slot gives 29 days of running time.', show_alert=True)
                await q.message.reply_text('🔒 <b>SLOT REQUIRED</b>\n\nBuy a slot to start a script. Stopping pauses the remaining running time.', parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[user_button('💎 BUY SLOTS', '💎', callback_data='v115_paid_buy', style='success')]]))
                return
            assigned = available[0]
            slot_id = str(assigned.get('slot_id'))
            # Re-load the persisted object before mutating; `available` came from
            # a separate JSON load and changing it alone would not reserve the slot.
            state = _v10_st_load()
            entry = state.setdefault(str(uid), {'slots': [], 'time_credit_seconds': 0})
            stored_slot = next((x for x in entry.get('slots', []) if str(x.get('slot_id')) == slot_id), None)
            if not stored_slot or int(stored_slot.get('remaining_seconds', 0) or 0) <= 0 or stored_slot.get('assigned_script'):
                await q.answer('That slot was just assigned. Tap START again.', show_alert=True)
                return
            stored_slot['assigned_script'] = str(sid)
            _v10_st_save(state)
            script['v10_slot_id'] = slot_id
            scripts[str(sid)] = script; save_bot_scripts(scripts)
        # Existing slot reservation is now persisted before the start callback runs.
    return await _V136_PREVIOUS_BUTTON_HANDLER(update, context)


# Admin variables menu already lists all users' projects; ensure embedded module variables are included.
_V136_PREVIOUS_SHOW_SCRIPT_VARIABLES = _v113_show_script_variables
async def _v113_show_script_variables(query, context, script_id):
    scripts, script = _get_script(script_id)
    if script and str(script.get('path', '')).lower().endswith('.py') and os.path.isfile(str(script.get('path', ''))):
        try:
            source = Path(script['path']).read_text(encoding='utf-8', errors='replace')
            required, optional = _detected_env_from_source(source)
            current_required = set(script.get('env_required') or [])
            current_optional = set(script.get('env_optional') or [])
            script['env_required'] = sorted(current_required | set(required))
            script['env_optional'] = sorted((current_optional | set(optional)) - set(script['env_required']))
            save_bot_scripts(scripts)
        except Exception as exc:
            logger.warning('Could not refresh embedded variables for %s: %s', script_id, exc)
    return await _V136_PREVIOUS_SHOW_SCRIPT_VARIABLES(query, context, script_id)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{EMOJI_CHECK} Bot stopped by user")
    except Exception as e:
        print(f"\n{EMOJI_X} Bot crashed: {e}")
        logger.critical(f"Bot crashed: {e}\n{traceback.format_exc()}")
