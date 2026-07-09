Write-Host "Running market screener..."
python -m trading_platform.market_screener

Write-Host "Optimizing portfolio..."
python -m trading_platform.portfolio_optimizer

Write-Host "Running walk-forward backtest..."
python -m trading_platform.walk_forward

Write-Host "Calculating performance metrics..."
python -m trading_platform.performance_metrics

Write-Host "Generating SHAP explanations..."
python -m trading_platform.shap_explainer

Write-Host "Launching Streamlit..."
streamlit run app/app.py