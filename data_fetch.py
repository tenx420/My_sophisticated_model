# data_fetch.py
import requests
import pandas as pd
from datetime import datetime, timedelta
from api_keys import POLYGON_API_KEY
from config import TARGET_TICKER, TRAINING_LOOKBACK_DAYS

def fetch_daily_data(symbol, lookback_days=TRAINING_LOOKBACK_DAYS):
    """
    Fetch daily OHLCV data for `symbol` from Polygon,
    covering approximately `lookback_days`.
    Returns a DataFrame with date as index.
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 50000,
        "apiKey": POLYGON_API_KEY
    }
    try:
        r = requests.get(url, params=params)
        data = r.json()
        if "results" not in data or not data["results"]:
            print(f"[WARN] No daily data found for {symbol}.")
            return pd.DataFrame()
        
        df = pd.DataFrame(data["results"])
        df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume", "t": "Timestamp"}, inplace=True)
        df["date"] = pd.to_datetime(df["Timestamp"], unit="ms")
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)
        return df
    except Exception as e:
        print(f"[ERROR] Failed to fetch data for {symbol}: {e}")
        return pd.DataFrame()