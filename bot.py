from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

logging.basicConfig(level=logging.INFO)
user_state = {}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Assalomu alaykum! Mahsulot rasmini yuboring.")

# Foydalanuvchi tugma bosgandan keyin /start ni bosmay turib yozgan bo‘lsa
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user

    if chat_id not in user_state or "step" not in user_state[chat_id]:
        await update.message.reply_text("Iltimos, buyurtma tugmasini bosing yoki /start buyrug'ini yuboring.")
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
        address = text
        product = user_state[chat_id].get("product", "Nomaʼlum")
        phone = user_state[chat_id]["phone"]
        photo_id = user_state[chat_id].get("photo_id")
        user_link = f"@{user.username}" if user.username else f"[{user.full_name}](tg://user?id={user.id})"

        caption = (
            f"🆕 *Yangi buyurtma:*\n"
            f"👤 {user_link}\n"
            f"📦 Mahsulot: {product}\n"
            f"📞 Telefon: {phone}\n"
            f"📍 Manzil: {address}"
        )

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada bogʻlanamiz.")

        try:
            if photo_id:
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=caption, parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text=caption, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Admin xabari yuborishda xatolik: {e}")

        user_state.pop(chat_id)

# Admin rasm yuboradi
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish ➡️", callback_data="order_now")]
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
    user = query.from_user
    user_id = user.id
    message = query.message

    await query.answer()

    # Rasm ID sini saqlaymiz
    if message.photo:
        photo_id = message.photo[-1].file_id
        user_state[user_id] = {
            "step": "product",
            "photo_id": photo_id
        }
    else:
        user_state[user_id] = {
            "step": "product"
        }

    await context.bot.send_message(chat_id=user_id, text="📦 Buyurtma uchun mahsulot nomini kiriting:")

# Test xabar
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=ADMIN_ID, text="🔔 Test xabari.")
    await update.message.reply_text("✅ Adminga test xabar yuborildi.")

# Botni ishga tushuramiz
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", test_admin))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    app.run_polling()
