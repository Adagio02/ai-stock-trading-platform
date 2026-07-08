from trading_platform.risk import calculate_position_size

def test_position_size_positive():
    shares = calculate_position_size(
        account_equity=10000,
        risk_per_trade=0.01,
        entry_price=100,
        stop_loss_price=95,
        max_leverage=1.0
    )
    assert shares > 0