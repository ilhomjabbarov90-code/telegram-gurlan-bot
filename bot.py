from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import logging

BOT_TOKEN = "8032558089:AAE00ASKBWHhcmsE1zYW2_u4ZLaLo6F7CIA"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

logging.basicConfig(level=logging.INFO)

user_state = {}

async def handle_admin_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    if update.message.photo and update.message.caption:
        photo = update.message.photo[-1].file_id
        caption = update.message.caption

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Buyurtma berish", callback_data="order")]
        ])

        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ Kanalga yuborildi.")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_state[user_id] = {"step": "ask_address"}
    await query.message.reply_text("📍 Manzilingizni yozing:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id in user_state:
        step = user_state[user_id].get("step")

        if step == "ask_address":
            user_state[user_id]["address"] = text
            user_state[user_id]["step"] = "ask_phone"
            await update.message.reply_text("📞 Telefon raqamingizni yozing:")
        elif step == "ask_phone":
            address = user_state[user_id]["address"]
            phone = text
            name = update.message.from_user.full_name

            msg = f"📥 Yangi buyurtma:\n👤 Ism: {name}\n📍 Manzil: {address}\n📞 Tel: {phone}"
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
            await update.message.reply_text("✅ Buyurtmangiz qabul qilindi.")
            user_state.pop(user_id)
    else:
        await update.message.reply_text("❗ Iltimos, kanal orqali buyurtma bering.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.PHOTO & filters.Caption(), handle_admin_photo))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi...")
    app.run_polling()
