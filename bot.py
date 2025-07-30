from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

logging.basicConfig(level=logging.INFO)

user_state = {}  # Foydalanuvchining bosqichlari
user_photo = {}  # Har bir foydalanuvchi yuborgan rasm ma'lumotlari

# 1. Admin rasm yuboradi → kanalga chiqadi
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    user_photo[user_id] = {"photo": photo, "caption": caption}

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish", callback_data=f"order_{user_id}")]
    ])

    try:
        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ Kanalga yuborildi.")
    except Exception as e:
        logging.error(f"Kanalga yuborilmadi: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi.")

# 2. Tugma bosilganda → foydalanuvchidan tel va manzil so‘rash
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    user_id = user.id

    # Kimning rasmiga buyurtma bosildi
    data = query.data
    poster_id = int(data.split("_")[1])
    product = user_photo.get(poster_id)

    if product:
        user_state[user_id] = {
            "step": "phone",
            "photo": product["photo"],
            "caption": product["caption"]
        }
        await context.bot.send_message(chat_id=user_id, text="📞 Telefon raqamingizni kiriting:")
    else:
        await context.bot.send_message(chat_id=user_id, text="❌ Mahsulot ma'lumoti topilmadi.")

# 3. Foydalanuvchining yozgan javoblarini qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user

    if user_id not in user_state:
        return

    step = user_state[user_id].get("step")

    if step == "phone":
        user_state[user_id]["phone"] = text
        user_state[user_id]["step"] = "address"
        await update.message.reply_text("📍 Manzilingizni kiriting:")
    elif step == "address":
        phone = user_state[user_id].get("phone")
        address = text
        photo = user_state[user_id].get("photo")
        caption = user_state[user_id].get("caption")

        username = f"@{user.username}" if user.username else f"{user.first_name or ''} {user.last_name or ''}".strip()
        if not username:
            username = f"ID: {user.id}"

        msg = f"🆕 Yangi buyurtma:\n👤 {username}\n📞 {phone}\n📍 {address}\n📝 {caption}"

        try:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo,
                caption=msg
            )
        except Exception as e:
            logging.error(f"Adminga yuborilmadi: {e}")

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.")
        user_state.pop(user_id)

# Ishga tushirish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    app.run_polling()
