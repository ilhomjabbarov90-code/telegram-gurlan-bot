# Rasm yuborilganda — admin mahsulot qo‘shmoqda
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    photo = update.message.photo[-1].file_id

    # Admin mahsulot qo‘shmoqda deb belgilaymiz
    user_state[chat_id] = {
        "step": "waiting_caption",
        "photo": photo
    }

    await update.message.reply_text("📝 Mahsulot nomi va narxini kiriting.\n\nMasalan: `Sumka - 35000`")


# Matnli xabarlar bilan ishlovchi yagona funksiya
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user

    # Agar bu admin mahsulot nomi/narxini kiritayotgan bo‘lsa
    if chat_id in user_state and user_state[chat_id].get("step") == "waiting_caption":
        photo = user_state[chat_id]["photo"]
        caption = text

        # Tugmadagi linkga captionni kiritamiz
        from urllib.parse import quote
        encoded_caption = quote(caption)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Buyurtma berish ➡️", url=f"https://t.me/Buyccc_bot?start={encoded_caption}")]
        ])

        try:
            await context.bot.send_photo(
                chat_id=CHANNEL_USERNAME,
                photo=photo,
                caption=caption,
                reply_markup=keyboard
            )
            await update.message.reply_text("✅ Mahsulot kanalga yuborildi.")
        except Exception as e:
            logging.error(f"Kanalga yuborishda xatolik: {e}")
            await update.message.reply_text("❌ Kanalga yuborishda xatolik.")

        user_state.pop(chat_id)
        return

    # Agar bu oddiy foydalanuvchi (mijoz) bo‘lsa
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
        username = f"@{user.username}" if user.username else f"{user.first_name or ''} {user.last_name or ''}".strip()
        if not username:
            username = f"ID: {user.id}"

        msg = f"🆕 Yangi buyurtma:\n👤 {username}\n📞 {phone}\n📍 {address}"

        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
        except Exception as e:
            logging.error(f"Admin xabar yuborishda xatolik: {e}")

        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.")
        user_state.pop(chat_id)
    else:
        await update.message.reply_text("Iltimos /start buyrug'ini bosing.")
