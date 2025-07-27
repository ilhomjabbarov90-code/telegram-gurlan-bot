import logging
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters,
    ConversationHandler, ContextTypes
)

TOKEN = '8032558089:AAE00ASKBWHhcmsE1zYW2_u4ZLaLo6F7CIA'
CHANNEL = '@gurlan_bozori1'
ADMIN_ID = 1722876301

logging.basicConfig(level=logging.INFO)

ASK_ADDRESS, ASK_PHONE = range(2)
user_data_dict = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Bu bot orqali siz mahsulotlar haqida ma’lumot olishingiz yoki buyurtma berishingiz mumkin.")

# /post (faqat admin uchun)
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Kechirasiz, bu buyruq faqat admin uchun.")
        return

    if not context.args:
        await update.message.reply_text("Foydalanish: /post Mahsulot | Narx | RasmURL")
        return

    try:
        text = " ".join(context.args)
        name, price, image_url = [x.strip() for x in text.split("|")]
    except:
        await update.message.reply_text("Xatolik: format noto‘g‘ri. /post Mahsulot | Narx | RasmURL")
        return

    caption = f"📌 Mahsulot: {name}\n💰 Narx: {price}\n\n👇 Buyurtma berish uchun tugmani bosing:"
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buyurtma berish", callback_data="buyurtma")]
    ])

    await context.bot.send_photo(
        chat_id=CHANNEL,
        photo=image_url,
        caption=caption,
        reply_markup=button
    )

    await update.message.reply_text("✅ Mahsulot kanalga yuborildi.")

# Tugma bosilganda
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data_dict[user_id] = {}
    await context.bot.send_message(chat_id=user_id, text="🚚 Buyurtma berish uchun manzilingizni kiriting:")
    return ASK_ADDRESS

# Manzil qabul qilish
async def ask_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_dict[user_id]['address'] = update.message.text
    await update.message.reply_text("📞 Endi telefon raqamingizni yuboring:")
    return ASK_PHONE

# Telefon qabul qilish
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_dict[user_id]['phone'] = update.message.text

    address = user_data_dict[user_id]['address']
    phone = user_data_dict[user_id]['phone']
    full_name = update.effective_user.full_name
    username = update.effective_user.username or "yo‘q"

    msg = f"📥 Yangi buyurtma:\n👤 Ism: {full_name}\n🔗 Username: @{username}\n📍 Manzil: {address}\n📞 Tel: {phone}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

    await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Buyurtma bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_click, pattern="^buyurtma$")],
        states={
            ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_address)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == '__main__':
    main()
