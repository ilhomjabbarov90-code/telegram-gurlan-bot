from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging
import os

BOT_TOKEN = "8032558089:AAE00ASKBWHhcmsE1zYW2_u4ZLaLo6F7CIA"
CHANNEL_ID = "@gurlan_bozori1"
ADMIN_ID = 1722876301

logging.basicConfig(level=logging.INFO)

user_state = {}

# ✅ Admin oddiy rasm yuborganda ishlaydi
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    
    # Rasmni yuklab olish
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f"temp.jpg"
    await photo_file.download_to_drive(photo_path)

    # Tagidagi matnni olish
    caption = update.message.caption or "Narx va nom yo‘q"

    # Tugma
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buyurtma berish", callback_data="order")]
    ])

    # Kanalga yuborish
    with open(photo_path, "rb") as photo:
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=photo,
            caption=caption,
            reply_markup=button
        )

    # Faylni o‘chirish
    os.remove(photo_path)

# 🛍 Buyurtma bosilganda
async def handle_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_state[query.from_user.id] = {}
    await query.message.reply_text("📍 Manzilingizni yuboring:")

# 📝 Manzil va tel raqam olish
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_state:
        if 'address' not in user_state[user_id]:
            user_state[user_id]['address'] = update.message.text
            await update.message.reply_text("📞 Telefon raqamingizni yuboring:")
        else:
            user_state[user_id]['phone'] = update.message.text
            # Adminga yuborish
            msg = (
                f"🆕 Yangi buyurtma:\n\n"
                f"👤 Ismi: {update.message.from_user.full_name}\n"
                f"📍 Manzil: {user_state[user_id]['address']}\n"
                f"📞 Tel: {user_state[user_id]['phone']}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
            await update.message.reply_text("✅ Buyurtmangiz qabul qilindi!")
            del user_state[user_id]

# 🔧 Botni ishga tushurish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), handle_photo))
app.add_handler(CallbackQueryHandler(handle_order_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()
