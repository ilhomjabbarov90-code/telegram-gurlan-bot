import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler, CallbackContext

TOKEN = '8032558089:AAE00ASKBWHhcmsE1zYW2_u4ZLaLo6F7CIA'
CHANNEL_ID = '@gurlan_bozori1'
ADMIN_ID = 1722876301

# Bosqichlar
ASK_ADDRESS, ASK_PHONE = range(2)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mahsulotni admin botga yuboradi (rasm + matn)
def handle_photo(update: Update, context: CallbackContext):
    if update.message.chat.id != ADMIN_ID:
        return

    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "Narx ko‘rsatilmagan"

    # Inline tugma
    button = InlineKeyboardButton("📦 BUYURTMA BERISH", callback_data='order')
    keyboard = InlineKeyboardMarkup([[button]])

    context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=photo,
        caption=f"📦 Mahsulot:\n{caption}\n\n👇 Buyurtma uchun tugmani bosing:",
        reply_markup=keyboard
    )

# Buyurtma bosilganda
def order_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    context.user_data['order_message'] = query.message.caption
    query.message.reply_text("📍 Manzilingizni kiriting:")
    return ASK_ADDRESS

def ask_address(update: Update, context: CallbackContext):
    context.user_data['address'] = update.message.text
    update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    return ASK_PHONE

def ask_phone(update: Update, context: CallbackContext):
    phone = update.message.text
    address = context.user_data.get('address')
    order_text = context.user_data.get('order_message')

    text = f"🛒 Yangi buyurtma:\n\n{order_text}\n\n📍 Manzil: {address}\n📞 Tel: {phone}\n👤 Foydalanuvchi: @{update.message.from_user.username or update.message.from_user.first_name}"

    # Adminga yuborish
    context.bot.send_message(chat_id=ADMIN_ID, text=text)
    update.message.reply_text("✅ Buyurtmangiz qabul qilindi, tez orada bog‘lanamiz.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Assalomu alaykum! Buyurtma uchun kanaldagi mahsulotlardan birini tanlang.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.photo & Filters.caption, handle_photo))

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(order_callback, pattern='^order$')],
        states={
            ASK_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, ask_address)],
            ASK_PHONE: [MessageHandler(Filters.text & ~Filters.command, ask_phone)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
