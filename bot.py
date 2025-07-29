from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler
)
import logging
import os

BOT_TOKEN = "8032558089:AAE00ASKBWHhcmsE1zYW2_u4ZLaLo6F7CIA"
CHANNEL_ID = "@gurlan_bozori1"
ADMIN_ID = 1722876301

logging.basicConfig(level=logging.INFO)

user_state = {}

# Admin rasm yuborsa ishlaydi
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    photo = update.message.photo[-1]
    caption = update.message.caption or "Mahsulot"

    file = await photo.get_file()
    await file.download_to_drive("temp.jpg")

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buyurtma berish", callback_data="order")]
    ])

    with open("temp.jpg", "rb") as img:
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=img,
            caption=caption,
            reply_markup=button
        )

    os.remove("temp.jpg")

# Buyurtma bosilganda
async def handle_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_state[query.from_user.id] = {}
    await query.message.reply_text("📍 Manzilingizni yuboring:")

# Manzil va tel raqam qabul qilish
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_state:
        if 'address' not in user_state[user_id]:
            user_state[user_id]['address'] = update.message.text
            await update.message.reply_text("📞 Telefon raqamingizni yuboring:")
        else:
            user_state[user_id]['phone'] = update.message.text
            msg = (
                f"🆕 Yangi buyurtma:\n\n"
                f"👤 Ismi: {update.message.from_user.full_name}\n"
                f"📍 Manzil: {user_state[user_id]['address']}\n"
                f"📞 Tel: {user_state[user_id]['phone']}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
            await update.message.reply_text("✅ Buyurtmangiz qabul qilindi!")
            del user_state[user_id]

# Botni ishga tushurish
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), handle_photo))
app.add_handler(CallbackQueryHandler(handle_order_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

import asyncio
if __name__ == "__main__":
    asyncio.run(app.run_polling())
