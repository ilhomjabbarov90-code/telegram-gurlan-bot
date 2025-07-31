from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

logging.basicConfig(level=logging.INFO)

user_state = {}  # Har bir foydalanuvchi uchun holat
product_map = {}  # message_id -> photo_file_id, caption

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    user_state[update.message.chat_id] = {"step": "phone"}

# Matnli xabarlar
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user

    if chat_id not in user_state:
        await update.message.reply_text("Iltimos /start buyrug'ini bosing.")
        return

    step = user_state[chat_id]["step"]

    if step == "phone":
        user_state[chat_id]["phone"] = text
        user_state[chat_id]["step"] = "address"
        await update.message.reply_text("📍 Manzilingizni kiriting:")
    elif step == "address":
        phone = user_state[chat_id]["phone"]
        address = text
        product = user_state[chat_id].get("product", {})

        username = f"@{user.username}" if user.username else f"{user.first_name or ''} {user.last_name or ''}".strip()
        if not username:
            username = f"ID: {user.id}"

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.")

        msg = (
            f"🆕 Yangi buyurtma:\n"
            f"👤 {username}\n"
            f"📞 {phone}\n"
            f"📍 {address}"
        )

        try:
            if product:
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=product["photo"],
                    caption=f"{product['caption']}\n\n{msg}"
                )
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
        except Exception as e:
            logging.error(f"Adminga yuborishda xatolik: {e}")

        user_state.pop(chat_id)

# Foto yuborilganda — kanalga yuboramiz
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish", callback_data=f"order|{photo}|{caption}")]
    ])

    try:
        sent = await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )

        message_id = sent.message_id
        product_map[message_id] = {"photo": photo, "caption": caption}

        await update.message.reply_text("✅ Kanalga yuborildi.")
    except Exception as e:
        logging.error(f"Kanalga yuborilmadi: {e}")
        await update.message.reply_text("❌ Kanalga yuborishda xatolik.")

# Tugma bosilganda
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data.startswith("order|"):
        try:
            _, photo, caption = data.split("|", 2)
            user_state[user_id] = {
                "step": "phone",
                "product": {"photo": photo, "caption": caption}
            }
            await context.bot.send_message(chat_id=user_id, text="📞 Telefon raqamingizni kiriting:")
        except Exception as e:
            logging.error(f"Callback parsing xatosi: {e}")
            await context.bot.send_message(chat_id=user_id, text="❌ Buyurtma boshlashda xatolik yuz berdi.")

# Admin test komandasi
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text="✅ Adminga test xabar yuborildi.")
        await update.message.reply_text("✅ Adminga yuborildi.")
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
