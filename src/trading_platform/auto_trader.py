import os
import pandas as pd

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from trading_platform.risk import (
    calculate_stop_loss,
    calculate_take_profit,
    calculate_position_size,
)
from trading_platform.trade_logger import log_trade
from trading_platform.config import (
    PAPER,
    ACCOUNT_EQUITY,
    RISK_PER_TRADE,
    MAX_LEVERAGE,
    MAX_TRADES_PER_DAY,
    MIN_ENTRY_SCORE,
    MAX_RSI,
    MIN_RETURN_20D,
    MARKET_SIGNALS_PATH,
)


def get_client():
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        raise ValueError("Missing ALPACA_API_KEY or ALPACA_SECRET_KEY")

    return TradingClient(api_key, secret_key, paper=PAPER)


def place_order(client, ticker, qty, side):
    order_request = MarketOrderRequest(
        symbol=ticker,
        qty=qty,
        side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
        time_in_force=TimeInForce.DAY,
    )

    return client.submit_order(order_request)


def main():
    client = get_client()

    account = client.get_account()
    print("Account status:", account.status)

    signals = pd.read_csv(MARKET_SIGNALS_PATH)

    buy_signals = signals[signals["Signal"] == "BUY"].copy()

    if "EntryScore" in buy_signals.columns:
        buy_signals = buy_signals[buy_signals["EntryScore"] >= MIN_ENTRY_SCORE]

    if "RSI" in buy_signals.columns:
        buy_signals = buy_signals[buy_signals["RSI"] < MAX_RSI]

    if "Return_20D" in buy_signals.columns:
        buy_signals = buy_signals[buy_signals["Return_20D"] > MIN_RETURN_20D]

    sort_columns = [
        col for col in ["EntryScore", "Return_20D"] if col in buy_signals.columns
    ]

    if sort_columns:
        buy_signals = buy_signals.sort_values(sort_columns, ascending=False)

    buy_signals = buy_signals.head(MAX_TRADES_PER_DAY)

    if buy_signals.empty:
        print("No qualified buy signals today.")
        return

    for _, row in buy_signals.iterrows():
        ticker = row["Ticker"]
        price = float(row["Close"])

        atr = row["ATR"] if "ATR" in row and pd.notna(row["ATR"]) else None

        stop = calculate_stop_loss(price, atr=atr)
        take_profit = calculate_take_profit(price, stop)

        qty = calculate_position_size(
            account_equity=ACCOUNT_EQUITY,
            risk_per_trade=RISK_PER_TRADE,
            entry_price=price,
            stop_loss_price=stop,
            max_leverage=MAX_LEVERAGE,
        )

        if qty <= 0:
            print(f"Skipping {ticker}: position size was 0")
            continue

        print(f"Paper buying {qty} shares of {ticker}")
        print(f"Entry: ${price:.2f}, Stop: ${stop:.2f}, Target: ${take_profit:.2f}")

        place_order(client, ticker, qty, "buy")

        log_trade(
            ticker=ticker,
            action="BUY",
            shares=qty,
            price=price,
            stop_loss=stop,
            take_profit=take_profit,
            reason="AI Buy Signal",
            pnl=None,
        )


if __name__ == "__main__":
    main()