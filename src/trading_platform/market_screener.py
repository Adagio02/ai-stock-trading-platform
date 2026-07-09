import pandas as pd
import yfinance as yf
from pathlib import Path

from trading_platform.index_loader import load_tickers
from trading_platform.config import (
    NASDAQ_SYMBOLS_PATH,
    SP500_SYMBOLS_PATH,
    MARKET_SIGNALS_PATH,
    MIN_RSI,
    MAX_RSI,
    MIN_RETURN_20D,
    MAX_VOLATILITY,
    MIN_ENTRY_SCORE,
)


def clean_ticker(ticker):
    return str(ticker).strip().replace(".", "-")


def main():
    Path("Reports").mkdir(exist_ok=True)

    nasdaq_tickers = load_tickers(NASDAQ_SYMBOLS_PATH)
    sp500_tickers = load_tickers(SP500_SYMBOLS_PATH)

    tickers = sorted(set(nasdaq_tickers + sp500_tickers))

    bad_tickers = ["CTRA", "DAY", "HOLX", "SEE"]
    tickers = [t for t in tickers if clean_ticker(t) not in bad_tickers]

    rows = []

    for ticker in tickers:
        ticker = clean_ticker(ticker)

        try:
            df = yf.download(
                ticker,
                period="1y",
                auto_adjust=True,
                progress=False,
                threads=False,
            )

            if df.empty:
                print(f"Skipping {ticker}: no data returned")
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]

            if "Close" not in df.columns or len(df) < 200:
                print(f"Skipping {ticker}: not enough usable price data")
                continue

            df["SMA_20"] = df["Close"].rolling(20).mean()
            df["SMA_50"] = df["Close"].rolling(50).mean()
            df["SMA_200"] = df["Close"].rolling(200).mean()
            df["Return_5D"] = df["Close"].pct_change(5)
            df["Return_20D"] = df["Close"].pct_change(20)
            df["Volatility"] = df["Close"].pct_change().rolling(20).std()
            df["Volume_20"] = df["Volume"].rolling(20).mean()

            df["High_Low"] = df["High"] - df["Low"]
            df["High_Close"] = abs(df["High"] - df["Close"].shift(1))
            df["Low_Close"] = abs(df["Low"] - df["Close"].shift(1))
            df["True_Range"] = df[["High_Low", "High_Close", "Low_Close"]].max(axis=1)
            df["ATR"] = df["True_Range"].rolling(14).mean()

            delta = df["Close"].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            df["RSI"] = 100 - (100 / (1 + rs))

            df["Breakout_20"] = df["Close"] >= df["Close"].rolling(20).max() * 0.98

            latest = df.iloc[-1]

            trend_filter = latest["Close"] > latest["SMA_200"]
            short_trend_filter = latest["SMA_20"] > latest["SMA_50"]
            momentum_filter = latest["Return_20D"] > MIN_RETURN_20D
            rsi_filter = MIN_RSI <= latest["RSI"] <= MAX_RSI
            volume_filter = latest["Volume"] > latest["Volume_20"]
            breakout_filter = latest["Breakout_20"]
            volatility_filter = latest["Volatility"] < MAX_VOLATILITY

            entry_score = sum([
                trend_filter,
                short_trend_filter,
                momentum_filter,
                rsi_filter,
                volume_filter,
                breakout_filter,
                volatility_filter,
            ])

            if entry_score >= MIN_ENTRY_SCORE:
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
                "SMA_200": latest["SMA_200"],
                "Return_5D": latest["Return_5D"],
                "Return_20D": latest["Return_20D"],
                "Volatility": latest["Volatility"],
                "RSI": latest["RSI"],
                "Volume_20": latest["Volume_20"],
                "ATR": latest["ATR"],
                "EntryScore": entry_score,
                "Signal": signal,
            })

        except Exception as e:
            print(f"Skipped {ticker}: {e}")

    signals = pd.DataFrame(rows)

    if signals.empty:
        print("No signals generated.")
        return

    signals = signals.sort_values("Return_20D", ascending=False)
    signals.to_csv(MARKET_SIGNALS_PATH, index=False)

    print(signals.head(25))


if __name__ == "__main__":
    main()