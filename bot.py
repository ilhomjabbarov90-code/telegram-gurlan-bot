from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging

BOT_TOKEN = "7980498195:AAERSaDhImL7ypJjYex0LNclaepboP-C6nE"
ADMIN_ID = 1722876301
CHANNEL_USERNAME = "@gurlan_bozori1"

logging.basicConfig(level=logging.INFO)

user_state = {}

/start komandasi

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
user_state[update.message.chat_id] = {"step": "phone"}

Matnli xabarlar

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
chat_id = update.message.chat_id
text = update.message.text
user = update.message.from_user

if not user_state.get(chat_id):  
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

    # Foydalanuvchi nomi yoki profili havolasi  
    if user.username:  
        username_link = f"@{user.username}"  
    else:  
        name = (user.first_name or "") + " " + (user.last_name or "")  
        username_link = f"[{name.strip()}](tg://user?id={user.id})"  

    msg = (  
        "🆕 Yangi buyurtma:\n"  
        f"👤 {username_link}\n"  
        f"📞 {phone}\n"  
        f"📍 {address}"  
    )  

    await update.message.reply_text("✅ Buyurtmangiz qabul qilindi.")  

    try:  
        await context.bot.send_message(  
            chat_id=ADMIN_ID, text=msg, parse_mode="Markdown"  
        )  
    except Exception as e:  
        logging.error(f"Admin xabar yuborishda xatolik: {e}")  

    user_state.pop(chat_id)  
else:  
    await update.message.reply_text("Iltimos /start buyrug'ini bosing.")

Rasm yuborish

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
photo = update.message.photo[-1].file_id
caption = update.message.caption or "🛍 Mahsulot"

keyboard = InlineKeyboardMarkup([  
    [InlineKeyboardButton("📦 Buyurtma berish ➡️", url="https://t.me/Buyccc_bot?start=order")]  
])  

try:  
    await context.bot.send_photo(  
        chat_id=CHANNEL_USERNAME,  
        photo=photo,  
        caption=caption,  
        reply_markup=keyboard  
    )  
    await update.message.reply_text("✅ Kanalga yuborildi.")  
except Exception as e:  
    logging.error(f"Rasm yuborilmadi: {e}")  
    await update.message.reply_text("❌ Kanalga yuborishda xatolik.")

Tugmani bosganda

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
user_id = query.from_user.id
user_state[user_id] = {"step": "phone"}

await context.bot.send_message(chat_id=user_id, text="📞 Telefon raqamingizni kiriting:")

Admin test

async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
try:
await context.bot.send_message(chat_id=ADMIN_ID, text="🔔 Test xabari.")
await update.message.reply_text("✅ Adminga xabar yuborildi.")
except Exception as e:
await update.message.reply_text(f"❌ Xatolik: {e}")

Botni ishga tushurish

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", test_admin))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

if name == "main":
app.run_polling()

            f"📦 Mahsulot: {product}\n"
            f"📞 Telefon: {phone}\n"
            f"📍 Manzil: {address}"
        )

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog'lanamiz.")

        try:
            if "photo_id" in user_state[chat_id]:
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=user_state[chat_id]["photo_id"],
                    caption=msg,
                    parse_mode="Markdown"
                )
            else:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=msg,
                    parse_mode="Markdown"
                )
        except Exception as e:
            logging.error(f"Admin xabar yuborishda xatolik: {e}")

        user_state.pop(chat_id)
    else:
        await update.message.reply_text("Iltimos /start buyrug'ini bosing.")

# Rasm yuborish
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or "🛍 Mahsulot"

    # Adminga yuborish
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve|{photo}|{user.id}"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data=f"reject|{user.id}")
        ]
    ])

    try:
        msg = await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo,
            caption=f"👤 @{user.username or user.first_name}\n📸 Yangi mahsulot:\n\n{caption}",
            reply_markup=keyboard
        )
        pending_posts[msg.message_id] = {
            "photo": photo,
            "caption": caption
        }
        await update.message.reply_text("✅ Rasm adminga yuborildi. Tasdiqlansa kanalga chiqadi.")
    except Exception as e:
        logging.error(f"Rasm yuborilmadi: {e}")
        await update.message.reply_text("❌ Rasm yuborishda xatolik.")

# Tugmani bosganda
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("approve"):
        _, photo_id, user_id = data.split("|")
        original = pending_posts.get(query.message.message_id)
        if original:
            try:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📦 Buyurtma berish ➡️", url="https://t.me/Buyccc_bot?start=order")]
                ])
                await context.bot.send_photo(
                    chat_id=CHANNEL_USERNAME,
                    photo=original["photo"],
                    caption=original["caption"],
                    reply_markup=keyboard
                )
                await context.bot.send_message(chat_id=int(user_id), text="✅ Mahsulotingiz kanalga chiqarildi.")
                await query.edit_message_caption(caption="✅ Mahsulot tasdiqlandi va kanalga chiqarildi.")
            except Exception as e:
                await query.edit_message_caption(caption="❌ Kanalga yuborishda xatolik.")
        pending_posts.pop(query.message.message_id, None)

    elif data.startswith("reject"):
        _, user_id = data.split("|")
        await context.bot.send_message(chat_id=int(user_id), text="❌ Mahsulotingiz admin tomonidan rad etildi.")
        await query.edit_message_caption(caption="🚫 Mahsulot rad etildi.")

    else:
        user_id = query.from_user.id
        user_state[user_id] = {"step": "product"}
        await context.bot.send_message(
            chat_id=user_id,
            text="👋 Assalomu alaykum! Buyurtma uchun mahsulot nomini kiriting:"
        )

# Admin tekshirish komandasi
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
