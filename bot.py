async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Sizda ruxsat yo'q.")
        return

    if len(context.args) < 3:
        await update.message.reply_text("Foydalanish: /post rasm_url narx mahsulot_nomi")
        return

    image_url = context.args[0]
    price = context.args[1]
    name = ' '.join(context.args[2:])

    caption = f"📦 Mahsulot: {name}\n💰 Narx: {price} so'm\n\n👇 Buyurtma uchun tugmani bosing:"
    keyboard = [[InlineKeyboardButton("📥 Buyurtma berish", callback_data=f"order|{name}|{price}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await context.bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=caption, reply_markup=reply_markup)
        await update.message.reply_text("Post kanalga yuborildi ✅")
    except Exception as e:
        print("XATOLIK:", e)
        await update.message.reply_text(f"❌ Xatolik yuz berdi: {e}")
