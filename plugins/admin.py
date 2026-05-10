# ============================================
#         PLUGIN: ADMIN PANEL
# ============================================

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from config import ADMIN_IDS
from database import (
    add_number, get_numbers_by_country, delete_number,
    get_all_users, get_countries, mark_number_available,
    get_deposit_stats
)
from utils.keyboards import admin_keyboard

# Admin filter
admin_filter = filters.user(ADMIN_IDS) & filters.private

# Track admin states
admin_states = {}

# ── Admin Panel ────────────────────────────────
@Client.on_message(filters.command("admin") & admin_filter)
async def admin_panel(client: Client, message: Message):
    await message.reply_text(
        "🔐 **Admin Panel**\n\nSelect an option:",
        reply_markup=admin_keyboard()
    )

# ── Add Number ─────────────────────────────────
@Client.on_callback_query(filters.regex("^admin_add_number$"))
async def admin_add_number(client: Client, callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Unauthorized!", show_alert=True)
        return
    await callback.answer()
    admin_states[callback.from_user.id] = {"step": "awaiting_number_data"}
    await callback.message.reply_text(
        "➕ **Add New Number**\n\n"
        "Send number details in this format:\n\n"
        "`country|flag|phone|session_string|price|2fa_pass`\n\n"
        "**Example:**\n"
        "`Nigeria|🇳🇬|+2348052933466|BQA...session...|37|mypass123`\n\n"
        "_(Leave 2fa_pass blank if no 2FA)_\n"
        "Send `/cancel` to cancel."
    )

@Client.on_message(filters.command("addnumber") & admin_filter)
async def add_number_cmd(client: Client, message: Message):
    """Alternative: /addnumber country|flag|phone|session|price|2fa"""
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply_text(
            "Usage: `/addnumber Nigeria|🇳🇬|+2348052933466|SESSION_STRING|37|2fa_pass`"
        )
        return
    await process_add_number(client, message, args[1])

@Client.on_message(admin_filter & filters.text)
async def admin_text_handler(client: Client, message: Message):
    user_id = message.from_user.id
    state = admin_states.get(user_id, {})

    if state.get("step") == "awaiting_number_data":
        if message.text == "/cancel":
            del admin_states[user_id]
            await message.reply_text("❌ Cancelled.")
            return
        await process_add_number(client, message, message.text)
        if user_id in admin_states:
            del admin_states[user_id]

    elif state.get("step") == "awaiting_broadcast":
        if message.text == "/cancel":
            del admin_states[user_id]
            await message.reply_text("❌ Broadcast cancelled.")
            return
        await do_broadcast(client, message, message.text)
        if user_id in admin_states:
            del admin_states[user_id]

async def process_add_number(client, message, data: str):
    parts = data.strip().split("|")
    if len(parts) < 5:
        await message.reply_text(
            "❌ Invalid format!\n"
            "Required: `country|flag|phone|session|price`\n"
            "Optional: `|2fa_pass`"
        )
        return
    
    country = parts[0].strip()
    flag = parts[1].strip()
    phone = parts[2].strip()
    session = parts[3].strip()
    price_str = parts[4].strip()
    twofa = parts[5].strip() if len(parts) > 5 else ""
    
    try:
        price = float(price_str)
    except ValueError:
        await message.reply_text("❌ Price must be a number!")
        return
    
    success = await add_number(country, flag, phone, session, price, twofa)
    if success:
        await message.reply_text(
            f"✅ **Number Added Successfully!**\n\n"
            f"🌍 Country: {flag} {country}\n"
            f"📱 Phone: `{phone}`\n"
            f"💲 Price: ₹{price}\n"
            f"🔑 2FA: {'Yes' if twofa else 'No'}"
        )
    else:
        await message.reply_text(f"❌ Phone `{phone}` already exists in database!")

# ── List Numbers ───────────────────────────────
@Client.on_callback_query(filters.regex("^admin_list_numbers$"))
async def admin_list_numbers(client: Client, callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Unauthorized!", show_alert=True)
        return
    await callback.answer()
    countries = await get_countries()
    if not countries:
        await callback.message.reply_text("📭 No numbers in database.")
        return
    
    text = "📋 **Available Numbers by Country:**\n\n"
    for c in countries:
        text += f"{c['flag']} **{c['_id']}** — ₹{c['price']} — {c['count']} available\n"
    await callback.message.reply_text(text)

@Client.on_message(filters.command("numbers") & admin_filter)
async def list_numbers_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Usage: `/numbers Nigeria`")
        return
    country = " ".join(args[1:])
    numbers = await get_numbers_by_country(country)
    if not numbers:
        await message.reply_text(f"No numbers for {country}")
        return
    
    text = f"📱 **Numbers for {country}:**\n\n"
    for n in numbers:
        status = "✅" if n["status"] == "available" else "❌"
        text += f"{status} `{n['phone']}` — ₹{n['price']}\n"
    await message.reply_text(text)

@Client.on_message(filters.command("delnumber") & admin_filter)
async def del_number_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Usage: `/delnumber +2348052933466`")
        return
    phone = args[1]
    await delete_number(phone)
    await message.reply_text(f"✅ Number `{phone}` deleted.")

@Client.on_message(filters.command("resetnumber") & admin_filter)
async def reset_number_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Usage: `/resetnumber +2348052933466`")
        return
    phone = args[1]
    await mark_number_available(phone)
    await message.reply_text(f"✅ Number `{phone}` reset to available.")

# ── Stats ──────────────────────────────────────
@Client.on_callback_query(filters.regex("^admin_stats$"))
async def admin_stats(client: Client, callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Unauthorized!", show_alert=True)
        return
    await callback.answer()
    users = await get_all_users()
    deposit_stats = await get_deposit_stats()
    countries = await get_countries()
    total_numbers = sum(c["count"] for c in countries)
    
    await callback.message.reply_text(
        f"📊 **Bot Statistics**\n\n"
        f"👥 Total Users: {len(users)}\n"
        f"📱 Available Numbers: {total_numbers}\n"
        f"💸 Total Deposits: {deposit_stats['total']}\n"
        f"✅ Verified Deposits: {deposit_stats['success']}\n"
    )

# ── Broadcast ──────────────────────────────────
@Client.on_callback_query(filters.regex("^admin_broadcast$"))
async def admin_broadcast_start(client: Client, callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Unauthorized!", show_alert=True)
        return
    await callback.answer()
    admin_states[callback.from_user.id] = {"step": "awaiting_broadcast"}
    await callback.message.reply_text(
        "📢 **Broadcast Message**\n\nSend your message now.\nSend `/cancel` to cancel."
    )

@Client.on_message(filters.command("broadcast") & admin_filter)
async def broadcast_cmd(client: Client, message: Message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        admin_states[message.from_user.id] = {"step": "awaiting_broadcast"}
        await message.reply_text("📢 Send your broadcast message:")
        return
    await do_broadcast(client, message, args[1])

async def do_broadcast(client: Client, message: Message, text: str):
    users = await get_all_users()
    success = 0
    fail = 0
    status_msg = await message.reply_text(f"📢 Broadcasting to {len(users)} users...")
    
    for user in users:
        try:
            await client.send_message(user["user_id"], text)
            success += 1
        except Exception:
            fail += 1
    
    await status_msg.edit_text(
        f"📢 **Broadcast Complete!**\n\n"
        f"✅ Sent: {success}\n"
        f"❌ Failed: {fail}"
    )

# ── Users List ─────────────────────────────────
@Client.on_callback_query(filters.regex("^admin_users$"))
async def admin_users(client: Client, callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Unauthorized!", show_alert=True)
        return
    await callback.answer()
    users = await get_all_users()
    await callback.message.reply_text(
        f"👥 **Total Users: {len(users)}**\n\n"
        f"Use /broadcast to message all users."
    )
