# feature_engineering.py

import numpy as np
import pandas as pd

def ema(series, span):
    """
    Compute the Exponential Moving Average (EMA) of a Pandas Series.
    :param series: Pandas Series of price data.
    :param span: The EMA span (e.g., 12 or 26).
    :return: Pandas Series of EMA values.
    """
    return series.ewm(span=span, adjust=False).mean()

def sma(series, window):
    """
    Compute the Simple Moving Average (SMA) of a Pandas Series.
    :param series: Pandas Series of price data.
    :param window: The number of periods (bars) to average over.
    :return: Pandas Series of SMA values.
    """
    return series.rolling(window=window).mean()

def rsi(series, period=14):
    """
    Compute the Relative Strength Index (RSI).
    :param series: Pandas Series of price data.
    :param period: The RSI lookback period (default 14).
    :return: Pandas Series of RSI values.
    """
    delta = series.diff()
    gains = delta.clip(lower=0)
    losses = -1 * delta.clip(upper=0)
    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    out = 100 - (100 / (1 + rs))
    return out

def macd(series, fast=12, slow=26, signal=9):
    """
    Compute MACD (Moving Average Convergence Divergence) and its signal line.
    :param series: Pandas Series of price data (e.g., Close).
    :param fast: Fast EMA span (default 12).
    :param slow: Slow EMA span (default 26).
    :param signal: Signal EMA span (default 9).
    :return: Tuple (macd_line, signal_line) as Pandas Series.
    """
    fast_ema = ema(series, fast)
    slow_ema = ema(series, slow)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, signal)
    return macd_line, signal_line

def bollinger_bands(series, window=20, num_std=2):
    """
    Compute Bollinger Bands.
    :param series: Pandas Series of price data (e.g., Close).
    :param window: SMA window length (default 20).
    :param num_std: Number of standard deviations for the bands (default 2).
    :return: Tuple (upper_band, lower_band) as Pandas Series.
    """
    ma = sma(series, window)
    std = series.rolling(window).std()
    upper_band = ma + (num_std * std)
    lower_band = ma - (num_std * std)
    return upper_band, lower_band

def true_range(df):
    """
    Compute the True Range (TR) for each row in df.
    TR = max of:
        (High - Low),
        |High - Previous Close|,
        |Low - Previous Close|
    :param df: DataFrame with columns [High, Low, Close].
    :return: Pandas Series of True Range values.
    """
    prev_close = df["Close"].shift(1)
    tr1 = df["High"] - df["Low"]
    tr2 = (df["High"] - prev_close).abs()
    tr3 = (df["Low"] - prev_close).abs()
    return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

def atr(df, window=14):
    """
    Compute the Average True Range (ATR) over a rolling window.
    :param df: DataFrame with columns [High, Low, Close].
    :param window: The rolling window (default 14).
    :return: Pandas Series of ATR values.
    """
    tr = true_range(df)
    return tr.rolling(window).mean()

def build_features(df):
    """
    Given a DataFrame with columns [Open, High, Low, Close, Volume],
    add multiple technical indicators as new columns for ML training,
    and define a 'Target' column that indicates whether the next day's
    Close is higher than today's (1 for bullish, 0 for bearish).

    :param df: Original OHLCV DataFrame.
    :return: DataFrame with additional columns:
        RSI_14, MACD, MACD_signal, SMA_50, SMA_200,
        BB_upper, BB_lower, ATR_14, Target, (and 'future_close' used internally).
    """
    df = df.copy()  # avoid modifying original

    # 1) RSI
    df["RSI_14"] = rsi(df["Close"], 14)

    # 2) MACD & MACD Signal
    macd_line, signal_line = macd(df["Close"], fast=12, slow=26, signal=9)
    df["MACD"] = macd_line
    df["MACD_signal"] = signal_line

    # 3) SMA (50 & 200)
    df["SMA_50"] = sma(df["Close"], 50)
    df["SMA_200"] = sma(df["Close"], 200)

    # 4) Bollinger Bands
    upper_bb, lower_bb = bollinger_bands(df["Close"], window=20, num_std=2)
    df["BB_upper"] = upper_bb
    df["BB_lower"] = lower_bb

    # 5) ATR (14)
    df["ATR_14"] = atr(df, window=14)

    # 6) Define next-day "Target"
    #    If tomorrow's Close > today's Close => 1 (Bullish), else 0
    df["future_close"] = df["Close"].shift(-1)
    df["Target"] = (df["future_close"] > df["Close"]).astype(int)

    # Drop rows where indicators are NaN (e.g., early rows that can't compute rolling)
    df.dropna(inplace=True)

    return df
