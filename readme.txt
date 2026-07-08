# AI Stock Trading Platform

## Goal
Build a machine learning trading research dashboard with historical data, technical indicators, model comparison, backtesting, and paper-trading readiness.

## Features
- Historical stock data download
- Technical indicators
- Random Forest and XGBoost classifiers
- Automatic model comparison
- Walk-forward style train/test split
- Backtesting
- Equity curve
- Drawdown chart
- Risk management calculator
- Streamlit dashboard

## Important Disclaimer
This project is for educational and paper-trading purposes only. It is not financial advice.

## How to Run
pip install -r requirements.txt
python Src/train_models.py
python Src/backtest.py
streamlit run app/app.py