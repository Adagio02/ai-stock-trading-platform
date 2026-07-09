from trading_platform.config import (
    STOP_PERCENT,
    ATR_MULTIPLIER,
    REWARD_RISK_RATIO,
)


def calculate_position_size(
    account_equity: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss_price: float,
    max_leverage: float = 1.0,
) -> int:
    risk_amount = account_equity * risk_per_trade
    per_share_risk = abs(entry_price - stop_loss_price)

    if per_share_risk <= 0:
        return 0

    shares_by_risk = risk_amount / per_share_risk
    shares_by_leverage = (account_equity * max_leverage) / entry_price

    shares = int(min(shares_by_risk, shares_by_leverage))

    return max(shares, 0)


def calculate_stop_loss(
    entry_price: float,
    atr: float | None = None,
    stop_percent: float = STOP_PERCENT,
) -> float:
    if atr is not None and atr > 0:
        return round(entry_price - (ATR_MULTIPLIER * atr), 2)

    return round(entry_price * (1 - stop_percent), 2)


def calculate_take_profit(
    entry_price: float,
    stop_loss_price: float,
    reward_risk_ratio: float = REWARD_RISK_RATIO,
) -> float:
    risk = entry_price - stop_loss_price
    return round(entry_price + (risk * reward_risk_ratio), 2)