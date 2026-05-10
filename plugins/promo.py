# ============================================
#         PLUGIN: PROMOCODE
# ============================================

from pyrogram import Client, filters
from pyrogram.types import Message
from database import get_user, update_wallet
from config import ADMIN_IDS

# Simple in-memory promo codes (use DB for production)
promo_codes = {}
used_promos = {}  # {promo: [user_ids]}

# ── User: Redeem Promo ─────────────────────────
@Client.on_message(filters.regex("^🎁 Promocode$") & filters.private)
async def promocode_handler(client: Client, message: Message):
    await message.reply_text(
        "🎁 **Promocode**\n\n"
        "Send your promocode to redeem it:\n"
        "Format: `/promo CODE`"
    )

@Client.on_message(filters.command("promo") & filters.private)
async def redeem_promo(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Usage: `/promo YOURCODE`")
        return
    
    code = args[1].upper().strip()
    user_id = message.from_user.id
    
    if code not in promo_codes:
        await message.reply_text("❌ Invalid promocode!")
        return
    
    promo = promo_codes[code]
    users_used = used_promos.get(code, [])
    
    if user_id in users_used:
        await message.reply_text("❌ You have already used this promocode!")
        return
    
    if promo.get("uses", 0) <= 0:
        await message.reply_text("❌ This promocode has expired!")
        return
    
    # Apply promo
    amount = promo["amount"]
    new_balance = await update_wallet(user_id, amount, "add")
    
    # Update usage
    promo_codes[code]["uses"] -= 1
    if code not in used_promos:
        used_promos[code] = []
    used_promos[code].append(user_id)
    
    await message.reply_text(
        f"✅ **Promocode Applied!**\n\n"
        f"🎁 Code: `{code}`\n"
        f"💰 Amount Added: ₹{amount}\n"
        f"💳 New Balance: ₹{new_balance}"
    )

# ── Admin: Create Promo ────────────────────────
@Client.on_message(filters.command("createpromo") & filters.user(ADMIN_IDS))
async def create_promo(client: Client, message: Message):
    """Usage: /createpromo CODE AMOUNT USES"""
    args = message.text.split()
    if len(args) < 4:
        await message.reply_text("Usage: `/createpromo CODE AMOUNT USES`\nExample: `/createpromo WELCOME50 50 100`")
        return
    
    code = args[1].upper()
    try:
        amount = float(args[2])
        uses = int(args[3])
    except ValueError:
        await message.reply_text("❌ Invalid amount or uses!")
        return
    
    promo_codes[code] = {"amount": amount, "uses": uses}
    await message.reply_text(
        f"✅ **Promocode Created!**\n\n"
        f"🎁 Code: `{code}`\n"
        f"💰 Amount: ₹{amount}\n"
        f"🔢 Uses: {uses}"
    )

@Client.on_message(filters.command("deletepromo") & filters.user(ADMIN_IDS))
async def delete_promo(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Usage: `/deletepromo CODE`")
        return
    code = args[1].upper()
    if code in promo_codes:
        del promo_codes[code]
        await message.reply_text(f"✅ Promocode `{code}` deleted.")
    else:
        await message.reply_text("❌ Promocode not found.")

@Client.on_message(filters.command("listpromos") & filters.user(ADMIN_IDS))
async def list_promos(client: Client, message: Message):
    if not promo_codes:
        await message.reply_text("No active promocodes.")
        return
    text = "🎁 **Active Promocodes:**\n\n"
    for code, data in promo_codes.items():
        text += f"• `{code}` — ₹{data['amount']} — {data['uses']} uses left\n"
    await message.reply_text(text)
