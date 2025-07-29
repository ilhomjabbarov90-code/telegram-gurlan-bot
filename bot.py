from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import logging
import os

# Token va IDlar
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Render’da Environment variables ichida BOT_TOKEN ni qo'yasiz
ADMIN_ID = 1722876301
CHANNEL_ID = "@gurlan_bozori1"

logging.basicConfig(level=logging.INFO)

# Har bir foydalanuvchining holatini saqlaymiz
user_state = {}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Buyurtma uchun postlardagi tugmani bosing.")

# /post komandasi (faqat admin ishlatadi)
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID):
        return

    if not update.message.photo or not context.args:
        await update.message.reply_text("Rasm va narxni yuboring. Misol: /post 15000 so'm")
        return

    caption = "Narxi: " + " ".join(context.args)
    button = InlineKeyboardMarkup([[InlineKeyboardButton("Buyurtma berish", callback_data="buyurtma")]])
    photo_file = update.message.photo[-1].file_id

    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo_file, caption=caption, reply_markup=button)

# Tugma bosilganda
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_state[query.from_user.id] = {"step": "ask_address"}
    await query.message.reply_text("Buyurtma uchun manzilingizni yuboring:")

# Foydalanuvchi yozgan xabarlarni boshqarish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_state:
        return

    step = user_state[user_id].get("step")

    if step == "ask_address":
        user_state[user_id]["address"] = update.message.text
        user_state[user_id]["step"] = "ask_phone"
        await update.message.reply_text("Telefon raqamingizni yuboring:")
    elif step == "ask_phone":
        user_state[user_id]["phone"] = update.message.text

        msg = f"🛒 Yangi buyurtma:\n\n📍 Manzil: {user_state[user_id]['address']}\n📞 Tel: {user_state[user_id]['phone']}\n👤 User: @{update.effective_user.username or update.effective_user.first_name}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

        await update.message.reply_text("Buyurtmangiz qabul qilindi. Rahmat!")
        del user_state[user_id]

# Botni ishga tushirish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("post", post))
app.add_handler(CallbackQueryHandler(handle_button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
