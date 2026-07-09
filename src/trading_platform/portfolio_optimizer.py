import pandas as pd
import numpy as np
import yfinance as yf
from scipy.optimize import minimize
from pathlib import Path

Path("Reports").mkdir(exist_ok=True)

signals = pd.read_csv("Reports/market_signals.csv")
tickers = signals[signals["Signal"] == "BUY"]["Ticker"].head(10).tolist()

prices = yf.download(tickers, period="2y", auto_adjust=True, progress=False)["Close"]
returns = prices.pct_change().dropna()

mean_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252

num_assets = len(tickers)


def portfolio_volatility(weights):
    return np.sqrt(weights.T @ cov_matrix @ weights)


constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
bounds = tuple((0, 0.25) for _ in range(num_assets))
initial_weights = np.array([1 / num_assets] * num_assets)

result = minimize(
    portfolio_volatility,
    initial_weights,
    method="SLSQP",
    bounds=bounds,
    constraints=constraints
)

weights = result.x

portfolio = pd.DataFrame({
    "Ticker": tickers,
    "Weight": weights
}).sort_values("Weight", ascending=False)

portfolio.to_csv("Reports/optimized_portfolio.csv", index=False)

print(portfolio)