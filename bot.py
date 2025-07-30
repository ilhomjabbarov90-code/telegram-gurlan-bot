from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CallbackQueryHandler,
    CommandHandler, ConversationHandler, filters, ContextTypes
)

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

ASK_PHONE, ASK_ADDRESS = range(2)
user_orders = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Rasm yuboring (sarlavha bilan), uni kanalda eʼlon qilamiz.")

# Admin rasm yuboradi → kanalga post + tugma
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo = update.message.photo[-1].file_id
        caption = update.message.caption or "📦 Yangi mahsulot"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Buyurtma berish", callback_data="order_now")]
        ])

        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ Kanalga joylandi.")
    else:
        await update.message.reply_text("Iltimos, rasm yuboring.")

# Tugmani bosgan foydalanuvchi → so‘rov boshlanadi
async def order_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_orders[user_id] = {"username": query.from_user.username or "Nomaʼlum"}
    await context.bot.send_message(chat_id=user_id, text="📞 Telefon raqamingizni kiriting:")
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_orders[user_id]["phone"] = update.message.text
    await update.message.reply_text("📍 Manzilingizni kiriting:")
    return ASK_ADDRESS

async def ask_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_orders[user_id]["address"] = update.message.text
    order = user_orders[user_id]
    username = f"@{order['username']}" if order["username"] != "Nomaʼlum" else "Nomaʼlum"
    phone = order["phone"]
    address = order["address"]

    await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz. Rahmat!")

    msg = (
        f"🆕 Yangi buyurtma:\n"
        f"👤 {username}\n"
        f"📞 Telefon: {phone}\n"
        f"📍 Manzil: {address}"
    )

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    except Exception as e:
        print(f"❌ Admin xabarida xatolik: {e}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Buyurtma bekor qilindi.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(order_now, pattern="order_now")],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    print("✅ Bot ishga tushdi")
    app.run_polling()
