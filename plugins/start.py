# ============================================
#         PLUGIN: START
# ============================================

from pyrogram import Client, filters
from pyrogram.types import Message
from database import get_user
from utils.keyboards import main_menu_keyboard
from utils.messages import welcome_text, how_to_use_text

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await get_user(message.from_user.id)  # Register user
    await message.reply_text(
        welcome_text(message.from_user.first_name),
        reply_markup=main_menu_keyboard()
    )

@Client.on_message(filters.regex("^📖 How to Use$") & filters.private)
async def how_to_use_handler(client: Client, message: Message):
    await message.reply_text(how_to_use_text())

@Client.on_message(filters.regex("^🤝 Support$") & filters.private)
async def support_handler(client: Client, message: Message):
    from config import SUPPORT_USERNAME
    await message.reply_text(
        f"📞 **Support**\n\nContact our support team:\n{SUPPORT_USERNAME}"
    )
