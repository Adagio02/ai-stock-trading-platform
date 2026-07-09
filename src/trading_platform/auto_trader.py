import os
import pandas as pd

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from trading_platform.risk import calculate_stop_loss, calculate_take_profit


PAPER = True
MAX_TRADES_PER_DAY = 3
MAX_POSITION_VALUE = 1000


def get_client():
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        raise ValueError("Missing ALPACA_API_KEY or ALPACA_SECRET_KEY")

    return TradingClient(api_key, secret_key, paper=PAPER)


def place_order(client, symbol, qty, side):
    order = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
        time_in_force=TimeInForce.DAY,
    )

    return client.submit_order(order)


def main():
    client = get_client()

    account = client.get_account()
    print("Account status:", account.status)

    signals = pd.read_csv("Reports/market_signals.csv")

    buy_signals = signals[signals["Signal"] == "BUY"].head(MAX_TRADES_PER_DAY)

    for _, row in buy_signals.iterrows():

        ticker = row["Ticker"]
        price = row["Close"]

        stop = calculate_stop_loss(price)
        take_profit = calculate_take_profit(price)

        qty = int(MAX_POSITION_VALUE / price)

        if qty <= 0:
            continue

        print(f"Paper buying {qty} shares of {ticker}")

        place_order(client, ticker, qty, "buy")

        trade_log = pd.DataFrame([{
            "Ticker": ticker,
            "EntryPrice": price,
            "StopLoss": stop,
            "TakeProfit": take_profit,
            "Shares": qty,
            "Signal": "BUY",
            "Time": pd.Timestamp.now()
        }])

        trade_log.to_csv(
            "Reports/trade_log.csv",
            mode="a",
            header=not os.path.exists("Reports/trade_log.csv"),
            index=False
        )

if __name__ == "__main__":
    main()