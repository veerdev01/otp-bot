# ============================================
#    BHARATPE UTR VERIFICATION UTILITY
# ============================================

import aiohttp
import logging
from config import BHARATPE_TOKEN, BHARATPE_MERCHANT_ID

logger = logging.getLogger(__name__)

BHARATPE_BASE_URL = "https://api.bharatpe.com"

async def verify_utr(utr: str, expected_amount: float = None) -> dict:
    """
    Verify UTR via BharatPe API.
    Returns: {
        "success": bool,
        "amount": float,
        "utr": str,
        "message": str
    }
    """
    headers = {
        "Authorization": f"Bearer {BHARATPE_TOKEN}",
        "Content-Type": "application/json",
        "merchantId": BHARATPE_MERCHANT_ID
    }

    try:
        async with aiohttp.ClientSession() as session:
            # BharatPe transaction search endpoint
            url = f"{BHARATPE_BASE_URL}/v1/txn/getByRefId"
            params = {"refId": utr, "merchantId": BHARATPE_MERCHANT_ID}
            
            async with session.get(url, headers=headers, params=params, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Parse BharatPe response
                    if data.get("status") == "SUCCESS":
                        txn = data.get("response", {})
                        txn_amount = float(txn.get("txnAmount", 0))
                        txn_status = txn.get("txnStatus", "")
                        
                        if txn_status == "SUCCESS":
                            result = {
                                "success": True,
                                "amount": txn_amount,
                                "utr": utr,
                                "message": "Payment verified"
                            }
                            # Validate amount if provided
                            if expected_amount and txn_amount < expected_amount:
                                result["success"] = False
                                result["message"] = f"Amount mismatch: received ₹{txn_amount}"
                            return result
                        else:
                            return {
                                "success": False,
                                "amount": 0,
                                "utr": utr,
                                "message": f"Transaction status: {txn_status}"
                            }
                    else:
                        return {
                            "success": False,
                            "amount": 0,
                            "utr": utr,
                            "message": "UTR not found in BharatPe records"
                        }
                else:
                    logger.error(f"BharatPe API error: {resp.status}")
                    return {
                        "success": False,
                        "amount": 0,
                        "utr": utr,
                        "message": "Payment gateway error. Try again."
                    }

    except aiohttp.ClientTimeout:
        return {"success": False, "amount": 0, "utr": utr, "message": "Gateway timeout. Try again."}
    except Exception as e:
        logger.error(f"UTR verification error: {e}")
        return {"success": False, "amount": 0, "utr": utr, "message": "Verification failed. Contact support."}


async def get_merchant_balance() -> float:
    """Get BharatPe merchant wallet balance"""
    headers = {
        "Authorization": f"Bearer {BHARATPE_TOKEN}",
        "merchantId": BHARATPE_MERCHANT_ID
    }
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{BHARATPE_BASE_URL}/v1/merchant/balance"
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return float(data.get("response", {}).get("balance", 0))
    except Exception as e:
        logger.error(f"Balance fetch error: {e}")
    return 0.0
