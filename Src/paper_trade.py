import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce


def place_paper_order(symbol: str, qty: int, side: str):
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        raise ValueError("Missing Alpaca API credentials.")

    trading_client = TradingClient(
        api_key,
        secret_key,
        paper=True
    )

    order = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
        time_in_force=TimeInForce.DAY,
    )

    return trading_client.submit_order(order)