import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import os

TOKEN = os.getenv("TOKEN", "8032558089:AAGKPRzCZj5ZwiGCypW5cyHYuPS_UaZso5U")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@gurlan_bozori1")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1722876301"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=["post"])
async def send_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ Sizda ruxsat yo‘q.")
        return

    product_name = "📌 Mahsulot: Soqol olgich (Demo)"
    price = "💰 Narx: 25 000 so‘m"
    stock = "📦 Zaxirada: 12 dona"
    delivery = "🚚 Yetkazib berish mavjud"

    caption = f"{product_name}\n{price}\n{stock}\n{delivery}\n\n👇 Buyurtma uchun tugmani bosing:"
    photo_url = "https://via.placeholder.com/300x200.png?text=Demo+Mahsulot"

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🛒 Buyurtma berish", callback_data="order_now")
    )

    await bot.send_photo(chat_id=CHANNEL_USERNAME, photo=photo_url, caption=caption, reply_markup=keyboard)
    await message.reply("✅ Demo mahsulot kanalga yuborildi.")

@dp.callback_query_handler(lambda call: call.data == "order_now")
async def handle_order(call: types.CallbackQuery):
    user = call.from_user
    text = (f"📥 Buyurtma qabul qilindi!\n"
            f"👤 Ismi: {user.full_name}\n"
            f"🆔 ID: {user.id}\n"
            f"📨 Username: @{(user.username or 'yo‘q')}")
    await bot.send_message(chat_id=ADMIN_ID, text=text)
    await call.answer("✅ Buyurtmangiz qabul qilindi!", show_alert=True)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
