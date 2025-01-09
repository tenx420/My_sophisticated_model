import os
import openai
import schedule
import time
import pandas as pd
from datetime import datetime

from market_status import is_market_open
from config import TARGET_TICKER, BACKTEST_DAYS
from data_fetch import fetch_daily_data
from feature_engineering import build_features
from ml_model import train_random_forest
from backtest import simple_backtest
from analysis import analyze_current_spy_and_vxx

# NEW: Import functions from post_to_discord.py
from post_to_discord import generate_report, create_report_image, post_image_to_discord

# Import API keys
from api_keys import OPENAI_API_KEY, DISCORD_WEBHOOK_URL

##############################################
#  SET YOUR OPENAI API KEY
##############################################
# Instantiate the OpenAI client
client = openai.Client(api_key=OPENAI_API_KEY)

def save_data_to_csv(data, filename="historical_data.csv"):
    """
    Save the given data to a CSV file.
    """
    df = pd.DataFrame(data)
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, mode='w', header=True, index=False)

def fetch_and_save_data():
    """
    Fetch data, calculate TA indicators, and save to CSV.
    """
    if not is_market_open():
        print("Market is not open now. Skipping data fetch.")
        return

    print(f"=== Fetching daily data for {TARGET_TICKER} ===")
    df_raw = fetch_daily_data(TARGET_TICKER)
    if df_raw.empty:
        print(f"No data returned for {TARGET_TICKER}. Exiting.")
        return

    print("=== Building features ===")
    df_feat = build_features(df_raw)
    if df_feat.empty:
        print("No data after building features. Exiting.")
        return

    # Save the data to CSV
    save_data_to_csv(df_feat)

def save_data_for_symbols(symbols):
    """
    Fetch and save data for given symbols to CSV.
    """
    for symbol in symbols:
        print(f"=== Fetching and saving {symbol} data ===")
        df = fetch_daily_data(symbol)
        if not df.empty:
            save_data_to_csv(df, f"{symbol.lower()}_data.csv")
        else:
            print(f"No data for {symbol}.")

def main():
    # Save SPY, VXX, GLD, and OXY data before running the scheduler
    save_data_for_symbols(["SPY", "VXX", "GLD", "OXY"])

    # Prompt the user to run the scheduler
    input("Press Enter to start the scheduler...")

    # 1) Check if market is open
    print("=== Checking if market is open ===")
    if not is_market_open():
        print("Market is not open now. We'll proceed anyway...\n")
    else:
        print("Market is open. Today's daily bar might be partial.\n")
    
    # 2) Model pipeline (fetch data, build features, train RandomForest, backtest)
    print(f"=== Fetching daily data for {TARGET_TICKER} ===")
    df_raw = fetch_daily_data(TARGET_TICKER)
    if df_raw.empty:
        print(f"No data returned for {TARGET_TICKER}. Exiting.")
        return
    
    print("=== Building features ===")
    df_feat = build_features(df_raw)
    if df_feat.empty:
        print("No data after building features. Exiting.")
        return
    
    print("=== Training Random Forest Model ===")
    model, metrics = train_random_forest(df_feat, test_days=BACKTEST_DAYS)
    print(f"Train accuracy: {metrics['train_accuracy']:.2f}, "
          f"Test accuracy: {metrics['test_accuracy']:.2f}")
    print(f"Train size: {metrics['train_size']}, Test size: {metrics['test_size']}\n")
    
    print("=== Simple Backtest ===")
    bt_results = simple_backtest(df_feat, model, test_days=BACKTEST_DAYS, initial_capital=100000)
    print(f"Final capital: ${bt_results['final_capital']:.2f}")
    print(f"Total return: ${bt_results['total_return']:.2f} "
          f"({bt_results['return_pct']:.2f}%)\n")
    
    # 3) Quick SPY & VXX outlook
    print("=== Quick SPY & VXX Outlook ===")
    results = analyze_current_spy_and_vxx(
        spy_symbol="SPY", 
        vxx_symbol="VXX", 
        lookback_days=365 * 2, 
        return_data=True
    )
    if not results:
        print("No SPY/VXX data to pass to AI.")
        return
    
    # 4) Use ChatCompletion with a chat-based model (e.g. gpt-3.5-turbo)
    prompt_text = f"""
We have the following market context:
- SPY is {results['market_trend']}
- RSI_14 is {results['rsi_value']:.2f}, meaning {results['rsi_comment']}
- VXX is {results['vxx_close']:.2f}, indicating {results['vxx_comment']}
- Pivot Point: {results['pivot_point']}
- Resistance Levels: {results['resistance_1']}, {results['resistance_2']}, {results['resistance_3']}
- Support Levels: {results['support_1']}, {results['support_2']}, {results['support_3']}

Generate a concise set of bullet points on potential actions or considerations
for a trader or hedge fund in this scenario. Assume they have moderate risk tolerance.
""".strip()

    print("\n=== AI Chat Prompt ===")
    print(prompt_text)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or 'gpt-4' if you have access
            messages=[
                {"role": "system", "content": "You are a helpful financial assistant."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=200,
            temperature=0.7
        )
        # Access the AI-generated content
        ai_text = response.choices[0].message.content.strip()
        
        print("\n=== AI Response ===")
        print(ai_text)
    except Exception as e:
        ai_text = f"Error calling OpenAI ChatCompletion: {e}"
        print(ai_text)
    
    print("\nAll done!")

    # 5) Post Summary as an Image to Discord
    print("=== Preparing Summary ===")
    
    # Build weekly_data/daily_data from the above results
    weekly_data = {
        "trend": results['market_trend'],
        "rsi": f"{results['rsi_value']:.2f}",
        "rsi_comment": results['rsi_comment'],
        "support": f"{results['support_1']}, {results['support_2']}, {results['support_3']}",
        "resistance": f"{results['resistance_1']}, {results['resistance_2']}, {results['resistance_3']}",
    }
    daily_data = {
        "momentum": results['market_trend'],
        "rsi": f"{results['rsi_value']:.2f}",
        "rsi_comment": results['rsi_comment'],
        "atr": "N/A",        # Insert real ATR if computed
        "trade_setup": ai_text  # Embed the AI's response into the daily section
    }

    # Generate a human-readable report
    report = generate_report(weekly_data, daily_data)
    
    # Generate report as an image with color-coded support/resistance levels
    report_image_path = "report.png"
    create_report_image(
        report, 
        output_file=report_image_path,
        color_coding={
            "support": "green",  # Color for support levels
            "resistance": "red",  # Color for resistance levels
            "Pivot Point": "blue",  # Color for pivot points
            "trend": "blue",  # Color for the trend
        }
    )

    
    # Post the report image to Discord
    # if "discord.com/api/webhooks" in DISCORD_WEBHOOK_URL:
    #     post_image_to_discord(report_image_path, DISCORD_WEBHOOK_URL)
    # else:
    #     print("Discord Webhook URL not set or invalid. Skipping Discord post.")

    # Schedule the fetch_and_save_data function to run every hour during market hours
    schedule.every().hour.at(":00").do(fetch_and_save_data)

    print("=== Starting the scheduler ===")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()