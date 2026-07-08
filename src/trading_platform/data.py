import yfinance as yf
import pandas as pd
from pathlib import Path


def download_data(ticker: str = "AAPL", period: str = "5y") -> pd.DataFrame:
    df = yf.download(ticker, period=period, auto_adjust=True)

    if df.empty:
        raise ValueError(f"No data downloaded for {ticker}")

    df = df.reset_index()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    Path("Data").mkdir(exist_ok=True)
    df.to_csv(f"Data/{ticker}_prices.csv", index=False)

    return df