# ============================================
#         KEYBOARD HELPER UTILITY
# ============================================

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ── Main Menu ──────────────────────────────────
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📱 Telegram Accounts"), KeyboardButton("📱 Telegram Accounts 2")],
            [KeyboardButton("📱 WhatsApp SMS"),      KeyboardButton("💸 Deposit")],
            [KeyboardButton("👤 My Profile"),         KeyboardButton("🤝 Support")],
            [KeyboardButton("📖 How to Use"),         KeyboardButton("🎁 Promocode")]
        ],
        resize_keyboard=True
    )

# ── Country List ───────────────────────────────
def countries_keyboard(countries: list, page: int = 0, per_page: int = 6):
    """Generate paginated country buttons"""
    start = page * per_page
    end = start + per_page
    page_countries = countries[start:end]
    total_pages = (len(countries) + per_page - 1) // per_page

    buttons = []
    for c in page_countries:
        label = f"{c['flag']} {c['_id']} {c['flag']} : ₹{c['price']}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"country_{c['_id']}")])

    # Navigation row
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"page_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
    if end < len(countries):
        nav.append(InlineKeyboardButton("➡️", callback_data=f"page_{page+1}"))
    buttons.append(nav)

    # Utility row
    buttons.append([
        InlineKeyboardButton("🔍 Search Country", callback_data="search_country"),
        InlineKeyboardButton("🔄 Refresh", callback_data="refresh_countries")
    ])
    return InlineKeyboardMarkup(buttons)

# ── Purchase Confirm ───────────────────────────
def confirm_purchase_keyboard(country: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm Purchase", callback_data=f"confirm_{country}")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_countries")]
    ])

# ── After Purchase ─────────────────────────────
def after_purchase_keyboard(order_id: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Request the code", callback_data=f"getcode_{order_id}")],
        [InlineKeyboardButton("🔄 Request the code again", callback_data=f"recode_{order_id}")],
        [InlineKeyboardButton("🔁 Buy again", callback_data="buy_again")],
        [InlineKeyboardButton("🔙 Back to Accounts list", callback_data="back_to_countries")]
    ])

# ── Deposit ────────────────────────────────────
def deposit_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ I've Paid - Verify Now", callback_data="verify_payment")]
    ])

# ── Admin Panel ────────────────────────────────
def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Number", callback_data="admin_add_number")],
        [InlineKeyboardButton("📋 List Numbers", callback_data="admin_list_numbers")],
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👥 All Users", callback_data="admin_users")]
    ])
