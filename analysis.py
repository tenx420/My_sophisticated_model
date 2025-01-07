import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_fetch import fetch_daily_data  # Must be in your project
from support_resistance import calculate_pivot_points  # Import the support/resistance calculation function

############################
#     HELPER INDICATORS
############################

def sma(series, window):
    return series.rolling(window).mean()

def rsi(series, period=14):
    delta = series.diff()
    gains = delta.clip(lower=0)
    losses = -1 * delta.clip(upper=0)
    avg_gain = gains.rolling(period).mean()
    avg_loss = losses.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

############################
#  ANALYZE SPY & VXX
############################

def analyze_current_spy_and_vxx(spy_symbol="SPY", vxx_symbol="VXX", lookback_days=365*2, return_data=False):
    """
    Analyze SPY and VXX data, classify market trend, and compute support/resistance levels.
    """
    # --- Fetch SPY data
    df_spy = fetch_daily_data(spy_symbol, lookback_days)
    if df_spy.empty:
        print(f"No data for {spy_symbol}.")
        return {} if return_data else None
    
    df_spy["SMA_50"] = sma(df_spy["Close"], 50)
    df_spy["SMA_200"] = sma(df_spy["Close"], 200)
    df_spy["RSI_14"]  = rsi(df_spy["Close"], 14)
    df_spy.dropna(inplace=True)
    if df_spy.empty:
        print("Not enough SPY data after computing indicators.")
        return {} if return_data else None
    
    last = df_spy.iloc[-1]
    sma50, sma200 = last["SMA_50"], last["SMA_200"]
    rsi_val       = last["RSI_14"]
    high, low, close = last["High"], last["Low"], last["Close"]

    # Determine market trend
    if sma50 > sma200 * 1.01:
        market_trend = "BULLISH"
    elif sma50 < sma200 * 0.99:
        market_trend = "BEARISH"
    else:
        market_trend = "CONSOLIDATION"
    
    # RSI comment
    if rsi_val < 30:
        rsi_comment = "RSI < 30 => Oversold"
    elif rsi_val > 70:
        rsi_comment = "RSI > 70 => Overbought"
    else:
        rsi_comment = "RSI in neutral range"
    
    # --- Calculate Support and Resistance Levels
    levels = calculate_pivot_points(high, low, close)

    # --- Fetch VXX
    df_vxx = fetch_daily_data(vxx_symbol, lookback_days)
    if df_vxx.empty:
        vxx_comment = f"{vxx_symbol}: No data."
        vxx_close   = 0.0
    else:
        vxx_close = df_vxx["Close"].iloc[-1]
        vxx_comment = (f"{vxx_symbol}={vxx_close:.2f} => Elevated short-term volatility"
                       if vxx_close > 30
                       else f"{vxx_symbol}={vxx_close:.2f} => Moderate short-term volatility")
    
    # Print
    print("\n=== Current SPY & VXX Outlook ===")
    print(f"Last Close Date: {df_spy.index[-1].strftime('%Y-%m-%d')}")
    print(f"SPY Trend: {market_trend} (50 SMA={sma50:.2f}, 200 SMA={sma200:.2f})")
    print(f"RSI_14={rsi_val:.2f} => {rsi_comment}")
    print(f"Pivot Point: {levels['Pivot Point']}")
    print(f"Resistance 1: {levels['Resistance 1']}, Resistance 2: {levels['Resistance 2']}, Resistance 3: {levels['Resistance 3']}")
    print(f"Support 1: {levels['Support 1']}, Support 2: {levels['Support 2']}, Support 3: {levels['Support 3']}")
    print(vxx_comment)
    print("Note: VXX is a futures-based ETN. If market is open, these daily bars may be partial.")
    
    # Return data if requested
    if return_data:
        # Make a simpler vxx_comment for AI usage
        short_vxx_comment = "Elevated short-term volatility" if vxx_close > 30 else "Moderate short-term volatility"
        return {
            "market_trend": market_trend,
            "rsi_value": rsi_val,
            "rsi_comment": rsi_comment,
            "pivot_point": levels["Pivot Point"],
            "resistance_1": levels["Resistance 1"],
            "resistance_2": levels["Resistance 2"],
            "resistance_3": levels["Resistance 3"],
            "support_1": levels["Support 1"],
            "support_2": levels["Support 2"],
            "support_3": levels["Support 3"],
            "vxx_close": vxx_close,
            "vxx_comment": short_vxx_comment
        }

    return None
