caption = update.message.caption or "Mahsulot"

# Rasmni olish
photo = update.message.photo[-1]
file = await photo.get_file()
photo_path = "temp.jpg"
await file.download_to_drive(photo_path)

# Tugma
buttons = InlineKeyboardMarkup([
    [InlineKeyboardButton("🛒 Buyurtma berish", callback_data="order")]
])

# Kanalga yuborish
with open(photo_path, "rb") as img:
    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=img,
        caption=caption,
        reply_markup=buttons
    )

os.remove(photo_path)
