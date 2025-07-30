import logging
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)

# 🔐 Sozlamalar
BOT_TOKEN = "8032558089:AAE00ASKBWHhcmsE1zYW2_u4ZLaLo6F7CIA"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

# 🗂 Holatlar
ASK_ADDRESS, ASK_PHONE = range(2)
user_order_data = {}

# 📋 Loglar
logging.basicConfig(level=logging.INFO)

# 🔘 /start buyrug‘i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Mahsulotlar uchun rasm yuboring.")

# 📸 Rasm qabul qilish
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "📦 Yangi mahsulot"

    fancy_caption = (
        f"🍎 {caption}\n\n"
        "💰 Narxi: arzon va sifatli!\n"
        "🚚 Yetkazib berish: 1 kun ichida\n"
        "📦 Mahsulot soni cheklangan!\n\n"
        "👇 Hoziroq buyurtma bering:"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Buyurtma berish", callback_data="order_now")]
    ])

    await context.bot.send_photo(
        chat_id=CHANNEL_USERNAME,
        photo=photo,
        caption=fancy_caption,
        reply_markup=keyboard
    )

# 🔘 Tugma bosilganda
async def order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    user_order_data[user_id] = {}
    await context.bot.send_message(
        chat_id=user_id,
        text="📍 Manzilingizni kiriting:"
    )
    return ASK_ADDRESS

# 🏠 Manzil olish
async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_order_data[user_id]["address"] = update.message.text

    await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    return ASK_PHONE

# 📞 Telefon olish va adminga yuborish
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    user_order_data[user_id]["phone"] = update.message.text

    address = user_order_data[user_id]["address"]
    phone = user_order_data[user_id]["phone"]
    username = f"@{user.username}" if user.username else "Nomaʼlum"

    await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz. Rahmat!")

    message = (
        "🆕 Yangi buyurtma:\n"
        f"👤 {username}\n"
        f"📞 Telefon: {phone}\n"
        f"📍 Manzil: {address}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=message)

    return ConversationHandler.END

# ❌ Bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Buyurtma bekor qilindi.")
    return ConversationHandler.END

# 🔁 Botni ishga tushirish
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(order_callback, pattern="^order_now$")],
        states={
            ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(conv_handler)

    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
