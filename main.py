# ============================================
#         OTP BOT - MAIN.PY
# ============================================

import asyncio
import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Plugin list
plugins = dict(root="plugins")

app = Client(
    "otpbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=plugins
)

async def main():
    async with app:
        logger.info("✅ OTP Bot Started Successfully!")
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
