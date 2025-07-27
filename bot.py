import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = '8032558089:AAGKPRzCZj5ZwiGCypW5cyHYuPS_UaZso5U'
CHANNEL_USERNAME = '@gurlan_bozori1'
ORDER_BOT_USERNAME = '@Zakazbozor_bot'
ADMIN_ID = 1722876301

logging.basicConfig(level=logging.INFO)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mahsulot yuborish uchun: /post")

# /post komandasi: mahsulot rasm, narx va buyurtma tugmasi bilan kanalga yuboradi
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Sizda ruxsat yo‘q.")
        return

    if not context.args:
        await update.message.reply_text("Foydalanish: /post Mahsulot_nomi | Narx | Rasm_URL")
        return

    try:
        text = " ".join(context.args)
        name, price, photo_url = [x.strip() for x in text.split("|")]
    except:
        await update.message.reply_text("Xatolik: Foydalanish /post Mahsulot | Narx | Rasm_URL")
        return

    caption = f"📌 Mahsulot: {name}\n💰 Narx: {price}\n\n👇 Buyurtma uchun tugmani bosing:"
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buyurtma berish", url=f"https://t.me/{ORDER_BOT_USERNAME.lstrip('@')}")]
    ])

    await context.bot.send_photo(
        chat_id=CHANNEL_USERNAME,
        photo=photo_url,
        caption=caption,
        reply_markup=button
    )

    await update.message.reply_text("Mahsulot kanalga yuborildi.")

# Adminga tugma bosilgani haqida xabar berish (agar kerak bo‘lsa)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
