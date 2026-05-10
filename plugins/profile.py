# ============================================
#         PLUGIN: PROFILE
# ============================================

from pyrogram import Client, filters
from pyrogram.types import Message
from database import get_user, get_user_orders
from utils.messages import profile_text

@Client.on_message(filters.regex("^👤 My Profile$") & filters.private)
async def profile_handler(client: Client, message: Message):
    user = await get_user(message.from_user.id)
    orders = await get_user_orders(message.from_user.id)
    
    await message.reply_text(
        profile_text(
            user_id=message.from_user.id,
            wallet=user.get("wallet", 0),
            total_spent=user.get("total_spent", 0),
            orders=len(user.get("orders", []))
        )
    )
