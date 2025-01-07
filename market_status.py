# market_status.py
import requests
from config import API_KEY, MARKET_STATUS_URL

def is_market_open():
    """
    Calls the Polygon.io v1/marketstatus/now endpoint to see if market is open.
    """
    try:
        r = requests.get(MARKET_STATUS_URL, params={"apiKey": API_KEY})
        data = r.json()
        return (data.get("market", "").lower() == "open")
    except Exception as e:
        print(f"[WARN] Could not fetch market status: {e}")
        # By default, assume not open
        return False
