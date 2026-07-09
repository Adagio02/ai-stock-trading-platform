$LogFile = "Reports\daily_bot_log.txt"

Start-Transcript -Path $LogFile -Append

Write-Host "Starting Daily Trading Bot..."
Write-Host "Time: $(Get-Date)"

python -m trading_platform.market_screener

python -m trading_platform.auto_trader

python -m trading_platform.position_monitor

Write-Host "Finished Daily Trading Bot"

Stop-Transcript