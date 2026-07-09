import os
import pandas as pd
import yfinance as yf

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from trading_platform.trade_logger import log_trade
from trading_platform.config import PAPER, TRADE_LOG_PATH

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

    trade_log = pd.read_csv(TRADE_LOG_PATH, on_bad_lines="skip")
    if trade_log.empty:
        print("Trade log is empty.")
        return

    positions = client.get_all_positions()

    for position in positions:
        ticker = position.symbol
        qty = int(float(position.qty))

        ticker_trades = trade_log[
            (trade_log["Ticker"] == ticker) &
            (trade_log["Action"] == "BUY")
        ]

        if ticker_trades.empty:
            print(f"No logged entry found for {ticker}.")
            continue

        latest_trade = ticker_trades.iloc[-1]

        stop_loss = float(latest_trade["StopLoss"])
        take_profit = float(latest_trade["TakeProfit"])
        entry_price = float(latest_trade["Price"])

        current_price = get_latest_price(ticker)
        unrealized_return = (current_price - entry_price) / entry_price

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
        elif unrealized_return >= 0.04:
            new_stop = max(stop_loss, entry_price * 1.01)
            stop_loss = new_stop
            print(f"Trailing stop moved to ${stop_loss:.2f}")

        if exit_reason:
            print(f"Selling {qty} shares of {ticker}: {exit_reason}")

            try:
                sell_position(client, ticker, qty)
            except Exception as e:
                print(f"Error submitting sell order for {ticker}: {e}")
                continue

            log_trade(
                ticker=ticker,
                action="SELL",
                shares=qty,
                price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reason=exit_reason,
                pnl=(current_price - entry_price) * qty
            )
        else:
            print("No exit triggered.")


if __name__ == "__main__":
    main()