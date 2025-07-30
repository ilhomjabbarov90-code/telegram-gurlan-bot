from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import logging

# === 🔑 BOT TOKEN, ADMIN ID, CHANNEL USERNAME ===
BOT_TOKEN = "8032558089:AAE00ASKBWHhcmsE1zYW2_u4ZLaLo6F7CIA"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

# === 🪵 LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === 🗃️ FOYDALANUVCHI HOLATI ===
user_orders = {}

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📦 Buyurtma botiga xush kelibsiz! Mahsulot uchun rasm yuboring yoki kanaldan tanlang.")

# === 📤 ADMIN RASM YUBORSA ===
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        return

    caption = update.message.caption or "🆕 Yangi mahsulot!"
    photo = update.message.photo[-1].file_id
    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📦 Buyurtma berish", callback_data=f"order:{photo}|{caption}")]]
    )

    await context.bot.send_photo(
        chat_id=CHANNEL_USERNAME,
        photo=photo,
        caption=f"🛍 {caption}\n\n📲 Buyurtma berish uchun tugmani bosing:",
        reply_markup=button
    )

# === 📥 BUYURTMA BOSILGANDA ===
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("order:")[1]
    photo_id, caption = data.split("|", 1)

    user_id = query.from_user.id
    user_orders[user_id] = {
        "photo": photo_id,
        "caption": caption,
        "username": query.from_user.username or "Nomaʼlum",
    }

    await query.message.reply_text("📍 Manzilingizni kiriting:")
    return

# === 📩 FOYDALANUVCHI XABARI ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_orders:
        await update.message.reply_text("Iltimos, buyurtma berish uchun kanaldagi mahsulot tugmasini bosing.")
        return

    order = user_orders[user_id]

    if "address" not in order:
        user_orders[user_id]["address"] = update.message.text
        await update.message.reply_text("📞 Telefon raqamingizni yuboring:")
    elif "phone" not in order:
        user_orders[user_id]["phone"] = update.message.text

        username = order['username']
        address = order['address']
        phone = order['phone']
        caption = order['caption']
        photo_id = order['photo']

        # 🛎️ ADMINGA XABAR
        text = (
            "🆕 *Yangi buyurtma!*\n\n"
            f"👤 @{username}\n"
            f"📍 Manzil: {address}\n"
            f"📞 Tel: {phone}\n"
            f"📦 Mahsulot: {caption}"
        )

        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=text,
            parse_mode="Markdown"
        )

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi! Tez orada siz bilan bog‘lanamiz.")
        user_orders.pop(user_id)

# === 📦 BOSHLASH ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
