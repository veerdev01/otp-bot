# ============================================
#         OTP BOT - CONFIG FILE
# ============================================

import os

# --- Telegram ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# --- Admin IDs (list of int) ---
ADMIN_IDS = list(map(int, os.environ.get("ADMIN_IDS", "123456789").split(",")))

# --- MongoDB ---
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://user:pass@cluster.mongodb.net/otpbot")
DB_NAME = "otpbot"

# --- BharatPe ---
BHARATPE_TOKEN = os.environ.get("BHARATPE_TOKEN", "")
BHARATPE_MERCHANT_ID = os.environ.get("BHARATPE_MERCHANT_ID", "")
BHARATPE_UPI_ID = os.environ.get("BHARATPE_UPI_ID", "BHARATPE.8I0O0B6E7D63166@fbpe")

# --- Bot Settings ---
MIN_DEPOSIT = 10          # Minimum deposit in ₹
BOT_NAME = "EGRU_BOT"
SUPPORT_USERNAME = "@your_support"
