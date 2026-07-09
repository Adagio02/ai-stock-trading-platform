$ErrorActionPreference = "Stop"

Write-Host "Running daily paper-trading bot..."

python -m trading_platform.market_screener
python -m trading_platform.auto_trader
python -m trading_platform.position_monitor

Write-Host "Daily paper-trading bot complete."