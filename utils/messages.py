# ============================================
#         MESSAGES / TEXT TEMPLATES
# ============================================

from config import BHARATPE_UPI_ID, MIN_DEPOSIT, SUPPORT_USERNAME

def welcome_text(name: str) -> str:
    return (
        f"👋 **Welcome, {name}!**\n\n"
        f"🤖 This bot provides virtual phone numbers for Telegram & WhatsApp OTP verification.\n\n"
        f"📌 **How it works:**\n"
        f"1️⃣ Select a country & number\n"
        f"2️⃣ Confirm your purchase\n"
        f"3️⃣ Receive OTP code instantly\n\n"
        f"💰 Add balance via **Deposit** before buying.\n"
        f"📞 Need help? Contact {SUPPORT_USERNAME}"
    )

def how_to_use_text() -> str:
    return (
        "📖 **How to Use:**\n\n"
        "📱 **Get your number:**\n"
        "1️⃣ Select a country below.\n"
        "2️⃣ Confirm your purchase.\n"
        "3️⃣ Receive your number & code instantly.\n\n"
        "⚠️ **CRITICAL RULE:** Login **ONLY** using **Graph Manager** (Play Store). "
        "Other apps will force premium first.\n\n"
        "💡 **Tips:**\n"
        "• Numbers are valid for 20 minutes\n"
        "• No refund if OTP already delivered\n"
        "• Contact support for issues"
    )

def deposit_text() -> str:
    return (
        "💳 **UPI Deposit**\n\n"
        f"1️⃣ Pay using UPI ID:\n`{BHARATPE_UPI_ID}`\n\n"
        f"2️⃣ **Minimum amount:** ₹{MIN_DEPOSIT}\n\n"
        f"3️⃣ After payment, send **ONLY** your **UTR / Reference Number** here.\n\n"
        f"⚡ Balance will be added automatically after verification."
    )

def payment_verified_text(amount: float, new_balance: float) -> str:
    return (
        f"✅ **Payment Verified Successfully!**\n\n"
        f"💰 **Amount Added:** ₹{amount}\n"
        f"💳 **New Wallet Balance:** ₹{new_balance}\n\n"
        f"🎉 Your deposit has been credited instantly!"
    )

def purchase_disclaimer_text(country: str, flag: str, price: float) -> str:
    return (
        f"📋 **Terms of disclaimer.**\n\n"
        f"Dear customer, after you agree and click the purchase button, "
        f"the value of the number will be deducted, and the number will be "
        f"considered your property, and the money will **not be refunded** "
        f"if the OTP is already delivered.\n\n"
        f"- State: {flag} {country} {flag}\n"
        f"- Number price: ₹{price}\n\n"
        f"The number will be shown to you after the purchase is approved."
    )

def number_assigned_text(country: str, flag: str, phone: str, 
                          price: float, order_id: str) -> str:
    from datetime import date
    return (
        f"💬 -Waiting for the code...\n\n"
        f"✅ -State: {flag} {country} {flag}\n"
        f"✈️ -Application: Telegram\n\n"
        f"📱 -Number: `{phone}`\n"
        f"☑️ -the condition :••• Pending\n"
        f"💬 -Code: Waiting for the message\n"
        f"💲 -the price :₹{price}\n\n"
        f"📅 -on the date :{date.today()}\n\n"
        f"⚠️ **CRITICAL RULE:** Login **ONLY** using **Graph Messenger** (Available on Play Store). "
        f"Do not use any other app or you may be forced to buy Telegram Premium first "
        f"or you will not able to receive code."
    )

def code_received_text(country: str, flag: str, phone: str, 
                        code: str, twofa: str, price: float) -> str:
    from datetime import date
    msg = (
        f"✅ **Code Received Successfully!**\n\n"
        f"🗒️ State: {flag} {country} {flag}\n"
        f"📱 Number: `{phone}`\n"
        f"💲 Price: ₹{price}\n"
        f"📅 Date: {date.today()}\n\n"
        f"⚠️ RULE: Login **ONLY** using **Graph Manager** (Play Store). "
        f"Other apps will force you to buy Telegram Premium first!\n\n"
        f"─────────────────────\n"
        f"📱 NUMBER : `{phone}`\n"
        f"💬 CODE : `{code}`\n"
    )
    if twofa:
        msg += f"🔑 PASS : `{twofa}`\n"
    return msg

def profile_text(user_id: int, wallet: float, total_spent: float, orders: int) -> str:
    return (
        f"👤 **My Profile**\n\n"
        f"🆔 User ID: `{user_id}`\n"
        f"💰 Wallet Balance: ₹{wallet}\n"
        f"💸 Total Spent: ₹{total_spent}\n"
        f"📦 Total Orders: {orders}\n"
    )

def low_balance_text(price: float, wallet: float) -> str:
    needed = round(price - wallet, 2)
    return (
        f"❌ **Insufficient Balance!**\n\n"
        f"💰 Your wallet: ₹{wallet}\n"
        f"💲 Number price: ₹{price}\n"
        f"📉 You need: ₹{needed} more\n\n"
        f"👉 Please add balance via **Deposit**."
    )

def no_numbers_text(country: str) -> str:
    return (
        f"😔 **No numbers available for {country}**\n\n"
        f"Please try another country or check back later.\n"
        f"Contact support if urgent."
    )
