# ml_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def train_random_forest(df, test_days=180):
    """
    1) Splits data into train/test by date (last `test_days` are test).
    2) Trains a RandomForestClassifier to predict 'Target' from the feature set.
    Returns the model, plus performance metrics.
    """
    # Make sure we have enough data
    if len(df) < (test_days + 100):
        print("[WARN] Not enough data for a robust train/test. Proceeding anyway.")
    
    # Sort by index (date) just in case
    df = df.sort_index()
    
    # Decide which columns are features
    feature_cols = [
        "RSI_14", "MACD", "MACD_signal", "SMA_50", "SMA_200", "BB_upper", "BB_lower", "ATR_14", 
        "Open", "High", "Low", "Close", "Volume"
    ]
    df_features = df[feature_cols].copy()
    df_target = df["Target"].copy()
    
    # Split
    train_cutoff = df.index[-test_days]  # approximate
    df_train = df[df.index < train_cutoff]
    df_test  = df[df.index >= train_cutoff]
    
    X_train = df_train[feature_cols]
    y_train = df_train["Target"]
    X_test = df_test[feature_cols]
    y_test = df_test["Target"]
    
    rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf.fit(X_train, y_train)
    
    # Evaluate
    train_preds = rf.predict(X_train)
    test_preds = rf.predict(X_test)
    
    train_acc = accuracy_score(y_train, train_preds)
    test_acc  = accuracy_score(y_test, test_preds)
    
    metrics = {
        "train_accuracy": train_acc,
        "test_accuracy": test_acc,
        "train_size": len(df_train),
        "test_size": len(df_test)
    }
    
    return rf, metrics
