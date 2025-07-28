from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import logging

BOT_TOKEN = '8032558089:AAE00ASKBWHhcmsE1zYW2_u4ZLaLo6F7CIA'
ADMIN_ID = 1722876301

logging.basicConfig(level=logging.INFO)

users_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Men sizga buyurtma berishda yordam beraman.")

async def post_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID:
        return

    if not context.args or len(context.args) < 3:
        await update.message.reply_text("Foydalanish: /post rasm_url narx mahsulot_nomi")
        return

    photo_url = context.args[0]
    narx = context.args[1]
    nom = " ".join(context.args[2:])

    caption = f"📌 Mahsulot: {nom}\n💰 Narx: {narx} so‘m\n👇 Buyurtma berish uchun tugmani bosing:"
    button = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton("📦 Buyurtma berish", callback_data="order")
    )

    await context.bot.send_photo(
        chat_id='@gurlan_bozori1',
        photo=photo_url,
        caption=caption,
        reply_markup=button
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    users_state[user_id] = {"step": "ask_address"}

    await query.message.reply_text("📍 Manzilingizni kiriting:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in users_state:
        return

    step = users_state[user_id]["step"]

    if step == "ask_address":
        users_state[user_id]["address"] = text
        users_state[user_id]["step"] = "ask_phone"
        await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    elif step == "ask_phone":
        users_state[user_id]["phone"] = text

        address = users_state[user_id]["address"]
        phone = users_state[user_id]["phone"]

        msg = f"🆕 Yangi buyurtma:\n\n📍 Manzil: {address}\n📞 Telefon: {phone}\n👤 Foydalanuvchi: @{update.effective_user.username or 'Nomaʼlum'}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada bog‘lanamiz!")

        del users_state[user_id]

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("post", post_product))
app.add_handler(CallbackQueryHandler(button_click))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    app.run_polling()
