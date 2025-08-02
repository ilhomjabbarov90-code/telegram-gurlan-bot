from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

logging.basicConfig(level=logging.INFO)

user_state = {}
user_photos = {}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_state[chat_id] = {"step": "product"}
    await update.message.reply_text("🛍 Mahsulot nomini kiriting:")

# Matnli xabarlar
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user

    if chat_id not in user_state:
        await update.message.reply_text("Iltimos, /start buyrug'ini bosing.")
        return

    step = user_state[chat_id]["step"]

    if step == "product":
        user_state[chat_id]["product"] = text
        user_state[chat_id]["step"] = "phone"
        await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    elif step == "phone":
        user_state[chat_id]["phone"] = text
        user_state[chat_id]["step"] = "address"
        await update.message.reply_text("📍 Manzilingizni kiriting:")
    elif step == "address":
        product = user_state[chat_id].get("product", "Noma'lum")
        phone = user_state[chat_id].get("phone", "Noma'lum")
        address = text

        if user.username:
            user_link = f"@{user.username}"
        else:
            name = (user.first_name or "") + " " + (user.last_name or "")
            user_link = f"[{name.strip()}](tg://user?id={user.id})"

        msg = (
            "🆕 Yangi buyurtma:\n"
            f"👤 {user_link}\n"
            f"📦 Mahsulot: {product}\n"
            f"📞 Tel: {phone}\n"
            f"📍 Manzil: {address}"
        )

        # Rasm yuborish (agar mavjud bo‘lsa)
        photo = user_photos.get(chat_id)
        try:
            if photo:
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=photo,
                    caption=msg,
                    parse_mode="Markdown"
                )
            else:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=msg,
                    parse_mode="Markdown"
                )
        except Exception as e:
            logging.error(f"Adminga yuborishda xatolik: {e}")

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi.")
        user_state.pop(chat_id)
        user_photos.pop(chat_id, None)
    else:
        await update.message.reply_text("Iltimos, /start buyrug'ini bosing.")

# Rasm yuborish
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Buyurtma berish ➡️", url="https://t.me/Buyccc_bot")]
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
        logging.error(f"Kanalga yuborishda xatolik: {e}")
        await update.message.reply_text("❌ Kanalga yuborishda xatolik.")

# Tugma bosilganda
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Userga mahsulot nomini so‘rash
    user_state[user_id] = {"step": "product"}

    # Tugma qayerdan bosilganini tekshirib, rasmni saqlash
    if query.message.photo:
        user_photos[user_id] = query.message.photo[-1].file_id

    await context.bot.send_message(chat_id=user_id, text="🛍 Mahsulot nomini kiriting:")

# Admin test komandasi
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=ADMIN_ID, text="🔔 Test xabari.")
    await update.message.reply_text("✅ Adminga xabar yuborildi.")

# Botni ishga tushurish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", test_admin))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    app.run_polling()
