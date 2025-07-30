from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301

logging.basicConfig(level=logging.INFO)

# Har bir foydalanuvchi uchun vaqtincha ma'lumot saqlovchi lug'at
user_state = {}

# Botni ishga tushirish
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Buyurtma berish uchun telefon raqamingizni kiriting:")
    user_state[update.message.chat_id] = {"step": "phone"}

# Har bir yangi xabarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text

    user = update.message.from_user
    username = f"@{user.username}" if user.username else f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not username.strip():
        username = f"ID: {user.id}"

    if chat_id not in user_state:
        await update.message.reply_text("Iltimos /start buyrug'ini bosing.")
        return

    step = user_state[chat_id].get("step")

    if step == "phone":
        user_state[chat_id]["phone"] = text
        user_state[chat_id]["step"] = "address"
        await update.message.reply_text("Endi manzilingizni kiriting:")
    elif step == "address":
        phone = user_state[chat_id].get("phone")
        address = text

        # Buyurtma xabari
        confirmation = (
            "✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz. Rahmat!"
        )
        await update.message.reply_text(f"Buyurtma:\n{confirmation}")

        # Adminga xabar
        order_message = (
            f"🆕 Yangi buyurtma:\n"
            f"👤 {username}\n"
            f"📞 Telefon: {phone}\n"
            f"📍 Manzil: {address}"
        )

        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=order_message)
        except Exception as e:
            logging.error(f"Adminga xabar yuborilmadi: {e}")

        user_state.pop(chat_id)
    else:
        await update.message.reply_text("Iltimos /start buyrug'ini bosing.")

# Admin test buyrug'i (majburiy emas)
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text="🔔 Adminga test xabar.")
        await update.message.reply_text("✅ Adminga xabar yuborildi.")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")

# Botni ishga tushirish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", test_admin))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    app.run_polling()
