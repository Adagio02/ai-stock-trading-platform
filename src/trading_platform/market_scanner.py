import pandas as pd
import yfinance as yf
from pathlib import Path

Path("Reports").mkdir(exist_ok=True)

tickers = pd.read_csv("Data/tickers.csv")["Ticker"].tolist()

results = []

for ticker in tickers:
    try:
        df = yf.download(ticker, period="1y", auto_adjust=True, progress=False)

        if df.empty:
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        df["SMA_20"] = df["Close"].rolling(20).mean()
        df["SMA_50"] = df["Close"].rolling(50).mean()
        df["Return_5D"] = df["Close"].pct_change(5)
        df["Return_20D"] = df["Close"].pct_change(20)

        latest = df.iloc[-1]

        signal = "HOLD"

        if latest["SMA_20"] > latest["SMA_50"] and latest["Return_20D"] > 0:
            signal = "BUY"
        elif latest["SMA_20"] < latest["SMA_50"]:
            signal = "SELL"

        results.append({
            "Ticker": ticker,
            "Close": latest["Close"],
            "SMA_20": latest["SMA_20"],
            "SMA_50": latest["SMA_50"],
            "Return_5D": latest["Return_5D"],
            "Return_20D": latest["Return_20D"],
            "Signal": signal
        })

    except Exception as e:
        print(f"Error with {ticker}: {e}")

        BAD_TICKERS = ["DAY", "HOLX", "SEE", "CTRA"]

tickers = [t for t in tickers if t not in BAD_TICKERS]

signals = pd.DataFrame(results)
signals = signals.sort_values("Return_20D", ascending=False)
signals.to_csv("Reports/market_signals.csv", index=False)

print(signals.head(20))