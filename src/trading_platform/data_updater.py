from pathlib import Path
import pandas as pd
import yfinance as yf

DATA_DIR = Path("Data")
REPORTS_DIR = Path("Reports")

DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


def clean_ticker(ticker):
    return str(ticker).strip().replace(".", "-")


def load_tickers():
    path = DATA_DIR / "nasdaq100_latest_symbols.csv"

    df = pd.read_csv(path)

    for col in ["Ticker", "Symbol", "Ticker Symbol"]:
        if col in df.columns:
            return df[col].dropna().astype(str).str.strip().tolist()

    raise ValueError(f"No ticker column found. Columns: {df.columns.tolist()}")


def download_latest_data(period="5y"):
    tickers = load_tickers()
    rows = []

    for ticker in tickers:
        ticker = clean_ticker(ticker)

        try:
            df = yf.download(
                ticker,
                period=period,
                auto_adjust=True,
                progress=False,
                threads=False
            )

            if df.empty:
                print(f"Skipping {ticker}: no data")
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]

            df = df.reset_index()
            df["Ticker"] = ticker

            df.to_csv(DATA_DIR / f"{ticker}_prices.csv", index=False)
            rows.append(df)

            print(f"Downloaded {ticker}")

        except Exception as e:
            print(f"Skipped {ticker}: {e}")

    if rows:
        combined = pd.concat(rows, ignore_index=True)
        combined.to_csv(REPORTS_DIR / "all_market_data.csv", index=False)
        print("Saved Reports/all_market_data.csv")


if __name__ == "__main__":
    download_latest_data()