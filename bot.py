import logging
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters, Updater, CallbackContext, ConversationHandler

# Config
TOKEN = "8032558089:AAE00ASKBWHhcmsE1zYW2_u4ZLaLo6F7CIA"
CHANNEL_ID = "@gurlan_bozori1"
ADMIN_ID = 1722876301

# States
ASK_PHONE, ASK_ADDRESS = range(2)

# Logging
logging.basicConfig(level=logging.INFO)

# /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Salom! Men sizga buyurtma berishda yordam beraman.")

# /post <rasm_url> <narx> <mahsulot_nomi>
def post(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("Sizda ruxsat yo'q.")
        return

    if len(context.args) < 3:
        update.message.reply_text("Foydalanish: /post rasm_url narx mahsulot_nomi")
        return

    image_url = context.args[0]
    price = context.args[1]
    name = ' '.join(context.args[2:])

    caption = f"📦 Mahsulot: {name}\n💰 Narx: {price} so'm\n\n👇 Buyurtma uchun tugmani bosing:"
    keyboard = [[InlineKeyboardButton("📥 Buyurtma berish", callback_data=f"order|{name}|{price}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=caption, reply_markup=reply_markup)
    update.message.reply_text("Post kanalga yuborildi ✅")

# Tugma bosilganda
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data.split('|')
    if data[0] == "order":
        context.user_data['product'] = data[1]
        context.user_data['price'] = data[2]

        query.message.reply_text("📍 Manzilingizni kiriting:")
        return ASK_ADDRESS

# Manzil
def ask_address(update: Update, context: CallbackContext):
    context.user_data['address'] = update.message.text
    update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    return ASK_PHONE

# Telefon
def ask_phone(update: Update, context: CallbackContext):
    context.user_data['phone'] = update.message.text
    product = context.user_data['product']
    price = context.user_data['price']
    address = context.user_data['address']
    phone = context.user_data['phone']

    msg = f"📥 Yangi buyurtma!\n\n🛒 Mahsulot: {product}\n💰 Narx: {price} so'm\n📍 Manzil: {address}\n📞 Tel: {phone}\n👤 Mijoz: @{update.effective_user.username or update.effective_user.first_name}"
    context.bot.send_message(chat_id=ADMIN_ID, text=msg)

    update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada bog‘lanamiz.")
    return ConversationHandler.END

# Bekor qilish
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Buyurtma bekor qilindi.")
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            ASK_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, ask_address)],
            ASK_PHONE: [MessageHandler(Filters.text & ~Filters.command, ask_phone)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("post", post))
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
