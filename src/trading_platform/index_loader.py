import pandas as pd
from pathlib import Path


def load_tickers(path):

    path = Path(path)

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)

    elif path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(path)

    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    possible_columns = [
        "Ticker",
        "Symbol",
        "Ticker Symbol"
    ]

    for col in possible_columns:

        if col in df.columns:
            return (
                df[col]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            )

    raise ValueError(
        f"Could not find ticker column.\nColumns found:\n{df.columns.tolist()}"
    )