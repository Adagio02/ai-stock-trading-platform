import os
import pandas as pd
import yfinance as yf

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce


PAPER = True
TRADE_LOG_PATH = "Reports/trade_log.csv"


def get_client():
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        raise ValueError("Missing ALPACA_API_KEY or ALPACA_SECRET_KEY")

    return TradingClient(api_key, secret_key, paper=PAPER)


def sell_position(client, symbol, qty):
    order = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.DAY,
    )

    return client.submit_order(order)


def get_latest_price(symbol):
    df = yf.download(symbol, period="5d", auto_adjust=True, progress=False)

    if df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    return float(df["Close"].iloc[-1])


def main():
    client = get_client()

    if not os.path.exists(TRADE_LOG_PATH):
        print("No trade log found.")
        return

    trade_log = pd.read_csv(TRADE_LOG_PATH)

    if trade_log.empty:
        print("Trade log is empty.")
        return

    positions = client.get_all_positions()

    for position in positions:
        ticker = position.symbol
        qty = int(float(position.qty))

        ticker_trades = trade_log[
            (trade_log["Ticker"] == ticker) &
            (trade_log["Signal"] == "BUY")
        ]

        if ticker_trades.empty:
            print(f"No logged entry found for {ticker}.")
            continue

        latest_trade = ticker_trades.iloc[-1]

        stop_loss = float(latest_trade["StopLoss"])
        take_profit = float(latest_trade["TakeProfit"])
        entry_price = float(latest_trade["EntryPrice"])

        current_price = get_latest_price(ticker)

        if current_price is None:
            print(f"Could not get price for {ticker}.")
            continue

        print(f"\n{ticker}")
        print(f"Entry: ${entry_price:.2f}")
        print(f"Current: ${current_price:.2f}")
        print(f"Stop Loss: ${stop_loss:.2f}")
        print(f"Take Profit: ${take_profit:.2f}")

        exit_reason = None

        if current_price <= stop_loss:
            exit_reason = "Stop Loss Hit"

        elif current_price >= take_profit:
            exit_reason = "Take Profit Hit"

        if exit_reason:
            print(f"Selling {qty} shares of {ticker}: {exit_reason}")

            sell_position(client, ticker, qty)

            exit_log = pd.DataFrame([{
                "Ticker": ticker,
                "EntryPrice": entry_price,
                "ExitPrice": current_price,
                "StopLoss": stop_loss,
                "TakeProfit": take_profit,
                "Shares": qty,
                "Signal": "SELL",
                "Reason": exit_reason,
                "PnL": (current_price - entry_price) * qty,
                "Time": pd.Timestamp.now()
            }])

            exit_log.to_csv(
                TRADE_LOG_PATH,
                mode="a",
                header=False,
                index=False
            )
        else:
            print("No exit triggered.")


if __name__ == "__main__":
    main()