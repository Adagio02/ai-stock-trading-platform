from pathlib import Path
import pandas as pd

REPORTS_DIR = Path("Reports")
TRADE_LOG_PATH = REPORTS_DIR / "trade_log.csv"

REPORTS_DIR.mkdir(exist_ok=True)


def log_trade(
    ticker,
    action,
    shares,
    price,
    stop_loss=None,
    take_profit=None,
    reason=None,
    pnl=None
):
    row = pd.DataFrame([{
        "Time": pd.Timestamp.now(),
        "Ticker": ticker,
        "Action": action,
        "Shares": shares,
        "Price": price,
        "StopLoss": stop_loss,
        "TakeProfit": take_profit,
        "Reason": reason,
        "PnL": pnl
    }])

    row.to_csv(
        TRADE_LOG_PATH,
        mode="a",
        header=not TRADE_LOG_PATH.exists(),
        index=False
    )