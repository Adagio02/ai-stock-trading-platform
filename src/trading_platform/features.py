import pandas as pd
import ta


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Return"] = df["Close"].pct_change()
    df["SMA_10"] = df["Close"].rolling(10).mean()
    df["SMA_50"] = df["Close"].rolling(50).mean()
    df["Volatility"] = df["Return"].rolling(10).std()

    df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    df["MACD"] = ta.trend.MACD(df["Close"]).macd()
    df["Signal"] = ta.trend.MACD(df["Close"]).macd_signal()

    df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

    df = df.dropna()

    return df