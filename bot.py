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

# 📸 Admin rasm yuborganda
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id != ADMIN_ID:
        return

    caption = update.message.caption or "Mahsulot"

    # Rasmni olish
    photo = update.message.photo[-1]
    file = await photo.get_file()
    photo_path = "temp.jpg"
    await file.download_to_drive(photo_path)

    # Tugma
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buyurtma berish", callback_data="order")]
    ])

    # Kanalga yuborish
    with open(photo_path, "rb") as img:
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=img,
            caption=caption,
            reply_markup=buttons
        )

    os.remove(photo_path)

# 🛍 Buyurtma bosilganda
async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_state[query.from_user.id] = {}
    await query.message.reply_text("📍 Manzilingizni yozing:")

# ✍️ Foydalanuvchi matn yuborganda
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    msg = update.message.text

    if user_id in user_state:
        if 'address' not in user_state[user_id]:
            user_state[user_id]['address'] = msg
            await update.message.reply_text("📞 Endi telefon raqamingizni yuboring:")
        else:
            user_state[user_id]['phone'] = msg

            # Adminga yuborish
            full_name = update.message.from_user.full_name
            address = user_state[user_id]['address']
            phone = user_state[user_id]['phone']

            order_msg = (
                f"🆕 Buyurtma:\n"
                f"👤 Ism: {full_name}\n"
                f"📍 Manzil: {address}\n"
                f"📞 Telefon: {phone}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=order_msg)
            await update.message.reply_text("✅ Buyurtmangiz qabul qilindi!")

            del user_state[user_id]

# 🔄 Botni ishga tushurish
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), handle_photo))
app.add_handler(CallbackQueryHandler(handle_order))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

import asyncio
if __name__ == "__main__":
    asyncio.run(app.run_polling())
