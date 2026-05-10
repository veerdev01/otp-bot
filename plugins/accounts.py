# ============================================
#         PLUGIN: TELEGRAM ACCOUNTS
# ============================================

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram import errors as pyrogram_errors
from database import (
    get_countries, get_available_number, mark_number_sold,
    create_order, update_order_code, get_order, get_wallet, update_wallet
)
from utils.keyboards import countries_keyboard, confirm_purchase_keyboard, after_purchase_keyboard
from utils.messages import (
    purchase_disclaimer_text, number_assigned_text,
    code_received_text, low_balance_text, no_numbers_text
)

# Store active sessions per user: {user_id: {order_id, phone, session_client}}
active_sessions = {}

# ── Show Country List ──────────────────────────
@Client.on_message(filters.regex("^📱 Telegram Accounts$") & filters.private)
async def telegram_accounts_handler(client: Client, message: Message):
    await show_countries(client, message, page=0)

@Client.on_message(filters.regex("^📱 Telegram Accounts 2$") & filters.private)
async def telegram_accounts2_handler(client: Client, message: Message):
    await show_countries(client, message, page=0)

async def show_countries(client, message, page: int = 0):
    countries = await get_countries()
    if not countries:
        await message.reply_text("😔 No numbers available right now. Please check back later.")
        return

    total_pages = (len(countries) + 5) // 6
    await message.reply_text(
        f"📱 **Telegram Accounts**\n\n"
        f"📝 How to get your number:\n"
        f"1️⃣ Select a country below.\n"
        f"2️⃣ Confirm your purchase.\n"
        f"3️⃣ Receive your number & code instantly.\n\n"
        f"⚠️ **CRITICAL RULE:** Login **ONLY** using **Graph Manager** (Play Store). "
        f"Other apps will force premium first.\n\n"
        f"👇 Select a country *(Page {page+1}/{total_pages})*",
        reply_markup=countries_keyboard(countries, page=page)
    )

# ── Pagination ─────────────────────────────────
@Client.on_callback_query(filters.regex(r"^page_(\d+)$"))
async def page_callback(client: Client, callback: CallbackQuery):
    await callback.answer()
    page = int(callback.matches[0].group(1))
    countries = await get_countries()
    if not countries:
        await callback.message.edit_text("No numbers available.")
        return
    total_pages = (len(countries) + 5) // 6
    await callback.message.edit_text(
        f"📱 **Telegram Accounts**\n\n"
        f"👇 Select a country *(Page {page+1}/{total_pages})*",
        reply_markup=countries_keyboard(countries, page=page)
    )

@Client.on_callback_query(filters.regex("^refresh_countries$"))
async def refresh_callback(client: Client, callback: CallbackQuery):
    await callback.answer("🔄 Refreshed!")
    countries = await get_countries()
    total_pages = (len(countries) + 5) // 6
    await callback.message.edit_reply_markup(
        reply_markup=countries_keyboard(countries, page=0)
    )

@Client.on_callback_query(filters.regex("^back_to_countries$"))
async def back_to_countries(client: Client, callback: CallbackQuery):
    await callback.answer()
    countries = await get_countries()
    if not countries:
        await callback.message.edit_text("No numbers available.")
        return
    await callback.message.edit_text(
        "👇 Select a country *(Page 1)*",
        reply_markup=countries_keyboard(countries, page=0)
    )

# ── Country Selected ───────────────────────────
@Client.on_callback_query(filters.regex(r"^country_(.+)$"))
async def country_selected(client: Client, callback: CallbackQuery):
    await callback.answer()
    country = callback.matches[0].group(1)
    
    # Check if number available
    number = await get_available_number(country)
    if not number:
        await callback.message.edit_text(no_numbers_text(country))
        return
    
    # Check user wallet
    wallet = await get_wallet(callback.from_user.id)
    price = number["price"]
    
    if wallet < price:
        await callback.message.edit_text(
            low_balance_text(price, wallet),
        )
        return
    
    # Show disclaimer + confirm
    await callback.message.edit_text(
        purchase_disclaimer_text(country, number["flag"], price),
        reply_markup=confirm_purchase_keyboard(country)
    )

# ── Confirm Purchase ───────────────────────────
@Client.on_callback_query(filters.regex(r"^confirm_(.+)$"))
async def confirm_purchase(client: Client, callback: CallbackQuery):
    await callback.answer("⏳ Processing...")
    user_id = callback.from_user.id
    country = callback.matches[0].group(1)
    
    # Get available number
    number = await get_available_number(country)
    if not number:
        await callback.message.edit_text(no_numbers_text(country))
        return
    
    # Final wallet check
    wallet = await get_wallet(user_id)
    price = number["price"]
    if wallet < price:
        await callback.message.edit_text(low_balance_text(price, wallet))
        return
    
    # Deduct wallet & mark number sold
    await update_wallet(user_id, price, "deduct")
    await mark_number_sold(number["phone"], user_id)
    
    # Create order
    order_id = await create_order(user_id, country, number["phone"], price)
    
    # Store session info
    active_sessions[user_id] = {
        "order_id": order_id,
        "phone": number["phone"],
        "session_string": number["session_string"],
        "twofa": number.get("twofa_pass", ""),
        "country": country,
        "flag": number["flag"],
        "price": price
    }
    
    # Show number + waiting message
    await callback.message.edit_text(
        number_assigned_text(country, number["flag"], number["phone"], price, order_id),
        reply_markup=after_purchase_keyboard(order_id)
    )

# ── Request Code ───────────────────────────────
@Client.on_callback_query(filters.regex(r"^getcode_(.+)$"))
async def get_code(client: Client, callback: CallbackQuery):
    await callback.answer("📡 Requesting code...")
    user_id = callback.from_user.id
    order_id = callback.matches[0].group(1)
    
    session_data = active_sessions.get(user_id)
    if not session_data or session_data["order_id"] != order_id:
        await callback.message.reply_text("❌ Session expired. Please buy again.")
        return
    
    # Try to get OTP via Pyrogram session
    code = await request_otp_code(
        session_data["session_string"],
        session_data["phone"]
    )
    
    if code:
        await update_order_code(order_id, code)
        await callback.message.edit_text(
            code_received_text(
                session_data["country"],
                session_data["flag"],
                session_data["phone"],
                code,
                session_data["twofa"],
                session_data["price"]
            ),
            reply_markup=after_purchase_keyboard(order_id)
        )
    else:
        await callback.message.reply_text(
            "⏳ Code not yet received. Please wait and try again."
        )

@Client.on_callback_query(filters.regex(r"^recode_(.+)$"))
async def recode(client: Client, callback: CallbackQuery):
    # Same as get code - retry
    await get_code(client, callback)

@Client.on_callback_query(filters.regex("^buy_again$"))
async def buy_again(client: Client, callback: CallbackQuery):
    await callback.answer()
    countries = await get_countries()
    if not countries:
        await callback.message.edit_text("No numbers available.")
        return
    await callback.message.edit_text(
        "👇 Select a country to buy again:",
        reply_markup=countries_keyboard(countries, page=0)
    )

@Client.on_callback_query(filters.regex("^noop$"))
async def noop(client: Client, callback: CallbackQuery):
    await callback.answer()

# ── OTP Request via Pyrogram ───────────────────
async def request_otp_code(session_string: str, phone: str) -> str | None:
    """
    Use stored session string to request OTP for the phone number.
    Returns OTP code string or None.
    """
    from config import API_ID, API_HASH
    import re

    try:
        # Create client with the stored session
        user_client = Client(
            name=f"session_{phone}",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string,
            no_updates=True
        )
        
        async with user_client:
            # Listen for incoming messages (OTP) for 60 seconds
            otp_code = None
            
            @user_client.on_message(filters.incoming & filters.private)
            async def otp_listener(_, msg):
                nonlocal otp_code
                text = msg.text or msg.caption or ""
                # Extract 5-6 digit code
                match = re.search(r'\b(\d{5,6})\b', text)
                if match:
                    otp_code = match.group(1)
            
            # Wait up to 60 seconds for code
            for _ in range(60):
                await asyncio.sleep(1)
                if otp_code:
                    break
            
            return otp_code
            
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"OTP request error: {e}")
        return None
