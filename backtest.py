# backtest.py
import pandas as pd

def simple_backtest(df, model, test_days=180, initial_capital=100000):
    """
    Use the model's predicted class (0 or 1) to simulate going long on "1"
    and going flat on "0". If the model says 'bullish' for tomorrow, buy at today's close
    and sell at tomorrow's close, etc.
    
    Very naive. Real backtesting requires more detail.
    """
    # Sort index
    df = df.sort_index().copy()
    
    # We'll generate predictions for the test period
    feature_cols = [
        "RSI_14", "MACD", "MACD_signal", "SMA_50", "SMA_200", "BB_upper", "BB_lower", "ATR_14",
        "Open", "High", "Low", "Close", "Volume"
    ]
    train_cutoff = df.index[-test_days]
    
    df_test = df[df.index >= train_cutoff].copy()
    if df_test.empty:
        print("[WARN] No test data for backtest.")
        return
    
    X_test = df_test[feature_cols]
    df_test["pred"] = model.predict(X_test)
    
    # We'll track daily returns
    capital = initial_capital
    positions = 0  # how many shares
    shares_held = 0
    df_test["StrategyReturns"] = 0.0
    
    # For each day in test set:
    #   If model says '1' => go (or stay) long
    #   If model says '0' => close any long
    # We assume we buy/sell at the close, and realize PnL next day.
    # This is extremely simplified.
    
    prev_close = None
    for i in range(len(df_test) - 1):
        today_idx = df_test.index[i]
        next_idx = df_test.index[i+1]
        pred = df_test.loc[today_idx, "pred"]
        
        today_close = df_test.loc[today_idx, "Close"]
        next_close = df_test.loc[next_idx, "Close"]
        
        if pred == 1:
            # we want to be long overnight
            # buy at today's close
            if shares_held == 0:
                shares_held = int(capital // today_close)
                capital_left = capital - (shares_held * today_close)
            # next day we evaluate PnL
            daily_pnl = shares_held * (next_close - today_close)
            df_test.at[next_idx, "StrategyReturns"] = daily_pnl
            # capital changes
            capital += daily_pnl
        else:
            # pred == 0 => exit
            if shares_held > 0:
                # we assume we sold at today's close => realize no overnight PnL
                # reset
                shares_held = 0
    
    # If we end test still holding shares, let's 'sell' them at last close
    if shares_held > 0:
        last_idx = df_test.index[-1]
        last_close = df_test.loc[last_idx, "Close"]
        daily_pnl = shares_held * (last_close - last_close)  # basically 0 if we do final sale at same price
        capital += daily_pnl
        shares_held = 0
    
    total_return = capital - initial_capital
    return_pct = (total_return / initial_capital) * 100.0
    
    return {
        "final_capital": capital,
        "total_return": total_return,
        "return_pct": return_pct
    }
