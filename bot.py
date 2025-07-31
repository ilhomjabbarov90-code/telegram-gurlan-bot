from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import logging
import re

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

logging.basicConfig(level=logging.INFO)
user_state = {}

def escape_markdown(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!\\])', r'\\\1', text)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    user_state[update.message.chat_id] = {"step": "phone"}

# Foto yuborilganda — admin mahsulot joylaydi
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish ➡️", callback_data=f"order:{photo}")]
    ])

    try:
        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ Kanalga yuborildi.")
    except Exception as e:
        logging.error(f"Rasm yuborilmadi: {e}")
        await update.message.reply_text("❌ Kanalga yuborishda xatolik.")

# Tugma bosilganda — foydalanuvchiga telefon so‘raladi
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("order:"):
        photo_id = data.split("order:")[1]
        user_state[user_id] = {
            "step": "phone",
            "photo": photo_id
        }
        await context.bot.send_message(chat_id=user_id, text="📞 Telefon raqamingizni kiriting:")

# Matnli xabarlar bilan ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user

    if chat_id not in user_state:
        await update.message.reply_text("Iltimos /start buyrug'ini bosing.")
        return

    step = user_state[chat_id].get("step")

    if step == "phone":
        user_state[chat_id]["phone"] = text
        user_state[chat_id]["step"] = "address"
        await update.message.reply_text("📍 Endi manzilingizni kiriting:")

    elif step == "address":
        phone = escape_markdown(user_state[chat_id]["phone"])
        address = escape_markdown(text)
        name = escape_markdown(user.first_name or "Foydalanuvchi")
        user_link = f"[{name}](tg://user?id={user.id})"
        photo = user_state[chat_id].get("photo")

        msg = f"🆕 Yangi buyurtma:\n👤 {user_link}\n📞 {phone}\n📍 {address}"

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.")

        try:
            if photo:
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=photo,
                    caption=msg,
                    parse_mode="Markdown"
                )
            else:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=msg,
                    parse_mode="Markdown"
                )
        except Exception as e:
            logging.error(f"Admin xabar yuborishda xatolik: {e}")

        user_state.pop(chat_id)

    else:
        await update.message.reply_text("Iltimos /start buyrug'ini bosing.")

# Test komanda
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text="🔔 Test xabari.")
        await update.message.reply_text("✅ Adminga xabar yuborildi.")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")

# Ishga tushurish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", test_admin))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

if __name__ == "__main__":
    app.run_polling()
