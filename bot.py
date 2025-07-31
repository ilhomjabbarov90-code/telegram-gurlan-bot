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
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    user_state[update.message.chat_id] = {"step": "phone"}

# Matnli xabarlar bilan ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user

    if chat_id not in user_state:
        await update.message.reply_text("Iltimos, avval /start buyrug‘ini yuboring.")
        return

    step = user_state[chat_id].get("step")

    if step == "phone":
        user_state[chat_id]["phone"] = text
        user_state[chat_id]["step"] = "address"
        await update.message.reply_text("📍 Endi manzilingizni kiriting:")

    elif step == "address":
        phone = user_state[chat_id]["phone"]
        address = text

        if user.username:
            username = f"@{user.username}"
        else:
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username = full_name if full_name else f"ID: {user.id}"

        msg = (
            "🆕 Yangi buyurtma:\n"
            f"👤 {username}\n"
            f"📞 {phone}\n"
            f"📍 {address}"
        )

        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
            await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.")
        except Exception as e:
            logging.error(f"Admin xabar yuborishda xatolik: {e}")
            await update.message.reply_text("❌ Adminga yuborishda xatolik.")

        user_state.pop(chat_id, None)

    else:
        await update.message.reply_text("Iltimos, /start buyrug‘ini bosing.")

# Foto yuborilganda (Admin kanalga mahsulot joylaydi)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish ➡️", url="https://t.me/Buyccc_bot?start=order")]
    ])

    try:
        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ Mahsulot kanalga yuborildi.")
    except Exception as e:
        logging.error(f"Rasm kanalga yuborilmadi: {e}")
        await update.message.reply_text("❌ Kanalga yuborishda xatolik.")

# Buyurtma tugmasi bosilganda (fallback holatda, callback bo‘lsa)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_state[user_id] = {"step": "phone"}

    await context.bot.send_message(chat_id=user_id, text="📞 Telefon raqamingizni kiriting:")

# Test komanda - admin tekshiruvi uchun
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text="🔔 Test xabari.")
        await update.message.reply_text("✅ Adminga test xabari yuborildi.")
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
