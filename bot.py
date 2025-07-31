from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

logging.basicConfig(level=logging.INFO)

user_state = {}
product_data = {}  # message_id => {"photo": file_id, "caption": text}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    user_state[update.message.chat_id] = {"step": "phone"}

# Matnli xabarlar
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user

    username = f"@{user.username}" if user.username else f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not username:
        username = f"ID: {user.id}"

    if chat_id not in user_state:
        await update.message.reply_text("Iltimos /start buyrug'ini bosing.")
        return

    step = user_state[chat_id].get("step")

    if step == "phone":
        user_state[chat_id]["phone"] = text
        user_state[chat_id]["step"] = "address"
        await update.message.reply_text("📍 Endi manzilingizni kiriting:")
    elif step == "address":
        phone = user_state[chat_id]["phone"]
        address = text
        product = user_state[chat_id].get("product")

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.")

        msg = f"🆕 Yangi buyurtma:\n👤 {username}\n📞 {phone}\n📍 {address}"
        if product:
            msg += f"\n🛍 {product['caption']}"
            try:
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=product["photo"], caption=msg)
            except:
                await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

        user_state.pop(chat_id)
    else:
        await update.message.reply_text("Iltimos /start buyrug'ini bosing.")

# Rasm kelganda — kanalda e’lon qiladi
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtma berish", callback_data=f"order|{update.message.message_id}")]
    ])

    try:
        msg = await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ Kanalga yuborildi.")
        # Mahsulot ma’lumotini saqlab qo’yamiz
        product_data[msg.message_id] = {"photo": photo, "caption": caption}
    except Exception as e:
        logging.error(f"Kanalga yuborilmadi: {e}")
        await update.message.reply_text("❌ Kanalga yuborishda xatolik.")

# Tugma bosilganda
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    data = query.data
    if data.startswith("order|"):
        try:
            msg_id = int(data.split("|")[1])
            product = product_data.get(msg_id)
            if product:
                user_state[user_id] = {"step": "phone", "product": product}
                await context.bot.send_message(chat_id=user_id, text="📞 Telefon raqamingizni kiriting:")
            else:
                await context.bot.send_message(chat_id=user_id, text="❌ Mahsulot topilmadi.")
        except Exception as e:
            logging.error(f"Callback error: {e}")
            await context.bot.send_message(chat_id=user_id, text="❌ Xatolik yuz berdi.")

# Admin test
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
