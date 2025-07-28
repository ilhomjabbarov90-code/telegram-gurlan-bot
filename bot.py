async def handle_admin_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.message.from_user.id != ADMIN_ID:
        return

    if update.message.photo and update.message.caption:
        photo = update.message.photo[-1].file_id
        caption = update.message.caption

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Buyurtma berish", callback_data="order")]
        ])

        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ Kanalga yuborildi.")
