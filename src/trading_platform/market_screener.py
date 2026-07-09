import pandas as pd
import yfinance as yf
from pathlib import Path
from trading_platform.index_loader import load_tickers

Path("Reports").mkdir(exist_ok=True)

def clean_ticker(ticker):
    return str(ticker).strip().replace(".", "-")

nasdaq_tickers = load_tickers("Data/nasdaq100_latest_symbols.csv")
tickers = nasdaq_tickers
sp500_tickers = load_tickers("Data/sp500_Historical_Data.csv")

tickers = sorted(set(nasdaq_tickers + sp500_tickers))



rows = []

for ticker in tickers:
    ticker = clean_ticker(ticker)

    try:
        df = yf.download(
            ticker,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            print(f"Skipping {ticker}: no data returned")
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        if "Close" not in df.columns or len(df) < 50:
            print(f"Skipping {ticker}: not enough usable price data")
            continue

        df["SMA_20"] = df["Close"].rolling(20).mean()
        df["SMA_50"] = df["Close"].rolling(50).mean()
        df["Return_5D"] = df["Close"].pct_change(5)
        df["Return_20D"] = df["Close"].pct_change(20)
        df["Volatility"] = df["Close"].pct_change().rolling(20).std()

        latest = df.iloc[-1]

        if latest["SMA_20"] > latest["SMA_50"] and latest["Return_20D"] > 0:
            signal = "BUY"
        elif latest["SMA_20"] < latest["SMA_50"]:
            signal = "SELL"
        else:
            signal = "HOLD"

        rows.append({
            "Ticker": ticker,
            "Close": latest["Close"],
            "SMA_20": latest["SMA_20"],
            "SMA_50": latest["SMA_50"],
            "Return_5D": latest["Return_5D"],
            "Return_20D": latest["Return_20D"],
            "Volatility": latest["Volatility"],
            "Signal": signal
        })

    except Exception as e:
        print(f"Skipped {ticker}: {e}")

signals = pd.DataFrame(rows)
signals = signals.sort_values("Return_20D", ascending=False)
signals.to_csv("Reports/market_signals.csv", index=False)

print(signals.head(25))