from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters
import logging

# Logging
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args and args[0] == "order":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="📝 Mahsulot nomini kiriting:")
        context.user_data['ordering'] = True
    else:
        await update.message.reply_text("Assalomu alaykum! Bot orqali buyurtma berishingiz mumkin.")

# Rasmni qabul qilib kanalga yuborish
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "📦 Mahsulot"

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish ➡️", url="https://t.me/Buyccc_bot?start=order")]
    ])

    if user_id == ADMIN_ID:
        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo,
            caption=caption,
            reply_markup=button
        )
        await update.message.reply_text("✅ Kanalga yuborildi.")
    else:
        await update.message.reply_text("Raxmat! Admin ruxsatidan so‘ng e’lon qilinadi.")

# Buyurtmani qabul qilish
async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('ordering'):
        if 'product_name' not in context.user_data:
            context.user_data['product_name'] = update.message.text
            await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
        elif 'phone' not in context.user_data:
            context.user_data['phone'] = update.message.text
            await update.message.reply_text("📍 Manzilingizni yozing:")
        elif 'address' not in context.user_data:
            context.user_data['address'] = update.message.text
            user = update.effective_user

            order_info = (
                f"🆕 Yangi buyurtma!\n"
                f"👤 Foydalanuvchi: @{user.username or user.first_name}\n"
                f"📦 Mahsulot: {context.user_data['product_name']}\n"
                f"📞 Telefon: {context.user_data['phone']}\n"
                f"📍 Manzil: {context.user_data['address']}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=order_info)
            await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada bog‘lanamiz.")
            context.user_data.clear()

# Botni ishga tushirish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order))

app.run_polling()
