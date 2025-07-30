from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging

# 🔧 Sozlamalar
BOT_TOKEN = '7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE'
ADMIN_ID = 1722876301  # Sizning admin ID'ingiz

logging.basicConfig(level=logging.INFO)

user_state = {}

# /start buyrug‘i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish", callback_data="buyurtma")]
    ])
    await update.message.reply_text(
        "👋 Assalomu alaykum!\nBuyurtma berish uchun pastdagi tugmani bosing:",
        reply_markup=keyboard
    )

# Tugma bosilganda
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_state[user_id] = {"step": "ask_phone"}

    await query.message.reply_text(
        "📞 Hurmatli mijoz, iltimos telefon raqamingizni yuboring:"
    )

# Foydalanuvchidan xabar qabul qilish
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id in user_state:
        step = user_state[user_id].get("step")

        if step == "ask_phone":
            user_state[user_id]["phone"] = text
            user_state[user_id]["step"] = "ask_address"
            await update.message.reply_text("📍 Rahmat. Endi manzilingizni yozing:")
        
        elif step == "ask_address":
            phone = user_state[user_id].get("phone")
            address = text
            user_state.pop(user_id)

            # Mijozga tasdiq
            await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz. Rahmat!")

            # Adminga yuboriladi
            msg = (
                f"🆕 Yangi buyurtma:\n"
                f"👤 @{update.effective_user.username or 'Nomaʼlum'}\n"
                f"📞 Telefon: {phone}\n"
                f"📍 Manzil: {address}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    else:
        await update.message.reply_text(
            "❗ Iltimos, buyurtma berish uchun /start buyrug‘ini yuboring va tugmani bosing."
        )

# Botni ishga tushirish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.run_polling()
