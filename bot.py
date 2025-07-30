from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
)
import logging

BOT_TOKEN = "8032558089:AAE00ASKBWHhcmsE1zYW2_u4ZLaLo6F7CIA"
ADMIN_ID = 1722876301
CHANNEL_ID = "@gurlan_bozori1"
BOT_USERNAME = "gurlan_buyurtma_bot"  # bot_username ni almashtiring

logging.basicConfig(level=logging.INFO)

user_state = {}
user_data = {}

# /start komandasi
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    args = context.args

    if args and args[0] == "buyurtma":
        user_state[user_id] = "phone"
        await context.bot.send_message(chat_id=user_id, text="📞 Telefon raqamingizni kiriting:")
    else:
        await update.message.reply_text("Assalomu alaykum! Buyurtma berish uchun kanalimizdagi mahsulot tugmasini bosing.")

# Admin rasm yuboradi
async def photo_handler(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📦 Buyurtma berish", url=f"https://t.me/{BOT_USERNAME}?start=buyurtma")]]
    )

    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=photo,
        caption=caption,
        reply_markup=keyboard
    )

    # Buyurtma uchun rasmni saqlab qo’yamiz
    user_data["last_photo"] = photo
    user_data["last_caption"] = caption

# Foydalanuvchi xabar yuboradi (telefon / manzil)
async def message_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_state:
        await update.message.reply_text("📦 Buyurtma berish uchun avval mahsulotdagi tugmani bosing.")
        return

    step = user_state[user_id]

    if step == "phone":
        user_data[user_id] = {"phone": text}
        user_state[user_id] = "address"
        await update.message.reply_text("📍 Manzilingizni kiriting:")
    elif step == "address":
        user_data[user_id]["address"] = text
        user_state.pop(user_id)

        phone = user_data[user_id]["phone"]
        address = user_data[user_id]["address"]
        photo = user_data.get("last_photo")
        caption = user_data.get("last_caption", "")

        msg = f"✅ Yangi buyurtma:\n📞 Tel: {phone}\n📍 Manzil: {address}\n📦 {caption}"

        if photo:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=msg)
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Rahmat!")

# Botni ishga tushurish
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()
