# 🤖 OTP Bot - Virtual Number Telegram Bot

Telegram bot for selling virtual phone numbers for OTP verification.
Supports Telegram Accounts, WhatsApp SMS, UPI deposits via BharatPe.

---

## 📁 Project Structure

```
otpbot/
├── main.py              # Bot entry point
├── config.py            # All configuration variables
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── database/
│   ├── __init__.py
│   └── db.py            # MongoDB helper functions
├── utils/
│   ├── __init__.py
│   ├── bharatpe.py      # BharatPe UTR verification
│   ├── keyboards.py     # Inline/reply keyboards
│   └── messages.py      # Message text templates
└── plugins/
    ├── start.py         # /start, How to Use, Support
    ├── profile.py       # My Profile
    ├── deposit.py       # Deposit + UTR verification
    ├── accounts.py      # Country list + number buying
    ├── admin.py         # Admin panel
    └── promo.py         # Promocodes
```

---

## ⚙️ Setup & Installation

### 1. Clone & Install
```bash
git clone <your-repo>
cd otpbot
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
nano .env   # Fill in your values
```

### 3. Get API Credentials
- **API_ID & API_HASH**: https://my.telegram.org
- **BOT_TOKEN**: @BotFather on Telegram
- **MongoDB**: https://mongodb.com/atlas (free tier)
- **BharatPe API**: Apply at BharatPe merchant portal

### 4. Run the Bot
```bash
# Direct
python main.py

# With PM2 (recommended)
pm2 start main.py --name otpbot --interpreter python3
pm2 save
pm2 startup
```

---

## 🔧 Admin Commands

| Command | Description |
|---------|-------------|
| `/admin` | Open admin panel |
| `/addnumber country\|flag\|phone\|session\|price\|2fa` | Add a virtual number |
| `/numbers Nigeria` | List numbers for a country |
| `/delnumber +2348052933466` | Delete a number |
| `/resetnumber +2348052933466` | Reset number to available |
| `/broadcast MESSAGE` | Send message to all users |
| `/createpromo CODE AMOUNT USES` | Create a promocode |
| `/deletepromo CODE` | Delete a promocode |
| `/listpromos` | List all active promocodes |

---

## 📱 How to Add Numbers (Admin)

1. Login to the Telegram account using **Graph Manager** (Play Store)
2. Get the **session string** using Pyrogram:
```python
from pyrogram import Client
app = Client("my_session", api_id=API_ID, api_hash=API_HASH)
with app:
    print(app.export_session_string())
```
3. Add number via bot:
```
/addnumber Nigeria|🇳🇬|+2348052933466|BQA...session...|37|2fapass
```

---

## 💳 BharatPe Setup

1. Register at BharatPe Business portal
2. Get your **Merchant ID** and **API Token**
3. Set your **UPI ID** in `.env`
4. Bot automatically verifies UTR after user sends it

---

## 🗄️ MongoDB Collections

- **users** — user profiles, wallet balance, orders
- **numbers** — virtual numbers (available/sold)
- **orders** — purchase history
- **deposits** — deposit & UTR records

---

## 🚀 Features

- ✅ Country list with prices (paginated)
- ✅ Wallet system with UPI deposits
- ✅ Automatic UTR verification via BharatPe
- ✅ Admin panel for number management
- ✅ OTP auto-fetch via Pyrogram session
- ✅ Promocode system
- ✅ Broadcast to all users
- ✅ Purchase history & profile
