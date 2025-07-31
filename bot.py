import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)

# --- CONFIG ---
BOT_TOKEN = "8032558089:AAE00ASKBWHhcmsE1zYW2_u4ZLaLo6F7CIA"
CHANNEL_ID = -1002100521747  # <-- Bu yerga kanalning ID'si yoziladi
ADMIN_ID = 1722876301

# --- LOGGER ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- STATES ---
ASK_ADDRESS, ASK_PHONE = range(2)

# --- Global dict ---
user_data_store = {}

# --- Start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Rasm yuboring – kanalga buyurtma bilan joylayman.")

# --- Handle admin image (posting to channel) ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Siz admin emassiz.")
        return

    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish ➡️", callback_data=f"order:{photo}")]
    ])

    try:
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ Kanalga yuborildi.")
    except Exception as e:
        logger.error(f"Kanalga yuborishda xatolik: {e}")
        await update.message.reply_text(f"❌ Kanalga yuborishda xatolik:\n{e}")

# --- Callback: buyurtma bosilganda ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("order:"):
        photo_id = data.split("order:")[1]
        user_id = query.from_user.id
        user_data_store[user_id] = {"photo": photo_id}
        await context.bot.send_message(chat_id=user_id, text="📍 Manzilingizni yuboring:")
        return ASK_ADDRESS

# --- Step 1: Manzilni olish ---
async def ask_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id]["address"] = update.message.text
    await update.message.reply_text("📞 Telefon raqamingizni yuboring:")
    return ASK_PHONE

# --- Step 2: Telefon raqamini olish ---
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone = update.message.text
    data = user_data_store.get(user_id, {})

    if not data:
        await update.message.reply_text("❌ Ma’lumotlar topilmadi.")
        return ConversationHandler.END

    caption = (
        "🆕 Yangi buyurtma!\n\n"
        f"👤 Foydalanuvchi: @{update.effective_user.username or 'Nomalum'}\n"
        f"📍 Manzil: {data['address']}\n"
        f"📞 Telefon: {phone}"
    )

    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=data['photo'],
            caption=caption
        )
        await update.message.reply_text("✅ Buyurtma qabul qilindi.")
    except Exception as e:
        logger.error(f"Buyurtmani yuborishda xatolik: {e}")
        await update.message.reply_text(f"❌ Xatolik:\n{e}")

    user_data_store.pop(user_id, None)
    return ConversationHandler.END

# --- Cancel ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END

# --- Run bot ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern="^order:")],
        states={
            ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_address)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(conv_handler)

    print("🤖 Bot ishga tushdi...")
    app.run_polling()
