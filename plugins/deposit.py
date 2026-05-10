# ============================================
#         PLUGIN: DEPOSIT
# ============================================

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from database import get_user, update_wallet, create_deposit, verify_deposit, mark_deposit_success
from utils.keyboards import deposit_keyboard
from utils.messages import deposit_text, payment_verified_text
from utils.bharatpe import verify_utr
from config import MIN_DEPOSIT, BHARATPE_UPI_ID

# Track users waiting for UTR input
waiting_utr = {}

# ── Show Deposit Info ──────────────────────────
@Client.on_message(filters.regex("^💸 Deposit$") & filters.private)
async def deposit_handler(client: Client, message: Message):
    # Send QR code + instructions
    await message.reply_text(
        deposit_text(),
        reply_markup=deposit_keyboard()
    )
    # Ask for UTR directly
    await message.reply_text("📩 **Please send your UTR number after completing the payment.**")
    waiting_utr[message.from_user.id] = True

# ── UTR Input Handler ──────────────────────────
@Client.on_message(filters.private & filters.text)
async def utr_input_handler(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in waiting_utr:
        return
    
    utr = message.text.strip()
    
    # Basic UTR validation (10-22 digits)
    if not utr.isdigit() or not (10 <= len(utr) <= 22):
        await message.reply_text(
            "❌ Invalid UTR format. UTR should be **10-22 digits only**.\n"
            "Please send the correct UTR number."
        )
        return
    
    # Remove from waiting state
    del waiting_utr[user_id]
    
    # Check if UTR already used
    existing = await verify_deposit(utr)
    if existing and existing.get("status") == "success":
        await message.reply_text("❌ **This UTR has already been used!**\nContact support if this is an error.")
        return
    
    processing_msg = await message.reply_text("⏳ **Verifying your payment...**")
    
    # Create deposit record
    await create_deposit(user_id, 0, utr)
    
    # Verify via BharatPe API
    result = await verify_utr(utr)
    
    if result["success"]:
        amount = result["amount"]
        
        if amount < MIN_DEPOSIT:
            await processing_msg.edit_text(
                f"❌ **Amount too low!**\n\n"
                f"Received: ₹{amount}\n"
                f"Minimum: ₹{MIN_DEPOSIT}\n\n"
                f"Contact support to resolve this."
            )
            return
        
        # Credit wallet
        new_balance = await update_wallet(user_id, amount, "add")
        await mark_deposit_success(utr)
        
        await processing_msg.edit_text(
            payment_verified_text(amount, new_balance)
        )
    else:
        await processing_msg.edit_text(
            f"❌ **Payment Verification Failed**\n\n"
            f"Reason: {result['message']}\n\n"
            f"Please wait 2-5 minutes and try again, or contact support.\n"
            f"UTR: `{utr}`"
        )
        # Re-enable UTR waiting
        waiting_utr[user_id] = True

# ── Verify via button ──────────────────────────
@Client.on_callback_query(filters.regex("^verify_payment$"))
async def verify_payment_callback(client: Client, callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    waiting_utr[user_id] = True
    await callback.message.reply_text(
        "📩 Please send your **UTR / Reference Number** now:"
    )
