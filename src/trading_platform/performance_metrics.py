import pandas as pd
import numpy as np

df = pd.read_csv("Reports/backtest_results.csv")

returns = df["Strategy_Return"].fillna(0)

total_return = df["Equity_Curve"].iloc[-1] - 1
max_drawdown = df["Drawdown"].min()
sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
win_rate = (returns > 0).mean()

metrics = pd.DataFrame([{
    "Total Return": total_return,
    "Max Drawdown": max_drawdown,
    "Sharpe Ratio": sharpe,
    "Win Rate": win_rate
}])

metrics.to_csv("Reports/performance_metrics.csv", index=False)

print(metrics)