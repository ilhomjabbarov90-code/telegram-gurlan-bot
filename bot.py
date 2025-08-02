 from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import logging

# 🔐 Token, Admin ID va Kanal
BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

# 🔧 Log sozlash
logging.basicConfig(level=logging.INFO)

# 🧠 Har bir foydalanuvchi uchun holat
user_state = {}

# ▶️ /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_state[chat_id] = {"step": "product_name"}
    await update.message.reply_text("🛒 Mahsulot nomini kiriting:")

# 🧾 Oddiy matnli xabarlar
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user

    if chat_id not in user_state:
        await update.message.reply_text("Iltimos, /start buyrug‘ini bosing.")
        return

    step = user_state[chat_id]["step"]

    if step == "product_name":
        user_state[chat_id]["product"] = text
        user_state[chat_id]["step"] = "phone"
        await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    elif step == "phone":
        user_state[chat_id]["phone"] = text
        user_state[chat_id]["step"] = "address"
        await update.message.reply_text("📍 Manzilingizni kiriting:")
    elif step == "address":
        product = user_state[chat_id].get("product", "Noma'lum")
        phone = user_state[chat_id]["phone"]
        address = text

        if user.username:
            user_link = f"@{user.username}"
        else:
            full_name = (user.first_name or "") + " " + (user.last_name or "")
            user_link = f"[{full_name.strip()}](tg://user?id={user.id})"

        msg = (
            "🆕 Yangi buyurtma:\n"
            f"👤 {user_link}\n"
            f"📦 Mahsulot: {product}\n"
            f"📞 Tel: {phone}\n"
            f"📍 Manzil: {address}"
        )

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi.")

        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Adminga yuborishda xatolik: {e}")

        user_state.pop(chat_id)

# 🖼 Rasm yuborish (Admin tomonidan)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id != ADMIN_ID:
        await update.message.reply_text("⛔ Bu amal faqat admin uchun.")
        return

    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish", callback_data="order_now")]
    ])

    # Kanalga yuborish
    try:
        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ Kanalga muvaffaqiyatli yuborildi.")
    except Exception as e:
        logging.error(f"Kanalga yuborishda xatolik: {e}")
        await update.message.reply_text("❌ Kanalga yuborishda xatolik.")

# 📲 Tugmani bosganda (Buyurtma)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    user_state[user_id] = {"step": "product_name"}
    await context.bot.send_message(chat_id=user_id, text="🛒 Mahsulot nomini kiriting:")

# ✅ Adminga test xabar
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text="🔔 Test xabari.")
        await update.message.reply_text("✅ Admin xabari yuborildi.")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")

# 🚀 Botni ishga tushurish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", test_admin))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    app.run_polling()
