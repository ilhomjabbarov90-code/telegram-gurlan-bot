from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"  # Kanal usernameni to‘g‘ri yozing

logging.basicConfig(level=logging.INFO)

user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    user_state[update.message.chat_id] = {"step": "phone"}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user
    username = f"@{user.username}" if user.username else f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not username.strip():
        username = f"ID: {user.id}"

    if chat_id not in user_state:
        await update.message.reply_text("Iltimos /start buyrug'ini bosing.")
        return

    step = user_state[chat_id].get("step")
    if step == "phone":
        user_state[chat_id]["phone"] = text
        user_state[chat_id]["step
