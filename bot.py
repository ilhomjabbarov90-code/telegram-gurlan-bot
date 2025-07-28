from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import logging

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301

logging.basicConfig(level=logging.INFO)

user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Men sizga buyurtma berishda yordam beraman.")

async def post_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args or len(context.args) < 3:
        await update.message.reply_text("Foydalanish: /post rasm_url narx nom")
        return

    photo_url = context.args[0]
    price = context.args[1]
    name = " ".join(context.args[2:])

    caption = f"📌 Mahsulot: {name}\n💰 Narx: {price} so‘m\n👇 Buyurtma uchun tugma bosing:"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Buyurtma berish", callback_data="order")]])

    await context.bot.send_photo(chat_id='@gurlan_bozori1', photo=photo_url, caption=caption, reply_markup=kb)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_state[query.from_user.id] = {}
    await query.message.reply_text("📍 Manzilingizni yozing:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_state:
        return

    text = update.message.text
    state = user_state[uid]

    if "address" not in state:
        state["address"] = text
        await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    else:
        phone = text
        address = state["address"]
        username = update.effective_user.username or 'Nomaʼlum'

        await context.bot.send_message(chat_id=ADMIN_ID,
            text=f"🆕 Yangi buyurtma:\n👤 @{username}\n📍 Manzil: {address}\n📞 Tel: {phone}")
        await update.message.reply_text("✅ Buyurtma qabul qilindi.")

        del user_state[uid]

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post_product))
    app.add_handler(CallbackQueryHandler(button_click, pattern="order"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Konsolga xatoni yozadi
    logging.error("Exception while handling an update:", exc_info=context.error)

    # Foydalanuvchiga javob berishga harakat qiladi
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("Botda xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.")

# va bu qatorni ham qo‘shing — bu handlerni ro‘yxatdan o‘tkazadi
application.add_error_handler(error_handler)
