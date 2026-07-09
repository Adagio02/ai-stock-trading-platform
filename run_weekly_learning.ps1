$ErrorActionPreference = "Stop"

Write-Host "Running weekly learning pipeline..."

python -m trading_platform.weekly_learning_pipeline

Write-Host "Weekly learning pipeline complete."