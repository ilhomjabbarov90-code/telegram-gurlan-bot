from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging

# Asosiy sozlamalar
BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

logging.basicConfig(level=logging.INFO)

# Holatni saqlovchi dictlar
user_state = {}
product_info = {}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    user_state[update.message.chat_id] = {"step": "phone"}

# Matnli xabarlar bilan ishlovchi handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user

    username = f"@{user.username}" if user.username else f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not username:
        username = f"ID: {user.id}"

    if chat_id not in user_state:
        await update.message.reply_text("Iltimos, /start buyrug‘ini bosing.")
        return

    step = user_state[chat_id].get("step")

    if step == "phone":
        user_state[chat_id]["phone"] = text
        user_state[chat_id]["step"] = "address"
        await update.message.reply_text("📍 Endi manzilingizni kiriting:")
    elif step == "address":
        phone = user_state[chat_id]["phone"]
        address = text
        info = product_info.get(chat_id, {})
        photo = info.get("photo")
        caption = info.get("caption", "🛍 Mahsulot")

        msg = f"🆕 Yangi buyurtma:\n👤 {username}\n📞 {phone}\n📍 {address}\n\n📦 Mahsulot: {caption}"

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.")

        try:
            if photo:
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=msg)
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
        except Exception as e:
            logging.error(f"Admin xabar yuborishda xatolik: {e}")

        user_state.pop(chat_id, None)
        product_info.pop(chat_id, None)
    else:
        await update.message.reply_text("Iltimos, /start buyrug‘ini bosing.")

# Admin tomonidan rasm yuborilganda uni kanalda post qilish
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Faqat admin rasm yuborishi mumkin.")
        return

    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish", callback_data=f"order|{photo}|{caption}")]
    ])

    try:
        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ Kanalga muvaffaqiyatli yuborildi.")
    except Exception as e:
        logging.error(f"Kanalga yuborilmadi: {e}")
        await update.message.reply_text("❌ Kanalga yuborilmadi. Bot kanalga admin ekanligiga ishonch hosil qiling.")

# Tugmani bosganda buyurtma jarayonini boshlash
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    data = query.data
    if data.startswith("order|"):
        try:
            _, photo_id, caption = data.split("|", 2)
            product_info[user_id] = {"photo": photo_id, "caption": caption}
        except Exception as e:
            logging.error(f"Callback parsing xatosi: {e}")

        user_state[user_id] = {"step": "phone"}
        await context.bot.send_message(chat_id=user_id, text="📞 Telefon raqamingizni kiriting:")

# Admin test komandasi
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text="🔔 Test xabari.")
        await update.message.reply_text("✅ Adminga xabar yuborildi.")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")

# Botni ishga tushurish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", test_admin))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

if __name__ == "__main__":
    app.run_polling()
