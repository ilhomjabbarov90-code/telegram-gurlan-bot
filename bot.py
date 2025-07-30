import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🎯 Bu yerga bot tokeningizni yozing
BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"

# 📩 Admin Telegram ID
ADMIN_ID = 1722876301

# 🛠 Log sozlamasi
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 🧠 Foydalanuvchi holatini saqlovchi lug'at
user_state = {}
ASK_PHONE, ASK_ADDRESS = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 Iltimos, telefon raqamingizni yuboring:")
    user_state[update.message.chat_id] = ASK_PHONE


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    state = user_state.get(user_id)

    if state == ASK_PHONE:
        context.user_data["phone"] = update.message.text
        await update.message.reply_text("📍 Endi manzilingizni yuboring:")
        user_state[user_id] = ASK_ADDRESS

    elif state == ASK_ADDRESS:
        context.user_data["address"] = update.message.text
        phone = context.user_data.get("phone", "Nomaʼlum")
        address = context.user_data.get("address", "Nomaʼlum")
        username = update.message.from_user.username or "Nomaʼlum"
        telegram_id = update.message.from_user.id

        # ✅ Foydalanuvchiga javob
        await update.message.reply_text(
            "✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz. Rahmat!"
        )

        # 📨 Admin uchun xabar
        message = (
            f"🆕 Yangi buyurtma:\n"
            f"👤 @{username}\n"
            f"🆔 ID: {telegram_id}\n"
            f"📞 Telefon: {phone}\n"
            f"📍 Manzil: {address}"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=message)
        except Exception as e:
            logging.error(f"Adminga yuborishda xato: {e}")

        # 🔄 Holatni tozalash
        user_state.pop(user_id, None)

    else:
        await update.message.reply_text("Iltimos, /start buyrug‘i bilan boshlang.")


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
