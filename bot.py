from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

logging.basicConfig(level=logging.INFO)

user_state = {}
last_post = {}  # So‘nggi kanalga yuborilgan rasm va caption

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text("👋 Assalomu alaykum! Buyurtma uchun mahsulot nomini kiriting:")
    user_state[chat_id] = {"step": "product"}

# Matnli xabarlar
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user

    if not user_state.get(chat_id):
        await update.message.reply_text("Iltimos /start buyrug'ini bosing.")
        return

    step = user_state[chat_id].get("step")

    if step == "product":
        user_state[chat_id]["product"] = text
        user_state[chat_id]["step"] = "phone"
        await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    elif step == "phone":
        user_state[chat_id]["phone"] = text
        user_state[chat_id]["step"] = "address"
        await update.message.reply_text("📍 Endi manzilingizni kiriting:")
    elif step == "address":
        product = user_state[chat_id].get("product", "Noma'lum mahsulot")
        phone = user_state[chat_id]["phone"]
        address = text

        # Foydalanuvchi nomi yoki profili havolasi
        if user.username:
            username_link = f"@{user.username}"
        else:
            name = (user.first_name or "") + " " + (user.last_name or "")
            username_link = f"[{name.strip()}](tg://user?id={user.id})"

        msg = (
            "🆕 *Yangi buyurtma:*\n"
            f"👤 {username_link}\n"
            f"📦 Mahsulot: {product}\n"
            f"📞 Telefon: {phone}\n"
            f"📍 Manzil: {address}"
        )

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog'lanamiz.")

        try:
            if "photo_id" in user_state[chat_id]:
                caption = user_state[chat_id].get("caption", "🛍 Mahsulot")
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=user_state[chat_id]["photo_id"],
                    caption=msg + f"\n\n🖼 {caption}",
                    parse_mode="Markdown"
                )
            else:
                await context.bot.send_message(
                    chat_id=ADMIN_ID, text=msg, parse_mode="Markdown"
                )
        except Exception as e:
            logging.error(f"Admin xabar yuborishda xatolik: {e}")

        user_state.pop(chat_id)
    else:
        await update.message.reply_text("Iltimos /start buyrug'ini bosing.")

# Rasm yuborish
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish ➡️", callback_data="order_now")]
    ])

    try:
        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ Kanalga yuborildi.")

        # So‘nggi rasmni saqlaymiz
        last_post["photo_id"] = photo
        last_post["caption"] = caption

    except Exception as e:
        logging.error(f"Rasm yuborilmadi: {e}")
        await update.message.reply_text("❌ Kanalga yuborishda xatolik.")

# Tugmani bosganda
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    user_state[user_id] = {
        "step": "product",
        "photo_id": last_post.get("photo_id"),
        "caption": last_post.get("caption", "🛍 Mahsulot")
    }

    await context.bot.send_message(
        chat_id=user_id,
        text="👋 Assalomu alaykum! Buyurtma uchun mahsulot nomini kiriting:"
    )

# Admin test komandasi
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text="🔔 Test xabari.")
        await update.message.reply_text("✅ Adminga xabar yuborildi.")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")

# Botni ishga tushurish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", test_admin))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

if __name__ == "__main__":
    app.run_polling()
