from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging

# 🔧 Sozlamalar
BOT_TOKEN = '7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE'
CHANNEL_ID = '@kanalingiz_nomi'  # <-- EHTIYOT BO‘LING: @ bilan yoziladi
ADMIN_ID = 123456789  # <-- O‘zingizning Telegram ID’ingizni yozing

logging.basicConfig(level=logging.INFO)

# ⏳ Foydalanuvchi holati
user_state = {}

# ✅ /start buyrug‘i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Mahsulotlar uchun /post buyrug‘idan foydalaning (faqat admin).")

# ✅ Admin mahsulotni post qiladi: /post rasm_url narx nom
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        url = context.args[0]
        narx = context.args[1]
        nom = " ".join(context.args[2:])
        text = f"<b>{nom}</b>\nNarxi: {narx} so‘m"

        button = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Buyurtma berish", callback_data="buyurtma")]
        ])

        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=url,
            caption=text,
            parse_mode="HTML",
            reply_markup=button
        )

        await update.message.reply_text("Mahsulot kanalga yuborildi.")
    except:
        await update.message.reply_text("❗ Foydalanish: /post rasm_url narx nom")

# ✅ Tugma bosilganda ishlaydi
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_state[user_id] = {"step": "ask_phone"}
    await query.message.reply_text("📞 Telefon raqamingizni yuboring:")

# ✅ Xabarlarni qabul qilish
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id in user_state:
        step = user_state[user_id].get("step")

        if step == "ask_phone":
            user_state[user_id]["phone"] = text
            user_state[user_id]["step"] = "ask_address"
            await update.message.reply_text("🏠 Manzilingizni yuboring:")
        elif step == "ask_address":
            phone = user_state[user_id].get("phone")
            address = text
            user_state.pop(user_id)

            msg = f"📥 Yangi buyurtma:\n👤 @{update.effective_user.username or 'Nomaʼlum'}\n📞 {phone}\n🏠 {address}"
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
            await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog'lanamiz.")
    else:
        await update.message.reply_text("Buyurtma uchun avval mahsulotdagi 'Buyurtma' tugmasini bosing.")

# 🚀 Botni ishga tushirish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("post", post))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

app.run_polling()
