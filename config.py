# config.py
from api_keys import POLYGON_API_KEY

# Which ticker to model? For a broad market proxy, we might use SPY.
# You can adapt to e.g. QQQ, or a basket of symbols.
TARGET_TICKER = "SPY"

# If you want to incorporate a fear gauge
VIX_TICKER = "VIX"

# How many years of daily historical data to fetch for training
TRAINING_LOOKBACK_DAYS = 3 * 365  # ~3 years

# How many years (or days) to reserve for out-of-sample testing in backtest
BACKTEST_DAYS = 180  # last ~6 months

# Some threshold for "market open" check (if you want to skip or adapt intraday logic)
MARKET_STATUS_URL = "https://api.polygon.io/v1/marketstatus/now"
