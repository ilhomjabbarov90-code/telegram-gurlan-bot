import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# 🔧 Bot sozlamalari
BOT_TOKEN = "8032558089:AAE00ASKBWHhcmsE1zYW2_u4ZLaLo6F7CIA"
CHANNEL_USERNAME = "@gurlan_bozori1"
ADMIN_ID = 1722876301
BOT_USERNAME = "gurlan_buyurtma_bot"  # faqat username, @ belgisisiz

# 🔧 Loglar
logging.basicConfig(level=logging.INFO)
user_state = {}

# 🚀 /start buyrug'i va buyurtma boshlanishi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user_id = update.effective_user.id

    if args and args[0] == "buyurtma":
        user_state[user_id] = {"step": "phone"}
        await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    else:
        await update.message.reply_text("👋 Salom! Mahsulot tanlang va 📦 Buyurtma tugmasini bosing.")

# 🖼 Admin rasm yuborganda
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish", url=f"https://t.me/{BOT_USERNAME}?start=buyurtma")]
    ])

    await context.bot.send_photo(
        chat_id=CHANNEL_USERNAME,
        photo=photo,
        caption=caption,
        reply_markup=keyboard
    )
    await update.message.reply_text("✅ Kanalga yuborildi.")

# 📥 Telefon raqami va manzil qabul qilish
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_state:
        await update.message.reply_text("📦 Buyurtma uchun kanalimizdagi tugmani bosing.")
        return

    step = user_state[user_id]["step"]

    if step == "phone":
        user_state[user_id]["phone"] = text
        user_state[user_id]["step"] = "address"
        await update.message.reply_text("🏠 Manzilingizni kiriting:")
    elif step == "address":
        phone = user_state[user_id].get("phone")
        address = text

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📥 Yangi buyurtma:\n👤 @{update.effective_user.username or 'Nomaʼlum'}\n📞 Tel: {phone}\n🏠 Manzil: {address}"
        )

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi! Tez orada bog‘lanamiz.")
        del user_state[user_id]

# ⛔ Noto'g'ri buyruqlar
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Nomaʼlum buyruq. Iltimos, 📦 Buyurtma tugmasidan foydalaning.")

# 🔁 Botni ishga tushirish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.COMMAND, unknown))

if __name__ == "__main__":
    app.run_polling()
